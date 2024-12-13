# pages\client_dashboard\client_payment_form.py

"""
Client Payment Form Module
=========================

This module handles the payment form UI and logic with a sophisticated period/quarter system.

Key Concepts:
------------
1. Period vs Quarter Handling:
   - UI uses generic "period" terminology that adapts to contract schedule
   - Database always stores data in quarters for consistency
   - Automatic conversion happens in add_payment():
     * Monthly schedule: converts months to quarters before storage
     * Quarterly schedule: stores periods as-is (already quarters)

2. Form Data Structure:
   - Uses 'applied_start_period' and 'applied_end_period' in form
   - Converts to 'applied_start_quarter' and 'applied_end_quarter' for database
   - Conversion happens automatically in add_payment()

3. State Management:
   - Uses UIStateManager for all dialog state
   - Form data stored in UIStateManager.payment_form_data
   - All validation errors handled through UIStateManager

4. Payment Schedules:
   Monthly Display:
   - Shows months (e.g., "Jan 2024")
   - Converts to quarters (Jan-Mar → Q1) for storage
   
   Quarterly Display:
   - Shows quarters directly (e.g., "Q1 2024")
   - Stores as-is in database

5. Validation Flow:
   - UI validation during input (format_payment_amount_on_change)
   - Final validation before save (validate_payment_data)
   - Period validation ensures payments are in arrears

Important Notes:
--------------
- ALL payments are processed in arrears
- Period labels adapt to contract schedule (Month/Quarter)
- Expected fee calculation updates on total assets change
- Multi-period payments supported through custom range selection
- Contract start date validation included

Dependencies:
------------
- utils.ui_state_manager: For dialog state management
- utils.utils: For database operations and validation
- client_payment_utils: For period/quarter calculations
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.utils import (
    get_active_contract,
    format_currency_ui,
    format_currency_db,
    validate_payment_data,
    add_payment
)
from .client_payment_utils import (
    get_current_period,
    get_period_options,
    validate_period_range,
    format_period_display,
    calculate_expected_fee,
    parse_period_option,
    get_current_quarter,
    get_previous_quarter,
    get_quarter_month_range
)
from utils.utils import get_database_connection
from utils.ui_state_manager import UIStateManager

# Add caching for contract data
@st.cache_data(ttl=300)
def get_cached_contract(client_id: int) -> Optional[Tuple]:
    """Get contract data with caching for better performance."""
    return get_active_contract(client_id)

# Payment method options
METHOD_OPTIONS = [
    "Auto - ACH",
    "Auto - Check",
    "Invoice - Check",
    "None Specified",
    "Other"
]


def init_payment_dialog(ui_manager: UIStateManager, client_id: Optional[int] = None) -> None:
    """Initialize payment dialog state using UIStateManager.
    
    This function sets up the initial state for a new payment entry. It automatically
    determines the previous period (month/quarter) based on current date for arrears
    payment processing.
    
    Args:
        ui_manager: The UI state manager instance
        client_id: Optional client ID for the payment
        
    Note:
        - Uses generic period fields in form_data that will be converted to quarters
          during save operation
        - Initializes with previous period for arrears payments
    """
    current_quarter = get_current_quarter()
    current_year = datetime.now().year
    prev_quarter, prev_year = get_previous_quarter(current_quarter, current_year)
    
    initial_data = {
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
        'notes': '',
        'active_contract': None
    }
    
    ui_manager.open_payment_dialog(
        client_id=client_id,
        mode='add',
        initial_data=initial_data
    )


def clear_payment_dialog(ui_manager: UIStateManager) -> None:
    """Reset the payment dialog state using UIStateManager.
    
    Args:
        ui_manager: The UI state manager instance
    """
    # Close dialog and clear all associated data
    ui_manager.close_payment_dialog(clear_data=True)



def populate_payment_dialog_for_edit(payment_data: Tuple, ui_manager: UIStateManager) -> None:
    """Populate the payment dialog with existing payment data for editing using UIStateManager.
    
    Args:
        payment_data: Tuple containing payment data from database
        ui_manager: The UI state manager instance
    """
    if payment_data:
        form_data = {
            'received_date': payment_data[0],
            'applied_start_quarter': payment_data[1],
            'applied_start_year': payment_data[2], 
            'applied_end_quarter': payment_data[3],
            'applied_end_year': payment_data[4],
            'total_assets': format_currency_ui(payment_data[5]) if payment_data[5] else '',
            'actual_fee': format_currency_ui(payment_data[6]) if payment_data[6] else '',
            'method': payment_data[7] or 'None Specified',
            'notes': payment_data[8] or ''
        }
        
        # Open dialog in edit mode with the existing data
        ui_manager.open_payment_dialog(
            mode='edit',
            initial_data=form_data
        )


def has_payment_dialog_changes(ui_manager: UIStateManager) -> bool:
    """Check if the payment dialog has unsaved changes using UIStateManager.
    
    Args:
        ui_manager: The UI state manager instance
    
    Returns:
        bool: True if there are unsaved changes, False otherwise
    """
    current_quarter = get_current_quarter()
    current_year = datetime.now().year
    prev_quarter, prev_year = get_previous_quarter(current_quarter, current_year)
    
    initial_data = {
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
    
    current_data = ui_manager.payment_form_data
    return any(
        str(current_data.get(key, '')) != str(initial_data.get(key, ''))
        for key in initial_data
    )


def format_payment_amount_on_change(ui_manager: UIStateManager, field_key: str) -> None:
    """Format currency amount on input change using UIStateManager.
    
    This function handles real-time formatting of currency inputs and updates
    expected fee calculations when total assets change.
    
    Args:
        ui_manager: The UI state manager instance
        field_key: The field being updated ('total_assets' or 'actual_fee')
        
    Note:
        - Clears validation errors on each change
        - Updates expected fee when total_assets changes
        - Auto-populates actual_fee with expected_fee when empty
    """
    ui_manager.clear_payment_validation_errors()
    
    if field_key in st.session_state:
        value = st.session_state[field_key]
        if value:
            # More forgiving input
            cleaned = ''.join(c for c in str(value) if c.isdigit() or c in '.,')
            # Handle common input patterns
            if '.' not in cleaned:
                if len(cleaned) <= 2:  # Under $1
                    cleaned = '0.' + cleaned.zfill(2)
                else:  # Over $1
                    cleaned = cleaned[:-2] + '.' + cleaned[-2:]
            try:
                amount = float(cleaned)
                # Format with thousands separator as they type
                formatted = f"${amount:,.2f}"
                st.session_state[field_key] = formatted
                
                # Get current form data and update the changed field
                form_data = ui_manager.payment_form_data.copy()
                form_data[field_key] = formatted
                
                # Update expected fee when total assets changes
                if field_key == 'total_assets' and form_data.get('active_contract'):
                    expected_fee = calculate_expected_fee(
                        form_data['active_contract'],
                        formatted
                    )
                    if expected_fee is not None:
                        formatted_fee = f"${expected_fee:,.2f}"
                        form_data['expected_fee'] = formatted_fee
                        # Update the actual fee to match expected if it's empty
                        if not form_data.get('actual_fee'):
                            form_data['actual_fee'] = formatted_fee
                            st.session_state.actual_fee = formatted_fee
                
                # Update the form data in the manager
                ui_manager.update_payment_form_data(form_data)
            except ValueError:
                pass

def get_period_from_date(date_str: str, schedule: str, ui_manager: UIStateManager) -> Tuple[int, int]:
    """Get period from date string (for arrears payments)
    
    Args:
        date_str: The date string in format '%Y-%m-%d'
        schedule: The payment schedule ('monthly' or 'quarterly')
        ui_manager: The UI state manager instance
    
    Returns:
        Tuple[int, int]: (period, year) where period is month or quarter number
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        current_month = date.month
        current_year = date.year
        
        # Handle monthly schedule
        if schedule and schedule.lower() == 'monthly':
            if current_month == 1:
                return 12, current_year - 1
            return current_month - 1, current_year
            
        # Handle quarterly schedule
        current_quarter = (current_month - 1) // 3 + 1
        if current_quarter == 1:
            return 4, current_year - 1
        return current_quarter - 1, current_year
    except ValueError:
        # Default to previous period of current date
        current_period = get_current_period(schedule)
        current_year = datetime.now().year
        if (schedule and schedule.lower() == 'monthly' and current_period == 1) or \
           (schedule and schedule.lower() == 'quarterly' and current_period == 1):
            return 12 if schedule.lower() == 'monthly' else 4, current_year - 1
        return current_period - 1, current_year


