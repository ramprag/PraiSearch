// frontend/src/App.jsx - Improved version
import React, { useState } from 'react';
import Autosuggest from './Autosuggest';
import axios from 'axios';
import './styles.css';

function App() {
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState('');
  const [privacyLog, setPrivacyLog] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedResults, setExpandedResults] = useState(new Set());

  const handleSearch = async (query) => {
    if (!query.trim()) return;

    setLoading(true);
    setResults([]);
    setAnswer('');
    setPrivacyLog('');
    setExpandedResults(new Set());

    try {
      const response = await axios.post('http://127.0.0.1:8000/search', { query });
      setResults(response.data.results || []);
      setAnswer(response.data.answer || '');
      setPrivacyLog(response.data.privacy_log || '');
    } catch (error) {
      console.error('Error:', error);
      setAnswer('Error processing query. Please check if the backend server is running.');
      setPrivacyLog('Error occurred during query processing.');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (index) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedResults(newExpanded);
  };

  const truncateText = (text, maxLength = 300) => {
    if (text.length <= maxLength) return text;

    // Find the last complete sentence within the limit
    const truncated = text.substring(0, maxLength);
    const lastSentenceEnd = Math.max(
      truncated.lastIndexOf('.'),
      truncated.lastIndexOf('!'),
      truncated.lastIndexOf('?')
    );

    if (lastSentenceEnd > maxLength * 0.7) {
      return truncated.substring(0, lastSentenceEnd + 1);
    }

    // If no good sentence break, find last space
    const lastSpace = truncated.lastIndexOf(' ');
    return truncated.substring(0, lastSpace) + '...';
  };

  return (
    <div className="app">
      <h1>SafeQuery: Privacy-First AI Search</h1>
      <p>Search securely with local processing and privacy protection.</p>
      <Autosuggest onSearch={handleSearch} />

      {loading && (
        <div className="loading">
          Searching and generating answer...
        </div>
      )}

      {!loading && privacyLog && (
        <div className="privacy-log">
          <h3>🔒 Privacy Assurance</h3>
          <p>{privacyLog}</p>
        </div>
      )}

      {!loading && answer && (
        <div className="answer">
          <h3>💡 Answer</h3>
          <p>{answer}</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="results">
          <h3>📚 Search Results ({results.length} found)</h3>
          <ul>
            {results.map((result, index) => {
              const isExpanded = expandedResults.has(index);
              const shouldTruncate = result.content.length > 300;
              const displayContent = isExpanded || !shouldTruncate
                ? result.content
                : truncateText(result.content);

              return (
                <li key={index}>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={`Visit: ${result.title}`}
                  >
                    {result.title}
                  </a>
                  <div className={`result-content ${!isExpanded && shouldTruncate ? 'collapsed' : ''}`}>
                    <p>{displayContent}</p>
                  </div>
                  {shouldTruncate && (
                    <button
                      className="expand-btn"
                      onClick={() => toggleExpand(index)}
                    >
                      {isExpanded ? '▲ Show Less' : '▼ Show More'}
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {!loading && results.length === 0 && answer === '' && privacyLog && (
        <div className="no-results">
          <h3>🔍 No Results Found</h3>
          <p>Try rephrasing your question or adding more content to the knowledge base.</p>
          <div className="search-tips">
            <h4>Search Tips:</h4>
            <ul>
              <li>Use specific keywords related to your topic</li>
              <li>Try asking complete questions like "What is artificial intelligence?"</li>
              <li>Check spelling and try alternative terms</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;