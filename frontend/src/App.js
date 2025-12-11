import React, { useState } from 'react';
import ChatRoom from './components/ChatRoom';
import ChatTypeSelector from './components/ChatTypeSelector';
import GroupBrowser from './components/GroupBrowser';
import UserSearch from './components/UserSearch';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [currentView, setCurrentView] = useState('username'); // username, chatType, groupBrowser, userSearch, chat
  const [chatType, setChatType] = useState(''); // 'group' or 'personal'
  const [roomName, setRoomName] = useState('');

  const handleUsernameSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      setCurrentView('chatType');
    }
  };

  const handleChatTypeSelect = (type) => {
    setChatType(type);
    if (type === 'group') {
      setCurrentView('groupBrowser');
    } else {
      setCurrentView('userSearch');
    }
  };

  const handleJoinRoom = (room) => {
    setRoomName(room);
    setCurrentView('chat');
  };

  const handleSelectUser = (selectedUsername) => {
    setRoomName(selectedUsername);
    setCurrentView('chat');
  };

  const handleBackToTypeSelector = () => {
    setCurrentView('chatType');
    setChatType('');
    setRoomName('');
  };

  const handleBackToChat = () => {
    setCurrentView('chat');
  };

  // Username entry screen
  if (currentView === 'username') {
    return (
      <div className="app-container">
        <div className="join-container">
          <div className="join-card">
            <h1 className="app-title">💬 Real-Time Chat</h1>
            <p className="app-subtitle">Connect and chat instantly with WebSockets</p>

            <form onSubmit={handleUsernameSubmit} className="join-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  required
                  className="form-input"
                />
              </div>

              <button type="submit" className="join-button">
                Continue
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Chat type selector
  if (currentView === 'chatType') {
    return <ChatTypeSelector onSelectType={handleChatTypeSelect} />;
  }

  // Group browser
  if (currentView === 'groupBrowser') {
    return (
      <GroupBrowser
        username={username}
        onJoinRoom={handleJoinRoom}
        onBack={handleBackToTypeSelector}
      />
    );
  }

  // User search for DMs
  if (currentView === 'userSearch') {
    return (
      <UserSearch
        currentUsername={username}
        onSelectUser={handleSelectUser}
        onBack={handleBackToTypeSelector}
      />
    );
  }

  // Active chat
  if (currentView === 'chat') {
    return (
      <ChatRoom
        roomName={roomName}
        username={username}
        chatType={chatType === 'group' ? 'group' : 'dm'}
        onBack={handleBackToTypeSelector}
      />
    );
  }

  return null;
}

export default App;
