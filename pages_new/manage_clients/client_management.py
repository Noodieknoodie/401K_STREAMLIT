# client_management.py
import streamlit as st
from utils.utils import (
   add_client,
   update_client,
   delete_client,
   get_clients,
   get_client_details,
   get_database_connection,
   validate_shared_path,
   normalize_shared_path,
   reconstruct_full_path
)
from datetime import datetime
import os
import time

def get_full_client_details(client_id: int):
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
   st.title("👥 Manage Clients")
   
   if "selected_client" not in st.session_state:
       st.session_state.selected_client = None

   st.markdown("""
       <style>
       .stButton>button {
           height: 2.4rem;
       }
       div[data-testid="column"] {
           padding: 0px 0.5rem;
       }
       </style>
   """, unsafe_allow_html=True)
       
   col_main, col_form = st.columns([2, 1], gap="large")
   
   with col_main:
       search_col, add_col = st.columns([3, 1])
       with search_col:
           search = st.text_input("🔍", 
                                placeholder="Search clients...", 
                                label_visibility="collapsed",
                                key="client_search")
       with add_col:
           if st.button("➕ Add Client", type="primary", use_container_width=True):
               st.session_state.selected_client = "new"
               st.rerun()

       with st.container(border=True):
           show_client_list(search.lower() if search else "")

   with col_form:
       with st.container(border=True):
           if st.session_state.selected_client == "new":
               show_client_form("add")
           elif st.session_state.selected_client:
               show_client_form("edit", st.session_state.selected_client)
           else:
               st.info("Select a client to edit or click 'Add Client' to create one.")

def show_client_list(search: str):
   clients = get_clients()
   filtered = [c for c in clients if search in c[1].lower()]
   
   total = len(clients)
   filtered_count = len(filtered)
   
   st.caption(f"Found {filtered_count} of {total} clients" if search else f"Total Clients: {total}")
   
   if not filtered:
       st.info("No clients found" if search else "No clients added yet")
       return

   # Generate a unique session ID if not exists
   if 'session_id' not in st.session_state:
       st.session_state.session_id = int(time.time() * 1000)

   for idx, (client_id, display_name) in enumerate(filtered):
       with st.container():
           # Use session_id in the key to make it unique across sessions
           is_deleting = st.session_state.get(f"confirm_delete_{client_id}_{st.session_state.session_id}", False)
           
           if is_deleting:
               with st.container(border=True):
                   st.error(f"⚠️ Delete {display_name}?")
                   st.caption("This action cannot be undone")
                   col1, col2 = st.columns(2)
                   with col1:
                       if st.button("✓ Confirm", 
                                  key=f"confirm_{client_id}_{idx}_{st.session_state.session_id}", 
                                  type="primary", 
                                  use_container_width=True):
                           if delete_client(client_id):
                               st.rerun()
                   with col2:
                       if st.button("✗ Cancel", 
                                  key=f"cancel_{client_id}_{idx}_{st.session_state.session_id}", 
                                  use_container_width=True):
                           del st.session_state[f"confirm_delete_{client_id}_{st.session_state.session_id}"]
                           
           details = get_full_client_details(client_id)
           col_name, col_full, col_edit, col_del = st.columns([2, 4, 0.8, 0.8])
           
           with col_name:
               st.write(display_name)
           with col_full:
               st.write(details[1] if details and details[1] else "—")
           with col_edit:
               if st.button("✏️", 
                          key=f"edit_{client_id}_{idx}_{st.session_state.session_id}", 
                          use_container_width=True):
                   st.session_state.selected_client = client_id
                   st.rerun()
           with col_del:
               if st.button("🗑️", 
                          key=f"del_{client_id}_{idx}_{st.session_state.session_id}", 
                          use_container_width=True):
                   st.session_state[f"confirm_delete_{client_id}_{st.session_state.session_id}"] = True
                   st.rerun()
           st.divider()

