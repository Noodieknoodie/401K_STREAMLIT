#utils/triggers.py

"""
Triggers Module
=============

This module manages SQLite triggers that maintain summary table consistency.
It provides functions to create and manage triggers that automatically update
summary tables when payments are added, modified, or deleted.

Key Components:
- Trigger creation/management for quarterly summaries
- Trigger creation/management for yearly summaries  
- Trigger creation/management for client metrics
- Helper functions for trigger maintenance
"""

from typing import List
from .utils import get_database_connection

def create_summary_triggers() -> bool:
    """Create all necessary triggers for maintaining summary tables."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # First drop existing triggers
        drop_all_triggers()
        
        # Create triggers for payment changes
        triggers = [
            # After INSERT trigger for quarterly summaries
            """
            CREATE TRIGGER IF NOT EXISTS update_quarterly_after_insert
            AFTER INSERT ON payments
            BEGIN
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    NEW.client_id,
                    NEW.applied_start_year,
                    NEW.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = NEW.client_id
                AND applied_start_year = NEW.applied_start_year
                AND applied_start_quarter = NEW.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;
            END;
            """,

            # After UPDATE trigger for quarterly summaries
            """
            CREATE TRIGGER IF NOT EXISTS update_quarterly_after_update
            AFTER UPDATE ON payments
            BEGIN
                -- Update old quarter summary
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    OLD.client_id,
                    OLD.applied_start_year,
                    OLD.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = OLD.client_id
                AND applied_start_year = OLD.applied_start_year
                AND applied_start_quarter = OLD.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;

                -- Update new quarter summary
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    NEW.client_id,
                    NEW.applied_start_year,
                    NEW.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = NEW.client_id
                AND applied_start_year = NEW.applied_start_year
                AND applied_start_quarter = NEW.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;
            END;
            """,

            # After DELETE trigger for quarterly summaries
            """
            CREATE TRIGGER IF NOT EXISTS update_quarterly_after_delete
            AFTER DELETE ON payments
            BEGIN
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    OLD.client_id,
                    OLD.applied_start_year,
                    OLD.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = OLD.client_id
                AND applied_start_year = OLD.applied_start_year
                AND applied_start_quarter = OLD.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;

                -- Remove empty summaries
                DELETE FROM quarterly_summaries
                WHERE payment_count = 0;
            END;
            """,

            # After quarterly summary changes, update yearly summary
            """
            CREATE TRIGGER IF NOT EXISTS update_yearly_after_quarterly_change
            AFTER INSERT ON quarterly_summaries
            BEGIN
                INSERT INTO yearly_summaries (
                    client_id, year, total_payments, total_assets,
                    payment_count, avg_payment, yoy_growth, last_updated
                )
                SELECT 
                    NEW.client_id,
                    NEW.year,
                    COALESCE(SUM(total_payments), 0),
                    AVG(total_assets),
                    SUM(payment_count),
                    CASE 
                        WHEN SUM(payment_count) > 0 
                        THEN COALESCE(SUM(total_payments), 0) / SUM(payment_count)
                        ELSE 0
                    END,
                    CASE
                        WHEN (SELECT total_payments FROM yearly_summaries 
                              WHERE client_id = NEW.client_id 
                              AND year = NEW.year - 1) > 0
                        THEN ((COALESCE(SUM(total_payments), 0) - 
                              (SELECT total_payments FROM yearly_summaries 
                               WHERE client_id = NEW.client_id 
                               AND year = NEW.year - 1)) /
                              (SELECT total_payments FROM yearly_summaries 
                               WHERE client_id = NEW.client_id 
                               AND year = NEW.year - 1)) * 100
                        ELSE NULL
                    END,
                    datetime('now')
                FROM quarterly_summaries
                WHERE client_id = NEW.client_id AND year = NEW.year
                GROUP BY client_id, year
                ON CONFLICT(client_id, year) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    yoy_growth = excluded.yoy_growth,
                    last_updated = excluded.last_updated;
            END;
            """,

            # After any payment change, update client metrics
            """
            CREATE TRIGGER IF NOT EXISTS update_client_metrics_after_payment_change
            AFTER INSERT ON payments
            BEGIN
                INSERT INTO client_metrics (
                    client_id, last_payment_date, last_payment_amount,
                    last_payment_quarter, last_payment_year,
                    total_ytd_payments, avg_quarterly_payment,
                    last_recorded_assets, last_updated
                )
                SELECT 
                    p.client_id,
                    p.received_date,
                    p.actual_fee,
                    p.applied_start_quarter,
                    p.applied_start_year,
                    (SELECT COALESCE(SUM(actual_fee), 0)
                     FROM payments 
                     WHERE client_id = p.client_id 
                     AND applied_start_year = strftime('%Y', 'now')),
                    (SELECT AVG(total_payments)
                     FROM quarterly_summaries
                     WHERE client_id = p.client_id
                     AND total_payments > 0
                     ORDER BY year DESC, quarter DESC
                     LIMIT 4),
                    p.total_assets,
                    datetime('now')
                FROM payments p
                WHERE p.payment_id = NEW.payment_id
                ON CONFLICT(client_id) DO UPDATE SET
                    last_payment_date = excluded.last_payment_date,
                    last_payment_amount = excluded.last_payment_amount,
                    last_payment_quarter = excluded.last_payment_quarter,
                    last_payment_year = excluded.last_payment_year,
                    total_ytd_payments = excluded.total_ytd_payments,
                    avg_quarterly_payment = excluded.avg_quarterly_payment,
                    last_recorded_assets = excluded.last_recorded_assets,
                    last_updated = excluded.last_updated;
            END;
            """
        ]

        # Create each trigger
        for trigger in triggers:
            cursor.execute(trigger)
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error creating triggers: {str(e)}")
        return False
    finally:
        conn.close()

def drop_all_triggers() -> bool:
    """Drop all existing summary table triggers."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get list of all triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
        triggers = cursor.fetchall()
        
        # Drop each trigger
        for trigger in triggers:
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger[0]};")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error dropping triggers: {str(e)}")
        return False
    finally:
        conn.close()

