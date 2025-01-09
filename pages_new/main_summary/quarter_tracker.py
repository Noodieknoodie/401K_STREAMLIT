"""
Quarter Payment Tracker Module
============================
Sidebar component for accurate payment tracking in arrears.
"""

import streamlit as st
from datetime import datetime
from utils.utils import (
    get_database_connection,
    format_currency_ui,
)

def get_period_payments(quarter: int, year: int) -> dict:
    """Get accurate payment data for tracking period."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get all active clients with their contracts
        cursor.execute("""
            SELECT 
                c.client_id,
                c.display_name,
                con.contract_id,
                con.payment_schedule,
                con.fee_type,
                con.percent_rate,
                con.flat_rate
            FROM clients c
            JOIN contracts con ON c.client_id = con.client_id
            WHERE con.active = 'TRUE'
            ORDER BY c.display_name
        """)
        
        clients = cursor.fetchall()
        
        # Track payment status
        complete = []
        partial = []
        outstanding = []
        total_due = 0
        total_received = 0
        
        for client in clients:
            # Get payments for the period
            cursor.execute("""
                SELECT 
                    received_date,
                    actual_fee,
                    total_assets
                FROM payments
                WHERE client_id = ?
                AND applied_start_quarter = ?
                AND applied_start_year = ?
                ORDER BY received_date
            """, (client[0], quarter, year))
            
            payments = cursor.fetchall()
            
            # Calculate expected fee
            expected = None
            if client[4] == 'flat':  # Flat rate
                expected = client[6]  # flat_rate
            elif client[4] == 'percentage' and payments and payments[0][2]:  # Has AUM
                expected = client[5] * payments[0][2]  # percent_rate * total_assets
            
            received = sum(p[1] for p in payments if p[1]) if payments else 0
            
            if expected:
                total_due += expected
            total_received += received
            
            status = {
                'name': client[1],
                'schedule': client[3],
                'expected': expected,
                'received': received,
                'payment_count': len(payments)
            }
            
            # Categorize based on schedule
            if client[3] == 'monthly':
                if len(payments) == 3:
                    complete.append(status)
                elif payments:
                    partial.append(status)
                else:
                    outstanding.append(status)
            else:  # Quarterly
                if received >= (expected or 0) and received > 0:
                    complete.append(status)
                elif payments:
                    partial.append(status)
                else:
                    outstanding.append(status)
        
        return {
            'complete': complete,
            'partial': partial,
            'outstanding': outstanding,
            'total_due': total_due,
            'total_received': total_received
        }
    finally:
        conn.close()

def show_quarter_tracker():
    """Display compact payment tracking sidebar."""
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_quarter = (current_month - 1) // 3 + 1
    
    # Default to previous quarter
    default_quarter = 4 if current_quarter == 1 else current_quarter - 1
    default_year = current_year - 1 if current_quarter == 1 else current_year
    
    with st.sidebar:
        st.markdown("### Collections Dashboard")
        
        # Simple period selection
        col1, col2 = st.columns([1, 1])
        with col1:
            # Get year range from database
            conn = get_database_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(applied_start_year), MAX(applied_start_year) FROM payments")
            min_year, max_year = cursor.fetchone()
            conn.close()
            
            selected_year = st.selectbox(
                "Year",
                options=range(min_year, max_year + 2),
                index=list(range(min_year, max_year + 2)).index(default_year)
            )
        
        with col2:
            selected_quarter = st.selectbox(
                "Quarter",
                options=[1, 2, 3, 4],
                index=[1, 2, 3, 4].index(default_quarter)
            )
        
        data = get_period_payments(selected_quarter, selected_year)
        
        # Calculate meaningful metrics
        total_clients = len(data['outstanding']) + len(data['partial']) + len(data['complete'])
        clients_paid = len(data['complete']) + len(data['partial'])
        
        # Key metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Clients Paid",
                f"{clients_paid}/{total_clients}",
                help=f"Clients who have made full or partial payments this quarter"
            )
        with col2:
            st.metric(
                "Collected",
                format_currency_ui(data['total_received']),
                help="Total amount collected this quarter"
            )
        
        st.divider()
        
        # Custom CSS for compact display
        st.markdown("""
            <style>
                div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
                    padding: 0.25rem 0;
                    border-bottom: 1px solid rgba(49, 51, 63, 0.2);
                }
                div[data-testid="column"] > div > div > p {
                    margin: 0;
                    padding: 0;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Tabbed sections
        tab1, tab2, tab3 = st.tabs(["Outstanding", "Partial", "Complete"])
        
        with tab1:
            if data['outstanding']:
                for client in data['outstanding']:
                    cols = st.columns([3, 2, 2])
                    with cols[0]:
                        st.markdown(f"**{client['name']}**")
                    with cols[1]:
                        schedule = 'Monthly | 0/3' if client['schedule'] == 'monthly' else 'Quarterly'
                        st.markdown(f"<p style='color: #666;'>{schedule}</p>", unsafe_allow_html=True)
                    with cols[2]:
                        amount = format_currency_ui(client['expected']) if client['expected'] else 'TBD'
                        st.markdown(f"<p style='color: #ff4b4b; text-align: right;'>{amount}</p>", unsafe_allow_html=True)
            else:
                st.caption("No outstanding payments")
        
        with tab2:
            if data['partial']:
                for client in data['partial']:
                    cols = st.columns([3, 2, 2])
                    with cols[0]:
                        st.markdown(f"**{client['name']}**")
                    with cols[1]:
                        schedule = f"Monthly | {client['payment_count']}/3" if client['schedule'] == 'monthly' else 'Quarterly'
                        st.markdown(f"<p style='color: #666;'>{schedule}</p>", unsafe_allow_html=True)
                    with cols[2]:
                        remaining = (client['expected'] or 0) - client['received']
                        if remaining > 0 and client['received'] > 0:
                            st.markdown(f"<p style='color: #ffa726; text-align: right;'>{format_currency_ui(remaining)} / {format_currency_ui(client['expected'])}</p>", unsafe_allow_html=True)
                        else:
                            amount = format_currency_ui(remaining if remaining > 0 else client['received'])
                            st.markdown(f"<p style='color: #ffa726; text-align: right;'>{amount}</p>", unsafe_allow_html=True)
            else:
                st.caption("No partial payments")
        
        with tab3:
            if data['complete']:
                for client in data['complete']:
                    cols = st.columns([3, 2, 2])
                    with cols[0]:
                        st.markdown(f"**{client['name']}**")
                    with cols[1]:
                        st.markdown(f"<p style='color: #666;'>{client['schedule'].capitalize()}</p>", unsafe_allow_html=True)
                    with cols[2]:
                        st.markdown(f"<p style='color: #28a745; text-align: right;'>{format_currency_ui(client['received'])}</p>", unsafe_allow_html=True)
            else:
                st.caption("No completed payments")

if __name__ == "__main__":
    show_quarter_tracker()