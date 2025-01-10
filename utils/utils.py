# utils/utils.py
import sqlite3
import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import os
import logging
from pathlib import Path
import platform
from .summaries import (
    update_quarterly_summary,
    update_yearly_summary,
    update_client_metrics
)
from .database import get_database_connection

"""
File Path Handling System Documentation
=====================================

Overview
--------
This system enables universal file access across different user machines by storing
relative paths in the database and dynamically reconstructing full paths for each user.

Key Components
-------------
1. Path Storage:
   - Paths are stored relative to 'Hohimer Wealth Management' folder
   - Example stored path: 'Hohimer Wealth Management/Client Files/ABC Corp/Documents'

2. Path Reconstruction:
   - Each user's OneDrive root is detected automatically
   - Relative paths are combined with the user's root to create valid local paths
   - Example: 'C:/Users/UserA/OneDrive - Hohimer Wealth Management/Client Files/ABC Corp/Documents'

How It Works
-----------
1. When a user inputs a path:
   - Input: 'C:/Users/UserA/OneDrive - Hohimer Wealth Management/Client Files/ABC Corp'
   - normalize_shared_path() extracts: 'Hohimer Wealth Management/Client Files/ABC Corp'
   - This relative path is stored in the database

2. When accessing files:
   - get_onedrive_root() finds the user's OneDrive location
   - reconstruct_full_path() combines the root with the stored relative path
   - Result is a valid path for the current user's system

Example Usage
------------
# Storing a path:
full_path = "C:/Users/UserA/OneDrive - Hohimer Wealth Management/Client Files/ABC Corp"
relative_path = normalize_shared_path(full_path)
# Stores: "Hohimer Wealth Management/Client Files/ABC Corp"

# Accessing files (on different machine):
relative_path = get_client_file_paths(client_id)['account_documentation']
local_path = reconstruct_full_path(relative_path)
# Returns: "C:/Users/UserB/OneDrive - Hohimer Wealth Management/Client Files/ABC Corp"

For File Preview Implementation
-----------------------------
1. Get the stored path:
   relative_path = get_client_file_paths(client_id)['account_documentation']

2. Reconstruct for current user:
   local_path = reconstruct_full_path(relative_path)

3. Use local_path with file preview component:
   if local_path:
       # Show file preview using local_path
   else:
       # Handle invalid/inaccessible path

Notes
-----
- All paths are normalized to use forward slashes
- Validation ensures paths exist and are within the shared system
- Error handling is in place for missing/invalid paths
"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database_connection():
    """Create and return a database connection to the local database."""
    try:
        # Use a simple relative path from the project root
        database_path = 'DATABASE/401kDATABASE.db'
        
        if not os.path.exists(database_path):
            raise FileNotFoundError(
                "Database file not found. Please ensure:\n"
                "1. The DATABASE folder exists in the project root\n"
                f"2. The database file exists at: {database_path}"
            )

        return sqlite3.connect(database_path)
        
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

def get_clients():
    """Get all clients from the database"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT client_id, display_name 
            FROM clients 
            WHERE valid_to IS NULL
            ORDER BY display_name
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def get_active_contract(client_id):
    """Get active contract for a client"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                contract_id,
                provider_name,
                contract_number,
                payment_schedule,
                fee_type,
                percent_rate,
                flat_rate,
                num_people
            FROM contracts 
            WHERE client_id = ? 
            AND active = 'TRUE'
            AND valid_to IS NULL
            LIMIT 1
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_client_contracts(client_id: int):
    """Get all contracts for a client ordered by active status and start date."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                contract_id,
                client_id,
                active,
                contract_number,
                provider_name,
                contract_start_date,
                fee_type,
                percent_rate,
                flat_rate,
                payment_schedule,
                notes,
                num_people
            FROM contracts 
            WHERE client_id = ?
            AND valid_to IS NULL
            ORDER BY 
                CASE WHEN active = 'TRUE' THEN 0 ELSE 1 END,
                contract_start_date DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

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
            AND p.valid_to IS NULL
            ORDER BY p.received_date DESC
            LIMIT 1
        """, (client_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_client_details(client_id):
    """Get client details"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT display_name, full_name 
            FROM clients 
            WHERE client_id = ? AND valid_to IS NULL
        """, (client_id,))
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
                return f"${rate:,.2f}", f"M: ${monthly:,.2f} | Q: ${quarterly*100:.3f}%"
    except:
        return rate_value, None

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
            AND valid_to IS NULL
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

def get_payment_history(client_id, years=None, quarters=None):
    """Get payment history for a client with optional year/quarter filters"""
    ensure_summaries_initialized()  # Add this line
    
    base_query = """
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
            p.payment_id,
            p.method
        FROM payments p
        JOIN contracts c ON p.contract_id = c.contract_id
        JOIN quarterly_summaries qs ON  -- Add this JOIN
            p.client_id = qs.client_id AND
            p.applied_start_year = qs.year AND
            p.applied_start_quarter = qs.quarter
        WHERE p.client_id = ?
    """
    
    params = [client_id]
    
    if years and len(years) > 0:
        year_placeholders = ','.join(['?' for _ in years])
        base_query += f" AND p.applied_start_year IN ({year_placeholders})"
        params.extend(years)
    
    if quarters and len(quarters) > 0:
        quarter_placeholders = ','.join(['?' for _ in quarters])
        base_query += f" AND p.applied_start_quarter IN ({quarter_placeholders})"
        params.extend(quarters)
    
    base_query += " ORDER BY p.received_date DESC, p.payment_id DESC"
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(base_query, params)
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
        
        # Clear any cached data that might include this payment
        if 'get_payment_history' in st.session_state:
            st.session_state.get_payment_history.clear()
    finally:
        conn.close()
    
    return True

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
        contact_id = cursor.lastrowid
        
        # Clear contact-related caches
        if hasattr(st.session_state, 'get_contacts'):
            st.session_state.get_contacts.clear()
        if hasattr(st.session_state, 'get_client_dashboard_data'):
            st.session_state.get_client_dashboard_data.clear()
            
        return contact_id
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

def get_total_payment_count(client_id):
    """Get total number of payments for a client."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM payments p
            WHERE p.client_id = ?
        """, (client_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_payment_year_quarters(client_id):
    """Get all available year/quarter combinations for quick navigation."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT 
                applied_start_year as year,
                applied_start_quarter as quarter
            FROM payments 
            WHERE client_id = ?
            ORDER BY year DESC, quarter DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_paginated_payment_history(client_id, offset=0, limit=None, years=None, quarters=None):
    """Get paginated payment records with optional year/quarter filters."""
    base_query = """
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
            p.payment_id,
            p.method
        FROM payments p
        JOIN contracts c ON p.contract_id = c.contract_id
        WHERE p.client_id = ?
    """
    
    params = [client_id]
    
    # Handle multiple years filter
    if years and len(years) > 0:
        year_placeholders = ','.join(['?' for _ in years])
        base_query += f" AND p.applied_start_year IN ({year_placeholders})"
        params.extend(years)
    
    # Handle multiple quarters filter
    if quarters and len(quarters) > 0:
        quarter_placeholders = ','.join(['?' for _ in quarters])
        base_query += f" AND p.applied_start_quarter IN ({quarter_placeholders})"
        params.extend(quarters)
    
    base_query += " ORDER BY p.received_date DESC, p.payment_id DESC"
    
    if limit is not None:
        base_query += f" LIMIT {limit} OFFSET {offset}"
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(base_query, params)
        return cursor.fetchall()
    finally:
        conn.close()

