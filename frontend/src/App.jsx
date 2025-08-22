// frontend/src/App.jsx - ORIGINAL VERSION RESTORED
import React, { useState } from 'react';
import Autosuggest from './Autosuggest';
import SearchResultItem from './SearchResultItem';
import axios from 'axios';
import './styles.css';

function App() {
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState('');
  const [privacyLog, setPrivacyLog] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [expandedResults, setExpandedResults] = useState(new Set());

  // Use environment variable for API URL, with a fallback for local development
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  const handleSearch = async (query) => {
    if (!query.trim()) return;

    setLoading(true);
    setResults([]);
    setAnswer('');
    setPrivacyLog('');
    setExpandedResults(new Set());

    try {
      const response = await axios.post(`${API_BASE_URL}/search`, { query });

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

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedback.trim()) return;

    try {
      await axios.post(`${API_BASE_URL}/feedback`, { feedback });
      setFeedbackSubmitted(true);
      setFeedback('');
      setTimeout(() => setFeedbackSubmitted(false), 5000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again later.');
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
            {results.map((result, index) => (
              <SearchResultItem
                key={index}
                result={result}
                isExpanded={expandedResults.has(index)}
                onToggleExpand={() => toggleExpand(index)}
              />
            ))}
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

      {!loading && (
        <div className="feedback-section">
          <h3>Was this helpful? Give Feedback</h3>
          <p>Help us improve! Let us know what you think about the search results, the answer, or the overall experience.</p>
          {feedbackSubmitted ? (
            <div className="feedback-success">
              <p>✅ Thank you for your feedback!</p>
            </div>
          ) : (
            <form onSubmit={handleFeedbackSubmit}>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Was the answer helpful? Are the results relevant? Any suggestions?"
                rows="4"
                required
              />
              <button type="submit" disabled={!feedback.trim()}>
                Submit Feedback
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}

export default App;