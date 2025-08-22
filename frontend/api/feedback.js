export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { feedback } = req.body;

  if (!feedback || !feedback.trim()) {
    return res.status(400).json({ detail: 'Feedback cannot be empty.' });
  }

  // In a real app, you'd save this to a database
  // For demo purposes, we'll just log it
  console.log('Feedback received:', feedback);

  res.status(200).json({ message: 'Feedback received successfully.' });
}