def format_payment_data(payments):
    """Format payment data for display with consistent formatting."""
    table_data = []
    
    for payment in payments:
        provider_name = payment[0] or "N/A"
        
        # Format payment period with Q prefix
        if payment[1] == payment[3] and payment[2] == payment[4]:
            period = f"Q{payment[1]} {payment[2]}"
        else:
            period = f"Q{payment[1]} {payment[2]} - Q{payment[3]} {payment[4]}"
        
        frequency = payment[5].title() if payment[5] else "N/A"
        
        # Format date
        received_date = "N/A"
        if payment[6]:
            try:
                date_obj = datetime.strptime(payment[6], '%Y-%m-%d')
                received_date = date_obj.strftime('%b %d, %Y')
            except:
                received_date = payment[6]
        
        # Format currency values
        def format_currency(value):
            try:
                if value is None or value == "":
                    return "N/A"
                return f"${float(value):,.2f}"
            except (ValueError, TypeError):
                return "N/A"
        
        total_assets = format_currency(payment[7])
        expected_fee = format_currency(payment[8])
        actual_fee = format_currency(payment[9])
        
        # Calculate fee discrepancy
        try:
            if payment[8] is not None and payment[9] is not None and payment[8] != "" and payment[9] != "":
                discrepancy = float(payment[9]) - float(payment[8])
                discrepancy_str = f"${discrepancy:,.2f}" if discrepancy >= 0 else f"-${abs(discrepancy):,.2f}"
            else:
                discrepancy_str = "N/A"
        except (ValueError, TypeError):
            discrepancy_str = "N/A"
        
        method = payment[11] or "N/A"  # Add method to display
        notes = payment[10] or ""
        payment_id = payment[12]
        
        table_data.append({
            "Provider": provider_name,
            "Period": period,
            "Frequency": frequency,
            "Received": received_date,
            "Total Assets": total_assets,
            "Expected Fee": expected_fee,
            "Actual Fee": actual_fee,
            "Discrepancy": discrepancy_str,
            "Method": method,  # Add method to returned data
            "Notes": notes,
            "payment_id": payment_id
        })
    
    return table_data

