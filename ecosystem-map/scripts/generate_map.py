#!/usr/bin/env python3
"""Regenerate the ATScience Ecosystem Map HTML from the Notion projects database.

Reads every row of the "atproto.science Projects List" Notion database where
"Show on map" is checked, and rewrites the CATEGORIES/PROJECTS data block in
source/ATScience Ecosystem Map.dc.html to match.

Usage:
    set -a && source secrets.env && set +a
    python3 scripts/generate_map.py

Requires NOTION_TOKEN and NOTION_DATABASE_ID (or --token / --database-id) —
see secrets.env (gitignored, not part of this repo). The token must belong to
a Notion integration that has been shared with that database.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

NOTION_VERSION = "2022-06-28"
DEFAULT_HTML_PATH = os.path.join(
    os.path.dirname(__file__), "..", "source", "ATScience Ecosystem Map.dc.html"
)

# Accent colors for the categories that exist today. Any category found in
# Notion that isn't listed here still renders, using a color picked from
# FALLBACK_HUES so a newly-added category never breaks generation.
CATEGORY_ACCENTS = {
    "Annotation & knowledge tools": "oklch(0.55 0.15 255)",
    "Publishing": "oklch(0.58 0.14 62)",
    "Data": "oklch(0.55 0.15 305)",
    "Social apps for researchers": "oklch(0.53 0.13 150)",
    "Evaluation": "oklch(0.54 0.14 15)",
    "Citizen science": "oklch(0.50 0.13 135)",
    "AI": "oklch(0.54 0.12 205)",
    "Feeds": "oklch(0.55 0.12 180)",
    "Hosting": "oklch(0.54 0.14 275)",
    "Networking": "oklch(0.55 0.15 335)",
    "Funding": "oklch(0.55 0.15 30)",
    "Version control": "oklch(0.52 0.11 110)",
    "Communities": "oklch(0.55 0.13 95)",
}
CATEGORY_ORDER = list(CATEGORY_ACCENTS.keys())
FALLBACK_HUES = [10, 50, 90, 130, 170, 210, 250, 290, 330]

STATUS_KEYS = {
    "Live": "live",
    "In development": "in-development",
    "Beta": "beta",
    "Alpha": "alpha",
    "Code": "code",
    "Concept": "concept",
    "Coming soon": "coming-soon",
}

# Used to sort projects within a category by status. Overridden at runtime by
# the live order of the Status select's options in Notion when reachable;
# falls back to this hard-coded order otherwise.
STATUS_ORDER_FALLBACK = ["Live", "Code", "In development", "Concept", "Beta", "Alpha", "Coming soon"]

BLOCK_RE = re.compile(r"const CATEGORIES = \{.*?\n\};\n\nconst PROJECTS = \[.*?\n\];", re.DOTALL)


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def accent_for(label, already_assigned):
    if label in CATEGORY_ACCENTS:
        return CATEGORY_ACCENTS[label]
    hue = FALLBACK_HUES[len(already_assigned) % len(FALLBACK_HUES)]
    return f"oklch(0.55 0.13 {hue})"


def notion_request(token, path, payload):
    req = urllib.request.Request(
        f"https://api.notion.com/v1{path}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Notion API error {e.code}: {e.read().decode()}")


def fetch_rows(token, database_id):
    rows = []
    cursor = None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        data = notion_request(token, f"/databases/{database_id}/query", payload)
        rows.extend(data["results"])
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return rows


def fetch_status_order(token, database_id):
    """Live order of the Status select's options in Notion, or None if unreachable."""
    req = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{database_id}",
        headers={"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
        options = data["properties"]["Status"]["select"]["options"]
        return [opt["name"] for opt in options]
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TypeError):
        return None


def plain_text(prop):
    if not prop:
        return ""
    kind = prop.get("type")
    if kind in ("title", "rich_text"):
        return "".join(t.get("plain_text", "") for t in prop.get(kind, []))
    return ""


def select_name(prop):
    if not prop or prop.get("type") != "select" or not prop.get("select"):
        return None
    return prop["select"]["name"]


def url_value(prop):
    if not prop or prop.get("type") != "url":
        return None
    return prop.get("url") or None


def checkbox_value(prop):
    return bool(prop and prop.get("type") == "checkbox" and prop.get("checkbox"))


