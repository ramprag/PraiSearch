// This creates a serverless API route for Vercel
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { query } = req.body;

  // Simple mock search since we can't run the full Python backend on Vercel
  const mockResults = [
    {
      title: "Artificial Intelligence",
      content: "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction. AI applications include expert systems, natural language processing, speech recognition, and machine vision.",
      url: "https://en.wikipedia.org/wiki/Artificial_intelligence",
      score: 0.95
    },
    {
      title: "Machine Learning",
      content: "Machine Learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience.",
      url: "https://en.wikipedia.org/wiki/Machine_learning",
      score: 0.85
    }
  ];

  const filteredResults = mockResults.filter(result =>
    result.title.toLowerCase().includes(query.toLowerCase()) ||
    result.content.toLowerCase().includes(query.toLowerCase())
  );

  const answer = filteredResults.length > 0
    ? `Based on the available information: ${filteredResults[0].content.substring(0, 200)}...`
    : "No relevant information found for your query.";

  res.status(200).json({
    results: filteredResults,
    answer: answer,
    privacy_log: "Query processed securely on Vercel serverless function."
  });
}