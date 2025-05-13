"""
layouts/__init__.py - Package initialization file

This file makes the layouts directory a package, allowing imports
from the layouts module.
"""

from layouts.main_layout import create_main_layout, display_page
from layouts.login_layout import create_login_layout
from layouts.dashboard_layout import create_dashboard_layout

__all__ = [
    'create_main_layout',
    'display_page',
    'create_login_layout',
    'create_dashboard_layout'
]