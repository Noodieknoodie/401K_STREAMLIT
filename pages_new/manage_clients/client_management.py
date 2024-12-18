import streamlit as st
from ..client_display_and_forms.client_contacts import display_contacts_section

def show_manage_clients():
    st.title("⚙️ Manage Clients")
    display_contacts_section(None)  # Pass None as client_id for manage clients view 