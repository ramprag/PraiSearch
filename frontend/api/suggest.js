export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { query } = req.query;

  if (!query || query.length < 2) {
    return res.status(200).json({ suggestions: [] });
  }

  const baseSuggestions = [
    "What is artificial intelligence?",
    "How does machine learning work?",
    "What is blockchain technology?",
    "Explain cloud computing",
    "What is cybersecurity?",
    "How does quantum computing work?",
    "What is data science?",
    "Internet of things applications",
    "AI applications in healthcare",
    "Machine learning algorithms",
    "Blockchain use cases",
    "Cloud computing benefits",
    "Cybersecurity best practices",
    "Data science tools",
    "IoT devices examples"
  ];

  const suggestions = baseSuggestions
    .filter(suggestion =>
      suggestion.toLowerCase().includes(query.toLowerCase())
    )
    .slice(0, 6);

  // If no matches, provide query-based suggestions
  if (suggestions.length === 0) {
    const queryBased = [
      `What is ${query}?`,
      `How does ${query} work?`,
      `Explain ${query}`,
      `${query} applications`,
      `${query} benefits`
    ];
    suggestions.push(...queryBased.slice(0, 3));
  }

  res.status(200).json({ suggestions });
}