# Speaker Dialog Implementation Guide

This guide explains how to add speaker talk descriptions with interactive overlays to event pages.

## Overview

Each speaker card has an "i" info button that opens a modal dialog showing their talk title and description. The implementation uses HTML5 `<dialog>` elements with minimal JavaScript for accessibility.

## Files Modified

1. `/content/assets/speaker-dialog.js` - JavaScript for dialog functionality
2. `/content/assets/styles.scss` - Dialog styling (GOV.UK-aligned)
3. `/eleventy.config.js` - Passthrough copy for JavaScript file
4. `/content/events/event-atmosphere2026.md` - Speaker HTML with dialogs

## Adding a New Speaker with Talk Description

### Step 1: Add Speaker Card with Info Button

In your event markdown file (e.g., `event-atmosphere2026.md`), add this HTML structure within the speaker grid:

```html
<div style="text-align: center;">
  <div style="position: relative; display: inline-block;">
    <img src="/assets/images/atscience26-speakers/SPEAKER_IMAGE.jpg"
         alt="Photo of [Speaker Name]"
         style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
    <button class="speaker-info-btn"
            data-speaker="speaker-slug"
            aria-label="View talk information for [Speaker Name]"
            style="position: absolute; top: 0; right: 0; background: rgba(0, 0, 128, 0.9); border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; color: white; cursor: pointer; font-weight: bold; font-size: 18px;">
      i
    </button>
  </div>
  <h3 class="govuk-heading-s" style="margin-bottom: 0.25rem;">
    <a href="https://bsky.app/profile/[bluesky-handle]" class="govuk-link" target="_blank">[Speaker Name]</a>
  </h3>
  <p class="govuk-body-s" style="margin-bottom: 0.25rem; color: #505a5f;">[Title]</p>
  <p class="govuk-body-s" style="color: #505a5f;">[Affiliation]</p>
</div>
```

**Important:**
- Replace `speaker-slug` with a unique ID (lowercase, hyphens, e.g., "john-doe")
- This slug must match the dialog ID in Step 2

### Step 2: Add Dialog Element

After the speaker grid (before the `## Agenda` section), add the dialog HTML:

```html
<dialog id="dialog-speaker-slug" class="speaker-dialog" aria-labelledby="dialog-speaker-slug-title">
  <div class="speaker-dialog-content">
    <div class="speaker-dialog-header">
      <h2 id="dialog-speaker-slug-title" class="govuk-heading-m">[Speaker Name]</h2>
      <button class="speaker-dialog-close" aria-label="Close dialog" autofocus>
        <span aria-hidden="true">×</span>
      </button>
    </div>
    <div class="speaker-dialog-body">
      <p class="govuk-body-s" style="color: #505a5f; margin-bottom: 1rem;">
        [Title], [Affiliation]
      </p>
      <h3 class="govuk-heading-s">Talk: [Talk Title]</h3>
      <p class="govuk-body">
        [Talk description goes here. Can be multiple paragraphs.]
      </p>
      <p class="govuk-body" style="margin-top: 1rem;">
        <a href="https://bsky.app/profile/[bluesky-handle]" class="govuk-link" target="_blank">View profile on Bluesky</a>
      </p>
    </div>
  </div>
</dialog>
```

**Important:**
- The dialog `id` must be `dialog-` + the slug from Step 1
- The `aria-labelledby` must match the heading id

### Step 3: Placeholder for Speakers Without Talk Info

If you don't have talk details yet, use this simplified dialog body:

```html
<div class="speaker-dialog-body">
  <p class="govuk-body-s" style="color: #505a5f; margin-bottom: 1rem;">
    [Title], [Affiliation]
  </p>
  <p class="govuk-body">
    Talk details coming soon. Follow <a href="http://bsky.app/profile/atproto.science" class="govuk-link" target="_blank">@atproto.science</a> on Bluesky for updates.
  </p>
  <p class="govuk-body" style="margin-top: 1rem;">
    <a href="https://bsky.app/profile/[bluesky-handle]" class="govuk-link" target="_blank">View profile on Bluesky</a>
  </p>
</div>
```

## Example: Complete Speaker Implementation

Here's a full example for a speaker named "Jane Smith":

