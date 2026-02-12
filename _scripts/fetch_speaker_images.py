#!/usr/bin/env python3
"""
Fetch speaker profile images from Bluesky.

This script downloads profile images from Bluesky using the AT Protocol API
and saves them with the correct naming convention for the website.

Usage:
    python fetch_speaker_images.py <handle1> <handle2> ...

Example:
    python fetch_speaker_images.py skysquareapp.bsky.social smcgrath.phd infotainment.bsky.social
"""

import sys
import requests
from pathlib import Path
from urllib.parse import urlparse

# AT Protocol API endpoint
BSKY_API = "https://public.api.bsky.app"

def normalize_handle(handle):
    """Normalize Bluesky handle by removing @ prefix."""
    return handle.lstrip('@')

def fetch_profile(handle):
    """Fetch profile information from Bluesky."""
    handle = normalize_handle(handle)
    url = f"{BSKY_API}/xrpc/app.bsky.actor.getProfile"
    params = {"actor": handle}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching profile for {handle}: {e}")
        return None

def download_image(image_url, output_path):
    """Download image from URL and save to output path."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {image_url}: {e}")
        return False

def name_to_filename(display_name):
    """Convert display name to filename format (e.g., 'Travis Simpson' -> 'travis_simpson.jpg')."""
    # Remove special characters and convert to lowercase
    name = display_name.lower()
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove any non-alphanumeric characters except underscores
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    return f"{name}.jpg"

def fetch_speaker_image(handle, output_dir):
    """Fetch and save speaker profile image."""
    print(f"\nFetching profile for: {handle}")

    profile = fetch_profile(handle)
    if not profile:
        return False

    display_name = profile.get('displayName', profile.get('handle', 'unknown'))
    avatar_url = profile.get('avatar')

    if not avatar_url:
        print(f"  ⚠️  No profile image found for {display_name}")
        return False

    print(f"  ✓ Found profile: {display_name}")
    print(f"  ✓ Avatar URL: {avatar_url}")

    # Generate filename
    filename = name_to_filename(display_name)
    output_path = output_dir / filename

    print(f"  ⬇️  Downloading to: {output_path}")

    if download_image(avatar_url, output_path):
        print(f"  ✓ Successfully saved: {filename}")
        return True
    else:
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_speaker_images.py <handle1> [<handle2> ...]")
        print("\nExample:")
        print("  python fetch_speaker_images.py skysquareapp.bsky.social smcgrath.phd infotainment.bsky.social")
        print("\nYou can also use the @ prefix:")
        print("  python fetch_speaker_images.py @skysquareapp.bsky.social @smcgrath.phd")
        sys.exit(1)

    handles = sys.argv[1:]

    # Determine output directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "content" / "assets" / "images" / "atscience26-speakers"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("BLUESKY SPEAKER IMAGE FETCHER")
    print("=" * 80)
    print(f"Output directory: {output_dir}")
    print(f"Fetching {len(handles)} profile(s)...")

    # Fetch images
    success_count = 0
    for handle in handles:
        if fetch_speaker_image(handle, output_dir):
            success_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully fetched: {success_count}/{len(handles)} images")
    print(f"Images saved to: {output_dir}")

    if success_count < len(handles):
        print("\n⚠️  Some images failed to download. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✓ All images fetched successfully!")

if __name__ == "__main__":
    main()
