# pages\client_dashboard\client_contract_management.py
import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.utils import (
    get_active_contract,
    get_client_contracts,
    get_database_connection,
    format_currency_ui,
    format_currency_db
)
from utils.ui_state_manager import UIStateManager

@st.dialog('Contract Management')
def show_contract_management_dialog(client_id: int):
    """Show the contract management dialog."""
    if 'ui_manager' not in st.session_state:
        return
    
    ui_manager = st.session_state.ui_manager
    if not ui_manager.is_contract_dialog_open:
        return

    # Get current contract data and form state
    contract = get_active_contract(client_id)
    form_data = ui_manager.contract_form_data
    mode = form_data.get('mode', 'add')

    st.markdown("""
        <div style='padding: 0.5em; background-color: #E8F0FE; border-radius: 4px; margin-bottom: 1em; color: #1e1e1e;'>
            ℹ️ Current Active Contract
        </div>
    """, unsafe_allow_html=True)
    
    # Contract form
    with st.form("contract_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            provider = st.text_input(
                "Provider Name*", 
                value=form_data.get('provider_name', ''),
                placeholder="e.g., John Hancock",
                key="provider_name"
            )
            
            contract_num = st.text_input(
                "Contract Number", 
                value=form_data.get('contract_number', ''),
                placeholder="Optional",
                key="contract_number"
            )
            
            start_date = st.date_input(
                "Start Date",
                value=datetime.strptime(form_data.get('contract_start_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                format="YYYY-MM-DD",
                key="start_date"
            )

        with col2:
            fee_type = st.selectbox(
                "Fee Type*",
                options=['percentage', 'flat'],
                index=0 if form_data.get('fee_type', '') != 'flat' else 1,
                key="fee_type"
            )
            
            if fee_type == 'percentage':
                rate = st.number_input(
                    "Rate (%)*",
                    value=float(form_data.get('percent_rate', 0) * 100) if form_data.get('percent_rate') else 0.0,
                    format="%.4f",
                    step=0.0001,
                    help="Enter percentage as decimal (e.g., 0.75 for 0.75%)",
                    key="rate_percent"
                )
                rate_value = rate / 100
                form_data['percent_rate'] = rate_value
                form_data['flat_rate'] = None
            else:
                rate = st.number_input(
                    "Flat Rate ($)*",
                    value=float(form_data.get('flat_rate', 0)) if form_data.get('flat_rate') else 0.0,
                    format="%.2f",
                    step=100.0,
                    help="Enter dollar amount",
                    key="rate_flat"
                )
                rate_value = rate
                form_data['flat_rate'] = rate_value
                form_data['percent_rate'] = None
            
            schedule = st.selectbox(
                "Payment Schedule*",
                options=['monthly', 'quarterly'],
                index=0 if form_data.get('payment_schedule', '') != 'quarterly' else 1,
                key="payment_schedule"
            )
            
            participants = st.number_input(
                "Number of Participants",
                value=int(form_data.get('num_people', 0)) if form_data.get('num_people') else 0,
                min_value=0,
                step=1,
                key="num_people"
            )

        notes = st.text_area(
            "Notes",
            value=form_data.get('notes', ''),
            placeholder="Add any additional contract information here",
            key="notes"
        )

        # Update form data
        updated_data = {
            'provider_name': provider,
            'contract_number': contract_num,
            'contract_start_date': start_date.strftime('%Y-%m-%d'),
            'fee_type': fee_type,
            'percent_rate': form_data.get('percent_rate'),
            'flat_rate': form_data.get('flat_rate'),
            'payment_schedule': schedule,
            'num_people': participants,
            'notes': notes
        }
        ui_manager.update_contract_form_data(updated_data)

        # Show validation errors if any
        if ui_manager.contract_dialog_has_errors:
            for error in ui_manager.contract_validation_errors:
                st.error(error)

        # Show cancel confirmation if needed
        if form_data.get('show_cancel_confirm'):
            st.warning("You have unsaved changes. Are you sure you want to cancel?")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Yes, Discard Changes", type="primary", use_container_width=True):
                    ui_manager.close_contract_dialog()
                    st.rerun()
            with col2:
                if st.form_submit_button("No, Keep Editing", use_container_width=True):
                    form_data['show_cancel_confirm'] = False
                    ui_manager.update_contract_form_data(form_data)
                    st.rerun()
        else:
            # Form buttons
            col1, col2 = st.columns(2)
            with col1:
                submit_label = "Update Contract" if mode == 'edit' else "Create Contract"
                if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                    # Validate form
                    errors = validate_contract_data(updated_data)
                    if errors:
                        ui_manager.set_contract_validation_errors(errors)
                        st.rerun()
                    else:
                        # Save contract
                        if save_contract(client_id, updated_data, mode):
                            st.success(f"Contract successfully {'updated' if mode == 'edit' else 'created'}!")
                            ui_manager.close_contract_dialog()
                            st.rerun()
                        else:
                            ui_manager.set_contract_validation_errors(["Failed to save contract. Please try again."])
                            st.rerun()
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    if has_unsaved_changes(form_data):
                        form_data['show_cancel_confirm'] = True
                        ui_manager.update_contract_form_data(form_data)
                        st.rerun()
                    else:
                        ui_manager.close_contract_dialog()
                        st.rerun()

    # Show inactive contracts if any exist
    st.divider()
    with st.expander("Previous Contracts", expanded=False):
        inactive_contracts = get_client_contracts(client_id)
        if inactive_contracts:
            for old_contract in inactive_contracts:
                if not old_contract[2]:  # not active
                    with st.container():
                        # Contract header
                        st.markdown(f"""
                            <div style='padding: 0.5em 0;'>
                                <strong>{old_contract[4]}</strong> • {old_contract[5] or 'No start date'}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Contract details
                        cols = st.columns([2, 2, 2])
                        with cols[0]:
                            st.text(f"Contract #: {old_contract[3] or 'N/A'}")
                        with cols[1]:
                            st.text(f"Schedule: {old_contract[8].title() if old_contract[8] else 'N/A'}")
                        with cols[2]:
                            rate_display = (
                                f"{old_contract[6]*100:.3f}%" if old_contract[6]
                                else f"${old_contract[7]:,.2f}" if old_contract[7]
                                else "N/A"
                            )
                            st.text(f"{old_contract[5].title() if old_contract[5] else 'N/A'} Rate: {rate_display}")
                        
                        if old_contract[10]:  # notes
                            st.caption(old_contract[10])
                        st.divider()
        else:
            st.info("No previous contracts found.")

def validate_contract_data(data: Dict[str, Any]) -> list:
    """Validate contract data before saving."""
    errors = []
    
    if not data.get('provider_name', '').strip():
        errors.append("Provider name is required")
    
    if data.get('fee_type') == 'percentage':
        if not data.get('percent_rate') or data.get('percent_rate') <= 0:
            errors.append("Please enter a valid rate percentage greater than 0")
    else:
        if not data.get('flat_rate') or data.get('flat_rate') <= 0:
            errors.append("Please enter a valid flat rate amount greater than 0")
    
    if not data.get('payment_schedule'):
        errors.append("Payment schedule is required")
    
    try:
        start_date = datetime.strptime(data.get('contract_start_date', ''), '%Y-%m-%d')
        if start_date > datetime.now():
            errors.append("Contract start date cannot be in the future")
    except ValueError:
        errors.append("Invalid contract start date")
    
    return errors

def has_unsaved_changes(form_data: Dict[str, Any]) -> bool:
    """Check if there are unsaved changes in the form."""
    if not form_data:
        return False
    
    # Fields to check for changes
    fields = [
        'provider_name', 'contract_number', 'contract_start_date',
        'fee_type', 'percent_rate', 'flat_rate', 'payment_schedule',
        'num_people', 'notes'
    ]
    
    # Compare current values with originals
    original_data = form_data.get('original_data', {})
    return any(
        form_data.get(field) != original_data.get(field)
        for field in fields
        if field in form_data or field in original_data
    )

def save_contract(client_id: int, contract_data: Dict[str, Any], mode: str = 'add') -> bool:
    """Save contract to database."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # If adding new contract, deactivate current active contract
        if mode == 'add':
            cursor.execute("""
                UPDATE contracts 
                SET active = 'FALSE' 
                WHERE client_id = ? AND active = 'TRUE'
            """, (client_id,))
        
        # Insert new contract or update existing
        if mode == 'add':
            cursor.execute("""
                INSERT INTO contracts (
                    client_id, active, contract_number, provider_name,
                    contract_start_date, fee_type, percent_rate, flat_rate,
                    payment_schedule, num_people, notes
                ) VALUES (?, 'TRUE', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                contract_data.get('contract_number'),
                contract_data.get('provider_name'),
                contract_data.get('contract_start_date'),
                contract_data.get('fee_type'),
                contract_data.get('percent_rate'),
                contract_data.get('flat_rate'),
                contract_data.get('payment_schedule'),
                contract_data.get('num_people'),
                contract_data.get('notes')
            ))
        else:
            cursor.execute("""
                UPDATE contracts SET
                    contract_number = ?,
                    provider_name = ?,
                    contract_start_date = ?,
                    fee_type = ?,
                    percent_rate = ?,
                    flat_rate = ?,
                    payment_schedule = ?,
                    num_people = ?,
                    notes = ?
                WHERE contract_id = ? AND active = 'TRUE'
            """, (
                contract_data.get('contract_number'),
                contract_data.get('provider_name'),
                contract_data.get('contract_start_date'),
                contract_data.get('fee_type'),
                contract_data.get('percent_rate'),
                contract_data.get('flat_rate'),
                contract_data.get('payment_schedule'),
                contract_data.get('num_people'),
                contract_data.get('notes'),
                contract_data.get('contract_id')
            ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving contract: {e}")
        return False
    finally:
        conn.close()