def on_payment_date_change(ui_manager: UIStateManager) -> None:
    """Handle payment date change events using UIStateManager.
    
    Args:
        ui_manager: The UI state manager instance
    """
    if 'received_date' in st.session_state:
        form_data = ui_manager.payment_form_data.copy()
        contract = form_data.get('active_contract')
        
        if contract:
            date_str = st.session_state.received_date.strftime('%Y-%m-%d')
            period, year = get_period_from_date(date_str, contract[3])  # contract[3] is payment_schedule
            
            # Update the period and year in form data
            form_data.update({
                'applied_start_period': period,
                'applied_start_year': year
            })
            
            # Update form data and clear any validation errors
            ui_manager.update_payment_form_data(form_data)
            ui_manager.clear_payment_validation_errors()

def get_previous_quarter(quarter: int, year: int) -> Tuple[int, int]:
    """Get the previous quarter and year"""
    if quarter == 1:
        return 4, year - 1
    return quarter - 1, year

def get_quarter_options() -> list[str]:
    """Generate quarter options for past 5 years, excluding current quarter"""
    options = []
    current_quarter = get_current_quarter()
    current_year = datetime.now().year
    
    # Start with previous quarter
    if current_quarter == 1:
        start_year = current_year - 1
        start_quarter = 4
    else:
        start_year = current_year
        start_quarter = current_quarter - 1
    
    # Generate options starting from previous quarter
    for year in range(start_year, start_year - 5, -1):
        for quarter in range(4, 0, -1):
            # Skip quarters after the previous quarter
            if year == start_year and quarter > start_quarter:
                continue
            options.append(f"Q{quarter} {year}")
    return options

