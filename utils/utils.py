# utils/utils.py
import sqlite3
import streamlit as st
from datetime import datetime
from typing import Dict, Any
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DOCS: Table Structures
# ============================================================================

# Client Table Structure:
# CREATE TABLE "clients" (
#     "client_id" INTEGER NOT NULL,
#     "display_name" TEXT NOT NULL,
#     "full_name" TEXT,
#     "ima_signed_date" TEXT,
#     "file_path_account_documentation" TEXT,
#     "file_path_consulting_fees" TEXT,
#     "file_path_meetings" TEXT,
#     PRIMARY KEY("client_id" AUTOINCREMENT)
# )

# Contact Table Structure:
# CREATE TABLE "contacts" (
#     "contact_id" INTEGER NOT NULL,
#     "client_id" INTEGER NOT NULL,
#     "contact_type" TEXT NOT NULL,
#     "contact_name" TEXT,
#     "phone" TEXT,
#     "email" TEXT,
#     "fax" TEXT,
#     "physical_address" TEXT,
#     "mailing_address" TEXT,
#     PRIMARY KEY("contact_id" AUTOINCREMENT),
#     FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
# )

# Contract Table Structure:
# CREATE TABLE "contracts" (
#     "contract_id" INTEGER NOT NULL,
#     "client_id" INTEGER NOT NULL,
#     "active" TEXT,
#     "contract_number" TEXT,
#     "provider_name" TEXT,
#     "contract_start_date" TEXT,
#     "fee_type" TEXT,
#     "percent_rate" REAL,
#     "flat_rate" REAL,
#     "payment_schedule" TEXT,
#     "num_people" INTEGER,
#     "notes" TEXT
# )

# Payment Table Structure:
# CREATE TABLE "payments" (
#     "payment_id" INTEGER NOT NULL,
#     "contract_id" INTEGER NOT NULL,
#     "client_id" INTEGER NOT NULL,
#     "received_date" TEXT,
#     "applied_start_quarter" INTEGER,
#     "applied_start_year" INTEGER,
#     "applied_end_quarter" INTEGER,
#     "applied_end_year" INTEGER,
#     "total_assets" INTEGER,
#     "expected_fee" REAL,
#     "actual_fee" REAL,
#     "method" TEXT,
#     "notes" TEXT
# )


