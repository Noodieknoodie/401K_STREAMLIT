import streamlit as st
from utils.client_data import (
    get_consolidated_client_data,
    get_client_contracts,
    save_contract
)
from utils.ui_state_manager import UIStateManager
from utils.debug_logger import debug
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List

@st.dialog("Contract Management")
def show_contract_management_dialog(client_id: int):
    """Show the contract management dialog."""
    # Get UI manager from session state
    if 'ui_manager' not in st.session_state:
        debug.log_ui_interaction(
            action='contract_dialog',
            element='ui_manager',
            data={'error': 'no_ui_manager_in_session'}
        )
        return
    ui_manager = st.session_state.ui_manager
    
    if not ui_manager.is_contract_dialog_open:
        return
        
    # Get current data
    data = get_consolidated_client_data(client_id)
    active_contract = data.get('active_contract')
    
    # Show form if in edit/add mode
    if ui_manager.contract_form_data.get('mode') in ['edit', 'add']:
        show_contract_form(client_id, ui_manager)
        return
    
    # Current Contract Section
    st.subheader("Current Contract")
    
    if active_contract:
        # Display current contract details
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Provider:**", active_contract['provider_name'])
            st.write("**Contract #:**", active_contract['contract_number'] or "N/A")
            st.write("**Start Date:**", active_contract['contract_start_date'] or "N/A")
        with col2:
            rate_display = (
                f"{active_contract['percent_rate']*100:.3f}%" 
                if active_contract['fee_type'] == 'percentage' and active_contract['percent_rate']
                else f"${active_contract['flat_rate']:,.2f}"
                if active_contract['fee_type'] == 'flat' and active_contract['flat_rate']
                else "N/A"
            )
            st.write("**Fee:**", f"{active_contract['fee_type'].title()} - {rate_display}")
            st.write("**Schedule:**", active_contract['payment_schedule'].title())
            st.write("**Participants:**", active_contract['num_people'] or "N/A")
        
        # Action buttons
        btn_col1, btn_col2, _ = st.columns([1,1,2])
        with btn_col1:
            if st.button("✏️ Edit Current", use_container_width=True):
                ui_manager.update_contract_form_data({
                    'mode': 'edit',
                    **active_contract
                })
                st.rerun()
        with btn_col2:
            if st.button("➕ Create New", use_container_width=True):
                if ui_manager.contract_confirm_new:
                    ui_manager.update_contract_form_data({'mode': 'add'})
                    ui_manager.set_contract_confirm_new(False)
                    st.rerun()
                else:
                    ui_manager.set_contract_confirm_new(True)
                    st.rerun()
                
                # Show confirmation if needed
                if ui_manager.contract_confirm_new:
                    st.warning(
                        "⚠️ Creating a new contract will archive the current active contract. "
                        "This action cannot be undone. Do you want to proceed?"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Create New", type="primary", use_container_width=True):
                            ui_manager.update_contract_form_data({'mode': 'add'})
                            ui_manager.set_contract_confirm_new(False)
                            st.rerun()
                    with col2:
                        if st.button("No, Keep Current", use_container_width=True):
                            ui_manager.set_contract_confirm_new(False)
                            st.rerun()
    else:
        st.info("No active contract found.")
        if st.button("➕ Create New Contract", use_container_width=True):
            ui_manager.update_contract_form_data({'mode': 'add'})
            st.rerun()
    
    # Previous Contracts Section
    if active_contract:  # Only show history if there's an active contract
        st.divider()
        st.subheader("Previous Contracts")
        
        # Get historical contracts
        all_contracts = get_client_contracts(client_id)
        historical = [c for c in all_contracts if not c['active']]
        
        if historical:
            df = pd.DataFrame(historical)
            
            # Format rate column
            df['rate'] = df.apply(
                lambda x: f"{x['percent_rate']*100:.3f}%" if x['fee_type'] == 'percentage' and x['percent_rate']
                else f"${x['flat_rate']:,.2f}" if x['fee_type'] == 'flat' and x['flat_rate']
                else "N/A",
                axis=1
            )
            
            # Display columns
            display_columns = [
                'provider_name',
                'contract_number',
                'contract_start_date',
                'fee_type',
                'rate',
                'payment_schedule'
            ]
            
            st.dataframe(
                df[display_columns],
                column_config={
                    "provider_name": st.column_config.TextColumn("Provider", width="medium"),
                    "contract_number": st.column_config.TextColumn("Contract #", width="small"),
                    "contract_start_date": st.column_config.DateColumn("Start Date", width="small"),
                    "fee_type": st.column_config.TextColumn("Fee Type", width="small"),
                    "rate": st.column_config.TextColumn("Rate", width="small"),
                    "payment_schedule": st.column_config.TextColumn("Schedule", width="small"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No previous contracts found.")
    
    # Close dialog button
    st.button("Close", on_click=lambda: close_contract_dialog(ui_manager))

def close_contract_dialog(ui_manager: UIStateManager):
    """Clean up and close the contract dialog."""
    ui_manager.set_contract_confirm_new(False)
    ui_manager.close_contract_dialog()

def show_contract_form(client_id: int, ui_manager: UIStateManager):
    """Show the contract form for editing or creating a contract."""
    form_data = ui_manager.contract_form_data
    mode = form_data.get('mode', 'add')
    
    # Handle date value
    try:
        if form_data.get('contract_start_date'):
            start_date_value = datetime.strptime(form_data['contract_start_date'], '%Y-%m-%d').date()
        else:
            start_date_value = datetime.now().date()
    except (ValueError, TypeError):
        start_date_value = datetime.now().date()
    
    with st.form("contract_form"):
        st.subheader("Contract Details")
        
        # Two column layout for form
        col1, col2 = st.columns(2)
        with col1:
            provider = st.text_input(
                "Provider Name*", 
                value=form_data.get('provider_name', ''),
                placeholder="e.g., John Hancock"
            )
            
            contract_num = st.text_input(
                "Contract Number", 
                value=form_data.get('contract_number', ''),
                placeholder="Optional"
            )
            
            start_date = st.date_input(
                "Start Date*",
                value=start_date_value,
                format="YYYY-MM-DD"
            )
        
        with col2:
            fee_type = st.selectbox(
                "Fee Type*",
                options=['percentage', 'flat'],
                index=0 if not form_data or form_data.get('fee_type') == 'percentage' else 1
            )
            
            if fee_type == 'percentage':
                rate = st.number_input(
                    "Rate (%)*",
                    value=float(form_data.get('percent_rate', 0) * 100) if form_data.get('percent_rate') else 0.0,
                    format="%.4f",
                    step=0.0001,
                    help="Enter percentage as decimal (e.g., 0.75 for 0.75%)"
                )
            else:
                rate = st.number_input(
                    "Flat Rate ($)*",
                    value=float(form_data.get('flat_rate', 0)) if form_data.get('flat_rate') else 0.0,
                    format="%.2f",
                    step=100.0,
                    help="Enter dollar amount"
                )
            
            schedule = st.selectbox(
                "Payment Schedule*",
                options=['monthly', 'quarterly'],
                index=0 if not form_data or form_data.get('payment_schedule') == 'monthly' else 1
            )
            
            participants = st.number_input(
                "Number of Participants",
                value=int(form_data.get('num_people', 0)) if form_data.get('num_people') else 0,
                min_value=0,
                step=1
            )
        
        notes = st.text_area(
            "Notes",
            value=form_data.get('notes', ''),
            placeholder="Add any additional contract information here"
        )
        
        # Show validation errors if any
        if ui_manager.contract_dialog_has_errors:
            for error in ui_manager.contract_validation_errors:
                st.error(error)
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button(
                "Save Changes" if mode == 'edit' else "Create Contract",
                type="primary",
                use_container_width=True
            )
        with col2:
            cancel = st.form_submit_button(
                "Cancel",
                type="secondary",
                use_container_width=True
            )
        
        if submit:
            # Validate form
            errors = []
            if not provider:
                errors.append("Provider Name is required")
            if not start_date:
                errors.append("Start Date is required")
            if rate <= 0:
                errors.append("Rate must be greater than 0")
            
            if errors:
                ui_manager.set_contract_validation_errors(errors)
                return
            
            # Format data for database
            new_data = {
                'client_id': client_id,
                'provider_name': provider,
                'contract_number': contract_num if contract_num else None,
                'contract_start_date': start_date.strftime('%Y-%m-%d'),
                'fee_type': fee_type,
                'percent_rate': rate/100 if fee_type == 'percentage' else None,
                'flat_rate': rate if fee_type == 'flat' else None,
                'payment_schedule': schedule,
                'num_people': participants if participants > 0 else None,
                'notes': notes if notes else None
            }
            
            # Add contract_id if editing
            if mode == 'edit' and 'contract_id' in form_data:
                new_data['contract_id'] = form_data['contract_id']
            
            # Save to database
            if save_contract(client_id, new_data, mode):
                ui_manager.close_contract_dialog()
                st.rerun()
            else:
                ui_manager.set_contract_validation_errors(["Failed to save contract. Please try again."])
                return
            
        if cancel:
            if has_unsaved_changes(form_data, ui_manager.contract_form_data):
                st.warning("You have unsaved changes. Are you sure you want to cancel?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Discard Changes", use_container_width=True):
                        ui_manager.close_contract_dialog()
                        st.rerun()
                with col2:
                    st.button("No, Keep Editing", use_container_width=True)
            else:
                ui_manager.close_contract_dialog()
                st.rerun()

def has_unsaved_changes(original: Dict[str, Any], current: Dict[str, Any]) -> bool:
    """Check if there are unsaved changes in the form."""
    if not original:
        return bool(current)
    
    # Compare only form fields
    form_fields = [
        'provider_name', 'contract_number', 'contract_start_date',
        'fee_type', 'percent_rate', 'flat_rate', 'payment_schedule',
        'num_people', 'notes'
    ]
    
    return any(
        original.get(field) != current.get(field)
        for field in form_fields
        if field in original or field in current
    )