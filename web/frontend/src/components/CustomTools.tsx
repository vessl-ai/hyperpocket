import { useState, FormEvent } from 'react';
import { FaSpinner } from 'react-icons/fa';

interface Tool {
  name: string;
  code: string;
  status: 'active' | 'error' | 'loading';
  error?: string;
}

function CustomTools() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [newToolCode, setNewToolCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('http://localhost:3001/api/tools/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: newToolCode }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to add tool');
      }

      const data = await res.json();
      setTools(prev => [...prev, {
        name: data.name,
        code: newToolCode,
        status: 'active'
      }]);
      setNewToolCode('');
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="custom-tools">
      <h2>Add Custom Tool</h2>
      <form onSubmit={handleSubmit} className="tool-form">
        <div className="code-editor">
          <textarea
            value={newToolCode}
            onChange={(e) => setNewToolCode(e.target.value)}
            placeholder={`@function_tool\ndef my_custom_tool(param1: str, param2: int) -> str:\n    """Your tool description"""\n    # Your code here`}
            disabled={loading}
          />
        </div>
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? <FaSpinner className="spinner" /> : 'Add Tool'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      <div className="tools-list">
        <h3>Added Tools</h3>
        {tools.map((tool, index) => (
          <div key={index} className={`tool-item ${tool.status}`}>
            <h4>{tool.name}</h4>
            <pre>{tool.code}</pre>
            {tool.error && <div className="error">{tool.error}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default CustomTools; 