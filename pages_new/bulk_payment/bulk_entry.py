import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from utils.utils import (
    get_payment_history,
    get_active_contract,
    format_currency_ui,
    format_currency_db,
    validate_payment_data,
    add_payment,
    get_payment_by_id,
    get_unique_payment_methods,
    get_clients
)
from ..client_display_and_forms.client_payment_utils import (
    get_period_options,
    parse_period_option,
    validate_period_range,
    calculate_expected_fee,
    get_current_period,
    format_period_display
)

def init_bulk_entry_state():
    """Initialize or reset bulk payment entry state."""
    if 'bulk_payments' not in st.session_state:
        st.session_state.bulk_payments = [{
            'client_id': None,
            'received_date': datetime.now().strftime('%Y-%m-%d'),
            'applied_start_period': None,
            'applied_start_year': None,
            'applied_end_period': None,
            'applied_end_year': None,
            'total_assets': None,
            'actual_fee': None,
            'method': 'None Specified',
            'notes': '',
            'contract': None,
            'is_valid': False
        }]
    
    if 'bulk_validation_errors' not in st.session_state:
        st.session_state.bulk_validation_errors = {}
    
    if 'bulk_entry_clients' not in st.session_state:
        st.session_state.bulk_entry_clients = get_clients()

def add_payment_card():
    """Add a new payment card to the session state."""
    st.session_state.bulk_payments.append({
        'client_id': None,
        'received_date': datetime.now().strftime('%Y-%m-%d'),
        'applied_start_period': None,
        'applied_start_year': None,
        'applied_end_period': None,
        'applied_end_year': None,
        'total_assets': None,
        'actual_fee': None,
        'method': 'None Specified',
        'notes': '',
        'contract': None,
        'is_valid': False
    })

def remove_payment_card(index: int):
    """Remove a payment card from the session state."""
    if len(st.session_state.bulk_payments) > 1:
        st.session_state.bulk_payments.pop(index)
        if index in st.session_state.bulk_validation_errors:
            del st.session_state.bulk_validation_errors[index]

def show_payment_card(index: int):
    """Display a single payment card."""
    card_data = st.session_state.bulk_payments[index]
    
    with st.expander(f"Payment Entry #{index + 1}", expanded=True):
        # Combine client selection and delete button in a more natural way
        client_col, delete_col = st.columns([11, 1])  # Use asymmetric ratio for better spacing
        
        # Client Selection
        with client_col:
            client_options = [(c[0], c[1]) for c in st.session_state.bulk_entry_clients]
            client_names = ["Select Client..."] + [c[1] for c in client_options]
            selected_index = 0
            if card_data['client_id']:
                try:
                    selected_index = [c[0] for c in client_options].index(card_data['client_id']) + 1
                except ValueError:
                    selected_index = 0
            
            selected_client = st.selectbox(
                "Client",
                options=client_names,
                index=selected_index,
                key=f"client_{index}"
            )
        
        # Delete Button - aligned with client selection
        with delete_col:
            st.write("")  # Add some vertical spacing to align with selectbox
            if st.button("❌", key=f"delete_{index}", help="Remove this payment"):
                remove_payment_card(index)
                st.rerun()
            
        # Handle client selection after UI elements are created    
        if selected_client != "Select Client...":
            client_id = client_options[client_names.index(selected_client) - 1][0]
            if client_id != card_data['client_id']:
                card_data['client_id'] = client_id
                card_data['contract'] = get_active_contract(client_id)
        
        # Payment Details
        if card_data['client_id'] and card_data['contract']:
            cols = st.columns(3)
            
            # Column 1: Date and Amount
            with cols[0]:
                received_date = st.date_input(
                    "Payment Date",
                    value=datetime.strptime(card_data['received_date'], '%Y-%m-%d'),
                    format="MM/DD/YYYY",
                    key=f"date_{index}"
                )
                card_data['received_date'] = received_date.strftime('%Y-%m-%d')
                
                amount = st.text_input(
                    "Payment Amount",
                    value=format_currency_ui(card_data['actual_fee']) if card_data['actual_fee'] else "",
                    key=f"amount_{index}",
                    help="Amount received"
                )
                if amount:
                    card_data['actual_fee'] = format_currency_db(amount)
            
            # Column 2: AUM and Method
            with cols[1]:
                assets = st.text_input(
                    "Assets Under Management",
                    value=format_currency_ui(card_data['total_assets']) if card_data['total_assets'] else "",
                    key=f"assets_{index}",
                    help="Total assets under management"
                )
                if assets:
                    card_data['total_assets'] = format_currency_db(assets)
                
                method_options = get_unique_payment_methods()
                method = st.selectbox(
                    "Payment Method",
                    options=method_options,
                    index=method_options.index(card_data['method']) if card_data['method'] in method_options else 0,
                    key=f"method_{index}"
                )
                card_data['method'] = method
            
            # Column 3: Period Selection
            with cols[2]:
                schedule = card_data['contract'][3].lower() if card_data['contract'][3] else ""
                period_label = "Month" if schedule == "monthly" else "Quarter"
                period_options = get_period_options(schedule)
                
                if period_options:
                    # Start Period
                    default_index = 0
                    if card_data['applied_start_period']:
                        period_display = format_period_display(
                            card_data['applied_start_period'],
                            card_data['applied_start_year'],
                            schedule
                        )
                        if period_display in period_options:
                            default_index = period_options.index(period_display)
                    
                    start_period_option = st.selectbox(
                        f"Start {period_label}",
                        options=period_options,
                        index=default_index,
                        key=f"start_period_{index}"
                    )
                    start_period, start_year = parse_period_option(start_period_option, schedule)
                    
                    # End Period - Filter valid options based on start period
                    valid_end_options = [
                        opt for opt in period_options
                        if validate_period_range(
                            start_period, start_year,
                            *parse_period_option(opt, schedule),
                            schedule
                        )
                    ]
                    
                    # Default to start period for end period
                    if card_data['applied_end_period'] and card_data['applied_end_period'] != card_data['applied_start_period']:
                        end_period_display = format_period_display(
                            card_data['applied_end_period'],
                            card_data['applied_end_year'],
                            schedule
                        )
                        default_end_index = valid_end_options.index(end_period_display) if end_period_display in valid_end_options else 0
                    else:
                        default_end_index = valid_end_options.index(start_period_option) if start_period_option in valid_end_options else 0
                    
                    end_period_option = st.selectbox(
                        f"End {period_label}",
                        options=valid_end_options,
                        index=default_end_index,
                        key=f"end_period_{index}"
                    )
                    end_period, end_year = parse_period_option(end_period_option, schedule)
                    
                    # Update card data with period information
                    card_data['applied_start_period'] = start_period
                    card_data['applied_start_year'] = start_year
                    card_data['applied_end_period'] = end_period
                    card_data['applied_end_year'] = end_year
                
                if card_data['total_assets']:
                    try:
                        assets = float(card_data['total_assets'])
                        expected = calculate_expected_fee(card_data['contract'], assets)
                        st.info(f"Expected Fee: ${expected:,.2f}")
                    except (ValueError, TypeError):
                        st.error("Invalid assets value")
            
            # Notes Section
            notes = st.text_area(
                "Notes",
                value=card_data['notes'],
                key=f"notes_{index}",
                height=75,
                placeholder=("Add any additional notes here..." if start_period_option == end_period_option else
                           "Add any additional notes here (e.g., reason for multi-period payment)...")
            )
            card_data['notes'] = notes
            
            # Validate card data
            validation_errors = validate_payment_data({
                'received_date': card_data['received_date'],
                'applied_start_period': card_data['applied_start_period'],
                'applied_start_year': card_data['applied_start_year'],
                'applied_end_period': card_data['applied_end_period'],
                'applied_end_year': card_data['applied_end_year'],
                'total_assets': card_data['total_assets'],
                'actual_fee': card_data['actual_fee'],
                'method': card_data['method'],
                'notes': card_data['notes'],
                'payment_schedule': card_data['contract'][3] if card_data['contract'] else None
            })
            
            st.session_state.bulk_validation_errors[index] = validation_errors
            card_data['is_valid'] = not validation_errors
            
            if validation_errors:
                st.error("\n".join(validation_errors))

                
