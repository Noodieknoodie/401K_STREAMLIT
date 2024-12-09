import streamlit as st
from datetime import datetime
from utils.utils import (
    get_active_contract,
    format_currency_ui,
    format_currency_db,
    validate_payment_data,
    add_payment
)
from .payment_utils import (
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

# Add caching for contract data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_contract(client_id):
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

def init_payment_form_state():
    """Initialize the payment form state"""
    if 'payment_form' not in st.session_state:
        st.session_state.payment_form = {
            'is_open': False,
            'mode': 'add',  # 'add' or 'edit'
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'form_data': {
                'received_date': datetime.now().strftime('%Y-%m-%d'),
                'applied_start_period': None,  # Will be set based on schedule
                'applied_start_year': None,
                'applied_end_period': None,
                'applied_end_year': None,
                'total_assets': '',
                'actual_fee': '',
                'expected_fee': None,
                'method': 'None Specified',
                'other_method': '',
                'notes': ''
            }
        }

def clear_form():
    """Reset the payment form state"""
    if 'payment_form' in st.session_state:
        # Get previous quarter for arrears payment
        current_quarter = get_current_quarter()
        current_year = datetime.now().year
        prev_quarter, prev_year = get_previous_quarter(current_quarter, current_year)
        
        # Clear form data
        st.session_state.payment_form['form_data'] = {
            'received_date': datetime.now().strftime('%Y-%m-%d'),
            'applied_start_quarter': prev_quarter,  # Now using previous quarter consistently
            'applied_start_year': prev_year,       # And its corresponding year
            'applied_end_quarter': None,
            'applied_end_year': None,
            'total_assets': '',
            'actual_fee': '',
            'expected_fee': None,
            'method': 'None Specified',
            'other_method': '',
            'notes': ''
        }
        # Reset form state
        st.session_state.payment_form['is_open'] = False
        st.session_state.payment_form['has_validation_error'] = False
        st.session_state.payment_form['show_cancel_confirm'] = False
        
        # Clear payment data to force refresh
        if 'payment_data' in st.session_state:
            st.session_state.payment_data = []
        if 'payment_offset' in st.session_state:
            st.session_state.payment_offset = 0
        if 'current_filters' in st.session_state:
            del st.session_state.current_filters

def has_unsaved_changes(form_data):
    """Check if the form has unsaved changes"""
    current_quarter = get_current_quarter()
    current_year = datetime.now().year
    prev_quarter, prev_year = get_previous_quarter(current_quarter, current_year)
    
    initial_data = {
        'received_date': datetime.now().strftime('%Y-%m-%d'),
        'applied_start_quarter': prev_quarter,  # Compare with previous quarter
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
    
    return any(
        str(form_data.get(key, '')) != str(initial_data.get(key, ''))
        for key in initial_data
    )

def clear_validation_error():
    """Clear the validation error state"""
    if 'payment_form' in st.session_state:
        st.session_state.payment_form['has_validation_error'] = False

def format_amount_on_change(field_key):
    """Format currency amount on input change"""
    clear_validation_error()
    
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
                
                # Update expected fee when total assets changes
                if field_key == 'total_assets' and st.session_state.payment_form.get('active_contract'):
                    expected_fee = calculate_expected_fee(
                        st.session_state.payment_form['active_contract'],
                        formatted
                    )
                    if expected_fee is not None:
                        formatted_fee = f"${expected_fee:,.2f}"
                        st.session_state.payment_form['form_data']['expected_fee'] = formatted_fee
                        # Update the actual fee to match expected if it's empty
                        if not st.session_state.payment_form['form_data'].get('actual_fee'):
                            st.session_state.payment_form['form_data']['actual_fee'] = formatted_fee
            except ValueError:
                # If conversion fails, keep original value
                pass

def get_period_from_date(date_str, schedule):
    """Get period from date string (for arrears payments)"""
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

def on_date_change():
    """Handle date change events"""
    if 'received_date' in st.session_state and 'payment_form' in st.session_state:
        contract = st.session_state.payment_form.get('active_contract')
        if contract:
            date_str = st.session_state.received_date.strftime('%Y-%m-%d')
            period, year = get_period_from_date(date_str, contract[3])  # contract[3] is payment_schedule
            st.session_state.payment_form['form_data']['applied_start_period'] = period
            st.session_state.payment_form['form_data']['applied_start_year'] = year
            clear_validation_error()

def get_previous_quarter(quarter, year):
    """Get the previous quarter and year"""
    if quarter == 1:
        return 4, year - 1
    return quarter - 1, year

def get_quarter_options():
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

def validate_quarter_range(start_quarter, start_year, end_quarter=None, end_year=None):
    """Validate that the quarter range is valid and chronological"""
    if end_quarter is None or end_year is None:
        return True
    
    # Convert to comparable values (e.g., 2023Q4 -> 20234)
    start_val = start_year * 10 + start_quarter
    end_val = end_year * 10 + end_quarter
    
    # End must be chronologically after start
    return end_val >= start_val

def get_previous_payment_defaults(client_id):
    """Get default values from client's most recent payment"""
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

@st.dialog('Add Payment')
def show_payment_form(client_id):
    """Display the payment form dialog"""
    if not st.session_state.payment_form['is_open']:
        return
    
    st.session_state.client_id = client_id
    st.subheader("Add Payment")
    
    # Get active contract
    contract = get_cached_contract(client_id)
    if not contract:
        st.error("No active contract found for this client. Please add a contract first.")
        if st.button("Close"):
            clear_form()
            st.rerun()
        return
    
    # Store active contract in session state
    st.session_state.payment_form['active_contract'] = contract
    
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
    
    # Add subtle arrears note once
    st.caption("All payments are processed in arrears")
    
    # Required field labels with asterisk
    st.markdown("Payment Date<span style='color: red'>*</span>", unsafe_allow_html=True)
    received_date = st.date_input(
        label="Payment Date",
        value=datetime.strptime(st.session_state.payment_form['form_data']['received_date'], '%Y-%m-%d'),
        key="received_date",
        label_visibility="collapsed",
        on_change=on_date_change
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
            # Filter end period options to only show periods after start
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
    
    # Get defaults from previous payment
    previous_defaults = get_previous_payment_defaults(client_id)
    default_method = previous_defaults[0] if previous_defaults else 'None Specified'
    default_assets = previous_defaults[1] if previous_defaults else ''
    
    # Amount fields
    col1, col2 = st.columns(2)
    with col1:
        total_assets_input = st.text_input(
            "Assets Under Management",
            value=st.session_state.payment_form['form_data'].get('total_assets') or default_assets,
            key="total_assets",
            on_change=lambda: format_amount_on_change("total_assets"),
            placeholder="Enter amount (e.g. 1234.56)"
        )
    with col2:
        st.markdown("Payment Amount<span style='color: red'>*</span>", unsafe_allow_html=True)
        actual_fee_input = st.text_input(
            label="Payment Amount",
            value=st.session_state.payment_form['form_data'].get('actual_fee', ''),
            key="actual_fee",
            on_change=lambda: format_amount_on_change("actual_fee"),
            placeholder="Enter amount (e.g. 1234.56)",
            label_visibility="collapsed"
        )
    
    # Show expected fee if calculated
    if st.session_state.payment_form['form_data'].get('expected_fee'):
        st.info(f"Expected Fee: {st.session_state.payment_form['form_data']['expected_fee']}")
        
        # Check if payment quarter matches contract dates
        contract = st.session_state.payment_form.get('active_contract')
        if contract and contract[2]:  # contract_start_date exists
            contract_start = datetime.strptime(contract[2], '%Y-%m-%d')
            contract_quarter = (contract_start.month - 1) // 3 + 1
            contract_year = contract_start.year
            
            # Get start quarter and year from form state
            start_quarter = st.session_state.payment_form['form_data']['applied_start_quarter']
            start_year = st.session_state.payment_form['form_data']['applied_start_year']
            
            payment_start = datetime(start_year, ((start_quarter - 1) * 3) + 1, 1)
            if payment_start < contract_start:
                st.warning("⚠️ Payment quarter is before contract start date")
    
    # Payment method (with default from previous payment)
    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox(
            "Payment Method",
            options=METHOD_OPTIONS,
            index=METHOD_OPTIONS.index(
                st.session_state.payment_form['form_data'].get('method', default_method)
            ),
            key="method"
        )
    
    # Show text input for "Other" method
    other_method = None
    if method == "Other":
        with col2:
            other_method = st.text_input(
                "Specify Method",
                value=st.session_state.payment_form['form_data'].get('other_method', ''),
                key="other_method"
            )
    
    # Notes field with multi-quarter hint
    notes_placeholder = (
        "Add any additional notes here..."
        if not is_custom_range else
        "Add any additional notes here (e.g., reason for multi-quarter payment)..."
    )
    
    notes = st.text_area(
        "Notes",
        value=st.session_state.payment_form['form_data']['notes'],
        key="notes",
        height=100,
        placeholder=notes_placeholder
    )
    
    # Capture form data
    form_data = {
        'received_date': received_date.strftime('%Y-%m-%d') if received_date else None,
        'applied_start_period': start_period,
        'applied_start_year': start_year,
        'applied_end_period': end_period if is_custom_range else start_period,
        'applied_end_year': end_year if is_custom_range else start_year,
        'total_assets': total_assets_input,
        'actual_fee': actual_fee_input,
        'expected_fee': st.session_state.payment_form['form_data'].get('expected_fee'),
        'method': other_method if method == "Other" else (None if method == "None Specified" else method),
        'notes': notes,
        'payment_schedule': contract[3]  # Add schedule to form data for validation
    }
    
    # Show validation error if present
    if st.session_state.payment_form['has_validation_error']:
        validation_errors = validate_payment_data(form_data)
        for error in validation_errors:
            st.error(error)
    
    # Show cancel confirmation if needed
    if st.session_state.payment_form['show_cancel_confirm']:
        st.warning("You have unsaved changes. Are you sure you want to cancel?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Discard Changes", type="primary", use_container_width=True):
                clear_form()
                st.rerun()
        with col2:
            if st.button("No, Keep Editing", use_container_width=True):
                st.session_state.payment_form['show_cancel_confirm'] = False
                st.rerun()
    else:
        # Normal save/cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary", use_container_width=True):
                validation_errors = validate_payment_data(form_data)
                if not validation_errors:
                    # Add period type info to form data
                    payment_id = add_payment(client_id, form_data)
                    if payment_id:
                        st.success("Payment added successfully!")
                        clear_form()
                        st.rerun()
                    else:
                        st.error("Failed to add payment. Please try again.")
                else:
                    st.session_state.payment_form['has_validation_error'] = True
                    st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                if has_unsaved_changes(form_data):
                    st.session_state.payment_form['show_cancel_confirm'] = True
                    st.rerun()
                else:
                    clear_form()
                    st.rerun() 