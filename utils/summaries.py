"""
Summaries Module
===============

This module handles the maintenance and updates of summary tables that optimize
query performance for the 401K Payment Tracker application.

Key Components:
- Quarterly summary management
- Yearly summary calculations
- Client metrics updates
- Bulk data population
- Cache invalidation
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .database import get_database_connection

def update_all_summaries(client_id: int, year: int, quarter: int) -> bool:
    """
    Update all summaries (quarterly, yearly, and client metrics) in a single transaction.
    This is the preferred way to update summaries as it maintains data consistency
    and avoids database locks.
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Update quarterly first as yearly depends on it
        success = _update_quarterly_summary(cursor, client_id, year, quarter)
        if not success:
            raise Exception("Failed to update quarterly summary")
            
        # Update yearly next as it depends on quarterly
        success = _update_yearly_summary(cursor, client_id, year)
        if not success:
            raise Exception("Failed to update yearly summary")
            
        # Finally update client metrics
        success = _update_client_metrics(cursor, client_id)
        if not success:
            raise Exception("Failed to update client metrics")
        
        # If we got here, all updates succeeded
        conn.commit()
        return True
        
    except Exception as e:
        # If anything fails, roll back all changes
        conn.rollback()
        print(f"Error updating summaries: {str(e)}")
        return False
    finally:
        conn.close()

def _update_quarterly_summary(cursor: sqlite3.Cursor, client_id: int, year: int, quarter: int) -> bool:
    """Internal function to update quarterly summary using existing cursor."""
    try:
        # Get payment data for the quarter
        cursor.execute("""
            SELECT 
                SUM(actual_fee) as total_payments,
                AVG(total_assets) as avg_assets,
                COUNT(*) as payment_count,
                MAX(expected_fee) as expected_total
            FROM payments
            WHERE client_id = ?
            AND applied_start_year = ?
            AND applied_start_quarter = ?
        """, (client_id, year, quarter))
        
        payment_data = cursor.fetchone()
        
        if not payment_data or payment_data[0] is None:
            # No payments for this quarter, delete any existing summary
            cursor.execute("""
                DELETE FROM quarterly_summaries
                WHERE client_id = ? AND year = ? AND quarter = ?
            """, (client_id, year, quarter))
        else:
            # Calculate average payment
            avg_payment = payment_data[0] / payment_data[2] if payment_data[2] > 0 else 0
            
            # Upsert the quarterly summary
            cursor.execute("""
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(client_id, year, quarter) 
                DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated
            """, (
                client_id, year, quarter,
                payment_data[0],  # total_payments
                payment_data[1],  # avg_assets
                payment_data[2],  # payment_count
                avg_payment,      # avg_payment
                payment_data[3]   # expected_total
            ))
        
        return True
        
    except Exception as e:
        print(f"Error in _update_quarterly_summary: {str(e)}")
        return False

