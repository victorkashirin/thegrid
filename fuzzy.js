/**
 * Fuzzy search function for searching through objects with specific keys
 * @param {Array} items - Array of objects to search through
 * @param {string} query - Search query string
 * @param {Object} options - Optional configuration
 * @returns {Array} Sorted array of matching items with scores
 */
function fuzzySearch(items, query, options = {}) {
  // Default options
  const config = {
    threshold: 0.25, // Minimum score to include in results (0-1)
    maxResults: null, // Maximum number of results to return
    weights: {
      module_name: 6,
      plugin_name: 3,
      description: 2,
      tags: 2
    },
    ...options
  };

  // Normalize and prepare query
  const normalizedQuery = query.toLowerCase().trim();
  if (!normalizedQuery) return [];

  // Split query into tokens for better matching
  const queryTokens = normalizedQuery.split(/\s+/);

  // Calculate fuzzy match score for a single token
  function calculateTokenScore(str, token) {
    if (!str) return 0;

    const normalizedStr = str.toLowerCase();

    // Exact match
    if (normalizedStr === token) return 1;

    // Word boundary exact match
    const wordBoundaryRegex = new RegExp(`\\b${token}\\b`, 'i');
    if (wordBoundaryRegex.test(str)) return 0.95;

    // Contains token
    if (normalizedStr.includes(token)) {
      // Prefer matches at the beginning
      if (normalizedStr.startsWith(token)) return 0.85;
      return 0.7;
    }

    // Character sequence matching (fuzzy)
    let charScore = 0;
    let tokenIndex = 0;
    let consecutive = 0;
    let gaps = 0;

    for (let i = 0; i < normalizedStr.length && tokenIndex < token.length; i++) {
      if (normalizedStr[i] === token[tokenIndex]) {
        charScore += 1;
        consecutive++;
        tokenIndex++;

        // Bonus for consecutive matches
        if (consecutive > 1) {
          charScore += consecutive * 0.1;
        }
      } else {
        if (tokenIndex > 0) gaps++;
        consecutive = 0;
      }
    }

    if (tokenIndex === token.length) {
      // All characters found
      charScore = charScore / (token.length + gaps * 0.5);
      return Math.min(charScore * 0.6, 0.6);
    }

    return 0;
  }

  // Calculate best match score for a token across all fields
  function getBestTokenScore(item, token, weights) {
    const fieldScores = {};

    // Calculate score for each field
    for (const [field, weight] of Object.entries(weights)) {
      let score = 0;

      if (field === 'tags' && Array.isArray(item.tags)) {
        // For tags, take the best matching tag score
        const tagScores = item.tags.map(tag => calculateTokenScore(tag, token));
        score = Math.max(...tagScores, 0);
      } else if (item[field]) {
        score = calculateTokenScore(item[field], token);
      }

      fieldScores[field] = {
        rawScore: score,
        weightedScore: score * weight
      };
    }

    // Find the field with the best weighted score
    let bestField = null;
    let bestWeightedScore = 0;

    for (const [field, scores] of Object.entries(fieldScores)) {
      if (scores.weightedScore > bestWeightedScore) {
        bestWeightedScore = scores.weightedScore;
        bestField = field;
      }
    }

    return {
      score: bestWeightedScore,
      field: bestField,
      fieldScores
    };
  }

  // Score each item
  const scoredItems = items.map(item => {
    const tokenResults = [];
    let totalScore = 0;

    // For each query token, find its best match across all fields
    for (const token of queryTokens) {
      const bestMatch = getBestTokenScore(item, token, config.weights);
      tokenResults.push({
        token,
        ...bestMatch
      });
      totalScore += bestMatch.score;
    }

    // Average score across all tokens (weighted by field weights)
    const maxPossibleScore = queryTokens.length * Math.max(...Object.values(config.weights));
    const normalizedScore = totalScore / maxPossibleScore;

    // Bonus for items where all tokens match
    const allTokensMatched = tokenResults.every(r => r.score > 0);
    const finalScore = allTokensMatched ? normalizedScore * 1.1 : normalizedScore;

    return {
      item,
      score: Math.min(finalScore, 1), // Cap at 1
      tokenResults,
      debug: {
        totalScore,
        maxPossibleScore,
        normalizedScore,
        allTokensMatched
      }
    };
  });

  // Filter by threshold and sort by score
  let results = scoredItems
    .filter(result => result.score >= config.threshold)
    .sort((a, b) => b.score - a.score);

  // Limit results if specified
  if (config.maxResults) {
    results = results.slice(0, config.maxResults);
  }

  return results;
}

// Helper function to get just the items without scores
function fuzzySearchItems(items, query, options = {}) {
  return fuzzySearch(items, query, options).map(result => result.item);
}

// Example usage:
/*
const items = [
  {
    module_name: "User Authentication",
    plugin_name: "auth-plugin",
    description: "Handles user login and registration",
    tags: ["security", "users", "login"]
  },
  {
    module_name: "Payment Gateway",
    plugin_name: "payment-processor",
    description: "Process credit card and PayPal payments",
    tags: ["payments", "checkout", "ecommerce"]
  },
  {
    module_name: "Email Service",
    plugin_name: "mail-sender",
    description: "Send transactional and marketing emails",
    tags: ["email", "notifications", "smtp"]
  }
];

// Search with default settings
const results = fuzzySearchItems(items, "user auth");

// Search with custom options and get scores
const detailedResults = fuzzySearch(items, "payment", {
  threshold: 0.2,
  maxResults: 5,
  weights: {
    module_name: 4,
    plugin_name: 3,
    description: 2,
    tags: 1
  }
});

// Debug example to see how scoring works
const debugResults = fuzzySearch(items, "auth-plugin");
console.log(debugResults[0].tokenResults); // Shows which field each token matched best
*/