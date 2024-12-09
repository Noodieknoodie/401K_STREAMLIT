import streamlit as st
from utils.utils import get_clients
from .state_management import ClientState

def get_selected_client():
    """Handle client selection and return client info if selected."""
    # Initialize client state
    ClientState.initialize()
    
    # Client selector
    clients = get_clients()
    client_options = ["Select a client..."] + [client[1] for client in clients]
    selected_client_name = st.selectbox(
        "🔍 Search or select a client",
        options=client_options,
        key="client_selector_dashboard",
        label_visibility="collapsed"
    )
    
    if selected_client_name == "Select a client...":
        return None, None
        
    # Set client and handle state resets
    client_id = next(
        client[0] for client in clients if client[1] == selected_client_name
    )
    ClientState.set_client(client_id, selected_client_name)
    
    return client_id, selected_client_name