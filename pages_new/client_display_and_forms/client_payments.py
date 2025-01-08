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
- format_period_display: Formats period display consistently

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
    format_period_display
)

### THE ONLY REQUIRED FIELDS ARE: Payment Date, Payment Amount

def init_payment_state():
    """Initialize payment-related session state variables."""
    if 'show_payment_form' not in st.session_state:
        st.session_state.show_payment_form = False
    if 'editing_payment_id' not in st.session_state:
        st.session_state.editing_payment_id = None
    if 'payment_form_data' not in st.session_state:
        st.session_state.payment_form_data = {}
    if 'payment_validation_errors' not in st.session_state:
        st.session_state.payment_validation_errors = []
    if 'delete_payment_id' not in st.session_state:
        st.session_state.delete_payment_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
    if 'payment_filter' not in st.session_state:
        st.session_state.payment_filter = {
            'time_filter': 'All Time',
            'year': datetime.now().year,
            'quarter': None
        }

def reset_payment_form():
    """Reset payment form state."""
    st.session_state.show_payment_form = False
    st.session_state.editing_payment_id = None
    st.session_state.payment_form_data = {}
    st.session_state.payment_validation_errors = []

def show_payment_form(client_id: int, contract: Tuple):
    """Display the payment form for adding/editing payments."""
    from streamlit_extras.grid import grid

    # Header and initial setup
    st.subheader("Add Payment" if not st.session_state.editing_payment_id else "Edit Payment")
    
    # Load existing payment data if editing
    if st.session_state.editing_payment_id:
        payment_data = get_payment_by_id(st.session_state.editing_payment_id)
        current_payment = payment_data if payment_data else None
    else:
        current_payment = None

    # Display contract info
    if not display_contract_info(contract):
        return
    
    # Get schedule info early for use throughout form
    schedule = contract[3].lower() if contract[3] else ""
    is_monthly = schedule == "monthly"
    period_label = "Month" if is_monthly else "Quarter"

    # Show validation errors if any
    if st.session_state.payment_validation_errors:
        for error in st.session_state.payment_validation_errors:
            st.error(error)
        # Clear errors after displaying
        st.session_state.payment_validation_errors = []

    # Create a centered container for the form
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.form(key="payment_form"):
            # === MAIN FORM LAYOUT ===
            # Top row grid: Date | Start Period | End Period
            top_row = grid([1.2, 1.5, 1.5], gap="small", vertical_align="bottom")
            
            with top_row.container():
                st.markdown("Payment Date<span style='color: red'>*</span>", unsafe_allow_html=True)
                received_date = st.date_input(
                    "Payment Date",
                    value=datetime.strptime(current_payment[0], '%Y-%m-%d') if current_payment else datetime.now(),
                    format="MM/DD/YYYY",
                    label_visibility="collapsed"
                )

            with top_row.container():
                st.markdown(f"Start {period_label}<span style='color: red'>*</span>", unsafe_allow_html=True)
                period_options = get_period_options(schedule)
                if not period_options:
                    st.error(f"No valid {period_label.lower()}s available for payment")
                    return
                
                current_period = get_current_period(schedule)
                if current_payment:
                    default_period = format_period_display(current_payment[1], current_payment[2], schedule)
                    default_index = period_options.index(default_period) if default_period in period_options else 0
                else:
                    default_index = 0

                start_period_option = st.selectbox(
                    f"Start {period_label}",
                    options=period_options,
                    index=default_index,
                    key="start_period",
                    label_visibility="collapsed"
                )
                start_period, start_year = parse_period_option(start_period_option, schedule)

            with top_row.container():
                st.markdown(f"End {period_label}", unsafe_allow_html=True)
                # Get valid end options based on start period
                valid_end_options = [
                    opt for opt in period_options
                    if validate_period_range(
                        start_period, start_year,
                        *parse_period_option(opt, schedule),
                        schedule
                    )
                ]
                
                # Default to start period
                if current_payment and current_payment[1] != current_payment[3]:
                    default_end_period = format_period_display(current_payment[3], current_payment[4], schedule)
                    default_end_index = valid_end_options.index(default_end_period) if default_end_period in valid_end_options else 0
                else:
                    default_end_index = valid_end_options.index(start_period_option) if start_period_option in valid_end_options else 0
                
                end_period_option = st.selectbox(
                    f"End {period_label}",
                    options=valid_end_options,
                    index=default_end_index,
                    key="end_period",
                    label_visibility="collapsed"
                )
                end_period, end_year = parse_period_option(end_period_option, schedule)

            # Financial Details Row
            finance_grid = grid([1, 1, 1], gap="small", vertical_align="top")
            
            with finance_grid.container():
                st.markdown("Assets Under Management")
                total_assets = st.text_input(
                    "Assets",
                    value=format_currency_ui(current_payment[5]) if current_payment else "",
                    key="total_assets",
                    label_visibility="collapsed"
                )

            with finance_grid.container():
                st.markdown("Payment Amount<span style='color: red'>*</span>", unsafe_allow_html=True)
                actual_fee = st.text_input(
                    "Payment",
                    value=format_currency_ui(current_payment[6]) if current_payment else "",
                    key="actual_fee",
                    label_visibility="collapsed"
                )

            with finance_grid.container():
                st.markdown("Payment Method")
                method_options = get_unique_payment_methods()
                current_method = current_payment[7] if current_payment else "None Specified"
                method = st.selectbox(
                    "Method",
                    options=method_options,
                    index=method_options.index(current_method) if current_method in method_options else 0,
                    label_visibility="collapsed"
                )
                if method == "Other":
                    other_method = st.text_input(
                        "Specify Method",
                        value=current_payment[7] if current_payment else "",
                        label_visibility="collapsed"
                    )
                else:
                    other_method = None

            # Notes field (full width but compact)
            notes = st.text_area(
                "Notes",
                value=current_payment[8] if current_payment else "",
                placeholder=("Add any additional notes here..." if start_period_option == end_period_option else
                            "Add any additional notes here (e.g., reason for multi-period payment)..."),
                height=75
            )

            # Calculate expected fee
            expected = None
            if total_assets:
                try:
                    assets = float(total_assets.replace('$', '').replace(',', ''))
                    expected = calculate_expected_fee(contract, assets)
                    st.info(f"Expected Fee: ${expected:,.2f}")
                except ValueError:
                    st.warning("Please enter a valid number for assets")

            # Add CSS for compact preview
            st.markdown("""
                <style>
                .preview-container {
                    background-color: #f0f2f6;
                    border-radius: 4px;
                    padding: 12px 20px;
                    margin: 15px 0 10px 0;
                }
                .preview-container p {
                    margin: 0;
                    padding: 2px 0;
                    line-height: 1.3;
                }
                .button-row {
                    display: flex;
                    gap: 10px;
                    margin-top: 10px;
                }
                </style>
            """, unsafe_allow_html=True)

            # Preview section using grid like the rest of the form
            preview_grid = grid([1], gap="small")
            with preview_grid.container():
                # Date and Period line
                period_info = f"Date: {received_date.strftime('%m/%d/%Y')}"
                if start_period_option == end_period_option:
                    period_info += f" | Period: {start_period_option}"
                else:
                    period_info += f" | Period: {start_period_option} → {end_period_option}"
                st.write(period_info)
                
                # Financial details line
                financial_info = []
                if total_assets:
                    financial_info.append(f"Assets: {format_currency_ui(total_assets)}")
                if expected is not None:
                    financial_info.append(f"Expected: ${expected:,.2f}")
                if actual_fee:
                    financial_info.append(f"Payment: {format_currency_ui(actual_fee)}")
                if financial_info:
                    st.write(' | '.join(financial_info))
                
                # Method line
                st.write(f"Method: {method if method != 'Other' else other_method}")
            
            # Buttons using grid like other sections
            button_grid = grid([1, 1], gap="small")
            with button_grid.container():
                submitted = st.form_submit_button("Save Payment", type="primary", use_container_width=True)
            with button_grid.container():
                cancelled = st.form_submit_button("Cancel", use_container_width=True)

    # Handle form submission
    if submitted:
        with st.spinner("Processing payment..."):
            # Clean currency values
            db_total_assets = format_currency_db(total_assets) if total_assets else None
            db_actual_fee = format_currency_db(actual_fee) if actual_fee else None
            
            # Prepare form data
            form_data = {
                'received_date': received_date.strftime('%Y-%m-%d'),
                'applied_start_period': start_period,
                'applied_start_year': start_year,
                'applied_end_period': end_period,
                'applied_end_year': end_year,
                'total_assets': db_total_assets,
                'actual_fee': db_actual_fee,
                'expected_fee': expected,
                'method': other_method if method == "Other" else method,
                'notes': notes,
                'payment_schedule': schedule
            }

            # Validate and save
            validation_errors = validate_payment_data(form_data)
            if validation_errors:
                # Store validation errors
                st.session_state.payment_validation_errors = validation_errors
                # Show errors without rerun
                for error in validation_errors:
                    st.error(error)
                return
            else:
                try:
                    if st.session_state.editing_payment_id:
                        success = update_payment(st.session_state.editing_payment_id, form_data)
                        if success:
                            st.toast("Payment updated successfully!", icon="✅")
                            reset_payment_form()
                            st.rerun()
                        else:
                            st.error("Failed to update payment")
                    else:
                        payment_id = add_payment(client_id, form_data)
                        if payment_id:
                            st.toast("Payment added successfully!", icon="✅")
                            reset_payment_form()
                            st.rerun()
                        else:
                            st.error("Failed to add payment. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    # Keep form data on error
                    st.session_state.payment_form_data = form_data

    if cancelled:
        reset_payment_form()
        st.rerun()

def display_contract_info(contract: Tuple):
    """Display contract information above the payment form."""
    fee_type = contract[4].title() if contract[4] else "N/A"
    rate = (
        f"{contract[5]*100:.3f}%" if contract[4] == 'percentage' and contract[5]
        else f"${contract[6]:,.2f}" if contract[4] == 'flat' and contract[6]
        else "N/A"
    )
    schedule = contract[3].title() if contract[3] else "N/A"
    provider = contract[1] or "N/A"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"Provider: {provider} | Fee Type: {fee_type} | Rate: {rate} | Schedule: {schedule} | All payments processed in arrears")
    return True

