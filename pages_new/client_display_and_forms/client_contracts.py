"""
Contract Management Module
========================

This module handles contract management for the 401K Payment Tracker application.
It provides functionality for creating, editing, and viewing client contracts with
specific validation and display requirements.

Key Components & Behaviors to Verify:
-----------------------------------

1. Contract Form Requirements:
   - Provider name is required
   - Fee type must be percentage or flat
   - Rate must be valid for selected fee type
   - Payment schedule (monthly/quarterly) is required
   - Start date must be valid
   - Contract number is optional
   - Notes are optional

2. Contract Display:
   - Form appears above metrics when editing
   - Previous contracts in expandable section
   - Clear fee type and rate display
   - Proper date formatting
   - Schedule display (Monthly/Quarterly)

3. State Management:
   - Form state resets after submission
   - Edit mode preserves existing data
   - Validation errors shown clearly
   - Cancel confirmation if needed

4. Data Validation Rules:
   - Provider name cannot be empty
   - Rate must be > 0
   - Percentage rate must be valid percentage
   - Flat rate must be valid currency
   - Start date cannot be in future

5. Common Issues to Check:
   - Form should never submit with invalid data
   - Rate formatting should handle edge cases
   - Cancel should prompt if changes made
   - Edit should load all fields correctly

Database Schema Dependencies:
---------------------------
contracts table:
- contract_id (primary key)
- client_id (foreign key to clients)
- is_active (boolean)
- contract_number (text, optional)
- provider_name (text)
- fee_type (text: 'percentage' or 'flat')
- percent_rate (decimal, null if flat)
- flat_rate (decimal, null if percentage)
- payment_schedule (text: 'monthly' or 'quarterly')
- start_date (date)
- num_participants (integer)
- notes (text, optional)

Required Functions:
-----------------
From utils.py:
- get_active_contract: Get current active contract
- get_client_contracts: Get all contracts for client
- save_contract: Save new/updated contract
- validate_contract_data: Validate form data
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from utils.client_data import (
    get_active_contract_optimized as get_active_contract
)
from utils.utils import (
    validate_contract_data,
    get_client_contracts,
    save_contract,
    format_currency_ui,
    format_currency_db,
    get_database_connection
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


def init_contract_state():
    """Initialize contract-related session state variables."""
    if 'show_contract_form' not in st.session_state:
        st.session_state.show_contract_form = False
    
    if 'contract_form_data' not in st.session_state:
        st.session_state.contract_form_data = {
            'provider_name': '',
            'contract_number': '',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'fee_type': 'percentage',
            'percent_rate': None,
            'flat_rate': None,
            'payment_schedule': 'monthly',
            'num_people': 0,
            'notes': '',
            'mode': 'add'  # or 'edit'
        }
    
    if 'contract_edit_id' not in st.session_state:
        st.session_state.contract_edit_id = None
    
    if 'contract_validation_errors' not in st.session_state:
        st.session_state.contract_validation_errors = []
    
    if 'show_contract_history' not in st.session_state:
        st.session_state.show_contract_history = False

def reset_contract_form():
    """Reset the contract form to its initial state."""
    st.session_state.contract_form_data = {
        'provider_name': '',
        'contract_number': '',
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'fee_type': 'percentage',
        'percent_rate': None,
        'flat_rate': None,
        'payment_schedule': 'monthly',
        'num_people': 0,
        'notes': '',
        'mode': 'add'
    }
    st.session_state.contract_edit_id = None
    st.session_state.show_contract_form = False
    st.session_state.contract_validation_errors = []

def show_contract_form(client_id: int):
    """Display the contract form for adding/editing contracts."""
    # Container to ensure form appears above metrics
    with st.container():
        with st.form("contract_form", clear_on_submit=False):
            st.subheader("Edit Contract" if st.session_state.contract_edit_id else "Add Contract")
            
            # Contract form layout
            col1, col2 = st.columns(2)
            with col1:
                provider = st.text_input(
                    "Provider Name*",
                    value=st.session_state.contract_form_data.get('provider_name', ''),
                    placeholder="e.g., John Hancock"
                )
                
                contract_num = st.text_input(
                    "Contract Number",
                    value=st.session_state.contract_form_data.get('contract_number', ''),
                    placeholder="Optional"
                )
                
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.strptime(st.session_state.contract_form_data.get('start_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
                    format="YYYY-MM-DD"
                )
            
            with col2:
                fee_type = st.selectbox(
                    "Fee Type*",
                    options=['percentage', 'flat'],
                    index=0 if st.session_state.contract_form_data.get('fee_type', '') != 'flat' else 1
                )
                
                if fee_type == 'percentage':
                    rate = st.number_input(
                        "Rate (%)*",
                        value=float(st.session_state.contract_form_data.get('percent_rate', 0) * 100) if st.session_state.contract_form_data.get('percent_rate') else 0.0,
                        format="%.4f",
                        step=0.0001,
                        help="Enter percentage as decimal (e.g., 0.75 for 0.75%)"
                    )
                    rate_value = rate / 100
                    st.session_state.contract_form_data['percent_rate'] = rate_value
                    st.session_state.contract_form_data['flat_rate'] = None
                else:
                    rate = st.number_input(
                        "Flat Rate ($)*",
                        value=float(st.session_state.contract_form_data.get('flat_rate', 0)) if st.session_state.contract_form_data.get('flat_rate') else 0.0,
                        format="%.2f",
                        step=100.0,
                        help="Enter dollar amount"
                    )
                    rate_value = rate
                    st.session_state.contract_form_data['flat_rate'] = rate_value
                    st.session_state.contract_form_data['percent_rate'] = None
                
                schedule = st.selectbox(
                    "Payment Schedule*",
                    options=['monthly', 'quarterly'],
                    index=0 if st.session_state.contract_form_data.get('payment_schedule', '') != 'quarterly' else 1
                )
                
                participants = st.number_input(
                    "Number of Participants",
                    value=int(st.session_state.contract_form_data.get('num_people', 0)) if st.session_state.contract_form_data.get('num_people') else 0,
                    min_value=0,
                    step=1
                )
            
            notes = st.text_area(
                "Notes",
                value=st.session_state.contract_form_data.get('notes', ''),
                placeholder="Add any additional contract information here"
            )
            
            # Update form data
            updated_data = {
                'provider_name': provider,
                'contract_number': contract_num,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'fee_type': fee_type,
                'percent_rate': st.session_state.contract_form_data.get('percent_rate'),
                'flat_rate': st.session_state.contract_form_data.get('flat_rate'),
                'payment_schedule': schedule,
                'num_people': participants,
                'notes': notes,
                'mode': 'edit' if st.session_state.contract_edit_id else 'add'
            }
            st.session_state.contract_form_data = updated_data
            
            # Show validation errors
            if st.session_state.contract_validation_errors:
                for error in st.session_state.contract_validation_errors:
                    st.error(error)
            
            # Form buttons
            col1, col2 = st.columns(2)
            with col1:
                submit_label = "Update Contract" if st.session_state.contract_edit_id else "Create Contract"
                if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                    errors = validate_contract_data(updated_data)
                    if errors:
                        st.session_state.contract_validation_errors = errors
                        st.rerun()
                    else:
                        if st.session_state.contract_form_data['mode'] == 'add':
                            # Confirm deactivating current contract
                            if 'confirm_new_contract' not in st.session_state:
                                st.session_state.confirm_new_contract = True
                                st.rerun()
                            elif st.session_state.confirm_new_contract:
                                if save_contract(client_id, updated_data, 'add'):
                                    st.success("New contract created successfully!")
                                    reset_contract_form()
                                    st.rerun()
                                else:
                                    st.error("Failed to save contract. Please try again.")
                        else:
                            if save_contract(client_id, updated_data, 'edit'):
                                st.success("Contract updated successfully!")
                                reset_contract_form()
                                st.rerun()
                            else:
                                st.error("Failed to save contract. Please try again.")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    reset_contract_form()
                    st.rerun()

def show_contract_history(client_id: int):
    """Display the contract history in an expander."""
    with st.expander("View Contract History", expanded=st.session_state.show_contract_history):
        inactive_contracts = get_client_contracts(client_id)
        if inactive_contracts:
            for contract in inactive_contracts:
                if not contract[2]:  # not active
                    with st.container():
                        # Contract header
                        st.markdown(f"""
                            <div style='padding: 0.5em 0;'>
                                <strong>{contract[1]}</strong> • {contract[3] or 'No start date'}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Contract details
                        cols = st.columns([2, 2, 2])
                        with cols[0]:
                            st.text(f"Contract #: {contract[2] or 'N/A'}")
                        with cols[1]:
                            st.text(f"Schedule: {contract[3].title() if contract[3] else 'N/A'}")
                        with cols[2]:
                            rate_display = (
                                f"{contract[5]*100:.3f}%" if contract[5]
                                else f"${contract[6]:,.2f}" if contract[6]
                                else "N/A"
                            )
                            st.text(f"{contract[4].title() if contract[4] else 'N/A'} Rate: {rate_display}")
                        
                        if contract[8]:  # notes
                            st.caption(contract[8])
                        st.divider()
        else:
            st.info("No previous contracts found.")

def display_contracts_section(client_id: int):
    """Main entry point for contract management."""
    init_contract_state()
    
    # Load active contract data when editing
    if st.session_state.show_contract_form and not st.session_state.contract_form_data.get('loaded_data'):
        active_contract = get_active_contract(client_id)
        if active_contract:
            st.session_state.contract_edit_id = active_contract[0]  # contract_id
            st.session_state.contract_form_data = {
                'provider_name': active_contract[1],  # provider_name
                'contract_number': active_contract[2],  # contract_number
                'payment_schedule': active_contract[3],  # payment_schedule
                'fee_type': active_contract[4],  # fee_type
                'percent_rate': active_contract[5],  # percent_rate
                'flat_rate': active_contract[6],  # flat_rate
                'num_people': active_contract[7],  # num_people
                'loaded_data': True,
                'mode': 'edit'
            }
    
    # Show contract form
    show_contract_form(client_id)
    
    # Show contract history
    show_contract_history(client_id)

if __name__ == "__main__":
    st.set_page_config(page_title="Client Contracts", layout="wide")
    # For testing
    display_contracts_section(1)
