"""
callbacks/__init__.py - Package initialization file

This file makes the callbacks directory a package, allowing imports
from the callbacks module.
"""


from callbacks.auth_callbacks import register_auth_callbacks
from callbacks.dashboard_callbacks import register_dashboard_callbacks
from callbacks.uploader_callbacks import register_uploader_callbacks

__all__ = [
    'register_auth_callbacks',
    'register_dashboard_callbacks',
    'register_uploader_callbacks'
]