def _update_yearly_summary(cursor: sqlite3.Cursor, client_id: int, year: int) -> bool:
    """Internal function to update yearly summary using existing cursor."""
    try:
        # Get quarterly data for the year
        cursor.execute("""
            SELECT 
                SUM(total_payments) as yearly_total,
                AVG(total_assets) as avg_assets,
                SUM(payment_count) as total_payments
            FROM quarterly_summaries
            WHERE client_id = ? AND year = ?
        """, (client_id, year))
        
        current_year_data = cursor.fetchone()
        
        if not current_year_data or current_year_data[0] is None:
            # No data for this year, delete any existing summary
            cursor.execute("""
                DELETE FROM yearly_summaries
                WHERE client_id = ? AND year = ?
            """, (client_id, year))
            return True
        
        # Get previous year's total for YoY calculation
        cursor.execute("""
            SELECT total_payments
            FROM yearly_summaries
            WHERE client_id = ? AND year = ?
        """, (client_id, year - 1))
        
        prev_year_total = cursor.fetchone()
        prev_total = prev_year_total[0] if prev_year_total else None
        
        # Calculate YoY growth
        yoy_growth = None
        if prev_total and prev_total > 0:
            yoy_growth = ((current_year_data[0] - prev_total) / prev_total) * 100
        
        # Calculate average payment
        avg_payment = current_year_data[0] / current_year_data[2] if current_year_data[2] > 0 else 0
        
        # Upsert the yearly summary
        cursor.execute("""
            INSERT INTO yearly_summaries (
                client_id, year, total_payments, total_assets,
                payment_count, avg_payment, yoy_growth, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(client_id, year) 
            DO UPDATE SET
                total_payments = excluded.total_payments,
                total_assets = excluded.total_assets,
                payment_count = excluded.payment_count,
                avg_payment = excluded.avg_payment,
                yoy_growth = excluded.yoy_growth,
                last_updated = excluded.last_updated
        """, (
            client_id, year,
            current_year_data[0],  # total_payments
            current_year_data[1],  # avg_assets
            current_year_data[2],  # payment_count
            avg_payment,           # avg_payment
            yoy_growth            # yoy_growth
        ))
        
        return True
        
    except Exception as e:
        print(f"Error in _update_yearly_summary: {str(e)}")
        return False

def _update_client_metrics(cursor: sqlite3.Cursor, client_id: int) -> bool:
    """Internal function to update client metrics using existing cursor."""
    try:
        # Get latest payment info
        cursor.execute("""
            SELECT 
                received_date,
                actual_fee,
                applied_start_quarter,
                applied_start_year,
                total_assets
            FROM payments
            WHERE client_id = ?
            ORDER BY received_date DESC, payment_id DESC
            LIMIT 1
        """, (client_id,))
        
        latest_payment = cursor.fetchone()
        
        if not latest_payment:
            # No payments for this client, delete any existing metrics
            cursor.execute("""
                DELETE FROM client_metrics
                WHERE client_id = ?
            """, (client_id,))
            return True
        
        # Get YTD payments
        current_year = datetime.now().year
        cursor.execute("""
            SELECT COALESCE(SUM(actual_fee), 0)
            FROM payments
            WHERE client_id = ?
            AND applied_start_year = ?
        """, (client_id, current_year))
        
        ytd_payments = cursor.fetchone()[0]
        
        # Calculate average quarterly payment
        cursor.execute("""
            SELECT AVG(total_payments)
            FROM quarterly_summaries
            WHERE client_id = ?
            AND total_payments > 0
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """, (client_id,))
        
        avg_quarterly = cursor.fetchone()[0] or 0
        
        # Upsert the client metrics
        cursor.execute("""
            INSERT INTO client_metrics (
                client_id, last_payment_date, last_payment_amount,
                last_payment_quarter, last_payment_year,
                total_ytd_payments, avg_quarterly_payment,
                last_recorded_assets, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(client_id) 
            DO UPDATE SET
                last_payment_date = excluded.last_payment_date,
                last_payment_amount = excluded.last_payment_amount,
                last_payment_quarter = excluded.last_payment_quarter,
                last_payment_year = excluded.last_payment_year,
                total_ytd_payments = excluded.total_ytd_payments,
                avg_quarterly_payment = excluded.avg_quarterly_payment,
                last_recorded_assets = excluded.last_recorded_assets,
                last_updated = excluded.last_updated
        """, (
            client_id,
            latest_payment[0],    # last_payment_date
            latest_payment[1],    # last_payment_amount
            latest_payment[2],    # last_payment_quarter
            latest_payment[3],    # last_payment_year
            ytd_payments,         # total_ytd_payments
            avg_quarterly,        # avg_quarterly_payment
            latest_payment[4]     # last_recorded_assets
        ))
        
        return True
        
    except Exception as e:
        print(f"Error in _update_client_metrics: {str(e)}")
        return False

