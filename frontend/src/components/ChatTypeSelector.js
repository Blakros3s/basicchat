import React from 'react';
import './ChatTypeSelector.css';

const ChatTypeSelector = ({ onSelectType }) => {
    return (
        <div className="chat-type-container">
            <div className="chat-type-card">
                <h1 className="app-title">💬 Real-Time Chat</h1>
                <p className="app-subtitle">Choose how you want to chat</p>

                <div className="chat-type-options">
                    <button
                        className="chat-type-button group-chat"
                        onClick={() => onSelectType('group')}
                    >
                        <div className="icon">👥</div>
                        <h3>Group Chat</h3>
                        <p>Join or create group conversations</p>
                    </button>

                    <button
                        className="chat-type-button personal-chat"
                        onClick={() => onSelectType('personal')}
                    >
                        <div className="icon">💬</div>
                        <h3>Personal Message</h3>
                        <p>Direct message with other users</p>
                    </button>
                </div>

                <div className="info-section">
                    <p className="info-text">
                        <strong>Group Chat:</strong> Browse and join existing rooms or create your own
                    </p>
                    <p className="info-text">
                        <strong>Personal Message:</strong> Search for users and start private conversations
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ChatTypeSelector;
