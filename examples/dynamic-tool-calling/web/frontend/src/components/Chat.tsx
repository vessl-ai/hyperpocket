import { useState, FormEvent, useEffect } from 'react';
import { FaCamera, FaImage, FaEnvelope, FaSpinner, FaSlack, FaRobot, FaCheck } from 'react-icons/fa';

// Types
interface Message {
  text: string;
  role?: 'user' | 'assistant';
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

interface Tool {
  name: string;
  description: string;
}

// Tool Icons Mapping
const TOOL_ICONS: Record<string, JSX.Element> = {
  'take_a_picture': <FaCamera />,
  'call_diffusion_model': <FaImage />,
  'send_mail': <FaEnvelope />,
  'get_slack_messages': <FaSlack />,
  'post_slack_message': <FaSlack />,
  'get_channel_members': <FaSlack />,
};

interface ChatProps {
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  toolCalls: ToolCall[];
  setToolCalls: (toolCalls: ToolCall[]) => void;
}

function Chat({ messages, setMessages, toolCalls, setToolCalls }: ChatProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tools, setTools] = useState<Tool[]>([]);

  // Effects
  useEffect(() => {
    fetchTools();
  }, []);

  // Handlers
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    setToolCalls([]);

    const newMessage: Message = { text: prompt, role: 'user' };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);

    try {
      const response = await sendChatRequest(updatedMessages);
      handleChatResponse(response);
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
      setPrompt('');
    }
  };

  // API Calls
  const fetchTools = async () => {
    try {
      const res = await fetch('http://localhost:3001/api/tools');
      if (!res.ok) throw new Error('Failed to fetch tools');
      const data = await res.json();
      setTools(data.tools);
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

  const sendChatRequest = async (messages: Message[]): Promise<ApiResponse> => {
    const res = await fetch('http://localhost:3001/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Failed to get response');
    }

    return res.json();
  };

  // Helper Functions
  const handleChatResponse = (data: ApiResponse) => {
    setMessages(prev => [...prev, { text: data.response, role: 'assistant' }]);
    if (data.tool_calls) setToolCalls(data.tool_calls);
  };

  const handleError = (error: unknown) => {
    console.error('Error:', error);
    setError(error instanceof Error ? error.message : 'An error occurred');
  };

  const getToolIcon = (toolName: string) => {
    return TOOL_ICONS[toolName] || <FaRobot />;
  };

  const convertLinksToHtml = (text: string) => {
    // First, replace newlines with <br> tags
    let formattedText = text.replace(/\n/g, '<br>');
    
    // Then handle URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    formattedText = formattedText.replace(urlRegex, (url) => {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });

    return formattedText;
  };

  // Render Functions
  const renderMessages = () => (
    <div className="messages-container">
      {messages.length > 0 ? (
        messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div 
              className="message-content"
              dangerouslySetInnerHTML={{ __html: convertLinksToHtml(message.text) }}
            />
            {message.role === 'assistant' && toolCalls.length > 0 && (
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
        ))
      ) : (
        <div className="empty-chat">
          Start a conversation by sending a message
        </div>
      )}
    </div>
  );

  const renderToolsSection = () => (
    <div className="tools-section">
      <span className="tools-label">Tools integrated:</span>
      <div className="tools">
        {tools.map((tool) => (
          <div 
            key={tool.name} 
            className="tool-wrapper" 
            data-tooltip={`${tool.name.replace(/_/g, ' ')}\n${tool.description}`}
          >
            <span className="tool-icon">
              {getToolIcon(tool.name)}
              <div className={`check-icon ${toolCalls.some(call => call.function.name === tool.name) ? 'active' : ''}`}>
                ✓
              </div>
            </span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="chat-wrapper">
      <div className="chat-container">
        {renderMessages()}
        <form onSubmit={handleSubmit} className="prompt-form">
          <div className="prompt-input-wrapper">
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
          </div>
        </form>
      </div>
      
      {renderToolsSection()}

      {loading && (
        <div className="loading">
          <FaSpinner className="spinner" />
          Processing...
        </div>
      )}
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default Chat; 