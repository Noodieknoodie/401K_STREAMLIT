# pages\client_dashboard\client_selection.py

import streamlit as st
from utils.utils import get_clients

def reset_client_state():
    """Reset client-related state when client changes."""
    old_state = {
        'payment_data': st.session_state.get('payment_data', []),
        'payment_offset': st.session_state.get('payment_offset', 0),
        'current_year': st.session_state.get('current_year'),
        'current_quarter': st.session_state.get('current_quarter')
    }
    
    st.session_state.payment_data = []
    st.session_state.payment_offset = 0
    if 'current_year' in st.session_state:
        del st.session_state.current_year
    if 'current_quarter' in st.session_state:
        del st.session_state.current_quarter

def get_selected_client():
    """Handle client selection and return client info if selected."""
    if 'previous_client' not in st.session_state:
        st.session_state.previous_client = None
    
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
            # Client selector
            clients = get_clients()
            client_options = ["Select a client..."] + [client[1] for client in clients]
            selected_client_name = st.selectbox(
                "🔍 Search or select a client",
                options=client_options,
                key="client_selector_dashboard",
                label_visibility="collapsed"
            )
        
        with col2:
            if selected_client_name != "Select a client...":
                if st.button("✏️", key="edit_contract", help="Manage Contract", use_container_width=True):
                    if 'ui_manager' in st.session_state:
                        client_id = next(
                            client[0] for client in clients if client[1] == selected_client_name
                        )
                        ui_manager = st.session_state.ui_manager
                        ui_manager.open_contract_dialog(client_id=client_id)
                        st.rerun()
    
    if selected_client_name == "Select a client...":
        return None, None
        
    # Reset data when client changes
    if st.session_state.previous_client != selected_client_name:
        reset_client_state()
        st.session_state.previous_client = selected_client_name
    
    client_id = next(
        client[0] for client in clients if client[1] == selected_client_name
    )
    
    return client_id, selected_client_name
