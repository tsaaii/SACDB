"""
auth.py - Modified for GCP deployment with improved security
"""

from flask_login import UserMixin
import os
import hashlib
import json

class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user'):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
    
    def check_password(self, password):
        """
        Check if provided password matches the hash.
        
        Args:
            password (str): The password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        # Create a hash of the provided password with the salt
        hashed = hashlib.sha256((password + _get_salt()).encode()).hexdigest()
        return hashed == self.password_hash

def _get_salt():
    """
    Get the salt for password hashing.
    
    Returns:
        str: The salt
    """
    return os.environ.get('PASSWORD_SALT', 'swaccha_andhra_default_salt')

def _load_users():
    """
    Load users from environment variable or config file.
    
    Returns:
        dict: Dictionary of users
    """
    users_dict = {}
    
    # Try to load from environment variable first
    users_json = os.environ.get('USERS_CONFIG')
    
    if users_json:
        try:
            # Parse JSON from environment variable
            user_list = json.loads(users_json)
            
            # Convert to User objects
            for user_data in user_list:
                user_id = user_data.get('id')
                if user_id:
                    users_dict[user_id] = User(
                        id=user_id,
                        username=user_data.get('username'),
                        password_hash=user_data.get('password_hash'),
                        role=user_data.get('role', 'user')
                    )
        except json.JSONDecodeError:
            print("Error: Unable to parse USERS_CONFIG environment variable")
    
    # If no users from environment, use default users (for development only)
    if not users_dict and os.environ.get('DASH_ENV') != 'production':
        # Default users (FOR DEVELOPMENT ONLY)
        # In production, always set USERS_CONFIG environment variable
        users_dict = {
            'user1': User(
                id='user1', 
                username='admin', 
                # Hash of 'password123' with default salt
                password_hash=hashlib.sha256(('password123' + _get_salt()).encode()).hexdigest()
            ),
            'user2': User(
                id='user2', 
                username='user', 
                # Hash of 'password456' with default salt
                password_hash=hashlib.sha256(('password456' + _get_salt()).encode()).hexdigest()
            ),
            'user3': User(
                id='user3', 
                username='test@test.com', 
                # Hash of '@password!' with default salt
                password_hash=hashlib.sha256(('@password!' + _get_salt()).encode()).hexdigest()
            )
        }
    
    return users_dict

# Initialize users
users = _load_users()

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
        if user.username == username and user.check_password(password):
            return user
    return None

def create_user(username, password, role='user'):
    """
    Create a new user (admin utility function, not exposed in web interface).
    
    Args:
        username (str): The username
        password (str): The password
        role (str): The role (default: 'user')
    
    Returns:
        dict: User info as a dictionary
    """
    # Generate a unique ID
    user_id = f"user{len(users) + 1}"
    
    # Hash the password
    password_hash = hashlib.sha256((password + _get_salt()).encode()).hexdigest()
    
    # Create user info dictionary (for storing in environment or config)
    user_info = {
        'id': user_id,
        'username': username,
        'password_hash': password_hash,
        'role': role
    }
    
    # For development mode, add user to in-memory dict
    if os.environ.get('DASH_ENV') != 'production':
        users[user_id] = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=role
        )
    
    return user_info