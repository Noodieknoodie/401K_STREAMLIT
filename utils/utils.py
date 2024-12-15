# utils\utils.py
import sqlite3
import streamlit as st
from datetime import datetime
from utils.debug_logger import debug

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
            p.payment_id
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
    debug.log_db_operation(
        operation='update',
        table='payments',
        data={'payment_id': payment_id, 'new_note': new_note},
        result='attempting'
    )
    
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
        
        debug.log_db_operation(
            operation='update',
            table='payments',
            data={'payment_id': payment_id},
            result='success'
        )
        debug.log_state_change(
            component='payment_history_cache',
            old_value='cached',
            new_value='cleared',
            context={'payment_id': payment_id}
        )
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
    debug.log_db_operation(
        operation='insert',
        table='contacts',
        data={
            'client_id': client_id,
            'contact_type': contact_type,
            'contact_data': contact_data
        },
        result='attempting'
    )
    
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
        
        debug.log_db_operation(
            operation='insert',
            table='contacts',
            data={'client_id': client_id, 'contact_id': contact_id},
            result='success'
        )
        return contact_id
    finally:
        conn.close()    

def delete_contact(contact_id):
    """Delete a contact from the database"""
    debug.log_db_operation(
        operation='delete',
        table='contacts',
        data={'contact_id': contact_id},
        result='attempting'
    )
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE contact_id = ?", (contact_id,))
        conn.commit()
        
        debug.log_db_operation(
            operation='delete',
            table='contacts',
            data={'contact_id': contact_id},
            result='success'
        )
        return True
    finally:
        conn.close()

def update_contact(contact_id, contact_data):
    """Update an existing contact in the database"""
    debug.log_db_operation(
        operation='update',
        table='contacts',
        data={'contact_id': contact_id, 'updates': contact_data},
        result='attempting'
    )
    
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
        
        debug.log_db_operation(
            operation='update',
            table='contacts',
            data={'contact_id': contact_id},
            result='success'
        )
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
            p.payment_id
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
    debug.log_db_operation(
        operation='insert',
        table='payments',
        data={'client_id': client_id, 'payment_data': payment_data},
        result='attempting'
    )
    
    # Get active contract
    contract = get_active_contract(client_id)
    if not contract:
        debug.log_db_operation(
            operation='insert',
            table='payments',
            data={'client_id': client_id},
            result={'error': 'no_active_contract'}
        )
        return None
        
    conn = get_database_connection()
    try:
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
        """, (
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
        ))
        conn.commit()
        payment_id = cursor.lastrowid
        
        debug.log_db_operation(
            operation='insert',
            table='payments',
            data={
                'client_id': client_id,
                'payment_id': payment_id,
                'schedule': schedule
            },
            result='success'
        )
        return payment_id
    except sqlite3.Error as e:
        debug.log_db_operation(
            operation='insert',
            table='payments',
            data={'client_id': client_id},
            result={'error': str(e)}
        )
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

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
        debug.log_db_operation(
            operation='fetch',
            table='payments',
            data={'payment_id': payment_id},
            result='success' if result else 'not_found'
        )
        return result
    finally:
        conn.close()

@st.cache_data(ttl=300)  # Cache for 5 minutes
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
    debug.log_db_operation(
        operation='delete',
        table='payments',
        data={'payment_id': payment_id},
        result='attempting'
    )
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
        conn.commit()
        
        debug.log_db_operation(
            operation='delete',
            table='payments',
            data={'payment_id': payment_id},
            result='success'
        )
        return True
    finally:
        conn.close()

