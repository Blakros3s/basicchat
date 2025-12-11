import React, { useState, useEffect } from 'react';
import './GroupBrowser.css';

const GroupBrowser = ({ username, onJoinRoom, onBack }) => {
    const [rooms, setRooms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newRoomName, setNewRoomName] = useState('');
    const [newRoomDescription, setNewRoomDescription] = useState('');
    const [showCreateForm, setShowCreateForm] = useState(false);

    useEffect(() => {
        fetchRooms();
    }, []);

    const fetchRooms = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/rooms/');
            const data = await response.json();
            setRooms(data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching rooms:', error);
            setLoading(false);
        }
    };

    const handleCreateRoom = async (e) => {
        e.preventDefault();
        if (!newRoomName.trim()) return;

        try {
            const response = await fetch('http://localhost:8000/api/rooms/create_or_get/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: newRoomName,
                    description: newRoomDescription
                })
            });

            if (response.ok) {
                const room = await response.json();
                setNewRoomName('');
                setNewRoomDescription('');
                setShowCreateForm(false);
                fetchRooms();
                // Automatically join the newly created room
                onJoinRoom(room.name);
            }
        } catch (error) {
            console.error('Error creating room:', error);
        }
    };

    return (
        <div className="group-browser-container">
            <div className="group-browser-card">
                <div className="browser-header">
                    <button className="back-button" onClick={onBack}>
                        ← Back
                    </button>
                    <h2>Group Chats</h2>
                    <button
                        className="create-button"
                        onClick={() => setShowCreateForm(!showCreateForm)}
                    >
                        {showCreateForm ? '✕' : '+ Create'}
                    </button>
                </div>

                {showCreateForm && (
                    <form className="create-room-form" onSubmit={handleCreateRoom}>
                        <input
                            type="text"
                            placeholder="Room name"
                            value={newRoomName}
                            onChange={(e) => setNewRoomName(e.target.value)}
                            className="room-input"
                            required
                        />
                        <input
                            type="text"
                            placeholder="Description (optional)"
                            value={newRoomDescription}
                            onChange={(e) => setNewRoomDescription(e.target.value)}
                            className="room-input"
                        />
                        <button type="submit" className="submit-button">
                            Create Room
                        </button>
                    </form>
                )}

                <div className="rooms-list">
                    {loading ? (
                        <p className="loading-text">Loading rooms...</p>
                    ) : rooms.length === 0 ? (
                        <div className="empty-state">
                            <p>No group chats available</p>
                            <p className="empty-hint">Create one to get started!</p>
                        </div>
                    ) : (
                        rooms.map((room) => (
                            <div key={room.id} className="room-card">
                                <div className="room-info">
                                    <h3 className="room-name">#{room.name}</h3>
                                    {room.description && (
                                        <p className="room-description">{room.description}</p>
                                    )}
                                    <div className="room-meta">
                                        <span className="member-count">
                                            👥 {room.member_count || 0} members
                                        </span>
                                        <span className="message-count">
                                            💬 {room.message_count || 0} messages
                                        </span>
                                    </div>
                                </div>
                                <button
                                    className="join-button"
                                    onClick={() => onJoinRoom(room.name)}
                                >
                                    Join
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default GroupBrowser;
