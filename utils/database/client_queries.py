import streamlit as st
from .connection import get_database_connection

@st.cache_data
def get_clients():
    """Get all clients from the database"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT client_id, display_name FROM clients ORDER BY display_name")
        return cursor.fetchall()
    finally:
        conn.close()

@st.cache_data
def get_client_details(client_id):
    """Get client details"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT display_name, full_name FROM clients WHERE client_id = ?", (client_id,))
        return cursor.fetchone()
    finally:
        conn.close() 