def project_from_page(page):
    props = page["properties"]
    name = plain_text(props.get("Project title")) or plain_text(props.get("Name"))
    status = select_name(props.get("Status"))
    return {
        "name": name,
        "category": select_name(props.get("Category")),
        "description": plain_text(props.get("Project description")),
        "url": url_value(props.get("URL")),
        "repo": url_value(props.get("Repo")),
        "icon": url_value(props.get("Icon override")),
        "handle": plain_text(props.get("Bluesky handle")) or None,
        "status": STATUS_KEYS.get(status, "concept"),
    }


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def build_categories_block(categories, category_keys):
    lines = ["const CATEGORIES = {"]
    for label, accent in categories.items():
        lines.append(f'  {js_string(category_keys[label])}: {{ label: {js_string(label)}, accent: "{accent}" }},')
    lines.append("};")
    return "\n".join(lines)


def build_projects_block(projects, category_keys):
    lines = ["const PROJECTS = ["]
    for p in projects:
        fields = [
            f"name: {js_string(p['name'])}",
            f"category: {js_string(category_keys[p['category']])}",
            f"description: {js_string(p['description'])}",
        ]
        if p["url"]:
            fields.append(f"url: {js_string(p['url'])}")
        if p["repo"]:
            fields.append(f"repo: {js_string(p['repo'])}")
        if p["icon"]:
            fields.append(f"icon: {js_string(p['icon'])}")
        if p["handle"]:
            fields.append(f"handle: {js_string(p['handle'])}")
        fields.append(f"status: {js_string(p['status'])}")
        lines.append("  { " + ", ".join(fields) + " },")
    lines.append("];")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.environ.get("NOTION_TOKEN"), help="Notion integration token (defaults to $NOTION_TOKEN)")
    parser.add_argument("--database-id", default=os.environ.get("NOTION_DATABASE_ID"), help="Notion database ID to read from (defaults to $NOTION_DATABASE_ID)")
    parser.add_argument("--html-path", default=DEFAULT_HTML_PATH, help="Path to the .dc.html file to update")
    args = parser.parse_args()

    if not args.token:
        sys.exit("Set NOTION_TOKEN (or pass --token) to a Notion integration token shared with the Projects List database.")
    if not args.database_id:
        sys.exit("Set NOTION_DATABASE_ID (or pass --database-id) to the target Notion database ID.")

    rows = fetch_rows(args.token, args.database_id)

    projects = []
    for page in rows:
        if not checkbox_value(page["properties"].get("Show on map")):
            continue
        p = project_from_page(page)
        if not p["name"] or not p["category"]:
            print(f"Skipping row missing name/category: {page['id']}", file=sys.stderr)
            continue
        projects.append(p)

    status_order_labels = fetch_status_order(args.token, args.database_id) or STATUS_ORDER_FALLBACK
    status_rank = {}
    for idx, label in enumerate(status_order_labels):
        key = STATUS_KEYS.get(label)
        if key and key not in status_rank:
            status_rank[key] = idx
    unranked = len(status_order_labels)

    projects.sort(
        key=lambda p: (
            CATEGORY_ORDER.index(p["category"]) if p["category"] in CATEGORY_ORDER else len(CATEGORY_ORDER),
            status_rank.get(p["status"], unranked),
            p["name"],
        )
    )

    categories = {}
    for p in projects:
        if p["category"] not in categories:
            categories[p["category"]] = accent_for(p["category"], categories)
    ordered_categories = {k: categories[k] for k in CATEGORY_ORDER if k in categories}
    for label, accent in categories.items():
        ordered_categories.setdefault(label, accent)

    category_keys = {label: slug(label) for label in ordered_categories}

    new_block = (
        build_categories_block(ordered_categories, category_keys)
        + "\n\n"
        + build_projects_block(projects, category_keys)
    )

    with open(args.html_path, "r", encoding="utf-8") as f:
        html = f.read()

    if not BLOCK_RE.search(html):
        sys.exit("Could not find the CATEGORIES/PROJECTS block in the HTML file.")
    html = BLOCK_RE.sub(new_block, html, count=1)

    with open(args.html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote {len(projects)} projects across {len(ordered_categories)} categories to {args.html_path}")


if __name__ == "__main__":
    main()
