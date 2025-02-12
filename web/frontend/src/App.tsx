import { useState } from 'react';
import { FaComment, FaTools } from 'react-icons/fa';
import './App.css';
import Chat from './components/Chat';
import CustomTools from './components/CustomTools';

type TabType = 'chat' | 'tools';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');

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

        {activeTab === 'chat' ? <Chat /> : <CustomTools />}
      </div>
    </div>
  );
}

export default App; 