# Legacy functions for backward compatibility
def update_quarterly_summary(client_id: int, year: int, quarter: int) -> bool:
    """Legacy function - prefer using update_all_summaries instead."""
    return update_all_summaries(client_id, year, quarter)

def update_yearly_summary(client_id: int, year: int) -> bool:
    """Legacy function - prefer using update_all_summaries instead."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        success = _update_yearly_summary(cursor, client_id, year)
        if success:
            conn.commit()
        return success
    except Exception as e:
        print(f"Error updating yearly summary: {str(e)}")
        return False
    finally:
        conn.close()

def update_client_metrics(client_id: int) -> bool:
    """Legacy function - prefer using update_all_summaries instead."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        success = _update_client_metrics(cursor, client_id)
        if success:
            conn.commit()
        return success
    except Exception as e:
        print(f"Error updating client metrics: {str(e)}")
        return False
    finally:
        conn.close()

def populate_all_summaries() -> bool:
    """Populate all summary tables from scratch."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get all client IDs
        cursor.execute("SELECT DISTINCT client_id FROM clients")
        client_ids = [row[0] for row in cursor.fetchall()]
        
        # Get all year/quarter combinations
        cursor.execute("""
            SELECT DISTINCT 
                client_id,
                applied_start_year as year,
                applied_start_quarter as quarter
            FROM payments
            ORDER BY year, quarter
        """)
        periods = cursor.fetchall()
        
        # Clear existing summaries
        cursor.execute("DELETE FROM quarterly_summaries")
        cursor.execute("DELETE FROM yearly_summaries")
        cursor.execute("DELETE FROM client_metrics")
        
        # Process each period
        for client_id, year, quarter in periods:
            update_quarterly_summary(client_id, year, quarter)
        
        # Process each year
        years = set((client_id, year) for client_id, year, _ in periods)
        for client_id, year in years:
            update_yearly_summary(client_id, year)
        
        # Update current metrics for each client
        for client_id in client_ids:
            update_client_metrics(client_id)
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error populating summaries: {str(e)}")
        return False
    finally:
        conn.close()

def get_latest_summaries(client_id: int) -> Dict[str, Any]:
    """Get latest summary data for a client."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get current quarter metrics
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        
        cursor.execute("""
            SELECT 
                qs.total_payments,
                qs.total_assets,
                qs.payment_count,
                qs.avg_payment,
                qs.expected_total,
                cm.last_payment_date,
                cm.last_payment_amount,
                cm.total_ytd_payments,
                cm.avg_quarterly_payment,
                ys.yoy_growth
            FROM quarterly_summaries qs
            LEFT JOIN client_metrics cm ON qs.client_id = cm.client_id
            LEFT JOIN yearly_summaries ys ON 
                qs.client_id = ys.client_id AND 
                qs.year = ys.year
            WHERE qs.client_id = ?
            AND qs.year = ?
            AND qs.quarter = ?
        """, (client_id, current_year, current_quarter))
        
        result = cursor.fetchone()
        
        if not result:
            return {
                'current_quarter': {
                    'total_payments': 0,
                    'total_assets': 0,
                    'payment_count': 0,
                    'avg_payment': 0,
                    'expected_total': 0
                },
                'metrics': {
                    'last_payment_date': None,
                    'last_payment_amount': 0,
                    'total_ytd_payments': 0,
                    'avg_quarterly_payment': 0,
                    'yoy_growth': None
                }
            }
            
        return {
            'current_quarter': {
                'total_payments': result[0],
                'total_assets': result[1],
                'payment_count': result[2],
                'avg_payment': result[3],
                'expected_total': result[4]
            },
            'metrics': {
                'last_payment_date': result[5],
                'last_payment_amount': result[6],
                'total_ytd_payments': result[7],
                'avg_quarterly_payment': result[8],
                'yoy_growth': result[9]
            }
        }
        
    finally:
        conn.close()