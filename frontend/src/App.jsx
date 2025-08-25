// frontend/src/App.jsx - Updated with privacy indicators
import React, { useState, useEffect } from 'react';
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
  const [privacyStatus, setPrivacyStatus] = useState(null);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Load privacy status on mount
  useEffect(() => {
    const loadPrivacyStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/privacy-audit`);
        setPrivacyStatus(response.data);
      } catch (error) {
        console.log('Privacy audit not available');
      }
    };
    loadPrivacyStatus();
  }, [API_BASE_URL]);

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
      <header className="app-header">
        <h1>🛡️ SafeQuery</h1>
        <p className="tagline">The Anti-Perplexity: 100% Local Privacy-First Search</p>

        {/* Privacy Status Indicator */}
        <div className="privacy-status">
          <div className="privacy-indicator online">
            <span className="status-dot"></span>
            <span>100% Private • No Data Collection • No Tracking</span>
          </div>
          {isOffline && (
            <div className="offline-indicator">
              <span>🔒 Offline Mode Active - Maximum Privacy</span>
            </div>
          )}
        </div>

        {/* Privacy Guarantees */}
        <div className="privacy-guarantees">
          <div className="guarantee-item">✅ Zero Web Requests</div>
          <div className="guarantee-item">✅ No User Tracking</div>
          <div className="guarantee-item">✅ Local Processing Only</div>
          <div className="guarantee-item">✅ Works Offline</div>
        </div>
      </header>

      <Autosuggest onSearch={handleSearch} />

      {loading && (
        <div className="loading">
          <div className="loading-spinner"></div>
          Processing your query locally with maximum privacy...
        </div>
      )}

      {!loading && privacyLog && (
        <div className="privacy-log">
          <h3>🔒 Privacy Report</h3>
          <p>{privacyLog}</p>
          <div className="privacy-details">
            <small>
              ℹ️ Your search was processed entirely on local servers. No data was sent to third parties.
              Check your browser's Network tab (F12) - you'll see zero external requests!
            </small>
          </div>
        </div>
      )}

      {!loading && answer && (
        <div className="answer">
          <h3>💡 Answer</h3>
          <p>{answer}</p>
          <div className="answer-source">
            <small>Generated from local knowledge base • No web scraping • No data mining</small>
          </div>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="results">
          <h3>📚 Local Search Results ({results.length} found)</h3>
          <div className="results-info">
            <small>All results from local knowledge base - no web crawling performed</small>
          </div>
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
          <h3>🔍 No Local Results Found</h3>
          <p>Try rephrasing your question. SafeQuery searches only local knowledge for your privacy.</p>
          <div className="search-tips">
            <h4>Available Topics:</h4>
            <div className="topic-tags">
              <span className="topic-tag">Technology</span>
              <span className="topic-tag">Science</span>
              <span className="topic-tag">Health</span>
              <span className="topic-tag">Finance</span>
              <span className="topic-tag">AI & Machine Learning</span>
            </div>
          </div>
        </div>
      )}

      {/* Privacy Comparison */}
      <div className="privacy-comparison">
        <h3>🆚 SafeQuery vs. Other Search Engines</h3>
        <div className="comparison-grid">
          <div className="comparison-item safequery">
            <h4>SafeQuery (This App)</h4>
            <ul>
              <li>✅ Zero data collection</li>
              <li>✅ No user tracking</li>
              <li>✅ Works offline</li>
              <li>✅ Local processing only</li>
              <li>✅ No cookies or analytics</li>
            </ul>
          </div>
          <div className="comparison-item others">
            <h4>Perplexity & Others</h4>
            <ul>
              <li>❌ Collect user queries</li>
              <li>❌ Track user behavior</li>
              <li>❌ Require internet</li>
              <li>❌ Send data to servers</li>
              <li>❌ Use cookies & analytics</li>
            </ul>
          </div>
        </div>
      </div>

      {!loading && (
        <div className="feedback-section">
          <h3>💬 Anonymous Feedback</h3>
          <p>Help us improve while maintaining your privacy. Feedback is stored locally.</p>
          {feedbackSubmitted ? (
            <div className="feedback-success">
              <p>✅ Thank you for your anonymous feedback!</p>
            </div>
          ) : (
            <form onSubmit={handleFeedbackSubmit}>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="How was your privacy-first search experience?"
                rows="4"
                required
              />
              <button type="submit" disabled={!feedback.trim()}>
                Submit Anonymous Feedback
              </button>
            </form>
          )}
        </div>
      )}

      <footer className="app-footer">
        <div className="footer-content">
          <h4>🛡️ Privacy-First Promise</h4>
          <p>SafeQuery is the anti-thesis to data-hungry search engines. We believe search should be private by default.</p>
          <div className="tech-info">
            <small>
              Built with FastAPI • No external APIs • No web scraping • No user tracking
              <br />
              Open source • Auditable • Transparent
            </small>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;