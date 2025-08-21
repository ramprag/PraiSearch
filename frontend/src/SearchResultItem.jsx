import React from 'react';

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

const SearchResultItem = ({ result, isExpanded, onToggleExpand }) => {
    const shouldTruncate = result.content.length > 300;
    const displayContent = isExpanded || !shouldTruncate
        ? result.content
        : truncateText(result.content);

    return (
        <li>
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
                <button className="expand-btn" onClick={onToggleExpand}>
                    {isExpanded ? '▲ Show Less' : '▼ Show More'}
                </button>
            )}
        </li>
    );
};

export default SearchResultItem;