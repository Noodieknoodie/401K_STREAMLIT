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

def calculate_expected_fee(fee_type: str, flat_rate: float, percent_rate: float, total_assets: float) -> float:
    """Calculate expected fee based on fee type and rates."""
    if fee_type == 'flat':
        return flat_rate
    elif fee_type == 'percentage' and total_assets:
        return percent_rate * total_assets
    return None

def get_payment_status(schedule: str, payment_count: int, expected: float, received: float, total_contracts: int = 1) -> str:
    """Determine payment status based on schedule and amounts."""
    if schedule == 'monthly':
        required_payments = 3 * total_contracts
        if payment_count >= required_payments:
            return 'complete'
        elif payment_count > 0:
            return 'partial'
        return 'outstanding'
    else:  # Quarterly
        if received >= (expected or 0) and received > 0:
            return 'complete'
        elif received > 0:
            return 'partial'
        return 'outstanding'

def display_payment_row(item: dict, status_type: str):
    """Unified display logic for payment rows."""
    cols = st.columns([3, 2, 2])
    with cols[0]:
        st.markdown(f"**{item['name']}**")
    with cols[1]:
        schedule = 'Monthly | {}/3'.format(item['payment_count']) if item['schedule'] == 'monthly' else 'Quarterly'
        st.markdown(f"<p style='color: #666;'>{schedule}</p>", unsafe_allow_html=True)
    with cols[2]:
        amount = format_currency_ui(item['expected']) if item['expected'] else 'TBD'
        color = {
            'outstanding': '#ff4b4b',
            'partial': '#ffa726',
            'complete': '#28a745'
        }.get(status_type, '#666')
        st.markdown(f"<p style='color: {color}; text-align: right;'>{amount}</p>", unsafe_allow_html=True)

def get_period_payments(quarter: int, year: int, view_type: str = 'client') -> dict:
    """Get accurate payment data for tracking period."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        if view_type == 'client':
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
                expected = calculate_expected_fee(
                    client[4],  # fee_type
                    client[6],  # flat_rate
                    client[5],  # percent_rate
                    payments[0][2] if payments and payments[0][2] else None  # total_assets
                )
                
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
                
                # Determine status
                payment_status = get_payment_status(client[3], len(payments), expected, received)
                if payment_status == 'complete':
                    complete.append(status)
                elif payment_status == 'partial':
                    partial.append(status)
                else:
                    outstanding.append(status)
        
        else:  # Provider view
            # Get all active contracts grouped by provider
            cursor.execute("""
                SELECT 
                    con.provider_name,
                    con.payment_schedule,
                    con.fee_type,
                    con.percent_rate,
                    con.flat_rate,
                    con.contract_id,
                    con.client_id
                FROM contracts con
                WHERE con.active = 'TRUE'
                AND con.provider_name IS NOT NULL
                ORDER BY con.provider_name
            """)
            
            contracts = cursor.fetchall()
            
            # Track payment status
            complete = []
            partial = []
            outstanding = []
            total_due = 0
            total_received = 0
            
            # Group contracts by provider
            provider_contracts = {}
            for contract in contracts:
                provider = contract[0]
                if provider not in provider_contracts:
                    provider_contracts[provider] = []
                provider_contracts[provider].append(contract)
            
            for provider, provider_contracts_list in provider_contracts.items():
                provider_expected = 0
                provider_received = 0
                provider_payments = 0
                payment_schedule = provider_contracts_list[0][1]  # Use first contract's schedule
                
                for contract in provider_contracts_list:
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
                    """, (contract[6], quarter, year))
                    
                    payments = cursor.fetchall()
                    
                    # Calculate expected fee
                    expected = calculate_expected_fee(
                        contract[2],  # fee_type
                        contract[4],  # flat_rate
                        contract[3],  # percent_rate
                        payments[0][2] if payments and payments[0][2] else None  # total_assets
                    )
                    
                    received = sum(p[1] for p in payments if p[1]) if payments else 0
                    
                    if expected:
                        provider_expected += expected
                        total_due += expected
                    provider_received += received
                    total_received += received
                    provider_payments += len(payments)
                
                status = {
                    'name': provider,
                    'schedule': payment_schedule,
                    'expected': provider_expected,
                    'received': provider_received,
                    'payment_count': provider_payments
                }
                
                # Determine status
                payment_status = get_payment_status(
                    payment_schedule,
                    provider_payments,
                    provider_expected,
                    provider_received,
                    len(provider_contracts_list)
                )
                if payment_status == 'complete':
                    complete.append(status)
                elif payment_status == 'partial':
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
    # Initialize view preference in session state if not exists
    if 'tracker_view' not in st.session_state:
        st.session_state.tracker_view = 'client'
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_quarter = (current_month - 1) // 3 + 1
    
    # Default to previous quarter
    default_quarter = 4 if current_quarter == 1 else current_quarter - 1
    default_year = current_year - 1 if current_quarter == 1 else current_year
    
    with st.sidebar:
        st.markdown("### Collections Dashboard")
        
        # Single view selector with radio buttons
        view_type = st.radio(
            "View By",
            options=['client', 'provider'],
            format_func=lambda x: x.capitalize(),
            horizontal=True,
            label_visibility="collapsed",
            key='tracker_view'  # This automatically handles state
        )
        
        st.divider()
        
        # Period selection
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
        
        try:
            data = get_period_payments(selected_quarter, selected_year, view_type)
            
            # Calculate meaningful metrics
            total_entities = len(data['outstanding']) + len(data['partial']) + len(data['complete'])
            entities_paid = len(data['complete']) + len(data['partial'])
            metric_label = "Clients Paid" if view_type == 'client' else "Providers Paid"
            
            # Key metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    metric_label,
                    f"{entities_paid}/{total_entities}",
                    help=f"{'Clients' if view_type == 'client' else 'Providers'} who have made full or partial payments this quarter"
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
                    for item in data['outstanding']:
                        display_payment_row(item, 'outstanding')
                else:
                    st.caption("No outstanding payments")
            
            with tab2:
                if data['partial']:
                    for item in data['partial']:
                        display_payment_row(item, 'partial')
                else:
                    st.caption("No partial payments")
            
            with tab3:
                if data['complete']:
                    for item in data['complete']:
                        display_payment_row(item, 'complete')
                else:
                    st.caption("No completed payments")
                    
        except Exception as e:
            st.error(f"Error loading payment data: {str(e)}")
            st.error("Please try refreshing the page. If the error persists, contact support.")

if __name__ == "__main__":
    show_quarter_tracker()