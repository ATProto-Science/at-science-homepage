# Speaker Update Summary

## Quick Reference Guide

### Step 1: Export Data from Notion
Export speaker data to CSV and place in `_data/` directory:
- `ATScience Call for Proposals Tally form replies *.csv` (proposals)
- `Speaker volunteer candidates *.csv` (status tracking)

### Step 2: Extract Speaker Information
```bash
cd _scripts
python3 extract_speaker_info.py "Speaker Name 1" "Speaker Name 2"
```

### Step 3: Fetch Profile Images
```bash
cd _scripts
python3 fetch_speaker_images.py handle1.bsky.social handle2.bsky.social
```

### Step 4: Update Event Page
Edit `content/events/event-atmosphere2026.md`:
1. Add speaker cards to the grid (before `<!-- Add more speakers -->`)
2. Add speaker dialogs (before `<script src="/assets/speaker-dialog.js">`)

### Required Information Per Speaker
- Full name
- Bluesky handle (from Tally CSV: `ATproto ID`)
- Professional title (from Tally CSV: `Role/Title`)
- Affiliation/organization (infer from email or context)
- Talk title (from Tally CSV: `Proposal Tagline`)
- Talk description (from Tally CSV: `Description`)
- Profile photo (fetched from Bluesky or provided)

### File Locations
```
_data/                              # CSV exports
_scripts/
  ├── extract_speaker_info.py       # Extract data from CSV
  └── fetch_speaker_images.py       # Fetch Bluesky profile images
content/
  ├── events/
  │   └── event-atmosphere2026.md   # Event page with speakers
  └── assets/images/atscience26-speakers/  # Speaker photos
```

### Common Issues
- **Bluesky handle not found:** Check CSV for correct handle format
- **Image fetch fails:** Verify handle is correct or try searching on Bluesky
- **Missing affiliation:** Check email domain in Speaker Candidates CSV

For detailed instructions, see `SPEAKER_UPDATE_GUIDE.md`
