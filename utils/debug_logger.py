"""
Debug Logger for State Management and UI Interactions
Helps track form submissions, state changes, and UI interactions
"""

import streamlit as st
import json
from datetime import datetime
import os
from typing import Any, Dict, Optional

class DebugLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.log_dir = 'debug_logs'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Initialize session tracking
        if 'debug_session_id' not in st.session_state:
            st.session_state.debug_session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.session_id = st.session_state.debug_session_id
        self.log_file = f"{self.log_dir}/debug_{self.session_id}.jsonl"
    
    def _write_log(self, entry: Dict[str, Any]) -> None:
        """Write a log entry to file"""
        entry['timestamp'] = datetime.now().isoformat()
        entry['session_id'] = self.session_id
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def log_state_change(self, component: str, old_value: Any, new_value: Any, context: Optional[Dict] = None) -> None:
        """Log state changes with before/after values"""
        entry = {
            'type': 'state_change',
            'component': component,
            'old_value': old_value,
            'new_value': new_value,
            'context': context or {}
        }
        self._write_log(entry)
    
    def log_ui_interaction(self, action: str, element: str, data: Optional[Dict] = None) -> None:
        """Log UI interactions like button clicks, form submissions"""
        entry = {
            'type': 'ui_interaction',
            'action': action,
            'element': element,
            'data': data or {}
        }
        self._write_log(entry)
    
    def log_form_data(self, form_name: str, data: Dict, validation_errors: Optional[list] = None) -> None:
        """Log form data and validation results"""
        entry = {
            'type': 'form_data',
            'form_name': form_name,
            'data': data,
            'validation_errors': validation_errors or []
        }
        self._write_log(entry)
    
    def log_db_operation(self, operation: str, table: str, data: Dict, result: Any = None) -> None:
        """Log database operations"""
        entry = {
            'type': 'db_operation',
            'operation': operation,
            'table': table,
            'data': data,
            'result': result
        }
        self._write_log(entry)
    
    def show_debug_panel(self) -> None:
        """Display debug information in Streamlit"""
        with st.expander("🔍 Debug Information", expanded=False):
            # Show session info
            st.write("Session ID:", self.session_id)
            
            # Show recent logs
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    logs = [json.loads(line) for line in f.readlines()[-10:]]  # Last 10 entries
                    st.json(logs)
            
            # Show current session state
            if st.checkbox("Show Session State"):
                filtered_state = {
                    k: v for k, v in st.session_state.items() 
                    if not k.startswith('_')  # Filter out internal Streamlit keys
                }
                st.json(filtered_state)

# Create a singleton instance
debug = DebugLogger() 