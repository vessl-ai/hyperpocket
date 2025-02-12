import { useState, FormEvent, useEffect } from 'react';
import { FaSpinner, FaChevronDown, FaChevronRight, FaCode } from 'react-icons/fa';
import Editor, { OnChange } from "@monaco-editor/react";
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

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  readOnly?: boolean;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ value, onChange, language = "python", readOnly = false }) => {
  const handleEditorChange: OnChange = (value, _event) => {
    onChange(value || "");
  };

  return (
    <Editor
      height="300px"
      defaultLanguage={language}
      value={value}
      onChange={readOnly ? undefined : handleEditorChange}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 13,
        lineNumbers: "on",
        roundedSelection: false,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        wordWrap: "on",
        readOnly: readOnly,
        domReadOnly: readOnly,
        theme: "vs-dark",
        backgroundColor: "rgb(24, 24, 24)",
      }}
    />
  );
};

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

  const handleToolClick = (toolName: string) => {
    if (selectedTool?.name === toolName) {
      setSelectedTool(null);
    } else {
      fetchToolCode(toolName);
    }
  };

  const handleViewCodeClick = (e: React.MouseEvent, toolName: string) => {
    e.stopPropagation();
    fetchToolCode(toolName);
  };

  const renderGitSection = () => (
    <section className="from-git-section">
      <h2>From Git</h2>
      <form onSubmit={handleGitSubmit} className="form-container git-form">
        <div className="input-group git-input-wrapper">
          <input
            type="text"
            value={gitUrl}
            onChange={(e) => setGitUrl(e.target.value)}
            placeholder="Enter GitHub URL (e.g., https://github.com/user/repo/blob/main/tool.py)"
            className="input-base git-input"
            disabled={gitLoading}
          />
          <button type="submit" className="button-primary submit-button" disabled={gitLoading}>
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
      
      <form onSubmit={handlePromptSubmit} className="form-container prompt-form">
        <div className="input-group prompt-input-wrapper">
          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder="Describe your tool (e.g., 'Create a tool that sends an email')"
            className="input-base prompt-input"
            disabled={promptLoading}
          />
          <button type="submit" className="button-primary submit-button" disabled={promptLoading}>
            {promptLoading ? <FaSpinner className="spinner" /> : 'Generate Code'}
          </button>
        </div>
        {promptError && <div className="error">{promptError}</div>}
      </form>

      <form onSubmit={handleSubmit} className="form-container tool-form">
        <div className="code-editor-container">
          <CodeEditor
            value={newToolCode || DEFAULT_TOOL_CODE}
            onChange={(value) => setNewToolCode(value)}
            language="python"
          />
        </div>
        <button type="submit" className="button-primary submit-button" disabled={loading}>
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
            <div className="tool-header" onClick={() => handleToolClick(tool.name)}>
              <div className="tool-info">
                <div className="tool-name">
                  {tool.name.replace(/_/g, ' ')}
                  <span className={`tool-badge ${tool.isGitHub ? 'github' : 'custom'}`}>
                    {tool.isGitHub ? 'github' : 'custom'}
                  </span>
                </div>
                <div className="tool-description">{tool.description}</div>
              </div>
              <div className="tool-actions">
                <button 
                  className="view-code-button"
                  onClick={(e) => handleViewCodeClick(e, tool.name)}
                >
                  <FaCode /> View Code
                </button>
              </div>
            </div>
            {selectedTool?.name === tool.name && (
              <div className="tool-parameters">
                <h4>Parameters</h4>
                <div className="parameters-list">
                  {tool.parameters.map((param, idx) => (
                    <div key={idx} className="parameter-item">
                      <div>
                        <span className="parameter-name">{param.name}</span>
                        <span className="parameter-type">{param.type}</span>
                      </div>
                      {param.description && (
                        <div className="parameter-description">{param.description}</div>
                      )}
                    </div>
                  ))}
                </div>
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
        title={selectedTool ? `${selectedTool.name}` : ''}
      >
        <div className="code-editor-container">
          <CodeEditor
            value={selectedTool?.code || ''}
            onChange={() => {}}
            language="python"
            readOnly={true}
          />
        </div>
      </Modal>
    </div>
  );
}

export default CustomTools; 