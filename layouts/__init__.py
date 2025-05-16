
"""
layouts/__init__.py - Package initialization file

This file makes the layouts directory a package, allowing imports
from the layouts module.
"""
from auth import load_user, User, users
from layouts.main_layout import create_main_layout


from layouts.main_layout import create_main_layout, display_page
from layouts.login_layout import create_login_layout
from layouts.dashboard_layout import create_dashboard_layout
from layouts.uploader_layout import create_uploader_layout
from data_processing import load_data

__all__ = [
    'create_main_layout',
    'display_page',
    'create_login_layout',
    'create_dashboard_layout',
    'create_uploader_layout'
]