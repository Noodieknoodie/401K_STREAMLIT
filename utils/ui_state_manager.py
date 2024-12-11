import streamlit as st

class UIStateManager:
    """
    Central manager for form visibility and UI element coordination.
    This manager ensures that interactive elements don't conflict with each other.
    
    Rules:
    1. Only ONE form can be visible at a time
    2. Forms must close when other interactive elements need focus
    3. Never modify st.session_state form values directly
    
    Usage:
    ui_manager = UIStateManager()
    ui_manager.show_payment_form()  # Shows payment form, closes others
    ui_manager.show_contact_form()  # Shows contact form, closes others
    ui_manager.close_all()          # Closes all managed elements
    """
    
    def __init__(self):
        """Initialize the UI state manager if it doesn't exist"""
        if 'ui_state' not in st.session_state:
            st.session_state.ui_state = {
                'active_element': None,  # Only one element can be active
                'payment_form': {'is_visible': False},
                'contact_form': {'is_open': False}
            }
    
    def close_all(self):
        """Close all managed UI elements"""
        state = st.session_state.ui_state
        state['active_element'] = None
        state['payment_form']['is_visible'] = False
        state['contact_form']['is_open'] = False
        
        # Sync with legacy states for backward compatibility
        if 'payment_form' in st.session_state:
            st.session_state.payment_form['is_visible'] = False
        if 'contact_form' in st.session_state:
            st.session_state.contact_form['is_open'] = False
    
    def show_payment_form(self):
        """Exclusively show payment form"""
        self.close_all()
        state = st.session_state.ui_state
        state['active_element'] = 'payment_form'
        state['payment_form']['is_visible'] = True
        # Sync with legacy state
        if 'payment_form' in st.session_state:
            st.session_state.payment_form['is_visible'] = True
    
    def show_contact_form(self):
        """Exclusively show contact form"""
        self.close_all()
        state = st.session_state.ui_state
        state['active_element'] = 'contact_form'
        state['contact_form']['is_open'] = True
        # Sync with legacy state
        if 'contact_form' in st.session_state:
            st.session_state.contact_form['is_open'] = True
    
    @property
    def active_element(self):
        """Get the currently active UI element"""
        return st.session_state.ui_state['active_element']
    
    @property
    def is_payment_form_visible(self):
        """Check if payment form is visible"""
        return st.session_state.ui_state['payment_form']['is_visible']
    
    @property
    def is_contact_form_open(self):
        """Check if contact form is open"""
        return st.session_state.ui_state['contact_form']['is_open'] 