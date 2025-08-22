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

  // Comprehensive mock search database
  const mockResults = [
    {
      title: "Blockchain Technology",
      content: "A blockchain is a decentralized, distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data. Blockchain technology enables secure, transparent, and tamper-resistant record-keeping without the need for a central authority. It's the underlying technology behind cryptocurrencies like Bitcoin and Ethereum, but has applications in supply chain management, digital identity, smart contracts, and many other fields.",
      url: "https://en.wikipedia.org/wiki/Blockchain",
      score: 1.0
    },
    {
      title: "Artificial Intelligence",
      content: "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning (the acquisition of information and rules for using the information), reasoning (using rules to reach approximate or definite conclusions), and self-correction. AI applications include expert systems, natural language processing, speech recognition, and machine vision. Modern AI techniques include machine learning, deep learning, neural networks, and natural language processing. AI is used in various fields such as healthcare, finance, transportation, and entertainment.",
      url: "https://en.wikipedia.org/wiki/Artificial_intelligence",
      score: 1.0
    },
    {
      title: "Machine Learning",
      content: "Machine Learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. Machine learning algorithms build mathematical models based on training data to make predictions or decisions without being explicitly programmed to perform the task. Types include supervised learning, unsupervised learning, and reinforcement learning. Applications include image recognition, recommendation systems, fraud detection, and predictive analytics.",
      url: "https://en.wikipedia.org/wiki/Machine_learning",
      score: 1.0
    },
    {
      title: "Cloud Computing",
      content: "Cloud computing is the on-demand availability of computer system resources, especially data storage and computing power, without direct active management by the user. The term is generally used to describe data centers available to many users over the Internet. Large clouds, predominant today, often have functions distributed over multiple locations from central servers. Cloud computing relies on sharing of resources to achieve coherence and economies of scale. Types include Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS).",
      url: "https://en.wikipedia.org/wiki/Cloud_computing",
      score: 1.0
    },
    {
      title: "Cybersecurity",
      content: "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information; extorting money from users; or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative. Key areas include network security, application security, information security, operational security, disaster recovery, and end-user education.",
      url: "https://en.wikipedia.org/wiki/Computer_security",
      score: 1.0
    },
    {
      title: "Internet of Things (IoT)",
      content: "The Internet of Things describes the network of physical objects—'things'—that are embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices and systems over the Internet. These devices range from ordinary household objects to sophisticated industrial tools. IoT enables objects to be sensed or controlled remotely across existing network infrastructure, creating opportunities for more direct integration of the physical world into computer-based systems. Applications include smart homes, wearable devices, connected cars, and industrial IoT.",
      url: "https://en.wikipedia.org/wiki/Internet_of_things",
      score: 1.0
    },
    {
      title: "Data Science",
      content: "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. Data science is related to data mining, machine learning, and big data. It combines domain expertise, programming skills, and knowledge of mathematics and statistics to extract meaningful insights from data. The data science process typically includes data collection, cleaning, exploration, analysis, visualization, and interpretation. Tools commonly used include Python, R, SQL, Tableau, and various machine learning frameworks.",
      url: "https://en.wikipedia.org/wiki/Data_science",
      score: 1.0
    },
    {
      title: "Quantum Computing",
      content: "Quantum computing is a type of computation that harnesses the collective properties of quantum states, such as superposition, interference, and entanglement, to perform calculations. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits (qubits) that can exist in multiple states simultaneously. This allows quantum computers to potentially solve certain problems exponentially faster than classical computers. Applications include cryptography, optimization problems, drug discovery, and financial modeling. Current challenges include maintaining quantum coherence and error correction.",
      url: "https://en.wikipedia.org/wiki/Quantum_computing",
      score: 1.0
    }
  ];

  // Enhanced search logic with partial matching and keyword scoring
  const queryWords = query.toLowerCase().split(' ').filter(word => word.length > 2);

  const searchResults = mockResults.map(result => {
    let score = 0;
    const titleLower = result.title.toLowerCase();
    const contentLower = result.content.toLowerCase();

    // Exact title match gets highest score
    if (titleLower.includes(query.toLowerCase())) {
      score += 10;
    }

    // Exact content match
    if (contentLower.includes(query.toLowerCase())) {
      score += 5;
    }

    // Keyword matching
    queryWords.forEach(word => {
      if (titleLower.includes(word)) {
        score += 3;
      }
      if (contentLower.includes(word)) {
        score += 1;
      }
    });

    return { ...result, searchScore: score };
  });

  // Filter and sort by relevance
  const filteredResults = searchResults
    .filter(result => result.searchScore > 0)
    .sort((a, b) => b.searchScore - a.searchScore)
    .slice(0, 5); // Top 5 results

  const answer = filteredResults.length > 0
    ? `Based on the available information: ${filteredResults[0].content.substring(0, 200)}...`
    : "No relevant information found for your query.";

  res.status(200).json({
    results: filteredResults,
    answer: answer,
    privacy_log: "Query processed securely on Vercel serverless function."
  });
}