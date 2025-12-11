import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Custom hook for WebSocket connection to chat room or DM
 * @param {string} roomName - Name of the chat room or recipient username
 * @param {string} username - Username of the current user
 * @param {string} chatType - Type of chat: 'group' or 'dm'
 * @returns {object} - { messages, sendMessage, isConnected }
 */
export const useWebSocket = (roomName, username, chatType = 'group') => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    if (!roomName || !username) return;

    // WebSocket URL based on chat type
    // WebSocket URL based on chat type
    const wsBaseUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    const wsUrl = chatType === 'group'
      ? `${wsBaseUrl}/ws/group/${roomName}/?user=${username}`
      : `${wsBaseUrl}/ws/dm/${roomName}/?user=${username}`;

    console.log(`Connecting to WebSocket (${chatType}): ${wsUrl}`);

    // Create WebSocket connection
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);

      if (data.type === 'message_history') {
        // Load previous messages
        setMessages(data.messages);
      } else if (data.type === 'chat_message') {
        // Add new message
        setMessages(prev => [...prev, {
          username: data.username,
          message: data.message,
          timestamp: data.timestamp
        }]);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setIsConnected(false);
    };

    ws.current.onclose = (event) => {
      console.log('WebSocket Disconnected', event.code, event.reason);
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [roomName, username, chatType]);

  const sendMessage = useCallback((message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      const payload = {
        message,
        username,
        timestamp: new Date().toISOString()
      };
      ws.current.send(JSON.stringify(payload));
      console.log('Sent message:', payload);
    } else {
      console.error('WebSocket is not connected');
    }
  }, [username]);

  return { messages, sendMessage, isConnected };
};
