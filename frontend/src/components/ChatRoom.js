import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import './ChatRoom.css';

const ChatRoom = ({ roomName, username, chatType = 'group', onBack }) => {
    const [inputMessage, setInputMessage] = useState('');
    const { messages, sendMessage, isConnected } = useWebSocket(roomName, username, chatType);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Form submitted!', { inputMessage, isConnected });
        if (inputMessage.trim() && isConnected) {
            console.log('Calling sendMessage with:', inputMessage);
            sendMessage(inputMessage);
            setInputMessage('');
        } else {
            console.log('Message not sent. Conditions:', {
                hasMessage: !!inputMessage.trim(),
                isConnected
            });
        }
    };

    const formatTime = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const chatTitle = chatType === 'group' ? `#${roomName}` : `@${roomName}`;
    const chatSubtitle = chatType === 'group' ? 'Group Chat' : 'Direct Message';

    return (
        <div className="chat-container">
            {/* Header */}
            <div className="chat-header">
                <div className="header-content">
                    {onBack && (
                        <button className="back-btn" onClick={onBack}>
                            ←
                        </button>
                    )}
                    <div className="header-info">
                        <h2>{chatTitle}</h2>
                        <span className="chat-type-label">{chatSubtitle}</span>
                    </div>
                    <span className="username-badge">@{username}</span>
                </div>
                <div className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
                    <span className="status-dot"></span>
                    {isConnected ? 'Connected' : 'Disconnected'}
                </div>
            </div>

            {/* Messages Container */}
            <div className="messages-container">
                {messages.length === 0 ? (
                    <div className="empty-state">
                        <p>No messages yet. Start the conversation!</p>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`message ${msg.username === username ? 'own-message' : 'other-message'}`}
                        >
                            <div className="message-header">
                                <strong className="message-username">{msg.username}</strong>
                                <span className="message-time">{formatTime(msg.timestamp)}</span>
                            </div>
                            <div className="message-content">
                                {msg.message}
                            </div>
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="message-form">
                <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={isConnected ? "Type a message..." : "Connecting..."}
                    disabled={!isConnected}
                    className="message-input"
                />
                <button
                    type="submit"
                    disabled={!isConnected || !inputMessage.trim()}
                    className="send-button"
                >
                    Send
                </button>
            </form>
        </div>
    );
};

export default ChatRoom;