# ============================================================================
# Payment History Display
# ============================================================================

def show_payment_history(client_id: int):
    """Display the payment history table with filtering options."""
    # Get active contract first
    contract = get_active_contract(client_id)
    
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
        # Only show Add Payment button if contract has payment schedule
        if not contract or not contract[3]:
            st.error("Payment schedule must be set in the contract before adding payments.")
        else:
            def show_add_payment_form():
                st.session_state.show_payment_form = True
                st.session_state.editing_payment_id = None
                st.session_state.payment_form_data = {}

            st.button(
                "Add Payment", 
                type="primary", 
                use_container_width=True,
                on_click=show_add_payment_form
            )

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

def delete_payment_confirm(payment_id):
    """Set up confirmation dialog for payment deletion"""
    st.session_state.delete_payment_id = payment_id
    st.session_state.show_delete_confirm = True
    st.rerun()  # Force rerun to show confirmation immediately

def handle_delete_confirmed(payment_id):
    """Handle the actual deletion after confirmation"""
    with st.spinner("Deleting payment..."):
        if delete_payment(payment_id):
            st.toast("Payment deleted successfully!", icon="✅")
        else:
            st.error("Failed to delete payment")
    # Clear states after operation
    st.session_state.delete_payment_id = None
    st.session_state.show_delete_confirm = False
    st.rerun()  # Refresh to show updated list

