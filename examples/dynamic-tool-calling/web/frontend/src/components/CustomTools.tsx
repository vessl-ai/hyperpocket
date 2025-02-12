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
  isGitHub?: boolean;
  isCustom?: boolean;
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
  isGitHub?: boolean;
  url?: string;
}

interface ToolCode {
  name: string;
  code: string;
}

const DEFAULT_TOOL_CODE = `@function_tool
def my_custom_tool(param1: str, param2: int) -> str:
    """Your tool description"""
    # Your code here`;

function CustomTools() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [registeredTools, setRegisteredTools] = useState<RegisteredTool[]>([]);
  const [newToolCode, setNewToolCode] = useState('');
  const [gitUrl, setGitUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [gitLoading, setGitLoading] = useState(false);
  const [error, setError] = useState('');
  const [gitError, setGitError] = useState('');
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [selectedTool, setSelectedTool] = useState<ToolCode | null>(null);
  const [promptInput, setPromptInput] = useState('');
  const [promptLoading, setPromptLoading] = useState(false);
  const [promptError, setPromptError] = useState('');

  useEffect(() => {
    fetchRegisteredTools();
  }, [tools]);

  const toggleTool = (toolName: string) => {
    setExpandedTools(prev => ({
      ...prev,
      [toolName]: !prev[toolName]
    }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!newToolCode.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await addCustomTool(newToolCode);
      handleToolResponse(response);
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGitSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!gitUrl.trim()) return;

    setGitLoading(true);
    setGitError('');

    try {
      const response = await addGitTool(gitUrl);
      handleGitToolResponse(response);
    } catch (error) {
      handleGitError(error);
    } finally {
      setGitLoading(false);
    }
  };

  const handlePromptSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!promptInput.trim()) return;

    setPromptLoading(true);
    setPromptError('');

    try {
      const res = await fetch('http://localhost:3001/api/tools/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptInput }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to generate code');
      }

      const data = await res.json();
      setNewToolCode(data.code);
    } catch (error) {
      console.error('Error:', error);
      setPromptError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setPromptLoading(false);
    }
  };

  const fetchRegisteredTools = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/tools');
      if (!res.ok) throw new Error('Failed to fetch tools');
      
      const data = await res.json();
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

  const addCustomTool = async (code: string) => {
    const res = await fetch('http://localhost:3001/api/tools/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Failed to add tool');
    }

    return res.json();
  };

  const addGitTool = async (url: string) => {
    const res = await fetch('http://localhost:3001/api/tools/from-git', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Failed to add tool from git');
    }

    return res.json();
  };

  const fetchToolCode = async (toolName: string) => {
    try {
      const res = await fetch(`http://localhost:3001/api/tools/${toolName}/code`);
      if (!res.ok) throw new Error('Failed to fetch tool code');
      
      const data = await res.json();
      setSelectedTool({ name: toolName, code: data.code });
    } catch (error) {
      console.error('Error fetching tool code:', error);
    }
  };

  const handleToolResponse = (data: { name: string; message: string }) => {
    setTools(prev => [...prev, {
      name: data.name,
      code: newToolCode,
      status: 'active'
    }]);
    setNewToolCode('');
  };

  const handleGitToolResponse = (data: { name: string; message: string }) => {
    setTools(prev => [...prev, {
      name: data.name,
      code: '',
      status: 'active'
    }]);
    setGitUrl('');
    fetchRegisteredTools();
  };

  const handleError = (error: unknown) => {
    console.error('Error:', error);
    setError(error instanceof Error ? error.message : 'An error occurred');
  };

  const handleGitError = (error: unknown) => {
    console.error('Error:', error);
    setGitError(error instanceof Error ? error.message : 'An error occurred');
  };

  const renderGitSection = () => (
    <section className="from-git-section">
      <h2>From Git</h2>
      <form onSubmit={handleGitSubmit} className="git-form">
        <div className="git-input-wrapper">
          <input
            type="text"
            value={gitUrl}
            onChange={(e) => setGitUrl(e.target.value)}
            placeholder="Enter GitHub URL (e.g., https://github.com/user/repo/blob/main/tool.py)"
            className="git-input"
            disabled={gitLoading}
          />
          <button type="submit" className="submit-button" disabled={gitLoading}>
            {gitLoading ? <FaSpinner className="spinner" /> : 'Add from Git'}
          </button>
        </div>
        {gitError && <div className="error">{gitError}</div>}
      </form>
    </section>
  );

  const renderCustomToolForm = () => (
    <section className="add-tool-section">
      <h2>Add Custom Tool</h2>
      
      <form onSubmit={handlePromptSubmit} className="prompt-form">
        <div className="prompt-input-wrapper">
          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder="Describe your tool (e.g., 'Create a tool that sends an email')"
            className="prompt-input"
            disabled={promptLoading}
          />
          <button type="submit" className="submit-button" disabled={promptLoading}>
            {promptLoading ? <FaSpinner className="spinner" /> : 'Generate Code'}
          </button>
        </div>
        {promptError && <div className="error">{promptError}</div>}
      </form>

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
            {newToolCode || DEFAULT_TOOL_CODE}
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
  );

  const renderRegisteredTools = () => (
    <section className="registered-tools-section">
      <h2>Registered Tools</h2>
      <div className="registered-tools-list">
        {registeredTools.map((tool) => (
          <div key={tool.name} className="registered-tool-item">
            <button 
              className="tool-header" 
              onClick={() => toggleTool(tool.name)}
            >
              {expandedTools[tool.name] ? <FaChevronDown /> : <FaChevronRight />}
              <h3>
                {tool.name}
                <span className={`tool-badge ${
                  tool.isGitHub ? 'github' : 
                  tool.isCustom ? 'custom' : 
                  'builtin'
                }`}>
                  {tool.isGitHub ? 'GitHub' : 
                   tool.isCustom ? 'Custom' : 
                   'Built-in'}
                </span>
              </h3>
              {tool.isGitHub ? (
                <a 
                  href={tool.url}
                  className="github-link-button"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                >
                  <FaCode /> View on GitHub
                </a>
              ) : (
                <button 
                  className="view-code-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fetchToolCode(tool.name);
                  }}
                >
                  <FaCode /> View Code
                </button>
              )}
            </button>
            {expandedTools[tool.name] && !tool.isGitHub && (
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
  );

  return (
    <div className="custom-tools">
      {renderGitSection()}
      {renderCustomToolForm()}
      {renderRegisteredTools()}
      
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