// frontend/src/Autosuggest.jsx
import React, { useState } from 'react';
import Autosuggest from 'react-autosuggest';
import axios from 'axios';

const AutosuggestComponent = ({ onSearch }) => {
  const [value, setValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const getSuggestions = async (input) => {
    try {
      //const response = await axios.get(`http://127.0.0.1:8000/suggest?query=${input}`);
       const response = await axios.get(`${API_BASE_URL}/suggest?query=${input}`);
      return response.data.suggestions;
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      return [];
    }
  };

  const onSuggestionsFetchRequested = async ({ value }) => {
    if (value.length > 2) {
      const newSuggestions = await getSuggestions(value);
      setSuggestions(newSuggestions);
    } else {
      setSuggestions([]);
    }
  };

  const onSuggestionsClearRequested = () => {
    setSuggestions([]);
  };

  const onChange = (event, { newValue }) => {
    setValue(newValue);
  };

  const onSuggestionSelected = (event, { suggestionValue }) => {
    setValue(suggestionValue);
    onSearch(suggestionValue);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      onSearch(value);
    }
  };

  return (
    <div className="autosuggest-container">
      <Autosuggest
        suggestions={suggestions}
        onSuggestionsFetchRequested={onSuggestionsFetchRequested}
        onSuggestionsClearRequested={onSuggestionsClearRequested}
        getSuggestionValue={(suggestion) => suggestion}
        renderSuggestion={(suggestion) => <div>{suggestion}</div>}
        inputProps={{
          placeholder: 'Ask a question (e.g., What is blockchain?)',
          value,
          onChange,
          onKeyPress: handleKeyPress,
        }}
      />
    </div>
  );
};

export default AutosuggestComponent;