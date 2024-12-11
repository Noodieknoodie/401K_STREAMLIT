import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history,
    get_payment_by_id,
    update_payment_note,
    format_currency_ui
)
from utils.perf_logging import log_event
from .client_payment_form import show_payment_form

# CRITICAL!!! All contact-related functionality has been moved to client_dashboard.py and client_contact_management.py
# This file now ONLY handles payment-related functionality

# ============================================================================
# STATE MANAGEMENT INITIALIZATION FUNCTIONS
# ============================================================================

def init_payment_form_state():
    """Initialize payment form state if not already initialized"""
    current_quarter = (datetime.now().month - 1) // 3 + 1
    current_year = datetime.now().year
    prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
    prev_year = current_year if current_quarter > 1 else current_year - 1
    
    # CRITICAL!!! Initialize ALL required payment form fields
    if 'payment_form' not in st.session_state:
        st.session_state.payment_form = {
            'is_visible': False,
            'mode': 'add',
            'payment_id': None,
            'client_id': None,
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'modal_lock': False,  # Required for form modal handling
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
    else:
        # CRITICAL!!! Always ensure these values are reset on initialization
        st.session_state.payment_form['is_visible'] = False
        st.session_state.payment_form['modal_lock'] = False
        st.session_state.payment_form['show_cancel_confirm'] = False

def init_notes_state():
    """Initialize notes state if not already initialized"""
    if 'active_note_id' not in st.session_state:
        st.session_state.active_note_id = None

def init_filter_state():
    """Initialize filter state if not already initialized"""
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'year': None,
            'quarter': None
        }

def format_payment_data(payments):
    """Format payment data for display"""
    formatted_payments = []
    for payment in payments:
        formatted_payments.append({
            'payment_id': payment[11],
            'Provider': payment[0],
            'Period': f"Q{payment[1]} {payment[2]}",
            'Frequency': payment[5],
            'Received': payment[6],
            'Total Assets': format_currency_ui(payment[7]),
            'Expected Fee': format_currency_ui(payment[8]),
            'Actual Fee': format_currency_ui(payment[9]),
            'Discrepancy': format_currency_ui(float(payment[9]) - float(payment[8]) if payment[8] and payment[9] else None),
            'Notes': payment[10] or ''
        })
    return formatted_payments

def show_payment_history(client_id):
    """Display the payment history section."""
    # Initialize states
    init_payment_form_state()
    init_notes_state()
    init_filter_state()
    
    # CRITICAL!!! Check if we're switching clients and close form if needed
    if ('payment_form' in st.session_state and 
        st.session_state.payment_form['client_id'] != client_id):
        # We're switching clients, ensure form is closed
        st.session_state.payment_form['is_visible'] = False
    
    # Update client_id in payment form state
    if 'payment_form' in st.session_state:
        st.session_state.payment_form['client_id'] = client_id
    
    # Initialize delete confirmation state
    if 'delete_payment_id' not in st.session_state:
        st.session_state.delete_payment_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
        
    # Get data first
    payments = get_payment_history(client_id)
    
    if not payments:
        st.info("No payment history found.")
        return
        
    # Get available years
    years = sorted(set(year for payment in payments for year in [payment[2], payment[4]]), reverse=True)
    current_year = datetime.now().year
    
    # Create a row with the same width as the table
    filter_col1, filter_col2, filter_col3 = st.columns([2,2,1])
    
    with filter_col1:
        selected_time = st.radio(
            "Time Period",
            ["All Time", "This Year", "Custom"],
            horizontal=True,
            key="time_period"
        )
    
    with filter_col2:
        if selected_time == "Custom":
            selected_year = st.selectbox(
                "Year",
                years,
                index=0 if years else 0
            )
            st.session_state.filter_state['year'] = selected_year
    
    with filter_col3:
        if selected_time == "Custom":
            selected_quarter = st.selectbox(
                "Quarter",
                ["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                index=0
            )
            st.session_state.filter_state['quarter'] = selected_quarter
    
    # Add payment button
    if st.button("Add Payment"):
        st.session_state.payment_form['is_visible'] = True
        st.rerun()
    
    # Determine filters based on selection
    if selected_time == "All Time":
        year_filters = None
        quarter_filters = None
    elif selected_time == "This Year":
        year_filters = [current_year]
        quarter_filters = None
    else:  # Custom
        year_filters = [st.session_state.filter_state['year']]
        quarter_filters = None if st.session_state.filter_state['quarter'] == "All Quarters" else [int(st.session_state.filter_state['quarter'][1])]
    
    # Load and format payment data
    payments = get_payment_history(client_id, years=year_filters, quarters=quarter_filters)
    if not payments:
        st.info(f"No payments found for the selected period.")
        return
        
    formatted_payments = format_payment_data(payments)
    
    # Display payment table
    if formatted_payments:
        df = pd.DataFrame(formatted_payments)
        st.dataframe(
            df,
            use_container_width=True,  # Make it fill the page width
            height=400  # Add scrollable height
        )

def display_client_dashboard():
    """Display the client dashboard."""
    if 'client_data' not in st.session_state:
        st.error("No client selected. Please select a client first.")
        return

    client_id = st.session_state.client_data['client_id']
    show_payment_history(client_id)

def display_payments_section():
    """Display the payments section using the new data structure"""
    if 'client_data' not in st.session_state:
        st.error("No client selected. Please select a client first.")
        return

    client_id = st.session_state.client_data['client_id']
    show_payment_history(client_id)

def clear_client_specific_states():
    """Clear all client-specific states when switching clients."""
    # Clear filter state
    if 'filter_state' in st.session_state:
        st.session_state.filter_state = {
            'year': None,
            'quarter': None
        }
    
    # Clear notes state
    if 'active_note_id' in st.session_state:
        st.session_state.active_note_id = None
    
    # CRITICAL!!! Reset payment form completely
    if 'payment_form' in st.session_state:
        current_quarter = (datetime.now().month - 1) // 3 + 1
        current_year = datetime.now().year
        prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
        prev_year = current_year if current_quarter > 1 else current_year - 1
        
        # Ensure form is closed and all state is reset
        st.session_state.payment_form = {
            'is_visible': False,  # CRITICAL!!! Ensure form is closed
            'mode': 'add',
            'payment_id': None,
            'client_id': None,  # Reset client_id when switching
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'modal_lock': False,  # CRITICAL!!! Reset modal lock
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

def handle_note_edit(payment_id, new_note):
    """Handle updating a payment note."""
    log_event('note_saved', {'payment_id': payment_id, 'has_content': bool(new_note)})
    update_payment_note(payment_id, new_note)
    if 'active_note_id' in st.session_state:
        st.session_state.active_note_id = None
    