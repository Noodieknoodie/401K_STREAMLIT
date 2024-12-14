import streamlit as st
from utils.utils import get_clients
from utils.debug_logger import debug

def reset_client_state():
    """Reset client-related state when client changes."""
    debug.log_ui_interaction(
        action="reset_client_state",
        element="client_selection",
        data={
            "cleared_states": [
                "payment_data",
                "payment_offset",
                "current_year",
                "current_quarter"
            ]
        }
    )
    
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
    
    # Client selector
    clients = get_clients()
    client_options = ["Select a client..."] + [client[1] for client in clients]
    
    previous_selection = st.session_state.get("client_selector_dashboard")
    
    selected_client_name = st.selectbox(
        "🔍 Search or select a client",
        options=client_options,
        key="client_selector_dashboard",
        label_visibility="collapsed"
    )
    
    if selected_client_name == "Select a client...":
        if previous_selection and previous_selection != "Select a client...":
            debug.log_ui_interaction(
                action="client_deselected",
                element="client_selector",
                data={"previous_client": previous_selection}
            )
        return None, None
        
    # Reset data when client changes
    if st.session_state.previous_client != selected_client_name:
        debug.log_ui_interaction(
            action="client_changed",
            element="client_selector",
            data={
                "previous_client": st.session_state.previous_client,
                "new_client": selected_client_name
            }
        )
        reset_client_state()
        st.session_state.previous_client = selected_client_name
    
    client_id = next(
        client[0] for client in clients if client[1] == selected_client_name
    )
    
    debug.log_ui_interaction(
        action="client_selected",
        element="client_selector",
        data={
            "client_id": client_id,
            "client_name": selected_client_name
        }
    )
    
    return client_id, selected_client_name