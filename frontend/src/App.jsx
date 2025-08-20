// frontend/src/App.jsx
import React, { useState } from 'react';
import Autosuggest from './Autosuggest';
import axios from 'axios';
import './styles.css';

function App() {
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState('');
  const [privacyLog, setPrivacyLog] = useState('');

  const handleSearch = async (query) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/search', { query });
      setResults(response.data.results);
      setAnswer(response.data.answer);
      setPrivacyLog(response.data.privacy_log);
    } catch (error) {
      console.error('Error:', error);
      setAnswer('Error processing query.');
    }
  };

  return (
    <div className="app">
      <h1>SafeQuery: Privacy-First AI Search</h1>
      <p>Search securely with local processing, no data leaves your device.</p>
      <Autosuggest onSearch={handleSearch} />
      {privacyLog && (
        <div className="privacy-log">
          <h3>Privacy Assurance</h3>
          <p>{privacyLog}</p>
        </div>
      )}
      {answer && (
        <div className="answer">
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}
      {results.length > 0 && (
        <div className="results">
          <h3>Results</h3>
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                <a href={result.url} target="_blank" rel="noopener noreferrer">
                  {result.title}
                </a>
                <p>{result.content}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;