def get_active_contracts_for_client(client_id):
    """Get all active contracts for a client for payment provider selection"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                contract_id,
                provider_name,
                contract_number,
                payment_schedule,
                fee_type,
                percent_rate,
                flat_rate
            FROM contracts 
            WHERE client_id = ? AND active = 'TRUE'
            ORDER BY contract_start_date DESC
        """, (client_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def format_currency_db(amount):
    """Format currency for database storage: Convert UI format to decimal"""
    if not amount:
        return None
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = ''.join(c for c in str(amount) if c.isdigit() or c == '.')
        # Convert to float
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def format_currency_ui(amount):
    """Format currency for UI display: $X,XXX.XX"""
    if amount is None or amount == "":
        return ""
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = ''.join(c for c in str(amount) if c.isdigit() or c == '.')
        # Convert to float and format
        value = float(cleaned)
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return str(amount)

def validate_payment_data(data):
    """Validate payment data before saving to database"""
    errors = []
    
    # Check required fields
    if not data.get('received_date'):
        errors.append("Please enter when the payment was received")
    
    # Validate payment amount
    actual_fee = data.get('actual_fee', '')
    if not actual_fee:
        errors.append("Please enter the payment amount")
    elif actual_fee == "$0.00":
        errors.append("Please enter a payment amount")
    
    # Get schedule info
    schedule = data.get('payment_schedule', '').lower()
    if not schedule:
        errors.append("Payment schedule must be set in the contract before adding payments")
        return errors
    
    # Simple period validation
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_quarter = (current_month - 1) // 3 + 1
    
    start_period = data.get('applied_start_period')
    start_year = data.get('applied_start_year')
    end_period = data.get('applied_end_period')
    end_year = data.get('applied_end_year')
    
    # Validate start period is in arrears
    if start_year > current_year or (start_year == current_year and start_period >= current_quarter):
        errors.append("Payment must be for a previous period (in arrears)")
    
    # If multi-period, validate end period
    if end_period != start_period or end_year != start_year:
        # Validate end period is in arrears
        if end_year > current_year or (end_year == current_year and end_period >= current_quarter):
            errors.append("End period must be in arrears")
            
        # Validate end period is after start period
        start_absolute = start_year * 4 + start_period
        end_absolute = end_year * 4 + end_period
        if end_absolute < start_absolute:
            errors.append("End period cannot be before start period")
    
    return errors

def add_payment(client_id, payment_data):
    """Add a new payment to the database"""
    from .summaries import update_all_summaries
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            contract = get_active_contract(client_id)
            print(f"Active Contract: {contract}")
            if not contract:
                print("No active contract found!")
                return None
            
            conn = get_database_connection()
            cursor = conn.cursor()
            
            schedule = payment_data.get('payment_schedule', '').lower()
            if schedule == 'monthly':
                start_quarter = (payment_data['applied_start_period'] - 1) // 3 + 1
                end_quarter = (payment_data['applied_end_period'] - 1) // 3 + 1
            else:
                start_quarter = payment_data['applied_start_period']
                end_quarter = payment_data['applied_end_period']
            
            values = (
                client_id,
                contract[0],
                payment_data['received_date'],
                start_quarter,
                payment_data['applied_start_year'],
                end_quarter,
                payment_data['applied_end_year'],
                format_currency_db(payment_data.get('total_assets')),
                format_currency_db(payment_data.get('expected_fee')),
                format_currency_db(payment_data.get('actual_fee')),
                payment_data.get('method'),
                payment_data.get('notes', '')
            )
            
            cursor.execute("""
                INSERT INTO payments (
                    client_id, contract_id, received_date,
                    applied_start_quarter, applied_start_year,
                    applied_end_quarter, applied_end_year,
                    total_assets, expected_fee, actual_fee,
                    method, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            
            payment_id = cursor.lastrowid
            
            # Commit the payment first
            conn.commit()
            
            # Now update summaries in a separate transaction
            update_all_summaries(client_id, payment_data['applied_start_year'], start_quarter)
            
            return payment_id
            
        except sqlite3.Error as e:
            print(f"Database error (attempt {retry_count + 1}): {e}")
            if conn:
                conn.close()
            retry_count += 1
            if retry_count < max_retries:
                import time
                time.sleep(0.5)
            
    return None

def get_payment_by_id(payment_id):
    """Get complete payment data for editing"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.received_date,
                p.applied_start_quarter,
                p.applied_start_year,
                p.applied_end_quarter,
                p.applied_end_year,
                p.total_assets,
                p.actual_fee,
                p.method,
                p.notes,
                c.payment_schedule
            FROM payments p
            JOIN contracts c ON p.contract_id = c.contract_id
            WHERE p.payment_id = ?
        """, (payment_id,))
        result = cursor.fetchone()
        return result
    finally:
        conn.close()

def get_client_dashboard_data(client_id):
    """Get all necessary client data for the dashboard in a single database call"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get contacts
        cursor.execute("""
            SELECT 
                contact_type, contact_name, phone, email, 
                fax, physical_address, mailing_address, contact_id
            FROM contacts 
            WHERE client_id = ?
            ORDER BY 
                CASE contact_type
                    WHEN 'Primary Contact' THEN 1
                    WHEN 'Authorized Contact' THEN 2
                    WHEN 'Provider Contact' THEN 3
                    ELSE 4
                END,
                contact_name
        """, (client_id,))
        contacts = [
            {
                'contact_type': row[0],
                'contact_name': row[1],
                'phone': row[2],
                'email': row[3],
                'fax': row[4],
                'physical_address': row[5],
                'mailing_address': row[6],
                'contact_id': row[7]
            }
            for row in cursor.fetchall()
        ]

        # Get active contract
        cursor.execute("""
            SELECT 
                contract_id, provider_name, contract_number,
                payment_schedule, fee_type, percent_rate,
                flat_rate, num_people
            FROM contracts 
            WHERE client_id = ? AND active = 'TRUE'
            LIMIT 1
        """, (client_id,))
        contract_row = cursor.fetchone()
        active_contract = None
        if contract_row:
            active_contract = {
                'contract_id': contract_row[0],
                'provider_name': contract_row[1],
                'contract_number': contract_row[2],
                'payment_schedule': contract_row[3],
                'fee_type': contract_row[4],
                'percent_rate': contract_row[5],
                'flat_rate': contract_row[6],
                'num_people': contract_row[7]
            }

        # Get recent payments with contract info
        cursor.execute("""
            SELECT 
                p.payment_id,
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
                p.notes
            FROM payments p
            JOIN contracts c ON p.contract_id = c.contract_id
            WHERE p.client_id = ?
            ORDER BY p.received_date DESC
            LIMIT 50
        """, (client_id,))
        recent_payments = [
            {
                'payment_id': row[0],
                'provider_name': row[1],
                'applied_start_quarter': row[2],
                'applied_start_year': row[3],
                'applied_end_quarter': row[4],
                'applied_end_year': row[5],
                'payment_schedule': row[6],
                'received_date': row[7],
                'total_assets': row[8],
                'expected_fee': row[9],
                'actual_fee': row[10],
                'notes': row[11]
            }
            for row in cursor.fetchall()
        ]

        return {
            'contacts': contacts,
            'active_contract': active_contract,
            'recent_payments': recent_payments
        }
    finally:
        conn.close()

def delete_payment(payment_id):
    """Delete a payment from the database"""
    from .summaries import update_all_summaries
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get payment data for summary updates
        cursor.execute("SELECT client_id, applied_start_year, applied_start_quarter FROM payments WHERE payment_id = ?", (payment_id,))
        payment_data = cursor.fetchone()
        
        cursor.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
        
        # Commit the deletion first
        conn.commit()
        
        # Now update summaries in a separate transaction
        if payment_data:
            update_all_summaries(payment_data[0], payment_data[1], payment_data[2])
        
        return True
    finally:
        conn.close()

def get_unique_payment_methods():
    """Get all unique payment methods from the database, including 'None Specified' and 'Other'"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT method 
            FROM payments 
            WHERE method IS NOT NULL
            UNION
            SELECT 'None Specified'
            ORDER BY method
        """)
        methods = [row[0] if row[0] is not None else 'None Specified' for row in cursor.fetchall()]
        if 'Other' not in methods:
            methods.append('Other')
        return methods
    finally:
        conn.close()

def update_payment(payment_id: int, form_data: Dict[str, Any]) -> bool:
    """Update an existing payment in the database."""
    from .summaries import update_all_summaries
    
    try:
        total_assets = format_currency_db(form_data.get('total_assets'))
        actual_fee = format_currency_db(form_data.get('actual_fee'))
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Get original payment data for summary updates
        cursor.execute("SELECT client_id, applied_start_year, applied_start_quarter FROM payments WHERE payment_id = ?", (payment_id,))
        old_data = cursor.fetchone()
        
        cursor.execute("""
            UPDATE payments
            SET received_date = ?,
                applied_start_quarter = ?,
                applied_start_year = ?,
                applied_end_quarter = ?,
                applied_end_year = ?,
                total_assets = ?,
                actual_fee = ?,
                method = ?,
                notes = ?
            WHERE payment_id = ?
        """, (
            form_data['received_date'],
            form_data['applied_start_period'],
            form_data['applied_start_year'],
            form_data['applied_end_period'],
            form_data['applied_end_year'],
            total_assets,
            actual_fee,
            form_data.get('method'),
            form_data.get('notes'),
            payment_id
        ))
        
        # Commit the update first
        conn.commit()
        
        # Now update summaries for both old and new periods in separate transactions
        update_all_summaries(old_data[0], old_data[1], old_data[2])  # Update old period
        if old_data[1] != form_data['applied_start_year'] or old_data[2] != form_data['applied_start_period']:
            update_all_summaries(old_data[0], form_data['applied_start_year'], form_data['applied_start_period'])  # Update new period
        
        return True
        
    except Exception as e:
        st.error(f"Error updating payment: {str(e)}")
        return False
    finally:
        conn.close()

def save_contract(client_id: int, contract_data: Dict[str, Any], mode: str = 'add') -> bool:
    """Save contract to database.
    
    Args:
        client_id: The ID of the client
        contract_data: Dictionary containing contract data
        mode: Either 'add' for new contract or 'edit' for updating existing
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # If adding new contract, deactivate current active contract
        if mode == 'add':
            cursor.execute("""
                UPDATE contracts 
                SET active = 'FALSE' 
                WHERE client_id = ? AND active = 'TRUE'
            """, (client_id,))
        
        # Insert new contract or update existing
        if mode == 'add':
            cursor.execute("""
                INSERT INTO contracts (
                    client_id, active, contract_number, provider_name,
                    contract_start_date, fee_type, percent_rate, flat_rate,
                    payment_schedule, num_people, notes
                ) VALUES (?, 'TRUE', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                contract_data.get('contract_number'),
                contract_data.get('provider_name'),
                contract_data.get('contract_start_date'),
                contract_data.get('fee_type'),
                contract_data.get('percent_rate'),
                contract_data.get('flat_rate'),
                contract_data.get('payment_schedule'),
                contract_data.get('num_people'),
                contract_data.get('notes')
            ))
        else:
            cursor.execute("""
                UPDATE contracts SET
                    contract_number = ?,
                    provider_name = ?,
                    contract_start_date = ?,
                    fee_type = ?,
                    percent_rate = ?,
                    flat_rate = ?,
                    payment_schedule = ?,
                    num_people = ?,
                    notes = ?
                WHERE contract_id = ? AND active = 'TRUE'
            """, (
                contract_data.get('contract_number'),
                contract_data.get('provider_name'),
                contract_data.get('contract_start_date'),
                contract_data.get('fee_type'),
                contract_data.get('percent_rate'),
                contract_data.get('flat_rate'),
                contract_data.get('payment_schedule'),
                contract_data.get('num_people'),
                contract_data.get('notes'),
                contract_data.get('contract_id')
            ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving contract: {e}")
        return False
    finally:
        conn.close()

def validate_contract_data(data: Dict[str, Any]) -> list:
    """Validate contract data before saving.
    
    Args:
        data: Dictionary containing contract data to validate
        
    Returns:
        list: List of validation error messages, empty if valid
    """
    errors = []
    
    if not data.get('provider_name', '').strip():
        errors.append("Provider name is required")
    
    if data.get('fee_type') == 'percentage':
        if not data.get('percent_rate') or data.get('percent_rate') <= 0:
            errors.append("Please enter a valid rate percentage greater than 0")
    else:
        if not data.get('flat_rate') or data.get('flat_rate') <= 0:
            errors.append("Please enter a valid flat rate amount greater than 0")
    
    if not data.get('payment_schedule'):
        errors.append("Payment schedule is required")
    
    try:
        start_date = datetime.strptime(data.get('contract_start_date', ''), '%Y-%m-%d')
        if start_date > datetime.now():
            errors.append("Contract start date cannot be in the future")
    except ValueError:
        errors.append("Invalid contract start date")
    
    return errors

def add_client(display_name: str, **optional_fields) -> int:
    """
    Add a new client to the database.
    
    Args:
        display_name (str): Required display name for the client
        **optional_fields: Optional fields (full_name, ima_signed_date, file paths)
    
    Returns:
        int: The new client_id
    """
    if not display_name:
        raise ValueError("display_name is required")
        
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Build the query dynamically based on provided fields
        fields = ['display_name'] + list(optional_fields.keys())
        placeholders = ['?'] * len(fields)
        values = [display_name] + list(optional_fields.values())
        
        query = f"""
            INSERT INTO clients ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_client(client_id: int, **fields_to_update) -> bool:
    """
    Update an existing client's information.
    
    Args:
        client_id (int): The ID of the client to update
        **fields_to_update: Fields to update and their new values
    
    Returns:
        bool: True if successful
    """
    if not fields_to_update:
        return False
        
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Build the update query dynamically
        set_clause = ', '.join(f"{field} = ?" for field in fields_to_update.keys())
        values = list(fields_to_update.values()) + [client_id]
        
        query = f"""
            UPDATE clients 
            SET {set_clause}
            WHERE client_id = ?
        """
        
        cursor.execute(query, values)
        conn.commit()
        return True
    finally:
        conn.close()

def delete_client(client_id: int) -> bool:
    """
    Delete a client and all related records.
    
    Args:
        client_id (int): The ID of the client to delete
    
    Returns:
        bool: True if successful
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Start a transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Delete related records first (foreign key relationships)
        cursor.execute("DELETE FROM payments WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM contracts WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM contacts WHERE client_id = ?", (client_id,))
        
        # Finally delete the client
        cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
        
        # Commit the transaction
        conn.commit()
        return True
    except Exception as e:
        # Rollback on error
        conn.rollback()
        logger.error(f"Error deleting client {client_id}: {str(e)}")
        return False
    finally:
        conn.close()

def get_client_file_paths(client_id: int) -> dict:
    """Get document file paths for a specific client.
    
    Args:
        client_id: The ID of the client
        
    Returns:
        dict: Dictionary containing the document paths with keys:
            - account_documentation
            - consulting_fees
            - meetings
        Returns None if client not found
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                file_path_account_documentation,
                file_path_consulting_fees,
                file_path_meetings
            FROM clients 
            WHERE client_id = ?
        """, (client_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'account_documentation': result[0],
                'consulting_fees': result[1],
                'meetings': result[2]
            }
        return None
    finally:
        conn.close()

def get_onedrive_root() -> Optional[str]:
    """Get the OneDrive root path for the current user."""
    system = platform.system()
    if system == "Windows":
        # Standard OneDrive path on Windows
        onedrive_path = os.path.expandvars("%USERPROFILE%/OneDrive")
        if os.path.exists(onedrive_path):
            return onedrive_path
        # Business OneDrive path pattern
        business_path = os.path.expandvars("%USERPROFILE%/OneDrive - Hohimer Wealth Management")
        if os.path.exists(business_path):
            return business_path
    return None

def validate_shared_path(full_path: str) -> Tuple[bool, str]:
    """
    Validate if a path is within the shared OneDrive system.
    Returns (is_valid, error_message)
    """
    if not full_path:
        return False, "Path cannot be empty"
        
    # Clean the path
    clean_path = full_path.strip().replace('\\', '/')
    
    # Check if path contains the company identifier
    if "hohimer wealth management" not in clean_path.lower():
        return False, "Path must be within the Hohimer Wealth Management shared folder"
    
    # Get OneDrive root
    onedrive_root = get_onedrive_root()
    if not onedrive_root:
        return False, "Could not locate OneDrive folder"
        
    # Construct full path
    try:
        full_path = os.path.join(onedrive_root, clean_path)
        # Convert to Path object for validation
        path_obj = Path(full_path)
        
        # Check if path exists
        if not path_obj.exists():
            return False, f"Path does not exist: {clean_path}"
            
        # Ensure path is within OneDrive root
        if not str(path_obj).lower().startswith(onedrive_root.lower()):
            return False, "Path must be within OneDrive shared folder"
            
        return True, ""
    except Exception as e:
        return False, f"Invalid path: {str(e)}"

def normalize_shared_path(full_path: str) -> Optional[str]:
    """
    Convert a full path to a relative path within the shared system.
    Returns None if path is invalid.
    """
    if not full_path:
        return None
        
    # Clean the path
    clean_path = full_path.strip().replace('\\', '/')
    lower_path = clean_path.lower()
    
    # Find the company identifier in the path
    company_id = "hohimer wealth management"
    if company_id not in lower_path:
        return None
        
    # Extract relative path
    idx = lower_path.find(company_id)
    relative_path = clean_path[idx:].rstrip('/')
    
    # Validate the path exists
    is_valid, _ = validate_shared_path(relative_path)
    if not is_valid:
        return None
        
    return relative_path

def reconstruct_full_path(relative_path: str) -> Optional[str]:
    """
    Reconstruct a full path from a relative path for the current user.
    Returns None if path cannot be reconstructed.
    """
    if not relative_path:
        return None
        
    onedrive_root = get_onedrive_root()
    if not onedrive_root:
        return None
        
    try:
        full_path = os.path.join(onedrive_root, relative_path)
        path_obj = Path(full_path)
        
        # Validate the path exists
        if not path_obj.exists():
            return None
            
        return str(path_obj)
    except:
        return None

def ensure_summaries_initialized() -> bool:
    """Ensure summary tables are populated and triggers are active."""
    from .summaries import populate_all_summaries
    from .triggers import check_triggers_exist, initialize_triggers
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Check if summary tables have data
        cursor.execute("SELECT COUNT(*) FROM quarterly_summaries")
        has_quarterly = cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM yearly_summaries")
        has_yearly = cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM client_metrics")
        has_metrics = cursor.fetchone()[0] > 0
        
        # Initialize triggers if needed
        if not check_triggers_exist():
            if not initialize_triggers():
                return False
        
        # Populate summaries if empty
        if not (has_quarterly and has_yearly and has_metrics):
            if not populate_all_summaries():
                return False
        
        return True
        
    except Exception as e:
        print(f"Error initializing summaries: {str(e)}")
        return False
    finally:
        conn.close()

def get_summary_metrics(client_id: int, year: int = None, quarter: int = None) -> Dict[str, Any]:
    """Get summary metrics for a client with optional period filtering."""
    if year is None:
        year = datetime.now().year
    if quarter is None:
        quarter = (datetime.now().month - 1) // 3 + 1
        
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                qs.total_payments,
                qs.total_assets,
                qs.payment_count,
                qs.avg_payment,
                qs.expected_total,
                ys.yoy_growth,
                cm.last_payment_date,
                cm.last_payment_amount,
                cm.total_ytd_payments,
                cm.avg_quarterly_payment
            FROM quarterly_summaries qs
            LEFT JOIN yearly_summaries ys ON
                qs.client_id = ys.client_id AND
                qs.year = ys.year
            LEFT JOIN client_metrics cm ON
                qs.client_id = cm.client_id
            WHERE qs.client_id = ?
            AND qs.year = ?
            AND qs.quarter = ?
        """, (client_id, year, quarter))
        
        row = cursor.fetchone()
        
        if not row:
            return None
            
        return {
            'total_payments': row[0],
            'total_assets': row[1],
            'payment_count': row[2],
            'avg_payment': row[3],
            'expected_total': row[4],
            'yoy_growth': row[5],
            'last_payment_date': row[6],
            'last_payment_amount': row[7],
            'total_ytd_payments': row[8],
            'avg_quarterly_payment': row[9]
        }
        
    finally:
        conn.close()

