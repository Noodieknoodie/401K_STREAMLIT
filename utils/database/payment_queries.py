import streamlit as st
from .connection import get_database_connection

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_latest_payment(client_id):
    """Get latest payment for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.actual_fee, p.received_date, p.total_assets, 
                   p.applied_start_quarter, p.applied_start_year
            FROM payments p
            WHERE p.client_id = ?
            ORDER BY p.received_date DESC
            LIMIT 1
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_payment_history(client_id):
    """Get payment history for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.provider_name,
                p.applied_start_quarter,
                p.applied_start_year,
                p.applied_end_quarter,
                p.applied_end_year,
                c.payment_schedule,
                p.received_date,
                p.total_assets,
                p.expected_fee,
                p.actual_fee,
                p.notes,
                p.payment_id
            FROM payments p
            JOIN contracts c ON p.contract_id = c.contract_id
            WHERE p.client_id = ?
            ORDER BY p.received_date DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_paginated_payment_history(client_id, offset=0, limit=25, years=None, quarters=None):
    """Get paginated payment history with optional year/quarter filters"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Build the query based on filters
        query = """
            SELECT 
                c.provider_name,
                p.applied_start_quarter,
                p.applied_start_year,
                p.applied_end_quarter,
                p.applied_end_year,
                c.payment_schedule,
                p.received_date,
                p.total_assets,
                p.expected_fee,
                p.actual_fee,
                p.notes,
                p.payment_id
            FROM payments p
            JOIN contracts c ON p.contract_id = c.contract_id
            WHERE p.client_id = ?
        """
        params = [client_id]
        
        # Add year filter if specified
        if years:
            year_placeholders = ','.join('?' * len(years))
            query += f" AND p.applied_start_year IN ({year_placeholders})"
            params.extend(years)
        
        # Add quarter filter if specified
        if quarters:
            quarter_placeholders = ','.join('?' * len(quarters))
            query += f" AND p.applied_start_quarter IN ({quarter_placeholders})"
            params.extend(quarters)
        
        # Add ordering and pagination
        query += """
            ORDER BY p.received_date DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

def update_payment_note(payment_id, new_note):
    """Update payment note"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE payments 
            SET notes = ? 
            WHERE payment_id = ?
        """, (new_note, payment_id))
        conn.commit()
        
        # Clear relevant caches
        get_payment_history.clear()
        get_paginated_payment_history.clear()
    finally:
        conn.close() 