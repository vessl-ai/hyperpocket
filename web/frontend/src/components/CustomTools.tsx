import { useState, FormEvent, useEffect } from 'react';
import { FaSpinner, FaChevronDown, FaChevronRight, FaCode } from 'react-icons/fa';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Modal from './Modal';

interface Tool {
  name: string;
  code: string;
  status: 'active' | 'error' | 'loading';
  error?: string;
}

interface RegisteredTool {
  name: string;
  description: string;
  parameters: {
    name: string;
    type: string;
    description?: string;
    required?: boolean;
  }[];
  isCustom?: boolean;
}

interface ToolCode {
  name: string;
  code: string;
}

function CustomTools() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [registeredTools, setRegisteredTools] = useState<RegisteredTool[]>([]);
  const [newToolCode, setNewToolCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [selectedTool, setSelectedTool] = useState<ToolCode | null>(null);

  useEffect(() => {
    fetchRegisteredTools();
  }, [tools]);

  const toggleTool = (toolName: string) => {
    setExpandedTools(prev => ({
      ...prev,
      [toolName]: !prev[toolName]
    }));
  };

  const fetchRegisteredTools = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/tools');
      if (!res.ok) {
        throw new Error('Failed to fetch tools');
      }
      const data = await res.json();
      
      // Sort tools - custom tools first
      const sortedTools = [...data.tools].sort((a: RegisteredTool, b: RegisteredTool) => {
        if (a.isCustom && !b.isCustom) return -1;
        if (!a.isCustom && b.isCustom) return 1;
        return 0;
      });
      
      setRegisteredTools(sortedTools);
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

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

  const handleViewCode = async (toolName: string) => {
    try {
      const res = await fetch(`http://localhost:3001/api/tools/${toolName}/code`);
      if (!res.ok) {
        throw new Error('Failed to fetch tool code');
      }
      const data = await res.json();
      setSelectedTool({ name: toolName, code: data.code });
    } catch (error) {
      console.error('Error fetching tool code:', error);
    }
  };

  return (
    <div className="custom-tools">
      <section className="add-tool-section">
        <h2>Add Custom Tool</h2>
        <form onSubmit={handleSubmit} className="tool-form">
          <div className="code-editor">
            <SyntaxHighlighter
              language="python"
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: '16px',
                background: '#1e1e1e',
                fontSize: '14px',
                minHeight: '200px',
              }}
            >
              {newToolCode || `@function_tool\ndef my_custom_tool(param1: str, param2: int) -> str:\n    """Your tool description"""\n    # Your code here`}
            </SyntaxHighlighter>
            <textarea
              value={newToolCode}
              onChange={(e) => setNewToolCode(e.target.value)}
              className="code-input"
              disabled={loading}
            />
          </div>
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? <FaSpinner className="spinner" /> : 'Add Tool'}
          </button>
        </form>
        {error && <div className="error">{error}</div>}
      </section>

      <section className="registered-tools-section">
        <h2>Registered Tools</h2>
        <div className="registered-tools-list">
          {registeredTools.map((tool, index) => (
            <div key={index} className="registered-tool-item">
              <button 
                className="tool-header" 
                onClick={() => toggleTool(tool.name)}
              >
                {expandedTools[tool.name] ? <FaChevronDown /> : <FaChevronRight />}
                <h3>
                  {tool.name}
                  <span className={`tool-badge ${tool.isCustom ? 'custom' : 'builtin'}`}>
                    {tool.isCustom ? 'Custom' : 'Built-in'}
                  </span>
                </h3>
                <button 
                  className="view-code-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewCode(tool.name);
                  }}
                >
                  <FaCode /> View Code
                </button>
              </button>
              {expandedTools[tool.name] && (
                <div className="tool-details">
                  <p className="tool-description">{tool.description}</p>
                  {tool.parameters.length > 0 && (
                    <div className="tool-parameters">
                      <h4>Parameters:</h4>
                      <ul>
                        {tool.parameters.map((param, idx) => (
                          <li key={idx}>
                            <span className="param-name">{param.name}</span>
                            <span className="param-type">{param.type}</span>
                            {param.description && (
                              <p className="param-description">{param.description}</p>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {tools.length > 0 && (
        <section className="custom-tools-section">
          <h2>Added Custom Tools</h2>
          <div className="tools-list">
            {tools.map((tool, index) => (
              <div key={index} className={`tool-item ${tool.status}`}>
                <button 
                  className="tool-header" 
                  onClick={() => toggleTool(`custom-${tool.name}`)}
                >
                  {expandedTools[`custom-${tool.name}`] ? <FaChevronDown /> : <FaChevronRight />}
                  <h4>{tool.name}</h4>
                </button>
                {expandedTools[`custom-${tool.name}`] && (
                  <div className="tool-details">
                    <SyntaxHighlighter
                      language="python"
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        borderRadius: '4px',
                      }}
                    >
                      {tool.code}
                    </SyntaxHighlighter>
                    {tool.error && <div className="error">{tool.error}</div>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <Modal
        isOpen={!!selectedTool}
        onClose={() => setSelectedTool(null)}
        title={selectedTool ? `${selectedTool.name} Source Code` : ''}
      >
        <SyntaxHighlighter
          language="python"
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            borderRadius: '6px',
          }}
        >
          {selectedTool?.code || ''}
        </SyntaxHighlighter>
      </Modal>
    </div>
  );
}

export default CustomTools; 