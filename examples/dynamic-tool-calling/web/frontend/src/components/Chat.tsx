import { useState, FormEvent, useEffect } from 'react';
import { FaCamera, FaImage, FaEnvelope, FaSpinner, FaSlack, FaRobot, FaCheck } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

// Types
interface Message {
  text: string;
  role?: 'user' | 'assistant';
  thoughts?: string[];  // Add thoughts array to store debug logs
  toolCalls?: ToolCall[];  // Add tool calls to each message
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
  debug_logs?: string[];  // Add debug_logs field to store debug logs
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
  const [isTyping, setIsTyping] = useState(false);
  const [tools, setTools] = useState<Tool[]>([]);
  const [usedTools, setUsedTools] = useState<Set<string>>(new Set());  // Track used tools

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
    setPrompt('');
    
    // Show typing indicator
    setIsTyping(true);

    try {
      const response = await sendChatRequest(updatedMessages);
      setIsTyping(false);
      handleChatResponse(response);
    } catch (error) {
      setIsTyping(false);
      handleError(error);
    } finally {
      setLoading(false);
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
    setMessages(prev => [...prev, { 
      text: data.response, 
      role: 'assistant',
      thoughts: data.debug_logs || [],
      toolCalls: data.tool_calls || []
    }]);
    
    // Update used tools
    if (data.tool_calls) {
      setUsedTools(prev => {
        const newSet = new Set(prev);
        data.tool_calls?.forEach(call => newSet.add(call.function.name));
        return newSet;
      });
    }
  };

  const handleError = (error: unknown) => {
    console.error('Error:', error);
    setError(error instanceof Error ? error.message : 'An error occurred');
  };

  const getToolIcon = (toolName: string) => {
    return TOOL_ICONS[toolName] || <FaRobot />;
  };

  // Add a helper function to format debug logs
  const formatDebugLog = (log: string): string => {
    // Remove timestamp and log level
    const matches = log.match(/\[(DEBUG|INFO|WARNING|ERROR)\]\s+(.+)$/);
    if (matches) {
      // Get the message part
      let message = matches[2];
      
      // Remove common prefixes
      message = message
        .replace(/\[MainProcess\(\d+\):MainThread\(\d+\)\]\s+/, '')
        .replace(/\[pocket_logger\]\s+/, '')
        .replace(/\[thread_id\(default\):profile\(default\)\]\s+/, '');
      
      // Truncate if too long
      if (message.length > 100) {
        message = message.substring(0, 97) + '...';
      }
      
      return message;
    }
    return log;
  };

  // Render Functions
  const renderMessages = () => (
    <div className="messages-container">
      {messages.length > 0 ? (
        <>
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <ReactMarkdown
                  components={{
                    a: ({ node, ...props }) => (
                      <a 
                        {...props} 
                        target="_blank" 
                        rel="noopener noreferrer"
                      />
                    )
                  }}
                >
                  {message.text}
                </ReactMarkdown>
              </div>
              {message.role === 'assistant' && (message.thoughts?.length > 0 || message.toolCalls?.length > 0) && (
                <div className="thought-process">
                  {message.toolCalls && message.toolCalls.length > 0 && (
                    <div className="thought-actions">
                      <h4>Actions taken:</h4>
                      <ul>
                        {message.toolCalls.map((call, idx) => (
                          <li key={call.id || idx}>
                            {call.function.name.replace(/_/g, ' ')}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {message.thoughts?.length > 0 && (
                    <div className="thought-logs">
                      <h4>Thought process:</h4>
                      <pre>
                        {message.thoughts.map((thought, idx) => (
                          <div key={idx}>{formatDebugLog(thought)}</div>
                        ))}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          {isTyping && (
            <div className="message assistant typing">
              <div className="message-content">
                <div className="typing-dots">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          )}
        </>
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
              <div className={`check-icon ${usedTools.has(tool.name) ? 'active' : ''}`}>
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