def check_triggers_exist() -> List[str]:
    """Check which summary triggers exist.
    
    Returns:
        List of existing trigger names
    """
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get all triggers that are part of our summary system
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='trigger'
            AND name LIKE 'update_%';
        """)
        
        return [row[0] for row in cursor.fetchall()]
        
    finally:
        conn.close()

def verify_trigger_functionality() -> bool:
    """Verify that all summary triggers are functioning correctly."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Insert test payment
        cursor.execute("""
            INSERT INTO payments (
                client_id, contract_id, received_date,
                applied_start_quarter, applied_start_year,
                applied_end_quarter, applied_end_year,
                total_assets, actual_fee, method
            ) VALUES (
                1, 1, date('now'),
                1, strftime('%Y', 'now'),
                1, strftime('%Y', 'now'),
                100000, 1000, 'TEST'
            );
        """)
        
        # Verify quarterly summary was created
        cursor.execute("""
            SELECT COUNT(*)
            FROM quarterly_summaries
            WHERE client_id = 1
            AND year = strftime('%Y', 'now')
            AND quarter = 1;
        """)
        quarterly_exists = cursor.fetchone()[0] > 0
        
        # Verify yearly summary was updated
        cursor.execute("""
            SELECT COUNT(*)
            FROM yearly_summaries
            WHERE client_id = 1
            AND year = strftime('%Y', 'now');
        """)
        yearly_exists = cursor.fetchone()[0] > 0
        
        # Verify client metrics were updated
        cursor.execute("""
            SELECT COUNT(*)
            FROM client_metrics
            WHERE client_id = 1;
        """)
        metrics_exist = cursor.fetchone()[0] > 0
        
        # Cleanup test data
        cursor.execute("DELETE FROM payments WHERE method = 'TEST';")
        conn.commit()
        
        return quarterly_exists and yearly_exists and metrics_exist
        
    except Exception as e:
        print(f"Error verifying triggers: {str(e)}")
        return False
    finally:
        conn.close()

def initialize_triggers() -> bool:
    """Initialize or reinitialize all summary triggers."""
    try:
        # Drop existing triggers
        if not drop_all_triggers():
            return False
            
        # Create new triggers
        if not create_summary_triggers():
            return False
            
        # Verify functionality
        if not verify_trigger_functionality():
            return False
            
        return True
        
    except Exception as e:
        print(f"Error initializing triggers: {str(e)}")
        return False