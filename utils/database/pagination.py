"""Pagination utilities for database queries."""
import streamlit as st
from .connection import get_database_connection

@st.cache_data
def get_total_payment_count(client_id):
    """Get total number of payments for a client."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM payments
            WHERE client_id = ?
        """, (client_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

@st.cache_data
def get_payment_year_quarters(client_id):
    """Get all year-quarter combinations for a client's payments."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT applied_start_year, applied_start_quarter
            FROM payments
            WHERE client_id = ?
            ORDER BY applied_start_year DESC, applied_start_quarter DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

@st.cache_data
def get_paginated_payment_history(client_id, offset=0, limit=25, years=None, quarters=None):
    """Get paginated payment history for a client with optional year/quarter filters."""
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