import streamlit as st
from utils.utils import (
    add_client, update_client, delete_client,
    get_clients, get_client_details,
    get_database_connection
)
from datetime import datetime
import os

def get_full_client_details(client_id: int):
    """Get all client details from database"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT display_name, full_name, ima_signed_date,
                   file_path_account_documentation,
                   file_path_consulting_fees,
                   file_path_meetings
            FROM clients 
            WHERE client_id = ?
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def show_manage_clients():
    """Main client management interface"""
    st.title("👥 Manage Clients")
    
    # Initialize session state for selected client
    if "selected_client" not in st.session_state:
        st.session_state.selected_client = None
    
    tab1, tab2 = st.tabs(["View/Edit Clients", "Add New Client"])
    
    with tab1:
        col_main, col_edit = st.columns([2, 1])
        
        with col_main:
            show_client_list()
        
        # Show edit form in second column when client is selected
        with col_edit:
            if st.session_state.selected_client:
                show_edit_form(st.session_state.selected_client)
    
    with tab2:
        show_add_client_form()

def show_client_list():
    """Display clients in a clean table format"""
    # Search box at top
    search = st.text_input("🔍 Search Clients", key="client_search").lower()
    
    # Get and filter clients
    clients = get_clients()
    filtered = [c for c in clients if search in c[1].lower()]
    
    if not filtered:
        st.info("No clients found")
        return
    
    # Create table header
    st.write("---")
    cols = st.columns([3, 3, 1, 1])  # Split actions into two columns directly
    with cols[0]:
        st.write("**Display Name**")
    with cols[1]:
        st.write("**Full Name**")
    with cols[2]:
        st.write("**Edit**")
    with cols[3]:
        st.write("**Delete**")
    st.write("---")
    
    # List clients
    for client_id, display_name in filtered:
        cols = st.columns([3, 3, 1, 1])  # Match header columns
        details = get_client_details(client_id)
        
        with cols[0]:
            st.write(display_name)
        with cols[1]:
            st.write(details[1] if details and details[1] else "—")
        with cols[2]:
            if st.button("✏️", key=f"edit_{client_id}"):
                st.session_state.selected_client = client_id
        with cols[3]:
            if st.button("🗑️", key=f"del_{client_id}"):
                st.session_state[f"confirm_delete_{client_id}"] = True
            
            # Show confirm button if delete was clicked
            if st.session_state.get(f"confirm_delete_{client_id}"):
                if st.button("✓", key=f"confirm_{client_id}"):
                    if delete_client(client_id):
                        st.rerun()
        st.write("---")

def show_edit_form(client_id: int):
    """Show edit form for selected client"""
    details = get_full_client_details(client_id)
    if not details:
        st.error("Client not found")
        return
    
    st.header(f"Edit: {details[0]}")
    
    with st.form(key=f"edit_client_{client_id}"):
        display_name = st.text_input("Display Name*", 
                                   value=details[0])
        full_name = st.text_input("Full Name", 
                                 value=details[1] if details[1] else "")
        
        # Handle IMA date
        current_date = None
        if details[2]:
            try:
                current_date = datetime.strptime(details[2], '%Y-%m-%d').date()
            except:
                pass
        ima_date = st.date_input("IMA Signed Date", 
                                value=current_date)
        
        # Document paths
        st.write("### Document Folders")
        docs_path = st.text_input("Account Documentation", 
                                 value=details[3] if details[3] else "")
        fees_path = st.text_input("Consulting Fees", 
                                 value=details[4] if details[4] else "")
        meetings_path = st.text_input("Meetings", 
                                    value=details[5] if details[5] else "")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("Save"):
                if not display_name:
                    st.error("Display Name is required")
                    return
                
                if update_client(
                    client_id,
                    display_name=display_name,
                    full_name=full_name,
                    ima_signed_date=ima_date.strftime('%Y-%m-%d') if ima_date else None,
                    file_path_account_documentation=docs_path,
                    file_path_consulting_fees=fees_path,
                    file_path_meetings=meetings_path
                ):
                    st.session_state.selected_client = None
                    st.success("Updated successfully!")
                    st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.selected_client = None
                st.rerun()

def show_add_client_form():
    """Form for adding new clients"""
    with st.form("add_client"):
        st.subheader("Add New Client")
        
        display_name = st.text_input("Display Name*", 
                                   placeholder="Required")
        full_name = st.text_input("Full Name", 
                                 placeholder="Optional")
        ima_date = st.date_input("IMA Signed Date", 
                                value=None)
        
        st.write("### Document Folders")
        docs_path = st.text_input("Account Documentation", 
                                 placeholder="Optional")
        fees_path = st.text_input("Consulting Fees", 
                                 placeholder="Optional")
        meetings_path = st.text_input("Meetings", 
                                    placeholder="Optional")
        
        if st.form_submit_button("Add Client"):
            if not display_name:
                st.error("Display Name is required")
                return
            
            client_id = add_client(
                display_name=display_name,
                full_name=full_name,
                ima_signed_date=ima_date.strftime('%Y-%m-%d') if ima_date else None,
                file_path_account_documentation=docs_path,
                file_path_consulting_fees=fees_path,
                file_path_meetings=meetings_path
            )
            
            if client_id:
                st.success("Client added successfully!")
                st.rerun()