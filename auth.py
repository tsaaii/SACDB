"""
auth.py - Authentication functionality for Swaccha Andhra Dashboard

This file handles user authentication, including user data structures,
login validation, and user management.
"""

from flask_login import UserMixin

# Sample user database - in production, use a secure database
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Sample users - in production, use password hashing
users = {
    'user1': User('user1', 'admin', 'password123'),
    'user2': User('user2', 'user', 'password456'),
    'user3': User('user3', 'test@test.com', '@password!')
}

def load_user(user_id):
    """
    Load a user by their ID.
    
    Args:
        user_id (str): The user ID to load
        
    Returns:
        User: The user object if found, None otherwise
    """
    return users.get(user_id)

def validate_user(username, password):
    """
    Validate a user's credentials.
    
    Args:
        username (str): The username to validate
        password (str): The password to validate
        
    Returns:
        User: The user object if valid, None otherwise
    """
    for user_id, user in users.items():
        if user.username == username and user.password == password:
            return user
    return None