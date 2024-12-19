"""
Client Payments Module Documentation
==================================

This module handles the payment management interface for the 401K Payment Tracker application.
It provides functionality for adding, editing, and viewing payment history with specific validation
and display requirements.

Key Components & Behaviors to Verify:
-----------------------------------

Contract Table Structure:
CREATE TABLE "contracts" (
    "contract_id" INTEGER NOT NULL,
    "client_id" INTEGER NOT NULL,
    "active" TEXT,
    "contract_number" TEXT,
    "provider_name" TEXT,
    "contract_start_date" TEXT,
    "fee_type" TEXT,
    "percent_rate" REAL,
    "flat_rate" REAL,
    "payment_schedule" TEXT,
    "num_people" INTEGER,
    "notes" TEXT
)

Payment Table Structure:
CREATE TABLE "payments" (
    "payment_id" INTEGER NOT NULL,
    "contract_id" INTEGER NOT NULL,
    "client_id" INTEGER NOT NULL,
    "received_date" TEXT,
    "applied_start_quarter" INTEGER,
    "applied_start_year" INTEGER,
    "applied_end_quarter" INTEGER,
    "applied_end_year" INTEGER,
    "total_assets" INTEGER,
    "expected_fee" REAL,
    "actual_fee" REAL,
    "method" TEXT,
    "notes" TEXT
)


1. Payment Form Requirements:
   - Contract info must be displayed above form
   - Date picker must use MM/DD/YYYY format
   - Payments must be in arrears (can't be for current/future periods)
   - Multi-period payments must have valid period ranges
   - Currency fields must format in real-time with "$" and commas
   - Expected fee should auto-calculate based on contract terms
   - All required fields must be validated before submission

2. Payment History Display:
   - Table columns must maintain specific proportions [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1]
   - Notes show as: 🟢 (with note) or ◯ (without note), when clicked, the note expands to show the full note under the payment spanning half of the row or so
   - Actions show as: ✏️ (edit) and 🗑️ (delete)
   - Period display format:
     * Monthly: "MMM YYYY" or "MMM - MMM YYYY" for ranges
     * Quarterly: "QN YYYY" or "QN YYYY - QN YYYY" for ranges
   - Currency values must show with "$" and commas
   - Discrepancy shows as positive or negative with "-$" prefix for negative values

3. State Management:
   - Form state must reset after submission/cancellation
   - Note editing state must be exclusive (only one note editable at a time)
   - Delete confirmation must be exclusive
   - Filter state must persist during the session

4. Data Validation Rules:
   - Payment periods must be in arrears
   - Multi-period payments must have valid date ranges
   - Currency values must be valid numbers
   - Required fields: date, period, payment amount
   - Contract must exist before allowing payments

5. Period Handling:
   - Monthly payments map to quarters (e.g., Q1 = Jan, Feb, Mar)
   - Period ranges must be continuous and valid
   - Custom filters must respect period boundaries

6. Common Issues to Check:
   - Form should never submit with invalid data
   - Currency formatting should handle edge cases (empty, invalid input)
   - Period validation should prevent future payments
   - Note expansion should maintain table layout
   - Delete confirmation should be clear and reversible

Database Schema Dependencies:
---------------------------
- clients: client_id (primary key)
- contracts: contract_id, client_id (foreign key), fee_type, rate, schedule
- payments: payment_id, client_id, period_start, period_end, amount, notes

Required Utility Functions:
-------------------------
From utils.py:
- format_currency_ui: Formats currency for display
- format_currency_db: Formats currency for database storage
- validate_payment_data: Validates payment form data
- get_payment_history: Retrieves filtered payment history
- update_payment_note: Updates payment notes

From client_payment_utils.py:
- get_current_period: Gets current period based on schedule
- validate_period_range: Validates period selections
- parse_period_option: Parses period string into components
- calculate_expected_fee: Calculates expected fee based on contract
- get_period_options: Gets period options based on schedule

Testing Checklist:
----------------
1. Form Validation:
   - Try submitting without required fields
   - Try future dates/periods
   - Try invalid currency values
   - Try invalid period ranges

2. Display Formatting:
   - Verify currency formatting
   - Verify period display format
   - Verify table column alignment
   - Verify note/action button layout

3. State Management:
   - Verify form reset after actions
   - Verify filter state persistence
   - Verify note editing exclusivity
   - Verify delete confirmation flow

4. Data Integrity:
   - Verify payment updates in database
   - Verify note updates in database
   - Verify payment deletion
   - Verify period validation
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.utils import (
    get_payment_history,
    get_active_contract,
    format_currency_ui,
    format_currency_db,
    validate_payment_data,
    add_payment,
    update_payment,
    delete_payment,
    get_payment_by_id,
    get_unique_payment_methods,
    update_payment_note,
    get_payment_year_quarters
)
from .client_payment_utils import (
    get_period_options,
    parse_period_option,
    validate_period_range,
    calculate_expected_fee,
    get_current_period,
    get_previous_quarter,
    get_current_quarter
)

# ============================================================================
# DOCS: Table Structures
# ============================================================================

# Client Table Structure:
# CREATE TABLE "clients" (
#     "client_id" INTEGER NOT NULL,
#     "display_name" TEXT NOT NULL,
#     "full_name" TEXT,
#     "ima_signed_date" TEXT,
#     "file_path_account_documentation" TEXT,
#     "file_path_consulting_fees" TEXT,
#     "file_path_meetings" INTEGER,
#     PRIMARY KEY("client_id" AUTOINCREMENT)
# )

# Contact Table Structure:
# CREATE TABLE "contacts" (
#     "contact_id" INTEGER NOT NULL,
#     "client_id" INTEGER NOT NULL,
#     "contact_type" TEXT NOT NULL,
#     "contact_name" TEXT,
#     "phone" TEXT,
#     "email" TEXT,
#     "fax" TEXT,
#     "physical_address" TEXT,
#     "mailing_address" TEXT,
#     PRIMARY KEY("contact_id" AUTOINCREMENT),
#     FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
# )

# Contract Table Structure:
# CREATE TABLE "contracts" (
#     "contract_id" INTEGER NOT NULL,
#     "client_id" INTEGER NOT NULL,
#     "active" TEXT,
#     "contract_number" TEXT,
#     "provider_name" TEXT,
#     "contract_start_date" TEXT,
#     "fee_type" TEXT,
#     "percent_rate" REAL,
#     "flat_rate" REAL,
#     "payment_schedule" TEXT,
#     "num_people" INTEGER,
#     "notes" TEXT
# )

# Payment Table Structure:
# CREATE TABLE "payments" (
#     "payment_id" INTEGER NOT NULL,
#     "contract_id" INTEGER NOT NULL,
#     "client_id" INTEGER NOT NULL,
#     "received_date" TEXT,
#     "applied_start_quarter" INTEGER,
#     "applied_start_year" INTEGER,
#     "applied_end_quarter" INTEGER,
#     "applied_end_year" INTEGER,
#     "total_assets" INTEGER,
#     "expected_fee" REAL,
#     "actual_fee" REAL,
#     "method" TEXT,
#     "notes" TEXT
# )




# ============================================================================
# Payment Form State Management
# ============================================================================

def init_payment_state():
    """Initialize payment-related session state variables."""
    if 'show_payment_form' not in st.session_state:
        st.session_state.show_payment_form = False
    if 'payment_form_data' not in st.session_state:
        current_quarter = get_current_quarter()
        current_year = datetime.now().year
        prev_quarter, prev_year = get_previous_quarter(current_quarter, current_year)
        
        st.session_state.payment_form_data = {
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
    if 'payment_edit_id' not in st.session_state:
        st.session_state.payment_edit_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False

def reset_payment_form():
    """Reset payment form state."""
    st.session_state.show_payment_form = False
    st.session_state.payment_form_data = {}
    st.session_state.payment_edit_id = None

# ============================================================================
# Payment Form Display
# ============================================================================

def format_payment_amount_on_change(field_key: str) -> None:
    """Format currency amount on input change."""
    if field_key in st.session_state:
        value = st.session_state[field_key]
        if value:
            try:
                # Remove any existing formatting
                cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
                # Convert to float and format
                amount = float(cleaned)
                st.session_state[field_key] = f"${amount:,.2f}"
            except ValueError:
                pass

def show_payment_form(client_id: int, contract: Tuple):
    """Display the payment form for adding/editing payments."""
    # Load existing payment data if editing
    if st.session_state.payment_edit_id:
        payment_data = get_payment_by_id(st.session_state.payment_edit_id)
        if payment_data:
            st.session_state.payment_form_data = {
                'received_date': payment_data[0],
                'start_period': payment_data[1],
                'start_year': payment_data[2],
                'end_period': payment_data[3],
                'end_year': payment_data[4],
                'total_assets': format_currency_ui(payment_data[5]),
                'actual_fee': format_currency_ui(payment_data[6]),
                'method': payment_data[7],
                'notes': payment_data[8]
            }
    
    with st.form("payment_form", clear_on_submit=False):
        st.subheader("Add Payment" if not st.session_state.payment_edit_id else "Edit Payment")
        
        # Contract info display
        if not display_contract_info(contract):
            return
        
        # Payment Date
        st.markdown("Payment Date<span style='color: red'>*</span>", unsafe_allow_html=True)
        received_date = st.date_input(
            "Payment Date",
            value=datetime.strptime(st.session_state.payment_form_data.get('received_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
            format="MM/DD/YYYY",
            label_visibility="collapsed"
        )
        
        # Period selection based on contract schedule
        schedule = contract[3].lower() if contract[3] else ""
        period_label = "Month" if schedule == "monthly" else "Quarter"
        
        print(f"\n=== PERIOD SELECTION DIAGNOSTICS ===")
        print(f"Schedule: {schedule}")
        print(f"Period Label: {period_label}")
        print(f"Current Form Data: {st.session_state.payment_form_data}")
        
        st.markdown(f"Payment {period_label}<span style='color: red'>*</span>", unsafe_allow_html=True)
        period_options = get_period_options(schedule)
        print(f"Available Period Options: {period_options}")
        
        if not period_options:
            print("ERROR: No period options available!")
            st.error(f"No valid {period_label.lower()}s available for payment")
            
        # Get current period for validation
        current_period = get_current_period(schedule)
        print(f"Current Period: {current_period}")
        
        selected_period = st.selectbox(
            f"Payment {period_label}",
            options=period_options,
            label_visibility="collapsed"
        )
        print(f"Selected Period: {selected_period}")
        
        # Parse period but don't validate yet
        start_period, start_year = parse_period_option(selected_period, schedule)
        print(f"Parsed Start Period: {start_period}, Start Year: {start_year}")
        
        # Multi-period payment option
        has_end_period = st.session_state.payment_edit_id and st.session_state.payment_form_data.get('applied_end_quarter') is not None
        is_multi_period = st.checkbox(
            f"Payment covers multiple {period_label.lower()}s",
            value=has_end_period,
            key="is_custom_range"
        )
        
        if is_multi_period:
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
                
                end_period = st.selectbox(
                    "End Period",
                    options=valid_end_options,
                    key="end_period",
                    label_visibility="collapsed"
                )
        
        # Amount fields
        col1, col2 = st.columns(2)
        with col1:
            total_assets = st.text_input(
                "Assets Under Management",
                value=st.session_state.payment_form_data.get('total_assets', ''),
                key="total_assets",
                placeholder="Enter amount (e.g. 2000000)"
            )
            st.caption("Enter the total amount without commas or $ symbol")
        
        with col2:
            st.markdown("Payment Amount<span style='color: red'>*</span>", unsafe_allow_html=True)
            actual_fee = st.text_input(
                "Payment Amount",
                value=st.session_state.payment_form_data.get('actual_fee', ''),
                key="actual_fee",
                placeholder="Enter amount (e.g. 2000)",
                label_visibility="collapsed"
            )
            st.caption("Enter the payment amount without commas or $ symbol")
        
        # Show expected fee if we can calculate it
        if total_assets:
            try:
                assets = float(total_assets.replace('$', '').replace(',', ''))
                expected = calculate_expected_fee(contract, assets)
                if expected is not None:
                    formatted_fee = f"${expected:,.2f}"
                    st.session_state.payment_form_data['expected_fee'] = formatted_fee
                    st.info(f"Expected Fee: {formatted_fee}")
                    
                    # Auto-fill actual fee if empty
                    if not actual_fee:
                        st.session_state.actual_fee = formatted_fee
                        st.session_state.payment_form_data['actual_fee'] = formatted_fee
                        st.rerun()
            except ValueError:
                pass
        
        # Payment method
        col1, col2 = st.columns(2)
        with col1:
            method_options = get_unique_payment_methods()
            method = st.selectbox("Payment Method", options=method_options)
        
        if method == "Other":
            with col2:
                other_method = st.text_input("Specify Method")
        
        # Notes
        notes = st.text_area(
            "Notes",
            placeholder="Add any additional notes here..." if not is_multi_period else
                       "Add any additional notes here (e.g., reason for multi-period payment)..."
        )
        
        # Submit/Cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            # Clean currency values for database storage
            db_total_assets = format_currency_db(total_assets) if total_assets else None
            db_actual_fee = format_currency_db(actual_fee) if actual_fee else None
            
            # Prepare form data
            form_data = {
                'received_date': received_date.strftime('%Y-%m-%d'),
                'total_assets': db_total_assets,
                'actual_fee': db_actual_fee,
                'method': other_method if method == "Other" else method,
                'notes': notes,
                'payment_schedule': schedule
            }
            
            # Add period data
            if is_multi_period:
                form_data.update({
                    'start_period': start_period,
                    'end_period': end_period
                })
            else:
                form_data.update({
                    'start_period': selected_period,
                    'end_period': selected_period
                })
            
            # Validate and save
            validation_errors = validate_payment_data(form_data)
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                if st.session_state.payment_edit_id:
                    success = update_payment(st.session_state.payment_edit_id, form_data)
                    if success:
                        st.success("Payment updated successfully!")
                        st.session_state.show_payment_form = False
                        st.rerun()
                else:
                    payment_id = add_payment(client_id, form_data)
                    if payment_id:
                        st.success("Payment added successfully!")
                        st.session_state.show_payment_form = False
                        st.rerun()
                    else:
                        st.error("Failed to add payment. Please try again.")
        
        elif cancelled:
            st.session_state.show_payment_form = False
            st.rerun()

def display_contract_info(contract: Tuple):
    """Display contract information above the payment form."""
    if not contract:
        st.error("No active contract found. Please set up a contract first.")
        return False
    
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
    return True

# ============================================================================
# Payment History Display
# ============================================================================

def show_payment_history(client_id: int):
    """Display the payment history table with filtering options."""
    # Initialize filter state if needed
    if 'payment_filter' not in st.session_state:
        st.session_state.payment_filter = {
            'time_filter': 'All Time',
            'year': datetime.now().year,
            'quarter': None
        }
    
    # Filter controls
    left_col, middle_col, right_col = st.columns([4, 2, 4])
    
    with left_col:
        selected_filter = st.radio(
            "Time Period Filter",
            options=["All Time", "This Year", "Custom"],
            key="time_filter",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if selected_filter == "Custom":
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                year = st.selectbox(
                    "Select Year",
                    options=range(datetime.now().year, datetime.now().year - 5, -1),
                    key="filter_year"
                )
            
            with col2:
                quarter = st.selectbox(
                    "Select Quarter",
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    key="filter_quarter"
                )
    
    with middle_col:
        if st.button("Add Payment", type="primary", use_container_width=True):
            st.session_state.show_payment_form = True
            st.rerun()
    
    with right_col:
        filter_text = (
            "Showing all payments" if selected_filter == "All Time"
            else f"Showing payments from {datetime.now().year}" if selected_filter == "This Year"
            else f"Showing payments from {year}" + (f" Q{quarter[1]}" if quarter != "All Quarters" else "")
        )
        st.markdown(f"<div style='text-align: right'>{filter_text}</div>", unsafe_allow_html=True)
    
    # Get filtered data
    years = None
    quarters = None
    
    if selected_filter == "This Year":
        years = [datetime.now().year]
    elif selected_filter == "Custom":
        years = [year]
        if quarter != "All Quarters":
            quarters = [int(quarter[1])]
    
    # Get and display payments
    raw_payments = get_payment_history(client_id, years=years, quarters=quarters)
    if not raw_payments:
        st.info("No payment history available for this client.")
        return
    
    # Format payments for display
    formatted_payments = format_payment_data(raw_payments)
    
    # Display payment table
    display_payment_table(formatted_payments)

def display_payment_table(payments: list):
    """Display the formatted payment history table."""
    # Add CSS for table styling
    st.markdown("""
        <style>
        div.payment-table div[data-testid="column"] > div > div > div > div {
            padding: 0;
            margin: 0;
            line-height: 0.8;
        }
        
        div.payment-table p {
            margin: 0;
            padding: 0;
            line-height: 1;
        }
        
        div.payment-table div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0.1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="payment-table">', unsafe_allow_html=True)
    
    # Table headers
    cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
    headers = [
        "Provider", "Period", "Frequency", "Method", "Received",
        "Total Assets", "Expected Fee", "Actual Fee", "Discrepancy",
        "Notes", "Actions"
    ]
    
    for col, header in zip(cols, headers):
        with col:
            st.markdown(f"<p style='font-weight: bold'>{header}</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 0.1rem 0; border-color: #eee;'>", unsafe_allow_html=True)
    
    # Display data rows
    for payment in payments:
        with st.container():
            cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
            
            # Display payment data
            for i, (col, key) in enumerate(zip(cols[:-2], [
                "Provider", "Period", "Frequency", "Method", "Received",
                "Total Assets", "Expected Fee", "Actual Fee", "Discrepancy"
            ])):
                with col:
                    st.markdown(f"<p>{payment[key]}</p>", unsafe_allow_html=True)
            
            # Notes column
            with cols[-2]:
                if payment['Notes']:
                    if st.button("🟢", key=f"note_{payment['payment_id']}", help=payment['Notes']):
                        st.session_state.editing_note_id = payment['payment_id']
                else:
                    if st.button("◯", key=f"note_{payment['payment_id']}", help="Add note"):
                        st.session_state.editing_note_id = payment['payment_id']
            
            # Actions column
            with cols[-1]:
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    if st.button("✏️", key=f"edit_{payment['payment_id']}", help="Edit payment"):
                        st.session_state.payment_edit_id = payment['payment_id']
                        st.session_state.show_payment_form = True
                        st.rerun()
                
                with action_cols[1]:
                    if st.button("🗑️", key=f"delete_{payment['payment_id']}", help="Delete payment"):
                        st.session_state.delete_confirm_id = payment['payment_id']
                        st.rerun()
            
            # Show note editor if active
            if getattr(st.session_state, 'editing_note_id', None) == payment['payment_id']:
                with st.container():
                    st.markdown("<div style='border-top: 1px solid #eee; padding-top: 0.5rem;'></div>", unsafe_allow_html=True)
                    note_cols = st.columns([4, 12, 1])
                    with note_cols[1]:
                        edited_note = st.text_area(
                            f"Note for {payment['Provider']} - {payment['Period']}",
                            value=payment['Notes'] or "",
                            key=f"note_text_{payment['payment_id']}",
                            height=100,
                            placeholder="Enter note here..."
                        )
                        
                        save_cols = st.columns([6, 2, 2])
                        with save_cols[1]:
                            if st.button("Save", key=f"save_note_{payment['payment_id']}", type="primary"):
                                update_payment_note(payment['payment_id'], edited_note)
                                st.session_state.editing_note_id = None
                                st.rerun()
                        with save_cols[2]:
                            if st.button("Cancel", key=f"cancel_note_{payment['payment_id']}"):
                                st.session_state.editing_note_id = None
                                st.rerun()
            
            # Show delete confirmation if active
            if getattr(st.session_state, 'delete_confirm_id', None) == payment['payment_id']:
                with st.container():
                    confirm_cols = st.columns([6, 2, 2])
                    with confirm_cols[0]:
                        st.warning(f"Delete this payment for {payment['Period']}?")
                    with confirm_cols[1]:
                        if st.button("Yes, Delete", key=f"confirm_delete_{payment['payment_id']}", type="primary"):
                            if delete_payment(payment['payment_id']):
                                st.success("Payment deleted successfully!")
                                st.session_state.delete_confirm_id = None
                                st.rerun()
                            else:
                                st.error("Failed to delete payment")
                    with confirm_cols[2]:
                        if st.button("Cancel", key=f"cancel_delete_{payment['payment_id']}"):
                            st.session_state.delete_confirm_id = None
                            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Main Display Function
