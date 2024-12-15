import streamlit as st
from utils.utils import get_clients
from utils.debug_logger import get_debug_logger

# Initialize debug logger
debug = get_debug_logger()

def reset_client_state():
    """Reset client-related state when client changes."""
    debug.log_ui_interaction(
        action='reset_state',
        element='client_state',
        data={'resetting': True}
    )
    
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
        
    debug.log_state_change(
        component='client_state',
        old_value=old_state,
        new_value={
            'payment_data': [],
            'payment_offset': 0,
            'current_year': None,
            'current_quarter': None
        },
        context={'action': 'reset'}
    )

def get_selected_client():
    """Handle client selection and return client info if selected."""
    debug.log_ui_interaction(
        action='init_client_selection',
        element='client_selector',
        data={'initializing': True}
    )
    
    if 'previous_client' not in st.session_state:
        st.session_state.previous_client = None
        debug.log_state_change(
            component='previous_client',
            old_value=None,
            new_value=None,
            context={'initialization': True}
        )
    
    # Client selector
    clients = get_clients()
    debug.log_db_operation(
        operation='fetch',
        table='clients',
        data={},
        result={'client_count': len(clients) if clients else 0}
    )
    
    client_options = ["Select a client..."] + [client[1] for client in clients]
    selected_client_name = st.selectbox(
        "🔍 Search or select a client",
        options=client_options,
        key="client_selector_dashboard",
        label_visibility="collapsed"
    )
    
    debug.log_ui_interaction(
        action='select_client',
        element='client_dropdown',
        data={'selected': selected_client_name}
    )
    
    if selected_client_name == "Select a client...":
        debug.log_ui_interaction(
            action='client_selection',
            element='client_selector',
            data={'status': 'no_selection'}
        )
        return None, None
        
    # Reset data when client changes
    if st.session_state.previous_client != selected_client_name:
        debug.log_state_change(
            component='client_selection',
            old_value=st.session_state.previous_client,
            new_value=selected_client_name,
            context={'client_changed': True}
        )
        reset_client_state()
        st.session_state.previous_client = selected_client_name
    
    client_id = next(
        client[0] for client in clients if client[1] == selected_client_name
    )
    
    debug.log_ui_interaction(
        action='client_selection',
        element='client_selector',
        data={
            'client_id': client_id,
            'client_name': selected_client_name,
            'status': 'selected'
        }
    )
    
    return client_id, selected_client_name