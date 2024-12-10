"""
CRITICAL!!! Performance optimization module for client data.
This module provides consolidated database queries to replace multiple separate calls.
The original functions in utils.py remain unchanged for safety and backward compatibility.
"""

import streamlit as st
import json
from .utils import get_database_connection
from .perf_logging import log_db_call, log_event
import time
from typing import Dict, Optional, Any, Tuple

# CRITICAL!!! Cache implementation to prevent redundant DB calls
# Cache structure: {client_id: (data, timestamp)}
_client_cache: Dict[int, Tuple[Dict[str, Any], float]] = {}
CACHE_TTL_SECONDS = 5  # Cache data for 5 seconds

def _get_cached_client_data(client_id: int) -> Optional[Dict[str, Any]]:
    """Get client data from cache if valid."""
    if client_id in _client_cache:
        data, timestamp = _client_cache[client_id]
        if time.time() - timestamp <= CACHE_TTL_SECONDS:
            log_event("cache_hit", {"client_id": client_id})
            return data
        # Clear expired cache entry
        del _client_cache[client_id]
        log_event("cache_expired", {"client_id": client_id})
    log_event("cache_miss", {"client_id": client_id})
    return None

def _cache_client_data(client_id: int, data: Dict[str, Any]) -> None:
    """Cache client data with current timestamp."""
    _client_cache[client_id] = (data, time.time())
    log_event("cache_store", {"client_id": client_id})

@log_db_call
def get_consolidated_client_data(client_id: int) -> Dict[str, Any]:
    """Get consolidated client data with caching."""
    # CRITICAL!!! Check cache first
    cached_data = _get_cached_client_data(client_id)
    if cached_data is not None:
        return cached_data.copy()  # Return a copy to prevent cache corruption

    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Get client info
        cursor.execute("""
            WITH LatestPayment AS (
                SELECT 
                    client_id,
                    actual_fee,
                    received_date,
                    total_assets,
                    applied_start_quarter,
                    applied_start_year
                FROM payments
                WHERE payment_id IN (
                    SELECT MAX(payment_id)
                    FROM payments
                    GROUP BY client_id
                )
            )
            SELECT 
                c.display_name,
                c.full_name,
                -- Active Contract
                ac.contract_id,
                ac.provider_name,
                ac.contract_number,
                ac.payment_schedule,
                ac.fee_type,
                ac.percent_rate,
                ac.flat_rate,
                ac.num_people,
                -- Latest Payment
                lp.actual_fee as latest_fee,
                lp.received_date as latest_date,
                lp.total_assets as latest_assets,
                lp.applied_start_quarter as latest_quarter,
                lp.applied_start_year as latest_year,
                -- Contacts (JSON aggregated)
                json_group_array(
                    json_object(
                        'type', co.contact_type,
                        'name', co.contact_name,
                        'phone', co.phone,
                        'email', co.email,
                        'fax', co.fax,
                        'physical_address', co.physical_address,
                        'mailing_address', co.mailing_address,
                        'contact_id', co.contact_id
                    )
                ) as contacts
            FROM clients c
            LEFT JOIN (
                SELECT * FROM contracts 
                WHERE active = 'TRUE'
            ) ac ON c.client_id = ac.client_id
            LEFT JOIN LatestPayment lp ON c.client_id = lp.client_id
            LEFT JOIN contacts co ON c.client_id = co.client_id
            WHERE c.client_id = ?
            GROUP BY c.client_id
        """, (client_id,))
        
        row = cursor.fetchone()
        if not row:
            return {}
            
        contacts_json = row[15]  # The contacts JSON array from the query
        contacts = json.loads(contacts_json) if contacts_json != '[null]' else []
        
        consolidated_data = {
            'client': {
                'display_name': row[0],
                'full_name': row[1],
                'has_contract': row[2] is not None,
                'has_payments': row[10] is not None,
                'contact_count': len(contacts)
            },
            'active_contract': {
                'contract_id': row[2],
                'provider_name': row[3],
                'contract_number': row[4],
                'payment_schedule': row[5],
                'fee_type': row[6],
                'percent_rate': row[7],
                'flat_rate': row[8],
                'num_people': row[9]
            } if row[2] else None,
            'latest_payment': {
                'actual_fee': row[10],
                'received_date': row[11],
                'total_assets': row[12],
                'quarter': row[13],
                'year': row[14]
            } if row[10] else None,
            'contacts': contacts
        }
        
        # Cache the results before returning
        _cache_client_data(client_id, consolidated_data)
        return consolidated_data.copy()  # Return a copy to prevent cache corruption
    finally:
        conn.close()

# Wrapper functions that match the original API but use consolidated query
def get_client_details_optimized(client_id):
    """Get client details using consolidated query"""
    data = get_consolidated_client_data(client_id)
    if not data:
        return None
    return (data['client']['display_name'], data['client']['full_name'])

def get_active_contract_optimized(client_id):
    """Get active contract using consolidated query"""
    data = get_consolidated_client_data(client_id)
    if not data or not data['active_contract']:
        return None
    contract = data['active_contract']
    return (
        contract['contract_id'],
        contract['provider_name'],
        contract['contract_number'],
        contract['payment_schedule'],
        contract['fee_type'],
        contract['percent_rate'],
        contract['flat_rate'],
        contract['num_people']
    )

def get_latest_payment_optimized(client_id):
    """Get latest payment using consolidated query"""
    data = get_consolidated_client_data(client_id)
    if not data or not data['latest_payment']:
        return None
    payment = data['latest_payment']
    return (
        payment['actual_fee'],
        payment['received_date'],
        payment['total_assets'],
        payment['quarter'],
        payment['year']
    )

def get_contacts_optimized(client_id):
    """Get contacts using consolidated query"""
    data = get_consolidated_client_data(client_id)
    if not data:
        return []
    return [
        (
            contact['type'],
            contact['name'],
            contact['phone'],
            contact['email'],
            contact['fax'],
            contact['physical_address'],
            contact['mailing_address'],
            contact['contact_id']
        )
        for contact in data['contacts']
        if contact['type']  # Filter out null entries
    ] 