# ============================================================================

def display_payments_section(client_id: int):
    """Main entry point for the payments section."""
    # Initialize state
    init_payment_state()
    
    # Get active contract
    contract = get_active_contract(client_id)
    
    # Show form or history
    if st.session_state.show_payment_form:
        show_payment_form(client_id, contract)
    else:
        show_payment_history(client_id)

def format_payment_data(payments: list) -> list:
    """Format payment data for display with consistent formatting."""
    table_data = []
    
    for payment in payments:
        provider_name = payment[0] or "N/A"
        
        def format_currency(value):
            try:
                if value is None or value == "":
                    return "N/A"
                return f"${float(value):,.2f}"
            except (ValueError, TypeError):
                return "N/A"
        
        # Format payment period based on frequency
        frequency = payment[5].title() if payment[5] else "N/A"
        
        if frequency.lower() == "monthly":
            # For monthly payments, convert quarter to month range
            start_month = ((payment[1] - 1) * 3) + 1
            end_month = ((payment[3] - 1) * 3) + 3
            
            if payment[2] == payment[4] and start_month == end_month:
                # Single month
                period = f"{datetime.strptime(f'2000-{start_month}-1', '%Y-%m-%d').strftime('%b')} {payment[2]}"
            else:
                # Month range
                start_date = datetime.strptime(f'2000-{start_month}-1', '%Y-%m-%d')
                end_date = datetime.strptime(f'2000-{end_month}-1', '%Y-%m-%d')
                if payment[2] == payment[4]:
                    period = f"{start_date.strftime('%b')} - {end_date.strftime('%b')} {payment[2]}"
                else:
                    period = f"{start_date.strftime('%b')} {payment[2]} - {end_date.strftime('%b')} {payment[4]}"
        else:
            # Quarterly payments
            if payment[1] == payment[3] and payment[2] == payment[4]:
                period = f"Q{payment[1]} {payment[2]}"
            else:
                period = f"Q{payment[1]} {payment[2]} - Q{payment[3]} {payment[4]}"
        
        # Format date
        received_date = "N/A"
        if payment[6]:
            try:
                date_obj = datetime.strptime(payment[6], '%Y-%m-%d')
                received_date = date_obj.strftime('%b %d, %Y')
            except:
                received_date = payment[6]
        
        # Format all currency values
        total_assets = format_currency(payment[7])
        expected_fee = format_currency(payment[8])
        actual_fee = format_currency(payment[9])
        
        # Calculate fee discrepancy
        try:
            if payment[8] is not None and payment[9] is not None and payment[8] != "" and payment[9] != "":
                discrepancy = float(payment[9]) - float(payment[8])
                discrepancy_str = f"${discrepancy:,.2f}" if discrepancy >= 0 else f"-${abs(discrepancy):,.2f}"
            else:
                discrepancy_str = "N/A"
        except (ValueError, TypeError):
            discrepancy_str = "N/A"
        
        notes = payment[10] or ""
        payment_id = payment[11]
        method = payment[12] or "N/A"
        
        formatted_payment = {
            "Provider": provider_name,
            "Period": period,
            "Frequency": frequency,
            "Method": method,
            "Received": received_date,
            "Total Assets": total_assets,
            "Expected Fee": expected_fee,
            "Actual Fee": actual_fee,
            "Discrepancy": discrepancy_str,
            "Notes": notes,
            "payment_id": payment_id
        }
        
        table_data.append(formatted_payment)
    
    return table_data

if __name__ == "__main__":
    st.set_page_config(page_title="Client Payments", layout="wide")
    # For testing
    display_payments_section(1)
