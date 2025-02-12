import { useState } from 'react';
import { FaComment, FaTools } from 'react-icons/fa';
import './App.css';
import Chat from './components/Chat';
import CustomTools from './components/CustomTools';

type TabType = 'chat' | 'tools';

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

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);

  return (
    <div className="container">
      <div className="content">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <FaComment /> Chat
          </button>
          <button 
            className={`tab ${activeTab === 'tools' ? 'active' : ''}`}
            onClick={() => setActiveTab('tools')}
          >
            <FaTools /> Tools
          </button>
        </div>

        {activeTab === 'chat' ? (
          <Chat 
            messages={messages}
            setMessages={setMessages}
            toolCalls={toolCalls}
            setToolCalls={setToolCalls}
          />
        ) : (
          <CustomTools />
        )}
      </div>
    </div>
  );
}

export default App; 