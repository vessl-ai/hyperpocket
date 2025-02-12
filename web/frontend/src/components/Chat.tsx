import { useState, FormEvent, useEffect } from 'react';
import { FaCamera, FaImage, FaEnvelope, FaCheck, FaSpinner } from 'react-icons/fa';
import { FaSlack, FaRobot } from 'react-icons/fa';

interface Tool {
  name: string;
  description: string;
}

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

interface Message {
  text: string;
}

// Map tool names to icons
const TOOL_ICONS: Record<string, JSX.Element> = {
  'take_a_picture': <FaCamera />,
  'call_diffusion_model': <FaImage />,
  'send_mail': <FaEnvelope />,
  'get_slack_messages': <FaSlack />,
  'post_slack_message': <FaSlack />,
  'get_channel_members': <FaSlack />,
};

function Chat() {
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string>('');
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [error, setError] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [usedTools, setUsedTools] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/tools');
      if (!res.ok) {
        throw new Error('Failed to fetch tools');
      }
      const data = await res.json();
      setTools(data.tools);
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

  const getToolIcon = (toolName: string) => {
    return TOOL_ICONS[toolName] || <FaRobot />;  // Default icon for custom tools
  };

  const convertLinksToHtml = (text: string) => {
    const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const urlRegex = /(?<![[\]])\b(https?:\/\/[^\s<>"']+)(?![^<]*>|[^<>]*<\/)/g;

    let processedText = text.replace(markdownLinkRegex, 
      (match, text, url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`
    );
    
    processedText = processedText.replace(urlRegex, 
      (match, url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
    );

    return processedText;
  };

  const renderToolStatus = (toolName: string) => {
    const isToolUsed = toolCalls.some(
      call => call.function.name.toLowerCase().includes(toolName.toLowerCase())
    );
    return (
      <div className="tool-wrapper">
        <span className="tool-icon">
          {getToolIcon(toolName)}
        </span>
        <div className={`check-icon ${usedTools.has(toolName) ? 'active' : ''}`} />
      </div>
    );
  };

  const renderMessages = () => {
    return messages.map((message, index) => (
      <div 
        key={index} 
        className={`message ${index % 2 === 0 ? 'user' : 'assistant'}`}
      >
        <div 
          className="message-content"
          dangerouslySetInnerHTML={{ 
            __html: convertLinksToHtml(message.text) 
          }}
        />
        {index % 2 === 1 && toolCalls.length > 0 && (
          <div className="tool-calls">
            <h4>Actions taken:</h4>
            <ul>
              {toolCalls.map((call, idx) => (
                <li key={call.id || idx}>
                  {call.function.name.replace(/_/g, ' ')}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    ));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');
    setToolCalls([]);

    // Add new user message to history
    const newMessage: Message = { text: prompt };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);

    try {
      const res = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: updatedMessages }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data: ApiResponse = await res.json();
      setResponse(data.response);
      
      // Add assistant's response to message history
      setMessages(prev => [...prev, { text: data.response }]);
      
      if (data.tool_calls) {
        setToolCalls(data.tool_calls);
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
      setPrompt(''); // Clear input after submission
    }
  };

  return (
    <>
      <div className="chat-container">
        <div className="messages-container">
          {messages.length > 0 ? (
            renderMessages()
          ) : (
            <div className="empty-chat">
              Start a conversation by sending a message
            </div>
          )}
        </div>

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
            {loading ? <FaSpinner className="spinner" /> : 'Send'}
          </button>
        </form>
      </div>
      
      <div className="tools-section">
        <span className="tools-label">Tools integrated:</span>
        <div className="tools">
          {tools.map((tool) => (
            <div 
              key={tool.name} 
              className="tool-wrapper" 
              data-tooltip={`${tool.name}\n${tool.description}`}
            >
              <span className="tool-icon">
                {getToolIcon(tool.name)}
              </span>
              <FaCheck className="tool-check" />
            </div>
          ))}
        </div>
      </div>

      {loading && (
        <div className="loading">
          <FaSpinner className="spinner" />
          Processing...
        </div>
      )}
      {error && <div className="error">{error}</div>}
    </>
  );
}

export default Chat; 