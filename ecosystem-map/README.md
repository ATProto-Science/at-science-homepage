# ATScience Ecosystem Map

An interactive map of the AT Protocol science ecosystem. The source lives at
`source/ATScience Ecosystem Map.dc.html` and is served as-is (via passthrough
copy in `eleventy.config.js`) at
[atproto.science/ecosystem](https://atproto.science/ecosystem), alongside
[atproto.science/projects](https://atproto.science/projects/) — the two pages
are kept side by side for now, not as a replacement.

The map's project list is generated from a Notion database, not hand-edited.

## How it fits together

- **Notion DB** — the "🚀 atproto.science Projects List" database is the
  source of truth for which projects appear on the map and their metadata.
  Its URL/ID is not published in this repo; see `secrets.env` (gitignored) or
  ask a maintainer for access.
- **`scripts/generate_map.py`** — reads the DB via the Notion API and rewrites
  the `CATEGORIES` / `PROJECTS` data block inside the `.dc.html` file. This is
  the only part of the HTML file you should regenerate rather than hand-edit;
  everything else (layout, styling, component logic) is edited directly.
- **`source/ATScience Ecosystem Map.dc.html`** — the map itself, built with
  [Dropcode](https://dropcode.dev)'s `.dc.html` component format.

## Notion DB schema

Only rows with **Show on map** checked are included in the generated output.

| Property | Type | Used as |
|---|---|---|
| `Project title` | text | Display name (falls back to `Name` if blank) |
| `Project description` | text | Card/panel description |
| `Category` | select | Category grouping — label shown as-is; a URL-safe key is derived automatically |
| `Status` | select | Status badge — order of options in Notion controls sort order within a category |
| `URL` | url | Website link + favicon probing |
| `Repo` | url | Optional "Repo ↗" link |
| `Bluesky handle` | text | Optional `@handle` link to the Bluesky profile |
| `Icon override` | url | Optional explicit icon, skips favicon probing |
| `Show on map` | checkbox | Whether the row is included in the generated map |

New `Category` options don't need any code changes — the script assigns them
a fallback accent color automatically. To give a category the "real" hand
picked accent color used elsewhere, add it to `CATEGORY_ACCENTS` in
`scripts/generate_map.py`.

`Status` is not dynamic the same way: a new option added in Notion will
silently render as "Concept" until it's added to `STATUS_KEYS` in
`scripts/generate_map.py` *and* to the `STATUS` object in the `.dc.html`
file (label + badge colors).

## Regenerating the map from Notion

1. You need a Notion integration token with access to the Projects List
   database, and that database's ID. Ask a maintainer for both, then create
   `secrets.env` (gitignored, never commit it) with:

   ```
   NOTION_TOKEN=secret_xxx
   NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

2. Run the generator:

   ```bash
   set -a && source secrets.env && set +a
   python3 scripts/generate_map.py
   ```

   This overwrites the `CATEGORIES` / `PROJECTS` block in
   `source/ATScience Ecosystem Map.dc.html` in place; the rest of the file is
   untouched.

3. Review the diff (`git diff`) before committing — Notion edits (typos,
   category reassignments, newly-checked "Show on map" rows, etc.) flow
   straight through.

### Useful flags

```bash
python3 scripts/generate_map.py --token secret_xxx   # instead of $NOTION_TOKEN
python3 scripts/generate_map.py --database-id <id>   # point at a different DB
python3 scripts/generate_map.py --html-path <path>   # write to a different file
```

## Editing the map by hand

Anything outside the `CATEGORIES` / `PROJECTS` block — layout, styling,
component behavior — is edited directly in the `.dc.html` file. Just don't
hand-edit project entries themselves; they'll be overwritten on the next
`generate_map.py` run. Make those changes in Notion instead.
