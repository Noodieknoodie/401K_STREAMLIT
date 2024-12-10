"""Temporary performance logging utility - Can be safely deleted when no longer needed"""

import time
from datetime import datetime
import streamlit as st
from functools import wraps
import json
import os

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

def log_event(event_type, details=None, duration=None):
    """Log a single event with timestamp and optional details"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    log_entry = {
        'timestamp': timestamp,
        'event': event_type,
        'session_id': st.session_state.get('_session_id', 'unknown'),
        'details': details,
        'duration_ms': round(duration * 1000, 2) if duration else None
    }
    
    # Write to file
    with open('logs/perf_log.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def log_db_call(func):
    """Decorator to log database calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            log_event(
                'db_call',
                {
                    'function': func.__name__,
                    'args': str(args),
                    'success': True
                },
                duration
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            log_event(
                'db_call',
                {
                    'function': func.__name__,
                    'args': str(args),
                    'error': str(e),
                    'success': False
                },
                duration
            )
            raise
    return wrapper

def log_ui_action(action_name):
    """Decorator to log UI actions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_event(
                    'ui_action',
                    {
                        'action': action_name,
                        'success': True
                    },
                    duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_event(
                    'ui_action',
                    {
                        'action': action_name,
                        'error': str(e),
                        'success': False
                    },
                    duration
                )
                raise
        return wrapper
    return decorator

# Initialize session ID if not exists
if '_session_id' not in st.session_state:
    st.session_state._session_id = datetime.now().strftime('%Y%m%d_%H%M%S') 