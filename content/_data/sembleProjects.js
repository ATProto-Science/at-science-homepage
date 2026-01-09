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
    return data.urlCards.map(card => ({
      url: card.url,
      date: card.createdAt,
      data: {
        title: card.cardContent?.title || 'Untitled Project',
        description: card.cardContent?.description || ''
      }
    }));
  } catch (error) {
    console.error('Error fetching projects:', error);
    return [];
  }
}
