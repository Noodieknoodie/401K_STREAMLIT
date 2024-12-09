"""
Centralized state management for the client dashboard.
This file manages all state interactions and provides a single source of truth.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Union
from .payment_utils import (
    get_current_quarter,
    get_previous_quarter,
    get_current_period,
    calculate_expected_fee,
    validate_period_range
)

class DashboardState:
    """Central state manager for the client dashboard."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize all required dashboard states."""
        PaymentFormState.initialize()
        PaymentHistoryState.initialize()
        ContactFormState.initialize()
        NotesState.initialize()
        ClientState.initialize()

class ClientState:
    """Manages client selection and related state."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize client state."""
        if 'previous_client' not in st.session_state:
            st.session_state.previous_client = None
    
    @staticmethod
    def set_client(client_id: str, client_name: str) -> None:
        """Set the current client and handle state resets."""
        if st.session_state.previous_client != client_name:
            PaymentHistoryState.reset()
            st.session_state.previous_client = client_name
    
    @staticmethod
    def get_previous_client() -> Optional[str]:
        """Get the previous client name."""
        return st.session_state.get('previous_client')

class PaymentFormState:
    """Manages payment form state and interactions."""
    
    @staticmethod
    def get_default_state() -> Dict[str, Any]:
        """Get default payment form state."""
        current_quarter = get_current_quarter()
        current_year = datetime.now().year
        prev_quarter, prev_year = get_previous_quarter(current_quarter, current_year)
        
        return {
            'is_open': False,
            'mode': 'add',
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'active_contract': None,
            'form_data': {
                'received_date': datetime.now().strftime('%Y-%m-%d'),
                'applied_start_quarter': prev_quarter,
                'applied_start_year': prev_year,
                'applied_end_quarter': None,
                'applied_end_year': None,
                'total_assets': '',
                'actual_fee': '',
                'expected_fee': None,
                'method': 'None Specified',
                'other_method': '',
                'notes': ''
            }
        }
    
    @staticmethod
    def initialize() -> None:
        """Initialize payment form state."""
        if 'payment_form' not in st.session_state:
            st.session_state.payment_form = PaymentFormState.get_default_state()
    
    @staticmethod
    def clear() -> None:
        """Reset payment form state and related states."""
        PaymentFormState.initialize()
        st.session_state.payment_form = PaymentFormState.get_default_state()
        PaymentHistoryState.reset()
    
    @staticmethod
    def update_form_data(field: str, value: Any) -> None:
        """Update a form data field and handle dependencies."""
        PaymentFormState.initialize()
        st.session_state.payment_form['form_data'][field] = value
        
        # Handle dependent updates
        if field == 'total_assets' and st.session_state.payment_form.get('active_contract'):
            expected_fee = calculate_expected_fee(
                st.session_state.payment_form['active_contract'],
                value
            )
            if expected_fee is not None:
                st.session_state.payment_form['form_data']['expected_fee'] = f"${expected_fee:,.2f}"
    
    @staticmethod
    def is_open() -> bool:
        """Check if payment form is open."""
        return bool(st.session_state.get('payment_form', {}).get('is_open', False))
    
    @staticmethod
    def set_open(is_open: bool) -> None:
        """Set payment form open state."""
        PaymentFormState.initialize()
        st.session_state.payment_form['is_open'] = is_open
    
    @staticmethod
    def has_validation_error() -> bool:
        """Check if payment form has validation errors."""
        return bool(st.session_state.get('payment_form', {}).get('has_validation_error', False))
    
    @staticmethod
    def set_validation_error(has_error: bool) -> None:
        """Set validation error state."""
        PaymentFormState.initialize()
        st.session_state.payment_form['has_validation_error'] = has_error
    
    @staticmethod
    def get_form_data() -> Dict[str, Any]:
        """Get current form data."""
        PaymentFormState.initialize()
        return st.session_state.payment_form['form_data'].copy()
    
    @staticmethod
    def set_contract(contract_data: Optional[tuple]) -> None:
        """Set active contract data and update period defaults."""
        PaymentFormState.initialize()
        st.session_state.payment_form['active_contract'] = contract_data
        
        if contract_data:
            schedule = contract_data[3]  # contract[3] is payment_schedule
            current_period = get_current_period(schedule)
            current_year = datetime.now().year
            
            # Get previous period based on schedule
            if schedule and schedule.lower() == 'monthly':
                prev_period = current_period - 1 if current_period > 1 else 12
                prev_year = current_year if current_period > 1 else current_year - 1
            else:  # Quarterly or null schedule
                prev_period = current_period - 1 if current_period > 1 else 4
                prev_year = current_year if current_period > 1 else current_year - 1
            
            PaymentFormState.update_form_data('applied_start_period', prev_period)
            PaymentFormState.update_form_data('applied_start_year', prev_year)
    
    @staticmethod
    def get_contract() -> Optional[tuple]:
        """Get active contract data."""
        PaymentFormState.initialize()
        return st.session_state.payment_form.get('active_contract')
    
    @staticmethod
    def toggle_cancel_confirm() -> None:
        """Toggle the cancel confirmation dialog state."""
        PaymentFormState.initialize()
        current_state = st.session_state.payment_form.get('show_cancel_confirm', False)
        st.session_state.payment_form['show_cancel_confirm'] = not current_state
    
    @staticmethod
    def validate_period_range(
        start_period: int,
        start_year: int,
        end_period: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> bool:
        """Validate that the period range is valid for the contract's schedule."""
        contract = PaymentFormState.get_contract()
        if not contract:
            return False
        
        schedule = contract[3]  # contract[3] is payment_schedule
        return validate_period_range(start_period, start_year, end_period, end_year, schedule)

class PaymentHistoryState:
    """Manages payment history state and pagination."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize payment history state."""
        if 'payment_data' not in st.session_state:
            st.session_state.payment_data = []
        if 'payment_offset' not in st.session_state:
            st.session_state.payment_offset = 0
        if 'current_filters' not in st.session_state:
            st.session_state.current_filters = None
    
    @staticmethod
    def reset() -> None:
        """Reset payment history state."""
        st.session_state.payment_data = []
        st.session_state.payment_offset = 0
        if 'current_filters' in st.session_state:
            del st.session_state.current_filters
    
    @staticmethod
    def get_payment_data() -> List[Dict[str, Any]]:
        """Get current payment data."""
        PaymentHistoryState.initialize()
        return st.session_state.payment_data.copy()
    
    @staticmethod
    def get_offset() -> int:
        """Get current pagination offset."""
        PaymentHistoryState.initialize()
        return st.session_state.payment_offset
    
    @staticmethod
    def set_filters(filters: tuple) -> None:
        """Set current filters and handle state reset if needed."""
        PaymentHistoryState.initialize()
        if st.session_state.current_filters != filters:
            PaymentHistoryState.reset()
            st.session_state.current_filters = filters
    
    @staticmethod
    def get_filters() -> Optional[tuple]:
        """Get current filters."""
        PaymentHistoryState.initialize()
        return st.session_state.current_filters
    
    @staticmethod
    def append_data(data: List[Dict[str, Any]]) -> None:
        """Append new payment data."""
        PaymentHistoryState.initialize()
        st.session_state.payment_data.extend(data)
        st.session_state.payment_offset = len(st.session_state.payment_data)

class NotesState:
    """Manages notes state for payments."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize notes state."""
        if 'notes_state' not in st.session_state:
            st.session_state.notes_state = {
                'active_note': None,
                'edited_notes': {}
            }
    
    @staticmethod
    def set_active_note(payment_id: Optional[str], save_callback: Optional[Callable[[str, str], None]] = None) -> None:
        """Set the active note and handle auto-save."""
        NotesState.initialize()
        
        # Get current active note before changing
        current_active = st.session_state.notes_state['active_note']
        
        # If we're toggling the same note off, save it first
        if current_active == payment_id and save_callback is not None:
            if payment_id in st.session_state.notes_state['edited_notes']:
                save_callback(
                    payment_id,
                    st.session_state.notes_state['edited_notes'][payment_id]
                )
                st.session_state.notes_state['edited_notes'].pop(payment_id)
        # If we're switching to a different note, save the previous one
        elif current_active and current_active != payment_id and save_callback is not None:
            if current_active in st.session_state.notes_state['edited_notes']:
                save_callback(
                    current_active,
                    st.session_state.notes_state['edited_notes'][current_active]
                )
                st.session_state.notes_state['edited_notes'].pop(current_active)
        
        st.session_state.notes_state['active_note'] = payment_id
    
    @staticmethod
    def get_active_note() -> Optional[str]:
        """Get currently active note ID."""
        NotesState.initialize()
        return st.session_state.notes_state['active_note']
    
    @staticmethod
    def set_edited_note(payment_id: str, note: str) -> None:
        """Set an edited note value."""
        NotesState.initialize()
        st.session_state.notes_state['edited_notes'][payment_id] = note
    
    @staticmethod
    def get_edited_note(payment_id: str) -> Optional[str]:
        """Get an edited note value."""
        NotesState.initialize()
        return st.session_state.notes_state['edited_notes'].get(payment_id)

class ContactFormState:
    """Manages contact form state."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize contact form state."""
        if 'contact_form' not in st.session_state:
            st.session_state.contact_form = {
                'is_open': False,
                'has_validation_error': False,
                'show_cancel_confirm': False,
                'form_data': {
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'phone': '',
                    'contact_type': 'Primary'
                }
            }
        if 'delete_contact_id' not in st.session_state:
            st.session_state.delete_contact_id = None
        if 'show_delete_confirm' not in st.session_state:
            st.session_state.show_delete_confirm = False
    
    @staticmethod
    def is_open() -> bool:
        """Check if contact form is open."""
        return bool(st.session_state.get('contact_form', {}).get('is_open', False))
    
    @staticmethod
    def set_open(is_open: bool) -> None:
        """Set contact form open state."""
        ContactFormState.initialize()
        st.session_state.contact_form['is_open'] = is_open
    
    @staticmethod
    def has_validation_error() -> bool:
        """Check if contact form has validation errors."""
        return bool(st.session_state.get('contact_form', {}).get('has_validation_error', False))
    
    @staticmethod
    def set_validation_error(has_error: bool) -> None:
        """Set validation error state."""
        ContactFormState.initialize()
        st.session_state.contact_form['has_validation_error'] = has_error