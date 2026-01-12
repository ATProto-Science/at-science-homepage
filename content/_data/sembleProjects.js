// Helper function to parse structured data from note
function parseNoteFields(noteText) {
  if (!noteText) return null;

  try {
    // Try to parse as JSON first
    const parsed = JSON.parse(noteText);
    if (typeof parsed === 'object' && parsed !== null) {
      return parsed;
    }
  } catch (e) {
    // Not JSON, return null to use fallback behavior
  }

  return null;
}

export default async function() {
  try {
    const response = await fetch(
      'https://api.semble.so/api/collections/at/atproto.science/3m5f7jpl6pk2j?page=1&limit=100&sortBy=createdAt&sortOrder=desc'
    );

    if (!response.ok) {
      console.error('Failed to fetch projects from Semble API');
      return [];
    }

    const data = await response.json();

    // Transform the API response to match the expected project format
    return data.urlCards.map(card => {
      // Try to extract structured fields from note
      const noteFields = parseNoteFields(card.note?.text);

      return {
        url: card.url,
        date: card.createdAt,
        data: {
          // Prioritize note.title > card title > fallback
          title: noteFields?.title || card.cardContent?.title || 'Untitled Project',
          // Prioritize note.description > note.text > card description > empty
          description: noteFields?.description || card.note?.text || card.cardContent?.description || ''
        }
      };
    });
  } catch (error) {
    console.error('Error fetching projects:', error);
    return [];
  }
}
