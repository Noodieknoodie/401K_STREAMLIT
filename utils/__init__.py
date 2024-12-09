"""Utilities for the 401K Payment Tracker."""

# Database
from .database.connection import get_database_connection
from .database.client_queries import get_clients, get_client_details
from .database.contact_queries import get_contacts, add_contact, delete_contact, update_contact
from .database.contract_queries import get_active_contract, get_all_contracts
from .database.payment_queries import get_latest_payment, get_payment_history, update_payment_note
from .database.pagination import get_paginated_payment_history, get_total_payment_count, get_payment_year_quarters

# Formatters
from .formatters.phone import format_phone_number_ui, format_phone_number_db
from .formatters.rate import calculate_rate_conversions

# Validators
from .validators.input import validate_phone_number

__all__ = [
    # Database
    'get_database_connection',
    'get_clients',
    'get_client_details',
    'get_contacts',
    'add_contact',
    'delete_contact',
    'update_contact',
    'get_active_contract',
    'get_all_contracts',
    'get_latest_payment',
    'get_payment_history',
    'update_payment_note',
    'get_paginated_payment_history',
    'get_total_payment_count',
    'get_payment_year_quarters',
    # Formatters
    'format_phone_number_ui',
    'format_phone_number_db',
    'calculate_rate_conversions',
    # Validators
    'validate_phone_number',
] 