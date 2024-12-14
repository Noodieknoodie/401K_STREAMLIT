import streamlit as st
from utils.client_data import (
    get_consolidated_client_data,  # New optimized query
    get_client_details_optimized as get_client_details,  # Optimized replacements
    get_active_contract_optimized as get_active_contract,
    get_latest_payment_optimized as get_latest_payment
)
from utils.utils import calculate_rate_conversions  # Still need this utility
from utils.debug_logger import debug

def show_client_metrics(client_id):
    """Display the client metrics section of the dashboard."""
    # Get all data in a single query
    data = get_consolidated_client_data(client_id)
    if not data:
        debug.log_ui_interaction(
            action="metrics_load_error",
            element="dashboard_metrics",
            data={
                "error": "no_client_data",
                "client_id": client_id
            }
        )
        return
    
    debug.log_ui_interaction(
        action="load_client_metrics",
        element="dashboard_metrics",
        data={
            "client_id": client_id,
            "has_contract": bool(data['active_contract']),
            "has_payment": bool(data['latest_payment'])
        }
    )
    
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
            
        debug.log_ui_interaction(
            action="display_client_info",
            element="dashboard_metrics",
            data={
                "display_name": data['client']['display_name'],
                "has_full_name": bool(data['client']['full_name']),
                "provider": data['active_contract']['provider_name'] if data['active_contract'] else "N/A",
                "contract_number": data['active_contract']['contract_number'] if data['active_contract'] else "N/A",
                "participants": data['active_contract']['num_people'] if data['active_contract'] else "N/A"
            }
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
                    
                    debug.log_ui_interaction(
                        action="calculate_rate_display",
                        element="dashboard_metrics",
                        data={
                            "fee_type": contract['fee_type'],
                            "rate": rate_value,
                            "schedule": schedule,
                            "has_conversions": bool(rate_conversions)
                        }
                    )
            
            st.metric(
                "Rate", 
                rate_value,
                rate_conversions if rate_conversions else rate_type
            )
        
        with col2:
            schedule = data['active_contract']['payment_schedule'].title() if data['active_contract'] and data['active_contract']['payment_schedule'] else "N/A"
            st.metric("Payment Schedule", schedule)
        
        with col3:
            last_payment = 'No payments'
            payment_date = None
            if data['latest_payment']:
                payment = data['latest_payment']
                if payment['actual_fee']:
                    last_payment = f"${payment['actual_fee']:,.2f}"
                    payment_date = payment['received_date']
                    
                    debug.log_ui_interaction(
                        action="display_last_payment",
                        element="dashboard_metrics",
                        data={
                            "amount": payment['actual_fee'],
                            "date": payment_date
                        }
                    )
            st.metric("Last Payment", last_payment, payment_date)
        
        with col4:
            aum_value = 'Not available'
            aum_date = None
            if data['latest_payment']:
                payment = data['latest_payment']
                if payment['total_assets']:
                    aum_value = f"${payment['total_assets']:,.2f}"
                    aum_date = f"Q{payment['quarter']} {payment['year']}"
                    
                    debug.log_ui_interaction(
                        action="display_last_aum",
                        element="dashboard_metrics",
                        data={
                            "amount": payment['total_assets'],
                            "period": aum_date
                        }
                    )
            st.metric("Last Recorded AUM", aum_value, aum_date)
            
        debug.log_ui_interaction(
            action="display_metrics_complete",
            element="dashboard_metrics",
            data={
                "client_id": client_id,
                "rate": rate_value,
                "schedule": schedule,
                "last_payment": last_payment,
                "last_aum": aum_value
            }
        ) 