def get_database_connection():
    """Create and return a database connection dynamically based on OneDrive path."""
    try:
        # Get user profile path
        user_profile = os.environ.get("USERPROFILE")
        
        # Construct the full path to the database
        database_path = os.path.join(
            user_profile,
            "Hohimer Wealth Management",
            "Hohimer Company Portal - Company",
            "Hohimer Team Shared 4-15-19",
            "401Ks",
            "Database_Payments",
            "401kDATABASE.db"
        )

        if not os.path.exists(database_path):
            # Try local development path as fallback
            local_path = 'DATABASE/401kDATABASE.db'
            if os.path.exists(local_path):
                return sqlite3.connect(local_path)
            
            raise FileNotFoundError(
                f"Database file not found. Please ensure it exists at {database_path} "
                "and that you have proper access permissions."
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
        cursor.execute("SELECT client_id, display_name FROM clients ORDER BY display_name")
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
            WHERE client_id = ? AND active = 'TRUE'
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
    
    # Check required fields with friendly messages
    if not data.get('received_date'):
        errors.append("Please enter when the payment was received")
    
    # Validate payment amount
    actual_fee = data.get('actual_fee', '')
    if not actual_fee:
        errors.append("Please enter the payment amount")
    elif actual_fee == "$0.00":  # Check for default value
        errors.append("Please enter a payment amount")
    
    # Get schedule-specific terms for error messages
    schedule = data.get('payment_schedule', '').lower()
    period_term = "month" if schedule == 'monthly' else "quarter"
    
    # Validate periods are in arrears
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_period = current_month if schedule == 'monthly' else (current_month - 1) // 3 + 1
    periods_per_year = 12 if schedule == 'monthly' else 4
    
    start_period = data.get('applied_start_period')
    start_year = data.get('applied_start_year')
    end_period = data.get('applied_end_period', start_period)
    end_year = data.get('applied_end_year', start_year)
    
    if not schedule:
        errors.append("Payment schedule must be set in the contract before adding payments")
        return errors
    
    # Convert to absolute periods for comparison
    start_absolute = start_year * periods_per_year + start_period
    end_absolute = end_year * periods_per_year + end_period
    current_absolute = current_year * periods_per_year + current_period
    
    if start_absolute >= current_absolute:
        errors.append(f"Payment must be for a previous {period_term} (in arrears)")
    
    if end_absolute >= current_absolute:
        errors.append(f"Payment end {period_term} must be a previous {period_term} (in arrears)")
    
    if end_absolute < start_absolute:
        errors.append(f"End {period_term} cannot be before start {period_term}")
    
    return errors

def add_payment(client_id, payment_data):
    """Add a new payment to the database"""
    print("\n=== DEBUG ADD PAYMENT ===")
    print(f"Client ID: {client_id}")
    print(f"Payment Data: {payment_data}")
    
    # Get active contract
    contract = get_active_contract(client_id)
    print(f"Active Contract: {contract}")
    if not contract:
        print("No active contract found!")
        return None
        
    # Add retry logic for database locks
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            
            # Convert period fields to quarter fields for database storage
            schedule = payment_data.get('payment_schedule', '').lower()
            if schedule == 'monthly':
                # Convert months to quarters
                start_quarter = (payment_data['applied_start_period'] - 1) // 3 + 1
                end_quarter = (payment_data['applied_end_period'] - 1) // 3 + 1
            else:
                # Already in quarters
                start_quarter = payment_data['applied_start_period']
                end_quarter = payment_data['applied_end_period']
            
            print(f"Inserting payment with quarters: {start_quarter} - {end_quarter}")
            
            # Prepare values for insertion
            values = (
                client_id,
                contract[0],  # contract_id from active contract
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
            print("\nInserting values:", values)
            
            cursor.execute("""
                INSERT INTO payments (
                    client_id,
                    contract_id,
                    received_date,
                    applied_start_quarter,
                    applied_start_year,
                    applied_end_quarter,
                    applied_end_year,
                    total_assets,
                    expected_fee,
                    actual_fee,
                    method,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            
            conn.commit()
            payment_id = cursor.lastrowid
            print(f"Successfully added payment with ID: {payment_id}")
            
            # Verify the payment was added
            cursor.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,))
            verification = cursor.fetchone()
            print("\nVerification - Payment in database:", verification)
            
            conn.close()
            
            # Clear all payment-related caches
            if hasattr(st.session_state, 'get_payment_history'):
                st.session_state.get_payment_history.clear()
            if hasattr(st.session_state, 'get_paginated_payment_history'):
                st.session_state.get_paginated_payment_history.clear()
            if hasattr(st.session_state, 'get_payment_year_quarters'):
                st.session_state.get_payment_year_quarters.clear()
            if hasattr(st.session_state, 'get_latest_payment'):
                st.session_state.get_latest_payment.clear()
                
            return payment_id
            
        except sqlite3.Error as e:
            print(f"Database error (attempt {retry_count + 1}): {e}")
            if conn:
                conn.close()
            retry_count += 1
            if retry_count < max_retries:
                import time
                time.sleep(0.5)  # Wait half a second before retrying
            
    return None  # Return None if all retries failed

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
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
        conn.commit()
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
    """Update an existing payment in the database.
    
    Args:
        payment_id: The ID of the payment to update
        form_data: Dictionary containing the updated payment data
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Clean currency values
        total_assets = format_currency_db(form_data.get('total_assets'))
        actual_fee = format_currency_db(form_data.get('actual_fee'))
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Update the payment record
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
            form_data['applied_end_period'] if form_data.get('applied_end_period') != form_data['applied_start_period'] else None,
            form_data['applied_end_year'] if form_data.get('applied_end_year') != form_data['applied_start_year'] else None,
            total_assets,
            actual_fee,
            form_data.get('method'),
            form_data.get('notes'),
            payment_id
        ))
        
        conn.commit()
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
