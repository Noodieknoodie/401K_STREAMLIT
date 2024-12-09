import streamlit as st
from .connection import get_database_connection

@st.cache_data
def get_contacts(client_id):
    """Get all contacts for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contact_type, contact_name, phone, email, fax, 
                   physical_address, mailing_address, contact_id
            FROM contacts 
            WHERE client_id = ?
            ORDER BY 
                CASE contact_type
                    WHEN 'Primary' THEN 1
                    WHEN 'Authorized' THEN 2
                    WHEN 'Provider' THEN 3
                    ELSE 4
                END,
                contact_name
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def add_contact(client_id, contact_type, contact_data):
    """Add a new contact to the database"""
    # Clean up contact type to match database values
    contact_type = contact_type.split()[0]  # Extract first word (Primary/Authorized/Provider)
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (
                client_id, contact_type, contact_name, phone, 
                email, fax, physical_address, mailing_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            contact_type,
            contact_data.get('contact_name'),
            contact_data.get('phone'),
            contact_data.get('email'),
            contact_data.get('fax'),
            contact_data.get('physical_address'),
            contact_data.get('mailing_address')
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def delete_contact(contact_id):
    """Delete a contact from the database"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE contact_id = ?", (contact_id,))
        conn.commit()
    finally:
        conn.close()

def update_contact(contact_id, contact_data):
    """Update an existing contact in the database"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts 
            SET contact_name = ?,
                phone = ?,
                email = ?,
                fax = ?,
                physical_address = ?,
                mailing_address = ?
            WHERE contact_id = ?
        """, (
            contact_data.get('contact_name'),
            contact_data.get('phone'),
            contact_data.get('email'),
            contact_data.get('fax'),
            contact_data.get('physical_address'),
            contact_data.get('mailing_address'),
            contact_id
        ))
        conn.commit()
        return True
    finally:
        conn.close() 