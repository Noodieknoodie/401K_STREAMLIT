# utils.py 
import sqlite3
import streamlit as st
from datetime import datetime

def get_database_connection():
    """Create and return a database connection"""
    return sqlite3.connect('DATABASE/401kDATABASE.db')

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
def get_active_contract(client_id):
    """Get active contract for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contract_number, provider_name, num_people, payment_type, 
                   payment_schedule, fee_type, percent_rate, flat_rate
            FROM contracts 
            WHERE client_id = ? AND active = 'TRUE'
            LIMIT 1
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

@st.cache_data
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

def calculate_rate_conversions(rate_value, fee_type, schedule):
    """Calculate rate conversions based on payment schedule"""
    if not rate_value or rate_value == 'N/A' or not schedule:
        return 'N/A', None
    
    try:
        if fee_type == 'percentage':
            rate = float(rate_value.strip('%')) / 100
            if schedule.lower() == 'monthly':
                return f"{rate*100:.3f}%", f"Q: {rate*3*100:.3f}% | A: {rate*12*100:.3f}%"
            elif schedule.lower() == 'quarterly':
                monthly = rate / 3
                return f"{rate*100:.3f}%", f"M: {monthly*100:.3f}% | A: {rate*4*100:.3f}%"
            else:  # annual
                monthly = rate / 12
                quarterly = rate / 4
                return f"{rate*100:.3f}%", f"M: {monthly*100:.3f}% | Q: {quarterly*100:.3f}%"
        else:  # flat rate
            rate = float(rate_value.strip('$').replace(',', ''))
            if schedule.lower() == 'monthly':
                return f"${rate:,.2f}", f"Q: ${rate*3:,.2f} | A: ${rate*12:,.2f}"
            elif schedule.lower() == 'quarterly':
                monthly = rate / 3
                return f"${rate:,.2f}", f"M: ${monthly:,.2f} | A: ${rate*4:,.2f}"
            else:  # annual
                monthly = rate / 12
                quarterly = rate / 4
                return f"${rate:,.2f}", f"M: ${monthly:,.2f} | Q: ${quarterly:,.2f}"
    except:
        return rate_value, None

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

@st.cache_data
def get_all_contracts(client_id):
    """Get all contracts for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contract_id, active, contract_number, provider_name, 
                   contract_start_date, fee_type, percent_rate, flat_rate,
                   payment_schedule, payment_type, num_people, notes
            FROM contracts 
            WHERE client_id = ?
            ORDER BY 
                CASE WHEN active = 'TRUE' THEN 0 ELSE 1 END,
                contract_start_date DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

@st.cache_data
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
    finally:
        conn.close()

def format_phone_number_ui(number):
    """Format phone number for UI display: (XXX) XXX-XXXX"""
    if not number:
        return ""
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, number))
    
    # Progressive formatting as user types
    if len(digits) <= 3:
        return digits
    elif len(digits) <= 6:
        return f"({digits[:3]}) {digits[3:]}"
    elif len(digits) <= 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:10]}"

def format_phone_number_db(number):
    """Format phone number for database storage: XXX-XXX-XXXX"""
    if not number:
        return ""
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, number))
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return number

def validate_phone_number(number):
    """Validate phone number format"""
    if not number:
        return True  # Empty is valid as field is optional
    digits = ''.join(filter(str.isdigit, number))
    return len(digits) == 10

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
        return True
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