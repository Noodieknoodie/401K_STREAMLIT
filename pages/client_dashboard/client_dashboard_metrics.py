# pages\client_dashboard\client_dashboard_metrics.py
import streamlit as st
from utils.client_data import (
    get_consolidated_client_data,  # New optimized query
    get_client_details_optimized as get_client_details,  # Optimized replacements
    get_active_contract_optimized as get_active_contract,
    get_latest_payment_optimized as get_latest_payment
)
from utils.utils import calculate_rate_conversions  # Still need this utility

def show_client_metrics(client_id):
    """Display the client metrics section of the dashboard."""
    # Get all data in a single query
    data = get_consolidated_client_data(client_id)
    if not data:
        return

    # Compact container for metrics
    with st.container():
        # First row - 4 columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Client Name", 
                data['client']['display_name'],
                data['client']['full_name'] if data['client']['full_name'] else None
            )
        with col2:
            st.metric(
                "Provider",
                data['active_contract']['provider_name'] if data['active_contract'] else "N/A"
            )
        with col3:
            st.metric(
                "Contract #",
                data['active_contract']['contract_number'] if data['active_contract'] else "N/A"
            )
        with col4:
            st.metric(
                "Participants",
                data['active_contract']['num_people'] if data['active_contract'] else "N/A"
            )

        # Second row - 4 columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            rate_value = 'N/A'
            rate_type = None
            rate_conversions = None
            if data['active_contract']:
                contract = data['active_contract']
                if contract['fee_type'] == 'percentage':
                    if contract['percent_rate']:
                        rate_value = f"{contract['percent_rate']*100:.3f}%"
                else:
                    if contract['flat_rate']:
                        rate_value = f"${contract['flat_rate']:,.2f}"
                if rate_value != 'N/A':
                    rate_type = contract['fee_type'].title()
                    schedule = contract['payment_schedule'] if contract['payment_schedule'] else None
                    rate_value, rate_conversions = calculate_rate_conversions(
                        rate_value, 
                        contract['fee_type'],
                        schedule
                    )
            st.metric(
                "Rate",
                rate_value,
                rate_conversions if rate_conversions else rate_type
            )

        with col2:
            st.metric(
                "Payment Schedule",
                data['active_contract']['payment_schedule'].title() if data['active_contract'] and data['active_contract']['payment_schedule'] else "N/A"
            )
        with col3:
            last_payment = 'No payments'
            payment_date = None
            if data['latest_payment']:
                payment = data['latest_payment']
                if payment['actual_fee']:
                    last_payment = f"${payment['actual_fee']:,.2f}"
                    payment_date = payment['received_date']
            st.metric("Last Payment", last_payment, payment_date)
        
        # Modified last metric card with edit button
        with col4:
            container = st.container()
            # Use columns for the metric and button
            metric_col, button_col = st.columns([5, 1])
            
            # Metric in left column
            with metric_col:
                aum_value = 'Not available'
                aum_date = None
                if data['latest_payment']:
                    payment = data['latest_payment']
                    if payment['total_assets']:
                        aum_value = f"${payment['total_assets']:,.2f}"
                        aum_date = f"Q{payment['quarter']} {payment['year']}"
                st.metric(
                    "Last Recorded AUM",
                    aum_value,
                    aum_date
                )
            
            # Edit button in right column, aligned with metric
            with button_col:
                st.write("")  # Add spacing to align with metric
                st.write("")  # Add spacing to align with metric
                if st.button("✏️", key="edit_contract", help="Manage Contract"):
                    if 'ui_manager' in st.session_state:
                        ui_manager = st.session_state.ui_manager
                        if data['active_contract']:
                            # Populate form with current contract data
                            ui_manager.open_contract_dialog(
                                client_id=client_id,
                                mode='edit',
                                contract_id=data['active_contract']['contract_id'],
                                initial_data={
                                    'provider_name': data['active_contract']['provider_name'],
                                    'contract_number': data['active_contract']['contract_number'],
                                    'payment_schedule': data['active_contract']['payment_schedule'],
                                    'fee_type': data['active_contract']['fee_type'],
                                    'percent_rate': data['active_contract']['percent_rate'],
                                    'flat_rate': data['active_contract']['flat_rate'],
                                    'num_people': data['active_contract']['num_people']
                                }
                            )
                        else:
                            # Open empty form for new contract
                            ui_manager.open_contract_dialog(client_id=client_id)
                        st.rerun()