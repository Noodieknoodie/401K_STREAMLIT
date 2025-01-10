# summary_data.py
from typing import Dict, List, Optional, Tuple, Any, Union
import streamlit as st
from datetime import datetime
import pandas as pd
from utils.database import get_database_connection

class SummaryDataError(Exception):
    """Custom exception for summary data processing errors."""
    pass

def get_summary_year_data(year: int) -> Dict[str, Any]:
    """Get consolidated payment data for a specific year using summary tables."""
    from utils.utils import ensure_summaries_initialized
    ensure_summaries_initialized()
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get quarterly summary data
        cursor.execute("""
            WITH QuarterlyData AS (
                SELECT 
                    c.client_id,
                    c.display_name,
                    qs.quarter,
                    qs.total_payments as total_fees,
                    qs.total_assets as avg_aum,
                    con.num_people as participant_count,
                    con.provider_name,
                    con.contract_number,
                    con.payment_schedule,
                    con.fee_type,
                    CASE 
                        WHEN con.fee_type = 'percentage' THEN con.percent_rate
                        ELSE con.flat_rate
                    END as rate,
                    qs.payment_count
                FROM clients c
                JOIN quarterly_summaries qs ON c.client_id = qs.client_id
                LEFT JOIN contracts con ON 
                    c.client_id = con.client_id AND 
                    con.active = 'TRUE'
                WHERE qs.year = ?
                ORDER BY c.display_name, qs.quarter
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
        """, (year,))
        
        quarterly_data = cursor.fetchall()
        
        # Get yearly summary data
        cursor.execute("""
            SELECT 
                ys.client_id,
                ys.total_payments as prev_year_total,
                ys.payment_count,
                ys.yoy_growth
            FROM yearly_summaries ys
            WHERE ys.year = ?
        """, (year,))
        
        yearly_data = {row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()}
        
        # Process data into required format
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
            
            # Add YoY metrics if available
            if client_id in yearly_data:
                total, count, yoy = yearly_data[client_id]
                client_metrics[client_id]['yoy_growth'] = yoy
            else:
                client_metrics[client_id]['yoy_growth'] = None
        
        # Calculate overall metrics
        active_clients = len([
            cid for cid, metrics in client_metrics.items()
            if metrics['payment_count'] > 0
        ])
        
        total_fees = sum(
            metrics['total_fees']
            for metrics in client_metrics.values()
        )
        
        prev_year_total = sum(
            total for total, count, _ in yearly_data.values()
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


def get_available_years() -> List[int]:
    """Get list of years with payment data from summary tables."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT year 
            FROM yearly_summaries 
            ORDER BY year DESC
        """)
        years = [row[0] for row in cursor.fetchall()]
        return years if years else []
    except Exception as e:
        raise SummaryDataError(f"Error getting available years: {str(e)}")
    finally:
        conn.close()