import React, { useState } from "react";

// Define the types for the search result data
interface SearchResult {
  topic: string;
  article: string;
}

const SearchApp: React.FC = () => {
  const [query, setQuery] = useState<string>(""); // To hold the user's search query
  const [results, setResults] = useState<SearchResult[]>([]); // To hold the search results
  const [loading, setLoading] = useState<boolean>(false); // Loading indicator
  const [error, setError] = useState<string | null>(null); // Error message

  // Function to fetch search results
  const fetchSearchResults = async () => {
    if (!query.trim()) {
      setError("Please enter a search query.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8001/api/v1/search/search?query=${encodeURIComponent(query)}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch search results");
      }

      const data: { search_data: SearchResult[] } = await response.json();
      setResults(data["data"].search_data || []);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1000px", margin: "auto" }}>
      <h1>Search App</h1>
      <div>
        <input
          type="text"
          placeholder="Enter your search query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ width: "70%", padding: "10px", fontSize: "16px" }}
        />
        <button
          onClick={fetchSearchResults}
          style={{
            marginLeft: "10px",
            padding: "10px 20px",
            fontSize: "16px",
            cursor: "pointer",
          }}
        >
          Search
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Scrollable Table */}
      <div style={{ marginTop: "20px", overflowX: "auto", border: "1px solid #ddd" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f4f4f4", textAlign: "left" }}>
              <th style={{
                   padding: "10px",
                   border: "1px solid #ddd",
                   minWidth: "150px",
                   textAlign: "center",
                   color: "black"}}>
                Topic
              </th>
              <th style={{
                   padding: "10px",
                   border: "1px solid #ddd",
                   minWidth: "500px",
                   textAlign: "center",
                   color: "black"}}>
                Article
              </th>
            </tr>
          </thead>
          <tbody>
            {results.length > 0 ? (
              results.map((item, index) => (
                <tr key={index}>
                  <td style={{ padding: "10px", border: "1px solid #ddd"}}>{item.topic}</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd", textAlign: "left", whiteSpace: "pre-wrap"}}>
                    {item.article}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={2}
                  style={{
                    padding: "10px",
                    border: "1px solid #ddd",
                    textAlign: "center",
                  }}
                >
                  No results found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SearchApp;