def show_client_form(mode="add", client_id=None):
   client_data = get_full_client_details(client_id) if mode == "edit" and client_id else None
   
   # Generate a unique form key using session_id
   if 'session_id' not in st.session_state:
       st.session_state.session_id = int(time.time() * 1000)
   form_key = f"client_form_{mode}_{st.session_state.session_id}"
   
   with st.form(form_key, clear_on_submit=True):
       st.write("✨ New Client" if mode == "add" else f"✏️ Edit Client: {client_data[0]}" if client_data else "✏️ Edit Client")
       
       col1, col2 = st.columns([1,1])
       with col1:
           display_name = st.text_input("Display Name*", 
                                      value=client_data[0] if client_data else "",
                                      placeholder="Required")
       with col2:
           full_name = st.text_input("Full Name", 
                                   value=client_data[1] if client_data else "",
                                   placeholder="Optional")
       
       ima_date = st.date_input("IMA Signed Date",
                               value=datetime.strptime(client_data[2], '%Y-%m-%d').date() 
                               if client_data and client_data[2] else None)

       st.write("📁 Document Folders")
       st.caption("Paste full path from OneDrive or use relative path from 'Hohimer Wealth Management'")
       
       # Get current paths for validation messages
       current_paths = {
           'docs': client_data[3] if client_data else None,
           'fees': client_data[4] if client_data else None,
           'meetings': client_data[5] if client_data else None
       }
       
       # Documentation path
       docs_col1, docs_col2 = st.columns([3, 1])
       with docs_col1:
           docs_path = st.text_input(
               "Account Documentation", 
               value=current_paths['docs'] if current_paths['docs'] else "",
               placeholder="Current Plans/Client Name/Documentation"
           )
       with docs_col2:
           if docs_path:
               is_valid, error_msg = validate_shared_path(docs_path)
               if is_valid:
                   st.success("✓ Valid path")
               else:
                   st.error("⚠ " + error_msg)
       
       # Fees path
       fees_col1, fees_col2 = st.columns([3, 1])
       with fees_col1:
           fees_path = st.text_input(
               "Consulting Fees",
               value=current_paths['fees'] if current_paths['fees'] else "",
               placeholder="Current Plans/Client Name/Fees"
           )
       with fees_col2:
           if fees_path:
               is_valid, error_msg = validate_shared_path(fees_path)
               if is_valid:
                   st.success("✓ Valid path")
               else:
                   st.error("⚠ " + error_msg)
       
       # Meetings path
       meetings_col1, meetings_col2 = st.columns([3, 1])
       with meetings_col1:
           meetings_path = st.text_input(
               "Meetings",
               value=current_paths['meetings'] if current_paths['meetings'] else "",
               placeholder="Current Plans/Client Name/Meetings"
           )
       with meetings_col2:
           if meetings_path:
               is_valid, error_msg = validate_shared_path(meetings_path)
               if is_valid:
                   st.success("✓ Valid path")
               else:
                   st.error("⚠ " + error_msg)

       col1, col2 = st.columns(2)
       with col1:
           submitted = st.form_submit_button(
               "Save Changes" if mode == "edit" else "Add Client",
               type="primary",
               use_container_width=True
           )
       with col2:
           if st.form_submit_button("Cancel", use_container_width=True):
               st.session_state.selected_client = None
               st.rerun()

       if submitted:
           if not display_name:
               st.error("Display Name is required")
               return

           try:
               # Validate all paths before saving
               paths_to_validate = {
                   'Account Documentation': docs_path,
                   'Consulting Fees': fees_path,
                   'Meetings': meetings_path
               }
               
               invalid_paths = []
               for path_name, path in paths_to_validate.items():
                   if path:
                       is_valid, error_msg = validate_shared_path(path)
                       if not is_valid:
                           invalid_paths.append(f"{path_name}: {error_msg}")
               
               if invalid_paths:
                   st.error("Invalid paths found:\n" + "\n".join(invalid_paths))
                   return

               data = {
                   "full_name": full_name if full_name else None,
                   "ima_signed_date": ima_date.strftime('%Y-%m-%d') if ima_date else None,
                   "file_path_account_documentation": normalize_shared_path(docs_path),
                   "file_path_consulting_fees": normalize_shared_path(fees_path),
                   "file_path_meetings": normalize_shared_path(meetings_path)
               }

               success = False
               if mode == "add":
                   new_id = add_client(display_name, **data)
                   success = bool(new_id)
               else:
                   success = update_client(client_id, display_name=display_name, **data)

               if success:
                   st.toast(f"Successfully {'added' if mode == 'add' else 'updated'} client: {display_name}")
                   st.session_state.selected_client = None
                   time.sleep(0.5)
                   st.rerun()
               else:
                   st.error(f"Failed to {'add' if mode == 'add' else 'update'} client")
                   
           except Exception as e:
               if "UNIQUE constraint" in str(e):
                   st.error("A client with this display name already exists")
               else:
                   st.error(f"Error: {str(e)}")