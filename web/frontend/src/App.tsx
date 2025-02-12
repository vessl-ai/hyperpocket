import { useState, FormEvent } from 'react';
import { FaCamera, FaImage, FaEnvelope, FaCheck, FaSpinner } from 'react-icons/fa';
import './App.css';

interface ToolCall {
  id: string;
  type: string;
  function: {
    name: string;
    arguments: string;
  };
}

interface ApiResponse {
  response: string;
  tool_calls?: ToolCall[];
}

function App() {
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string>('');
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');
    setToolCalls([]);

    try {
      const res = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data: ApiResponse = await res.json();
      setResponse(data.response);
      if (data.tool_calls) {
        setToolCalls(data.tool_calls);
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderToolStatus = (toolName: string) => {
    const isToolUsed = toolCalls.some(
      call => call.function.name.toLowerCase().includes(toolName.toLowerCase())
    );
    return (
      <div className="tool-wrapper">
        {toolName === 'camera' && <FaCamera className="tool-icon" title="Camera" />}
        {toolName === 'image' && <FaImage className="tool-icon" title="Image Editor" />}
        {toolName === 'mail' && <FaEnvelope className="tool-icon" title="Email" />}
        {isToolUsed && <FaCheck className="check-icon active" />}
        {!isToolUsed && <FaCheck className="check-icon" />}
      </div>
    );
  };

  return (
    <div className="container">
      <div className="content">
        <form onSubmit={handleSubmit} className="prompt-form">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Take my photo, make it funny, and send it to me"
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
            {renderToolStatus('camera')}
            {renderToolStatus('image')}
            {renderToolStatus('mail')}
          </div>
        </div>

        {(loading || response || error || toolCalls.length > 0) && (
          <div className="response-section">
            {loading && (
              <div className="loading">
                <FaSpinner className="spinner" />
                Processing...
              </div>
            )}
            {error && <div className="error">{error}</div>}
            {response && (
              <>
                <div className="response">{response}</div>
                {toolCalls.length > 0 && (
                  <div className="tool-calls">
                    <h4>Actions taken:</h4>
                    <ul>
                      {toolCalls.map((call, index) => (
                        <li key={call.id || index}>
                          {call.function.name.replace(/_/g, ' ')}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 