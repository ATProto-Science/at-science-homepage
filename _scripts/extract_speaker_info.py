#!/usr/bin/env python3
"""
Extract speaker information from ATScience proposal CSV files.

This script reads the Tally form CSV containing speaker proposals and extracts
the information needed to add speakers to the website.

Usage:
    python extract_speaker_info.py <speaker_name1> [<speaker_name2> ...]

Example:
    python extract_speaker_info.py "Travis Simpson" "Scott McGrath" "Jay Patel"
"""

import csv
import sys
from pathlib import Path

def find_csv_file(directory="_data"):
    """Find the Tally form CSV file in the specified directory."""
    data_dir = Path(directory)
    csv_files = list(data_dir.glob("*Tally*.csv"))

    if not csv_files:
        print(f"Error: No Tally form CSV found in {directory}/")
        sys.exit(1)

    # Prefer non-_all version
    for csv_file in csv_files:
        if not csv_file.name.endswith("_all.csv"):
            return csv_file

    return csv_files[0]

def extract_speaker_info(csv_file, speaker_names):
    """Extract information for specified speakers from CSV."""
    speakers = {}

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            full_name = row.get('Full Name', '').strip()

            # Check if this row matches any requested speaker
            for speaker_name in speaker_names:
                if speaker_name.lower() in full_name.lower():
                    speakers[full_name] = {
                        'name': full_name,
                        'title': row.get('Title', '').strip(),
                        'country': row.get('Country', '').strip(),
                        'bluesky': row.get('ATproto ID', '').strip(),
                        'role': row.get('Role/Title', '').strip(),
                        'tagline': row.get('Proposal Tagline', '').strip(),
                        'description': row.get('Description', '').strip(),
                        'proposal_type': row.get('Proposal Type', '').strip(),
                    }

    return speakers

def format_bluesky_url(atproto_id):
    """Format ATproto ID into full Bluesky URL."""
    if not atproto_id:
        return ""

    # Remove @ if present
    handle = atproto_id.lstrip('@')
    return f"https://bsky.app/profile/{handle}"

def format_speaker_slug(name):
    """Convert speaker name to slug format (e.g., 'Travis Simpson' -> 'travis-simpson')."""
    return name.lower().replace(' ', '-').replace('.', '')

def generate_speaker_card(speaker_info):
    """Generate HTML for speaker card."""
    name = speaker_info['name']
    slug = format_speaker_slug(name)
    bluesky_url = format_bluesky_url(speaker_info['bluesky'])
    role = speaker_info['role']

    # Try to infer affiliation (this would need manual adjustment)
    affiliation = "[Affiliation]"

    return f"""
  <!-- Speaker: {name} -->
  <div style="text-align: center;">
    <div style="position: relative; display: inline-block;">
      <img src="/assets/images/atscience26-speakers/{slug.replace(' ', '_')}.jpg" alt="Photo of {name}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
      <button class="speaker-info-btn"
              data-speaker="{slug}"
              aria-label="View talk information for {name}"
              style="position: absolute; top: 0; right: 0; background: rgba(0, 0, 128, 0.9); border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; color: white; cursor: pointer; font-weight: bold; font-size: 18px;">
        i
      </button>
    </div>
    <h3 class="govuk-heading-s" style="margin-bottom: 0.25rem;">
      <a href="{bluesky_url}" class="govuk-link" target="_blank">{name}</a>
    </h3>
    <p class="govuk-body-s" style="margin-bottom: 0.25rem; color: #505a5f;">{role}</p>
    <p class="govuk-body-s" style="color: #505a5f;">{affiliation}</p>
  </div>
"""

def generate_speaker_dialog(speaker_info):
    """Generate HTML for speaker dialog."""
    name = speaker_info['name']
    slug = format_speaker_slug(name)
    bluesky_url = format_bluesky_url(speaker_info['bluesky'])
    role = speaker_info['role']
    affiliation = "[Affiliation]"
    tagline = speaker_info['tagline']
    description = speaker_info['description']

    return f"""
<dialog id="dialog-{slug}" class="speaker-dialog" aria-labelledby="dialog-{slug}-title">
  <div class="speaker-dialog-content">
    <div class="speaker-dialog-header">
      <h2 id="dialog-{slug}-title" class="govuk-heading-m">{name}</h2>
      <button class="speaker-dialog-close" aria-label="Close dialog" autofocus>
        <span aria-hidden="true">×</span>
      </button>
    </div>
    <div class="speaker-dialog-body">
      <p class="govuk-body-s" style="color: #505a5f; margin-bottom: 1rem;">
        {role}, {affiliation}
      </p>
      <h3 class="govuk-heading-s">{tagline}</h3>
      <p class="govuk-body">
        {description}
      </p>
      <p class="govuk-body" style="margin-top: 1rem;">
        <a href="{bluesky_url}" class="govuk-link" target="_blank">View profile on Bluesky</a>
      </p>
    </div>
  </div>
</dialog>
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_speaker_info.py <speaker_name1> [<speaker_name2> ...]")
        print('Example: python extract_speaker_info.py "Travis Simpson" "Scott McGrath"')
        sys.exit(1)

    speaker_names = sys.argv[1:]

    # Find CSV file
    csv_file = find_csv_file()
    print(f"Reading from: {csv_file}\n")

    # Extract speaker information
    speakers = extract_speaker_info(csv_file, speaker_names)

    if not speakers:
        print("No speakers found matching the provided names.")
        sys.exit(1)

    # Print results
    print("=" * 80)
    print("SPEAKER INFORMATION")
    print("=" * 80)

    for name, info in speakers.items():
        print(f"\n{name}")
        print(f"  Bluesky: {info['bluesky']}")
        print(f"  Role/Title: {info['role']}")
        print(f"  Talk: {info['tagline']}")
        print(f"  Description: {info['description'][:100]}...")

    print("\n" + "=" * 80)
    print("SPEAKER CARDS (add to speakers grid)")
    print("=" * 80)

    for name, info in speakers.items():
        print(generate_speaker_card(info))

    print("\n" + "=" * 80)
    print("SPEAKER DIALOGS (add before </script> tag)")
    print("=" * 80)

    for name, info in speakers.items():
        print(generate_speaker_dialog(info))

    print("\n" + "=" * 80)
    print("NOTES:")
    print("=" * 80)
    print("1. Update [Affiliation] placeholders with correct affiliations")
    print("2. Add speaker photos to: content/assets/images/atscience26-speakers/")
    print("3. Photo filenames should match the slug format (e.g., travis_simpson.jpg)")
    print("4. Verify Bluesky handles are correct")

if __name__ == "__main__":
    main()
