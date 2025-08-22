// frontend/src/App.jsx - Updated for Vercel deployment
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

  // Detect if we're running on Vercel or localhost
  const isProduction = window.location.hostname !== 'localhost';
  const API_BASE_URL = isProduction
    ? '/api'  // Use Vercel API routes in production
    : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000');

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
      if (isProduction) {
        setAnswer('Search service temporarily unavailable. This is a demo version with limited functionality.');
        setPrivacyLog('Demo mode - limited search capability.');
      } else {
        setAnswer('Error processing query. Please check if the backend server is running.');
        setPrivacyLog('Error occurred during query processing.');
      }
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
      {isProduction && (
        <div className="demo-notice">
          <p><strong>Demo Version:</strong> This is a simplified version running on Vercel with basic search functionality.</p>
        </div>
      )}

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
        </div>
      )}

      {!loading && (
        <div className="feedback-section">
          <h3>Was this helpful? Give Feedback</h3>
          <p>Help us improve! Let us know what you think about the search results.</p>
          {feedbackSubmitted ? (
            <div className="feedback-success">
              <p>✅ Thank you for your feedback!</p>
            </div>
          ) : (
            <form onSubmit={handleFeedbackSubmit}>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Was the answer helpful? Any suggestions?"
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