def handle_delete_cancelled():
    """Handle cancellation of delete operation"""
    st.session_state.delete_payment_id = None
    st.session_state.show_delete_confirm = False
    st.rerun()

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
                    st.markdown(f"<p title='{payment['Notes']}'>🟢</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p>◯</p>", unsafe_allow_html=True)
            
            # Actions column
            with cols[-1]:
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    def set_payment_to_edit(payment_id):
                        st.session_state.show_payment_form = True
                        st.session_state.editing_payment_id = payment_id
                        # Load payment data for editing
                        payment_data = get_payment_by_id(payment_id)
                        if payment_data:
                            # Convert quarters to months if monthly schedule
                            schedule = payment_data[9].lower() if payment_data[9] else ""
                            if schedule == "monthly":
                                # Convert quarters back to months
                                start_period = (payment_data[1] - 1) * 3 + 1
                                end_period = (payment_data[3] - 1) * 3 + 3
                            else:
                                # Keep as quarters
                                start_period = payment_data[1]
                                end_period = payment_data[3]

                            # Only treat as multi-period if start and end are actually different
                            is_multi_period = (payment_data[1] != payment_data[3] or payment_data[2] != payment_data[4])

                            st.session_state.payment_form_data = {
                                'received_date': payment_data[0],
                                'applied_start_period': start_period,
                                'applied_start_year': payment_data[2],
                                'applied_end_period': end_period,
                                'applied_end_year': payment_data[4],
                                'total_assets': payment_data[5],
                                'actual_fee': payment_data[6],
                                'method': payment_data[7],
                                'notes': payment_data[8],
                                'payment_schedule': payment_data[9],
                                'is_multi_period': is_multi_period  # Add this to control checkbox state
                            }

                    st.button(
                        "✏️",
                        key=f"edit_payment_{payment['payment_id']}_{datetime.now().strftime('%Y%m%d')}",
                        help="Edit payment",
                        on_click=set_payment_to_edit,
                        args=(payment['payment_id'],)
                    )
                
                with action_cols[1]:
                    def delete_payment_confirm(payment_id):
                        # Clear any other delete confirmations first
                        if st.session_state.delete_payment_id is not None and st.session_state.delete_payment_id != payment_id:
                            st.session_state.show_delete_confirm = False
                        # Set new delete confirmation
                        st.session_state.delete_payment_id = payment_id
                        st.session_state.show_delete_confirm = True

                    st.button(
                        "🗑️",
                        key=f"delete_payment_{payment['payment_id']}_{datetime.now().strftime('%Y%m%d')}",
                        help="Delete payment",
                        on_click=delete_payment_confirm,
                        args=(payment['payment_id'],)
                    )
            
            # Show delete confirmation if active
            if st.session_state.show_delete_confirm and st.session_state.delete_payment_id == payment['payment_id']:
                # Use a modal-like container for confirmation
                with st.container():
                    st.markdown("---")  # Visual separator
                    confirm_cols = st.columns([6, 2, 2])
                    with confirm_cols[0]:
                        st.warning(f"Delete this payment for {payment['Period']}?")
                    with confirm_cols[1]:
                        if st.button(
                            "Yes, Delete",
                            key=f"confirm_delete_payment_{payment['payment_id']}_{datetime.now().strftime('%Y%m%d')}",
                            type="primary",
                            use_container_width=True
                        ):
                            handle_delete_confirmed(payment['payment_id'])
                    with confirm_cols[2]:
                        if st.button(
                            "Cancel",
                            key=f"cancel_delete_payment_{payment['payment_id']}_{datetime.now().strftime('%Y%m%d')}",
                            use_container_width=True
                        ):
                            handle_delete_cancelled()
                    st.markdown("---")  # Visual separator
    
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
    
    # Check for valid contract and payment schedule before proceeding
    if not contract:
        st.error("No active contract found. Please set up a contract first.")
        return
    
    if not contract[3]:  # payment_schedule is index 3 in contract tuple
        st.error("Payment schedule must be set in the contract before adding payments.")
        return
    
    # Show form or history based on state
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
