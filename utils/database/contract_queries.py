import streamlit as st
from .connection import get_database_connection

@st.cache_data
def get_active_contract(client_id):
    """Get active contract for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contract_number, provider_name, num_people,
                   payment_schedule, fee_type, percent_rate, flat_rate
            FROM contracts 
            WHERE client_id = ? AND active = 'TRUE'
            LIMIT 1
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

@st.cache_data
def get_all_contracts(client_id):
    """Get all contracts for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contract_id, active, contract_number, provider_name, 
                   contract_start_date, fee_type, percent_rate, flat_rate,
                   payment_schedule, num_people, notes
            FROM contracts 
            WHERE client_id = ?
            ORDER BY 
                CASE WHEN active = 'TRUE' THEN 0 ELSE 1 END,
                contract_start_date DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close() 