def validate_quarter_range(start_quarter: int, start_year: int, end_quarter: Optional[int] = None, end_year: Optional[int] = None) -> bool:
    """Validate that the quarter range is valid and chronological"""
    if end_quarter is None or end_year is None:
        return True
    
    # Convert to comparable values (e.g., 2023Q4 -> 20234)
    start_val = start_year * 10 + start_quarter
    end_val = end_year * 10 + end_quarter
    
    # End must be chronologically after start
    return end_val >= start_val

def get_previous_payment_defaults(client_id: int) -> Optional[Tuple[str, str]]:
    """Get default values from client's most recent payment
    
    Args:
        client_id: The ID of the client to get defaults for
        
    Returns:
        Optional[Tuple[str, str]]: Tuple of (method, total_assets) or None if no previous payment
    """
    if not client_id:
        return None
        
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT method, total_assets
            FROM payments
            WHERE client_id = ?
            ORDER BY received_date DESC
            LIMIT 1
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()


# New dialog display using UIStateManager
@st.dialog('Add Payment')
def show_payment_dialog(client_id: int) -> None:
    """Display the payment dialog using UIStateManager.
    
    This function manages the complete payment form UI, handling both monthly
    and quarterly payment schedules dynamically.
    
    Key behaviors:
    - Adapts period labels based on contract schedule (Month/Quarter)
    - Handles single and multi-period payments
    - Validates against contract start date
    - Manages payment method selection and notes
    - Performs validation before save
    
    Args:
        client_id: The ID of the client for this payment
        
    Note:
        - Form uses 'period' terminology but data is stored as quarters
        - All payments are processed in arrears
        - Multi-period payments maintain chronological order
    """
    ui_manager = UIStateManager()
    
    if not ui_manager.is_payment_dialog_open:
        return
    
    # Get active contract
    contract = get_cached_contract(client_id)
    if not contract:
        st.error("No active contract found for this client. Please add a contract first.")
        if st.button("Close"):
            ui_manager.close_payment_dialog()
            st.rerun()
        return
    
    st.subheader("Add Payment")
    
    # Update form data with active contract
    form_data = ui_manager.payment_form_data.copy()
    form_data['active_contract'] = contract
    ui_manager.update_payment_form_data(form_data)
    
    # Show contract details
    fee_type = contract[4].title() if contract[4] else "N/A"
    rate = (
        f"{contract[5]*100:.3f}%" if contract[4] == 'percentage' and contract[5]
        else f"${contract[6]:,.2f}" if contract[4] == 'flat' and contract[6]
        else "N/A"
    )
    schedule = contract[3].title() if contract[3] else "N/A"
    provider = contract[1] or "N/A"
    
    st.info(f"Provider: {provider} | Fee Type: {fee_type} | Rate: {rate} | Schedule: {schedule}")
    st.caption("All payments are processed in arrears")
    
    # Required field labels with asterisk
    st.markdown("Payment Date<span style='color: red'>*</span>", unsafe_allow_html=True)
    
    # Add an invisible element to prevent autofocus
    st.markdown("""
        <div style="width: 0; height: 0; overflow: hidden; position: absolute;">
            <input type="text" tabindex="-1" aria-hidden="true">
        </div>
    """, unsafe_allow_html=True)
    
    # Payment Date Input
    received_date = st.date_input(
        label="Payment Date",
        value=datetime.strptime(form_data['received_date'], '%Y-%m-%d'),
        key="received_date",
        label_visibility="collapsed",
        on_change=lambda: on_payment_date_change(ui_manager)
    )
    
    # Period selection - schedule aware
    period_label = "Month" if contract[3] and contract[3].lower() == 'monthly' else "Quarter"
    st.markdown(f"Payment {period_label}<span style='color: red'>*</span>", unsafe_allow_html=True)
    
    if not contract[3]:
        st.warning("Please set the payment schedule in the contract before adding payments.")
        return
    
    period_options = get_period_options(contract[3])
    if not period_options:
        st.error(f"No valid {period_label.lower()}s available for payment")
        return
    
    selected_period = st.selectbox(
        label=f"Payment {period_label}",
        options=period_options,
        index=0,  # First option is always previous period
        key="applied_period",
        label_visibility="collapsed"
    )
    
    # Parse selected period
    start_period, start_year = parse_period_option(selected_period, contract[3])
    
    # Custom range selection
    is_custom_range = st.checkbox(
        f"Payment covers multiple {period_label.lower()}s",
        value=False,
        key="is_custom_range"
    )
    
    # Show custom range fields if enabled
    end_period = start_period
    end_year = start_year
    
    if is_custom_range:
        st.markdown(f"##### Select {period_label} Range")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("From")
            start_period_option = st.selectbox(
                label=f"Start {period_label}",
                options=period_options,
                index=period_options.index(selected_period),
                key="custom_start_period",
                label_visibility="collapsed"
            )
            start_period, start_year = parse_period_option(start_period_option, contract[3])
        
        with col2:
            st.markdown("To")
            valid_end_options = [
                opt for opt in period_options
                if validate_period_range(
                    start_period, start_year,
                    *parse_period_option(opt, contract[3]),
                    contract[3]
                )
            ]
            
            if not valid_end_options:
                st.error(f"No valid end {period_label.lower()}s available")
                return
            
            end_period_option = st.selectbox(
                label=f"End {period_label}",
                options=valid_end_options,
                index=0,
                key="custom_end_period",
                label_visibility="collapsed"
            )
            end_period, end_year = parse_period_option(end_period_option, contract[3])
    
    # Update form data with period selection
    form_data.update({
        'received_date': received_date.strftime('%Y-%m-%d') if received_date else None,
        'applied_start_period': start_period,
        'applied_start_year': start_year,
        'applied_end_period': end_period if is_custom_range else start_period,
        'applied_end_year': end_year if is_custom_range else start_year,
    })
    ui_manager.update_payment_form_data(form_data)
    
    # Get defaults from previous payment
    previous_defaults = get_previous_payment_defaults(client_id)
    default_method = previous_defaults[0] if previous_defaults else 'None Specified'
    default_assets = previous_defaults[1] if previous_defaults else ''
    
    # Amount fields
    col1, col2 = st.columns(2)
    with col1:
        total_assets_input = st.text_input(
            "Assets Under Management",
            value=form_data.get('total_assets') or default_assets,
            key="total_assets",
            on_change=lambda: format_payment_amount_on_change(ui_manager, "total_assets"),
            placeholder="Enter amount (e.g. 1234.56)"
        )
    
    with col2:
        st.markdown("Payment Amount<span style='color: red'>*</span>", unsafe_allow_html=True)
        actual_fee_input = st.text_input(
            label="Payment Amount",
            value=form_data.get('actual_fee', ''),
            key="actual_fee",
            on_change=lambda: format_payment_amount_on_change(ui_manager, "actual_fee"),
            placeholder="Enter amount (e.g. 1234.56)",
            label_visibility="collapsed"
        )
    
    # Show expected fee if calculated
    if form_data.get('expected_fee'):
        st.info(f"Expected Fee: {form_data['expected_fee']}")
        
        # Check if payment quarter matches contract dates
        if contract[2]:  # contract_start_date exists
            contract_start = datetime.strptime(contract[2], '%Y-%m-%d')
            payment_start = datetime(start_year, ((start_period - 1) * 3) + 1, 1)
            if payment_start < contract_start:
                st.warning("⚠️ Payment quarter is before contract start date")
    
    # Payment method selection
    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox(
            "Payment Method",
            options=METHOD_OPTIONS,
            index=METHOD_OPTIONS.index(form_data.get('method', default_method)),
            key="method"
        )
    
    # Other method input if needed
    other_method = None
    if method == "Other":
        with col2:
            other_method = st.text_input(
                "Specify Method",
                value=form_data.get('other_method', ''),
                key="other_method"
            )
    
    # Notes field with multi-quarter hint
    notes_placeholder = (
        "Add any additional notes here (e.g., reason for multi-quarter payment)..."
        if is_custom_range else
        "Add any additional notes here..."
    )
    
    notes = st.text_area(
        "Notes",
        value=form_data.get('notes', ''),
        key="notes",
        height=100,
        placeholder=notes_placeholder
    )
    
    # Update form data with payment details
    form_data.update({
        'total_assets': total_assets_input,
        'actual_fee': actual_fee_input,
        'method': other_method if method == "Other" else (None if method == "None Specified" else method),
        'notes': notes,
        'payment_schedule': contract[3]  # Add schedule to form data for validation
    })
    ui_manager.update_payment_form_data(form_data)
    
    # Show validation errors if present
    if ui_manager.payment_dialog_has_errors:
        for error in ui_manager.payment_validation_errors:
            st.error(error)
    
    # Handle cancel confirmation
    if form_data.get('show_cancel_confirm'):
        st.warning("You have unsaved changes. Are you sure you want to cancel?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Discard Changes", type="primary", use_container_width=True):
                ui_manager.close_payment_dialog()
                st.rerun()
        with col2:
            if st.button("No, Keep Editing", use_container_width=True):
                form_data['show_cancel_confirm'] = False
                ui_manager.update_payment_form_data(form_data)
                st.rerun()
    else:
        # Save/Cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary", use_container_width=True):
                validation_errors = validate_payment_data(form_data)
                if not validation_errors:
                    payment_id = add_payment(client_id, form_data)
                    if payment_id:
                        st.success("Payment added successfully!")
                        ui_manager.close_payment_dialog()
                        st.rerun()
                    else:
                        st.error("Failed to add payment. Please try again.")
                else:
                    ui_manager.set_payment_validation_errors(validation_errors)
                    st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                if has_payment_dialog_changes(ui_manager):
                    form_data['show_cancel_confirm'] = True
                    ui_manager.update_payment_form_data(form_data)
                    st.rerun()
                else:
                    ui_manager.close_payment_dialog()
                    st.rerun() 