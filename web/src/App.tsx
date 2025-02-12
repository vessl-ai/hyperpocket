import { useState, FormEvent } from 'react';
import { FaCamera, FaImage, FaEnvelope, FaCheck, FaSpinner } from 'react-icons/fa';
import './App.css';

interface ApiResponse {
  response?: string;
  error?: string;
}

function App() {
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');

    try {
      const res = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      const data: ApiResponse = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Failed to get response');
      }

      if (data.response) {
        setResponse(data.response);
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="content">
        <form onSubmit={handleSubmit} className="prompt-form">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Take my photo, make it funny, and sent it to jaeman@vessl.ai"
            className="prompt-input"
            disabled={loading}
          />
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? <FaSpinner className="spinner" /> : 'Enter'}
          </button>
        </form>
        
        <div className="tools-section">
          <span className="tools-label">Tools integrated:</span>
          <div className="tools">
            <div className="tool-wrapper">
              <FaCamera className="tool-icon" title="Camera" />
              <FaCheck className="check-icon" />
            </div>
            <div className="tool-wrapper">
              <FaImage className="tool-icon" title="Image Editor" />
              <FaCheck className="check-icon" />
            </div>
            <div className="tool-wrapper">
              <FaEnvelope className="tool-icon" title="Email" />
              <FaCheck className="check-icon" />
            </div>
          </div>
        </div>

        {(loading || response || error) && (
          <div className="response-section">
            {loading && (
              <div className="loading">
                <FaSpinner className="spinner" />
                Processing...
              </div>
            )}
            {error && <div className="error">{error}</div>}
            {response && <div className="response">{response}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 