**Speaker Card:**
```html
<div style="text-align: center;">
  <div style="position: relative; display: inline-block;">
    <img src="/assets/images/atscience26-speakers/jane_smith.jpg"
         alt="Photo of Jane Smith"
         style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
    <button class="speaker-info-btn"
            data-speaker="jane-smith"
            aria-label="View talk information for Jane Smith"
            style="position: absolute; top: 0; right: 0; background: rgba(0, 0, 128, 0.9); border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; color: white; cursor: pointer; font-weight: bold; font-size: 18px;">
      i
    </button>
  </div>
  <h3 class="govuk-heading-s" style="margin-bottom: 0.25rem;">
    <a href="https://bsky.app/profile/janesmith.bsky.social" class="govuk-link" target="_blank">Jane Smith</a>
  </h3>
  <p class="govuk-body-s" style="margin-bottom: 0.25rem; color: #505a5f;">Research Scientist</p>
  <p class="govuk-body-s" style="color: #505a5f;">MIT Media Lab</p>
</div>
```

**Dialog:**
```html
<dialog id="dialog-jane-smith" class="speaker-dialog" aria-labelledby="dialog-jane-smith-title">
  <div class="speaker-dialog-content">
    <div class="speaker-dialog-header">
      <h2 id="dialog-jane-smith-title" class="govuk-heading-m">Jane Smith</h2>
      <button class="speaker-dialog-close" aria-label="Close dialog" autofocus>
        <span aria-hidden="true">×</span>
      </button>
    </div>
    <div class="speaker-dialog-body">
      <p class="govuk-body-s" style="color: #505a5f; margin-bottom: 1rem;">
        Research Scientist, MIT Media Lab
      </p>
      <h3 class="govuk-heading-s">Talk: Building Decentralized Knowledge Graphs</h3>
      <p class="govuk-body">
        This talk explores how ATProto can enable collaborative knowledge graphs that remain under user control. We'll demonstrate a prototype system that allows researchers to build shared taxonomies while maintaining data sovereignty.
      </p>
      <p class="govuk-body" style="margin-top: 1rem;">
        <a href="https://bsky.app/profile/janesmith.bsky.social" class="govuk-link" target="_blank">View profile on Bluesky</a>
      </p>
    </div>
  </div>
</dialog>
```

## Updating Existing Speaker Talk Info

To add or update talk information for a speaker who already has a placeholder:

1. Find their dialog element (search for `id="dialog-[speaker-slug]"`)
2. Replace the dialog body content with the new talk information
3. Add the talk title in an `<h3 class="govuk-heading-s">` heading
4. Add the description in a `<p class="govuk-body">` paragraph

## File Location for Reference

The complete implementation can be found in:
- `/content/events/event-atmosphere2026.md` (lines 96-262)

## Testing Checklist

After adding a new speaker:

1. ✓ Build the site: `bash -c "source ~/.nvm/nvm.sh && nvm use 20 && npx @11ty/eleventy"`
2. ✓ Check no build errors
3. ✓ Test clicking the info button opens the correct dialog
4. ✓ Test closing via X button
5. ✓ Test closing via Esc key
6. ✓ Test closing by clicking outside the dialog
7. ✓ Test keyboard navigation (Tab to button, Enter to open)
8. ✓ Verify Bluesky link works

## Technical Details

### JavaScript
- Located in `/content/assets/speaker-dialog.js`
- Uses HTML5 `<dialog>` element with `showModal()` API
- Handles clicks on info buttons via `data-speaker` attribute
- Automatically manages focus and keyboard accessibility

### Styling
- Located in `/content/assets/styles.scss`
- Classes: `.speaker-info-btn`, `.speaker-dialog`, `.speaker-dialog-close`
- GOV.UK yellow focus indicators (#ffdd00)
- Navy blue brand color (rgba(0, 0, 128, 0.9))
- Responsive: full-width on mobile (<640px)

### Accessibility Features
- ARIA labels on all interactive elements
- Keyboard navigation (Tab, Enter, Esc)
- Focus management (returns to trigger button on close)
- Screen reader support via `aria-labelledby`
- Proper dialog role (native to `<dialog>` element)

## Troubleshooting

**Info button doesn't open dialog:**
- Check that `data-speaker` attribute matches the dialog ID (without "dialog-" prefix)
- Verify JavaScript file is loaded: `<script src="/assets/speaker-dialog.js"></script>`

**Dialog has no styling:**
- Ensure SCSS compiled without errors
- Check that classes are spelled correctly

**Keyboard navigation doesn't work:**
- Verify `autofocus` attribute is on close button
- Check that dialog has proper `aria-labelledby` attribute

## Future Improvements

Consider these enhancements:
- Add talk schedule time when agenda is finalized
- Include session location/room information
- Add co-presenter links
- Support markdown in talk descriptions
- Add talk slides or video links
