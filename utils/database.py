import hashlib
from functools import lru_cache
from typing import List, Optional, Tuple, Dict, Any
import sqlite3
from datetime import datetime, timedelta
from utils.database.connection import get_db_connection

def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments"""
    key = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key.encode()).hexdigest()

@lru_cache(maxsize=128)
def get_cached_payment_history(
    client_id: int,
    cache_key: str,
    offset: int = 0,
    limit: int = 25,
    years: Optional[List[int]] = None,
    quarters: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """Cached version of get_paginated_payment_history"""
    return get_paginated_payment_history(client_id, offset, limit, years, quarters)

def get_paginated_payment_history(
    client_id: int,
    offset: int = 0,
    limit: int = 25,
    years: Optional[List[int]] = None,
    quarters: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """Get paginated payment history with optional year/quarter filters"""
    
    # Generate cache key for these exact parameters
    cache_key = get_cache_key(client_id, offset, limit, years, quarters)
    
    # Try to get from cache first
    try:
        return get_cached_payment_history(client_id, cache_key, offset, limit, years, quarters)
    except Exception:
        # If cache fails, proceed with normal query
        conn = get_db_connection()
        
        query = """
            SELECT 
                p.id,
                p.client_id,
                p.payment_date,
                p.amount,
                p.payment_type as payment_method,
                p.note,
                p.created_at,
                p.updated_at
            FROM payments p
            WHERE p.client_id = ?
        """
        params = [client_id]

        if years:
            year_placeholders = ','.join('?' * len(years))
            query += f" AND strftime('%Y', payment_date) IN ({year_placeholders})"
            params.extend(str(year) for year in years)

        if quarters:
            quarter_case = """
                CASE 
                    WHEN strftime('%m', payment_date) IN ('01','02','03') THEN 1
                    WHEN strftime('%m', payment_date) IN ('04','05','06') THEN 2
                    WHEN strftime('%m', payment_date) IN ('07','08','09') THEN 3
                    WHEN strftime('%m', payment_date) IN ('10','11','12') THEN 4
                END
            """
            quarter_placeholders = ','.join('?' * len(quarters))
            query += f" AND {quarter_case} IN ({quarter_placeholders})"
            params.extend(quarters)

        query += " ORDER BY payment_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = conn.execute(query, params)
        payments = [dict(payment) for payment in cursor.fetchall()]
        conn.close()
        return payments 