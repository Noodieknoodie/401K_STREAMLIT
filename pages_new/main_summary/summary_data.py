from typing import Dict, List, Optional, Tuple, Any, Union
import streamlit as st
from datetime import datetime
import pandas as pd
from utils.utils import get_database_connection

class SummaryDataError(Exception):
    """Custom exception for summary data processing errors."""
    pass

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_summary_year_data(year: int) -> Dict[str, Any]:
    """Get consolidated payment data for a specific year.
    
    Args:
        year: The year to get data for
        
    Returns:
        Dictionary containing:
        - quarterly_totals: Dict mapping client_id to quarter totals
        - client_metrics: Dict mapping client_id to annual metrics
        - overall_metrics: Dict of overall annual metrics
        
    Raises:
        SummaryDataError: If there's an error processing the data
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get quarterly payment data
        cursor.execute("""
            WITH QuarterlyData AS (
                SELECT 
                    c.client_id,
                    c.display_name,
                    p.applied_start_quarter as quarter,
                    SUM(p.actual_fee) as total_fees,
                    AVG(NULLIF(p.total_assets, 0)) as avg_aum,
                    MAX(con.num_people) as participant_count,
                    con.provider_name,
                    con.contract_number,
                    con.payment_schedule,
                    con.fee_type,
                    CASE 
                        WHEN con.fee_type = 'percentage' THEN con.percent_rate
                        ELSE con.flat_rate
                    END as rate,
                    COUNT(p.payment_id) as payment_count
                FROM clients c
                LEFT JOIN payments p ON c.client_id = p.client_id
                LEFT JOIN contracts con ON p.contract_id = con.contract_id
                WHERE p.applied_start_year = ?
                  AND p.actual_fee IS NOT NULL
                GROUP BY 
                    c.client_id, 
                    c.display_name, 
                    p.applied_start_quarter
            )
            SELECT 
                client_id,
                display_name,
                quarter,
                total_fees,
                avg_aum,
                participant_count,
                provider_name,
                contract_number,
                payment_schedule,
                fee_type,
                rate,
                payment_count
            FROM QuarterlyData
            ORDER BY display_name, quarter
        """, (year,))
        
        quarterly_data = cursor.fetchall()
        
        # Get previous year data for YoY calculations
        cursor.execute("""
            SELECT 
                c.client_id,
                SUM(COALESCE(p.actual_fee, 0)) as prev_year_total,
                COUNT(DISTINCT CASE WHEN p.actual_fee > 0 THEN p.payment_id END) as payment_count
            FROM clients c
            LEFT JOIN payments p ON c.client_id = p.client_id
            WHERE p.applied_start_year = ?
            GROUP BY c.client_id
        """, (year - 1,))
        
        prev_year_data = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        
        # Process data into usable format
        quarterly_totals: Dict[int, Dict[str, Any]] = {}
        client_metrics: Dict[int, Dict[str, Any]] = {}
        
        for row in quarterly_data:
            (client_id, name, quarter, fees, aum, participants,
             provider, contract_num, schedule, fee_type, rate, payment_count) = row
            
            # Initialize client data if needed
            if client_id not in quarterly_totals:
                quarterly_totals[client_id] = {
                    'name': name,
                    'Q1': 0.0, 'Q2': 0.0, 'Q3': 0.0, 'Q4': 0.0,
                    'provider': provider,
                    'contract_number': contract_num,
                    'schedule': schedule,
                    'fee_type': fee_type,
                    'rate': rate
                }
                client_metrics[client_id] = {
                    'total_fees': 0.0,
                    'avg_aum': 0.0,
                    'aum_samples': 0,
                    'avg_participants': participants or 0,
                    'payment_count': 0
                }
            
            # Update quarterly totals
            if quarter and fees:
                quarterly_totals[client_id][f'Q{quarter}'] = fees
                client_metrics[client_id]['total_fees'] = (
                    client_metrics[client_id]['total_fees'] + fees
                )
            
            # Update AUM with proper averaging
            if aum:
                current_avg = client_metrics[client_id]['avg_aum']
                current_count = client_metrics[client_id]['aum_samples']
                new_count = current_count + 1
                new_avg = ((current_avg * current_count) + aum) / new_count
                client_metrics[client_id]['avg_aum'] = new_avg
                client_metrics[client_id]['aum_samples'] = new_count
            
            client_metrics[client_id]['payment_count'] += payment_count or 0
            
            # Calculate YoY growth
            if client_id in prev_year_data:
                prev_total, prev_count = prev_year_data[client_id]
                if prev_total > 0 and prev_count > 0:
                    client_metrics[client_id]['yoy_growth'] = (
                        (client_metrics[client_id]['total_fees'] - prev_total)
                        / prev_total * 100
                    )
                else:
                    client_metrics[client_id]['yoy_growth'] = None
            else:
                client_metrics[client_id]['yoy_growth'] = None
        
        # Calculate overall metrics safely
        active_clients = len([
            cid for cid, metrics in client_metrics.items()
            if metrics['payment_count'] > 0
        ])
        
        total_fees = sum(
            metrics['total_fees']
            for metrics in client_metrics.values()
        )
        
        prev_year_total = sum(
            total for total, count in prev_year_data.values()
            if count > 0
        )
        
        overall_metrics = {
            'total_fees': total_fees,
            'active_clients': active_clients,
            'avg_fee_per_client': (
                total_fees / active_clients if active_clients > 0 else 0
            ),
            'yoy_growth': (
                ((total_fees - prev_year_total) / prev_year_total * 100)
                if prev_year_total > 0 else None
            )
        }
        
        return {
            'quarterly_totals': quarterly_totals,
            'client_metrics': client_metrics,
            'overall_metrics': overall_metrics
        }
        
    except Exception as e:
        raise SummaryDataError(f"Error processing summary data: {str(e)}")
    finally:
        conn.close()

@st.cache_data
def get_available_years() -> List[int]:
    """Get list of years with payment data.
    
    Returns:
        List of years in descending order
    
    Raises:
        SummaryDataError: If there's an error accessing the database
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT applied_start_year 
            FROM payments 
            WHERE actual_fee IS NOT NULL
              AND applied_start_year IS NOT NULL
            ORDER BY applied_start_year DESC
        """)
        years = [row[0] for row in cursor.fetchall()]
        return years if years else []
    except Exception as e:
        raise SummaryDataError(f"Error getting available years: {str(e)}")
    finally:
        conn.close()