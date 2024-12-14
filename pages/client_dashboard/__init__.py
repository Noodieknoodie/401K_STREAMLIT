"""
Package initialization for client dashboard
"""

from .client_contact_management import render_contact_section, render_contact_card, show_contact_form
from .client_contact_layout import show_contact_sections
from .client_dashboard import show_client_dashboard
from .client_payment_form import show_payment_dialog
from .client_payment_management import show_payment_history
from .client_selection import get_selected_client
from .client_dashboard_metrics import show_client_metrics

__all__ = [
    'render_contact_section',
    'render_contact_card',
    'show_contact_form',
    'show_contact_sections',
    'show_client_dashboard',
    'show_payment_dialog',
    'show_payment_history',
    'get_selected_client',
    'show_client_metrics'
] 