def submit_bulk_payments():
    """Submit all valid payments to the database."""
    valid_payments = [
        (i, payment) for i, payment in enumerate(st.session_state.bulk_payments)
        if payment.get('is_valid', False)
    ]
    
    if not valid_payments:
        st.error("No valid payments to submit.")
        return
    
    progress_text = "Submitting payments..."
    progress_bar = st.progress(0, text=progress_text)
    
    success_count = 0
    failed_payments = []
    
    for idx, (i, payment) in enumerate(valid_payments):
        try:
            form_data = {
                'received_date': payment['received_date'],
                'applied_start_period': payment['applied_start_period'],
                'applied_start_year': payment['applied_start_year'],
                'applied_end_period': payment['applied_end_period'],
                'applied_end_year': payment['applied_end_year'],
                'total_assets': payment['total_assets'],
                'actual_fee': payment['actual_fee'],
                'method': payment['method'],
                'notes': payment['notes'],
                'payment_schedule': payment['contract'][3] if payment['contract'] else None
            }
            
            if add_payment(payment['client_id'], form_data):
                success_count += 1
            else:
                failed_payments.append((i, "Database error"))
                
        except Exception as e:
            failed_payments.append((i, str(e)))
        
        progress_bar.progress((idx + 1) / len(valid_payments))
    
    if success_count:
        st.success(f"Successfully added {success_count} payments!")
        # Remove successful payments
        indices_to_remove = [i for i, _ in valid_payments]
        for i in sorted(indices_to_remove, reverse=True):
            st.session_state.bulk_payments.pop(i)
        
        if not st.session_state.bulk_payments:
            add_payment_card()
        
        st.rerun()
    
    if failed_payments:
        for i, error in failed_payments:
            st.error(f"Payment {i+1} failed: {error}")

def show_bulk_payment_entry():
    """Main entry point for bulk payment entry."""
    st.title("📝 Bulk Payment Entry")
    init_bulk_entry_state()
    
    # Display all payment cards
    for i in range(len(st.session_state.bulk_payments)):
        show_payment_card(i)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Add Payment", use_container_width=True):
            add_payment_card()
            st.rerun()
    
    with col2:
        valid_count = sum(1 for p in st.session_state.bulk_payments if p.get('is_valid', False))
        if valid_count > 0:
            if st.button("💾 Submit Valid Payments", type="primary", use_container_width=True):
                submit_bulk_payments()

if __name__ == "__main__":
    show_bulk_payment_entry()