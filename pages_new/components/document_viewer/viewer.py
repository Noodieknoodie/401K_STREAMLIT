import streamlit as st
import os
from typing import Optional, Dict, List

def init_document_state():
    """Initialize document viewer state"""
    if 'doc_view_state' not in st.session_state:
        st.session_state.doc_view_state = 'categories'
    if 'current_category' not in st.session_state:
        st.session_state.current_category = None
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

def get_files_in_path(folder_path: Optional[str]) -> List[str]:
    """Get list of files in a folder"""
    if not folder_path:
        return []
    
    try:
        user_profile = os.environ.get("USERPROFILE")
        full_path = os.path.join(user_profile, folder_path)
        if not os.path.exists(full_path):
            return []
            
        return [f for f in os.listdir(full_path) 
                if os.path.isfile(os.path.join(full_path, f))]
    except Exception:
        return []

def show_document_viewer(client_id: int):
    """Document viewer with navigation"""
    init_document_state()
    
    from utils.utils import get_client_file_paths, update_client, get_client_details
    
    # Get client details
    client_details = get_client_details(client_id)
    if not client_details:
        st.error("Client not found")
        return
    client_name = client_details[0]
    
    # Get document paths
    paths = get_client_file_paths(client_id) or {
        'account_documentation': None, 
        'consulting_fees': None, 
        'meetings': None
    }
    
    # Categories view
    if st.session_state.doc_view_state == 'categories':
        for category in ['account_documentation', 'consulting_fees', 'meetings']:
            label = category.replace('_', ' ').title()
            if st.button(label, use_container_width=True):
                st.session_state.current_category = category
                st.session_state.doc_view_state = 'files'
                st.rerun()
    
    # Files view
    elif st.session_state.doc_view_state == 'files':
        category = st.session_state.current_category
        folder_path = paths.get(category)
        
        # Back button
        if st.button("← Back"):
            st.session_state.doc_view_state = 'categories'
            st.rerun()
        
        # Show category name
        st.markdown(f"### {category.replace('_', ' ').title()}")
        
        # Configure path if none set
        if not folder_path:
            path = st.text_input("Enter folder path:")
            if path:
                paths[category] = path
                update_client(client_id, file_paths=paths)
                st.rerun()
            return
        
        # Show files
        files = get_files_in_path(folder_path)
        if not files:
            st.info("No files found")
            return
            
        for file in sorted(files):
            if st.button(file, use_container_width=True):
                st.session_state.current_file = os.path.join(folder_path, file)
                st.session_state.doc_view_state = 'viewer'
                st.rerun()
    
    # Document viewer
    elif st.session_state.doc_view_state == 'viewer':
        if st.button("← Back"):
            st.session_state.doc_view_state = 'files'
            st.rerun()
        
        file_path = st.session_state.current_file
        if not file_path:
            st.error("No file selected")
            return
            
        try:
            user_profile = os.environ.get("USERPROFILE")
            full_path = os.path.join(user_profile, file_path)
            
            if not os.path.exists(full_path):
                st.warning("File not found")
                return
                
            # Show PDF preview if it's a PDF
            if file_path.lower().endswith('.pdf'):
                with open(full_path, "rb") as f:
                    st.pdf_viewer(f)
            
            # Download button
            with open(full_path, "rb") as f:
                st.download_button(
                    "Download",
                    f,
                    file_name=os.path.basename(file_path)
                )
        except Exception:
            st.error("Error accessing file") 