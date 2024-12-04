import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd
import time
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    [data-testid="stExpander"] {
        width: 100% !important;
    }
    .contact-info {
        border-bottom: 1px solid #eee;
        padding: 8px 0;
        margin-bottom: 8px;
    }
    .contact-info:last-child {
        border-bottom: none;
    }
    .contact-name {
        font-weight: bold;
        color: #1f77b4;
    }
    .contact-detail {
        margin: 2px 0;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
def get_database_connection():
    return sqlite3.connect('DATABASE/401kDATABASE.db')

# Get all clients
def get_clients():
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT client_id, display_name FROM clients ORDER BY display_name")
        return cursor.fetchall()
    finally:
        conn.close()

# Database queries
@st.cache_data
def get_active_contract(client_id):
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

def main():
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Quarterly Summary'
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None

    # Sidebar Navigation
    with st.sidebar:
        st.title("401K Payment Tracker")
        st.subheader("Navigation")
        
        # Navigation buttons with icons
        nav_options = [
            ('📊 Quarterly Summary', 'Quarterly Summary'),
            ('👥 Client Dashboard', 'Client Dashboard'),
            ('⚙️ Manage Clients', 'Manage Clients'),
            ('📝 Bulk Payment Entry', 'Bulk Payment Entry')
        ]
        
        for icon_label, page in nav_options:
            if st.button(icon_label, key=f"nav_{page}"):
                st.session_state.current_page = page
                if page != 'Client Dashboard':
                    st.session_state.selected_client = None

    # Main content area
    if st.session_state.current_page == 'Quarterly Summary':
        st.title("📊 Quarterly Summary")
        st.write("Coming soon...")
        
    elif st.session_state.current_page == 'Client Dashboard':
        # More compact header layout
        st.markdown("""
            <style>
                div.block-container{padding-top:1rem;}
                div.metric-container {font-size: 0.9rem !important;}
                [data-testid="metric-container"] {
                    width: fit-content;
                    margin: auto;
                }
                [data-testid="metric-container"] > div {
                    width: fit-content;
                    margin: auto;
                }
                [data-testid="metric-container"] label {
                    font-size: 0.8rem !important;
                    color: #555;
                }
                [data-testid="metric-container"] div[data-testid="metric-value"] {
                    font-size: 1rem !important;
                }
                [data-testid="metric-container"] div[data-testid="metric-delta"] {
                    font-size: 0.8rem !important;
                }
            </style>
        """, unsafe_allow_html=True)
        st.write("👥 Client Dashboard")
        
        # Client selector in a compact container
        clients = get_clients()
        client_options = ["Select a client..."] + [client[1] for client in clients]
        selected_client_name = st.selectbox(
            "🔍 Search or select a client",
            options=client_options,
            key="client_selector_dashboard",
            label_visibility="collapsed"
        )
        
        if selected_client_name != "Select a client...":
            # Reset expanders when client changes
            if st.session_state.selected_client != selected_client_name:
                st.session_state.selected_client = selected_client_name
                if 'expander_states' in st.session_state:
                    del st.session_state.expander_states
            
            client_id = next(
                client[0] for client in clients if client[1] == selected_client_name
            )
            
            # Get all required data
            client_details = get_client_details(client_id)
            active_contract = get_active_contract(client_id)
            latest_payment = get_latest_payment(client_id)
            
            # Compact container for metrics
            with st.container():
                # First row - 4 columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Client Name", client_details[0], client_details[1] if client_details[1] else None)
                with col2:
                    st.metric("Provider", active_contract[1] if active_contract and active_contract[1] else "N/A")
                with col3:
                    st.metric("Contract #", active_contract[0] if active_contract and active_contract[0] else "N/A")
                with col4:
                    st.metric("Participants", active_contract[2] if active_contract and active_contract[2] else "N/A")

                # Second row - 4 columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    rate_value = 'N/A'
                    rate_type = None
                    rate_conversions = None
                    
                    if active_contract and active_contract[5]:
                        if active_contract[5] == 'percentage':
                            if active_contract[6]:
                                rate_value = f"{active_contract[6]*100:.3f}%"
                        else:
                            if active_contract[7]:
                                rate_value = f"${active_contract[7]:,.2f}"
                        
                        if rate_value != 'N/A':
                            rate_type = active_contract[5].title()
                            schedule = active_contract[4] if active_contract[4] else None
                            rate_value, rate_conversions = calculate_rate_conversions(
                                rate_value, 
                                active_contract[5],
                                schedule
                            )
                    
                    st.metric(
                        "Rate", 
                        rate_value,
                        rate_conversions if rate_conversions else rate_type
                    )
                
                with col2:
                    st.metric("Payment Schedule", active_contract[4].title() if active_contract and active_contract[4] else "N/A")
                
                with col3:
                    last_payment = 'No payments'
                    payment_date = None
                    if latest_payment and latest_payment[0]:
                        last_payment = f"${latest_payment[0]:,.2f}"
                        payment_date = latest_payment[1]
                    st.metric("Last Payment", last_payment, payment_date)
                
                with col4:
                    aum_value = 'Not available'
                    aum_date = None
                    if latest_payment and latest_payment[2]:
                        aum_value = f"${latest_payment[2]:,.2f}"
                        aum_date = f"Q{latest_payment[3]} {latest_payment[4]}"
                    st.metric("Last Recorded AUM", aum_value, aum_date)

            # Small spacing before next section
            st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
            
            # Create three equal-width columns for contact cards at root level
            c1, c2, c3 = st.columns(3)
            
            contacts = get_contacts(client_id)
            contact_types = {'Primary': [], 'Authorized': [], 'Provider': []}
            
            if contacts:
                for contact in contacts:
                    if contact[0] in contact_types:
                        contact_types[contact[0]].append(contact)
            
            # Primary Contacts Card
            with c1:
                with st.expander(f"Primary Contact ({len(contact_types['Primary'])})", expanded=False):
                    if contact_types['Primary']:
                        for contact in contact_types['Primary']:
                            st.markdown(f"""
                            <div class="contact-info">
                                <div class="contact-name">{contact[1] if contact[1] else ''}</div>
                                <div class="contact-detail">📞 {contact[2] if contact[2] else 'No phone'}</div>
                                <div class="contact-detail">✉️ {contact[3] if contact[3] else 'No email'}</div>
                                {'<div class="contact-detail">📍 ' + (contact[5] or contact[6]) + '</div>' if (contact[5] or contact[6]) else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No primary contacts")
                    st.button("Add Primary Contact", key="add_primary", use_container_width=True)
            
            # Authorized Contacts Card
            with c2:
                with st.expander(f"Authorized Contact ({len(contact_types['Authorized'])})", expanded=False):
                    if contact_types['Authorized']:
                        for contact in contact_types['Authorized']:
                            st.markdown(f"""
                            <div class="contact-info">
                                <div class="contact-name">{contact[1] if contact[1] else ''}</div>
                                <div class="contact-detail">📞 {contact[2] if contact[2] else 'No phone'}</div>
                                <div class="contact-detail">✉️ {contact[3] if contact[3] else 'No email'}</div>
                                {'<div class="contact-detail">📍 ' + (contact[5] or contact[6]) + '</div>' if (contact[5] or contact[6]) else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No authorized contacts")
                    st.button("Add Authorized Contact", key="add_authorized", use_container_width=True)
            
            # Provider Contacts Card
            with c3:
                with st.expander(f"Provider Contact ({len(contact_types['Provider'])})", expanded=False):
                    if contact_types['Provider']:
                        for contact in contact_types['Provider']:
                            st.markdown(f"""
                            <div class="contact-info">
                                <div class="contact-name">{contact[1] if contact[1] else ''}</div>
                                <div class="contact-detail">📞 {contact[2] if contact[2] else 'No phone'}</div>
                                <div class="contact-detail">✉️ {contact[3] if contact[3] else 'No email'}</div>
                                {'<div class="contact-detail">📍 ' + (contact[5] or contact[6]) + '</div>' if (contact[5] or contact[6]) else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No provider contacts")
                    st.button("Add Provider Contact", key="add_provider", use_container_width=True)

            # Payments History Section
            st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
            st.markdown("### Payment History")
            
            payments = get_payment_history(client_id)
            
            if not payments:
                st.info("No payment history available for this client.", icon="ℹ️")
            else:
                # Create a list to store the formatted data
                table_data = []
                
                for payment in payments:
                    provider_name = payment[0] or "N/A"
                    
                    # Format payment period
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
                    total_assets = f"${payment[7]:,.2f}" if payment[7] else "N/A"
                    expected_fee = f"${payment[8]:,.2f}" if payment[8] is not None else "N/A"
                    actual_fee = f"${payment[9]:,.2f}" if payment[9] is not None else "N/A"
                    
                    # Calculate fee discrepancy
                    if payment[8] is not None and payment[9] is not None:
                        discrepancy = payment[9] - payment[8]
                        discrepancy_str = f"${discrepancy:,.2f}" if discrepancy >= 0 else f"-${abs(discrepancy):,.2f}"
                    else:
                        discrepancy_str = "N/A"
                    
                    # Notes with edit functionality
                    notes = payment[10] or ""
                    payment_id = payment[11]
                    
                    table_data.append({
                        "Provider": provider_name,
                        "Period": period,
                        "Frequency": frequency,
                        "Received": received_date,
                        "Total Assets": total_assets,
                        "Expected Fee": expected_fee,
                        "Actual Fee": actual_fee,
                        "Discrepancy": discrepancy_str,
                        "Notes": notes,
                        "payment_id": payment_id
                    })
                
                # Create DataFrame for the table
                df = pd.DataFrame(table_data)
                
                # Function to handle note updates
                def handle_note_edit(payment_id, new_note):
                    update_payment_note(payment_id, new_note)
                    st.success("Note updated successfully!")
                    time.sleep(0.5)
                    st.rerun()
                
                # Display table with editable notes
                st.markdown("""
                <style>
                    .stDataFrame {
                        font-size: 0.9rem;
                    }
                    .stDataFrame td {
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        max-width: 200px;
                    }
                    .stDataFrame th {
                        white-space: nowrap;
                    }
                    [data-testid="stDataFrameResizable"] {
                        max-height: 600px;
                        overflow: auto;
                    }
                    .payment-header {
                        color: #555;
                        font-size: 0.9rem;
                        font-weight: 600;
                        margin-bottom: 8px;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # Display column headers
                header_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 3])
                with header_cols[0]:
                    st.markdown('<p class="payment-header">Provider</p>', unsafe_allow_html=True)
                with header_cols[1]:
                    st.markdown('<p class="payment-header">Period</p>', unsafe_allow_html=True)
                with header_cols[2]:
                    st.markdown('<p class="payment-header">Frequency</p>', unsafe_allow_html=True)
                with header_cols[3]:
                    st.markdown('<p class="payment-header">Received</p>', unsafe_allow_html=True)
                with header_cols[4]:
                    st.markdown('<p class="payment-header">Total Assets</p>', unsafe_allow_html=True)
                with header_cols[5]:
                    st.markdown('<p class="payment-header">Expected Fee</p>', unsafe_allow_html=True)
                with header_cols[6]:
                    st.markdown('<p class="payment-header">Actual Fee</p>', unsafe_allow_html=True)
                with header_cols[7]:
                    st.markdown('<p class="payment-header">Discrepancy</p>', unsafe_allow_html=True)
                with header_cols[8]:
                    st.markdown('<p class="payment-header">Notes</p>', unsafe_allow_html=True)
                
                # Display each row with editable notes
                for index, row in df.iterrows():
                    cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 3])
                    
                    with cols[0]:
                        st.write(row["Provider"])
                    with cols[1]:
                        st.write(row["Period"])
                    with cols[2]:
                        st.write(row["Frequency"])
                    with cols[3]:
                        st.write(row["Received"])
                    with cols[4]:
                        st.write(row["Total Assets"])
                    with cols[5]:
                        st.write(row["Expected Fee"])
                    with cols[6]:
                        st.write(row["Actual Fee"])
                    with cols[7]:
                        st.write(row["Discrepancy"])
                    with cols[8]:
                        new_note = st.text_input(
                            "Notes",
                            value=row["Notes"],
                            key=f"note_{row['payment_id']}",
                            label_visibility="collapsed"
                        )
                        if new_note != row["Notes"]:
                            handle_note_edit(row["payment_id"], new_note)

            # Contracts Section
            col1, col2 = st.columns([1, 1])

    elif st.session_state.current_page == 'Manage Clients':
        st.title("⚙️ Manage Clients")
        st.write("Coming soon...")
        
    elif st.session_state.current_page == 'Bulk Payment Entry':
        st.title("📝 Bulk Payment Entry")
        st.write("Coming soon...")

if __name__ == "__main__":
    main() 