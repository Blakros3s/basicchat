import React, { useState, useEffect } from 'react';
import './UserSearch.css';

const UserSearch = ({ currentUsername, onSelectUser, onBack }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [users, setUsers] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchAllUsers();
    }, []);

    const fetchAllUsers = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/users/');
            const data = await response.json();
            // Filter out current user
            const filteredUsers = data.filter(user => user.username !== currentUsername);
            setAllUsers(filteredUsers);
            setUsers(filteredUsers.slice(0, 10)); // Show first 10
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    };

    const handleSearch = async (query) => {
        setSearchQuery(query);

        if (!query.trim()) {
            setUsers(allUsers.slice(0, 10));
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/api/users/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            // Filter out current user
            const filteredUsers = data.users.filter(user => user.username !== currentUsername);
            setUsers(filteredUsers);
            setLoading(false);
        } catch (error) {
            console.error('Error searching users:', error);
            setLoading(false);
        }
    };

    return (
        <div className="user-search-container">
            <div className="user-search-card">
                <div className="search-header">
                    <button className="back-button" onClick={onBack}>
                        ← Back
                    </button>
                    <h2>Start a Conversation</h2>
                </div>

                <div className="search-box">
                    <input
                        type="text"
                        placeholder="Search users by username..."
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                        className="search-input"
                    />
                    <span className="search-icon">🔍</span>
                </div>

                <div className="users-list">
                    {loading ? (
                        <p className="loading-text">Searching...</p>
                    ) : users.length === 0 ? (
                        <div className="empty-state">
                            <p>No users found</p>
                            {searchQuery && (
                                <p className="empty-hint">Try a different search term</p>
                            )}
                        </div>
                    ) : (
                        users.map((user) => (
                            <div
                                key={user.id}
                                className="user-card"
                                onClick={() => onSelectUser(user.username)}
                            >
                                <div className="user-avatar">
                                    {user.username.charAt(0).toUpperCase()}
                                </div>
                                <div className="user-info">
                                    <h3 className="user-name">
                                        {user.username}
                                    </h3>
                                    {(user.first_name || user.last_name) && (
                                        <p className="user-full-name">
                                            {user.first_name} {user.last_name}
                                        </p>
                                    )}
                                </div>
                                <div className="message-icon">💬</div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default UserSearch;
