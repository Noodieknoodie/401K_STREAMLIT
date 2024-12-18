# pages\client_dashboard\client_dashboard.py

"""
Client Dashboard Module
=====================

This module serves as the main dashboard for the 401K Payment Tracker application.
It integrates all client management components into a cohesive interface while
maintaining the legacy layout and UX patterns but with modern state management.

Key Components:
-------------
1. Client Selection - Top bar with search/select
2. Metrics Display - Card layout showing key metrics
3. Contacts Section - Three-column layout with forms
4. Contracts Section - Active contract and history
5. Payments Section - Payment history with forms

State Management:
---------------
Each section manages its own state using st.session_state:
- Form visibility
- Edit/delete states
- Filter states
- Validation states
"""

import streamlit as st
from typing import Optional, Tuple
import time

from utils.utils import get_clients
from .client_display_and_forms.client_metrics import show_client_metrics
from .client_display_and_forms.client_contacts import display_contacts_section
from .client_display_and_forms.client_contracts import display_contracts_section
from .client_display_and_forms.client_payments import display_payments_section

def init_dashboard_state():
    """Initialize dashboard-wide session state."""
    if 'client_selector_dashboard' not in st.session_state:
        st.session_state.client_selector_dashboard = None
    if 'previous_client' not in st.session_state:
        st.session_state.previous_client = None
    if 'show_contract_form' not in st.session_state:
        st.session_state.show_contract_form = False
    if 'contract_form_data' not in st.session_state:
        st.session_state.contract_form_data = {}
    if 'contract_edit_id' not in st.session_state:
        st.session_state.contract_edit_id = None
    if 'contract_validation_errors' not in st.session_state:
        st.session_state.contract_validation_errors = []
    if 'show_contract_history' not in st.session_state:
        st.session_state.show_contract_history = False

def get_selected_client() -> Optional[Tuple]:
    """Get the currently selected client from the dropdown.
    
    Returns:
        Optional[Tuple]: Selected client data or None if no selection
    """
    # Client selector with edit button container
    st.markdown("""
        <style>
        .client-select-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .client-select-container > div {
            flex: 1;
        }
        .edit-contract-button {
            margin-top: -1rem;  /* Align with dropdown */
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([6, 1])
        
        with col1:
            # Get client list
            clients = get_clients()
            if not clients:
                st.error("No clients found in the database")
                return None
            
            # Create selection box
            client_names = ["Select a client..."] + [client[1] for client in clients]
            selected_name = st.selectbox(
                "🔍 Search or select a client",
                options=client_names,
                key='client_selector_dashboard',
                label_visibility="collapsed"
            )
        
        with col2:
            if selected_name != "Select a client...":
                if st.button("✏️", key="edit_contract", help="Manage Contract", use_container_width=True):
                    # Show contract form
                    client_id = next(
                        client[0] for client in clients if client[1] == selected_name
                    )
                    st.session_state.show_contract_form = True
                    st.session_state.contract_client_id = client_id
                    st.rerun()
    
    if selected_name == "Select a client...":
        return None
        
    # Reset data when client changes
    if st.session_state.previous_client != selected_name:
        st.session_state.previous_client = selected_name
        # Each section handles its own state reset
    
    # Get selected client data
    return next(
        (client for client in clients if client[1] == selected_name),
        None
    )

def display_client_dashboard():
    """Main dashboard display function."""
    start_time = time.time()
    
    # Initialize dashboard state
    init_dashboard_state()
    
    st.title("👥 Client Dashboard")
    
    # Get selected client (this needs to run always)
    selected_client = get_selected_client()
    if not selected_client:
        st.info("Please select a client to view their dashboard")
        return
    
    client_id = selected_client[0]
    
    # Show contract form above metrics if editing
    if st.session_state.show_contract_form:
        display_contracts_section(client_id)
    
    # Show dashboard components vertically
    show_client_metrics(client_id)
    
    # Add spacing between sections
    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
    
    # Contacts Section
    display_contacts_section(client_id)
    
    # Add spacing between sections
    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
    
    # Payments Section
    display_payments_section(client_id)
    
    # Log performance metrics
    end_time = time.time()
    load_time = end_time - start_time
    st.session_state.last_load_time = load_time

def show_client_dashboard():
    """Wrapper for display_client_dashboard to maintain backward compatibility with app.py"""
    display_client_dashboard()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Client Dashboard",
        page_icon="👥",
        layout="wide"
    )
    display_client_dashboard()

