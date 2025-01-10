# utils/client_data.py

"""
Performance optimization module for client data.
This module provides consolidated database queries to replace multiple separate calls.
The original functions in utils.py remain unchanged for safety and backward compatibility.
"""

import streamlit as st
from .database import get_database_connection
from typing import Dict, Any

def get_consolidated_client_data(client_id: int) -> Dict[str, Any]:
    """Get consolidated client data using summary tables."""
    from .utils import ensure_summaries_initialized
    ensure_summaries_initialized()  # Ensure summaries are ready
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            WITH LatestSummaries AS (
                SELECT 
                    qs.client_id,
                    qs.total_payments as quarterly_total,
                    qs.total_assets as latest_assets,
                    qs.payment_count,
                    qs.year,
                    qs.quarter,
                    cm.last_payment_date,
                    cm.last_payment_amount,
                    ys.yoy_growth
                FROM quarterly_summaries qs
                LEFT JOIN client_metrics cm ON qs.client_id = cm.client_id
                LEFT JOIN yearly_summaries ys ON 
                    qs.client_id = ys.client_id AND 
                    qs.year = ys.year
                WHERE qs.client_id = ?
                ORDER BY qs.year DESC, qs.quarter DESC
                LIMIT 1
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
                -- Latest Payment Metrics
                ls.quarterly_total,
                ls.last_payment_date,
                ls.latest_assets,
                ls.quarter,
                ls.year,
                ls.yoy_growth,
                -- Contacts
                co.contact_type,
                co.contact_name,
                co.phone,
                co.email,
                co.fax,
                co.physical_address,
                co.mailing_address,
                co.contact_id
            FROM clients c
            LEFT JOIN (
                SELECT * FROM contracts 
                WHERE active = 'TRUE'
            ) ac ON c.client_id = ac.client_id
            LEFT JOIN LatestSummaries ls ON c.client_id = ls.client_id
            LEFT JOIN contacts co ON c.client_id = co.client_id
            WHERE c.client_id = ?
        """, (client_id, client_id))
        
        rows = cursor.fetchall()
        if not rows:
            return {}
            
        # First row has all the non-contact data
        first_row = rows[0]
        
        # Build contacts list
        contacts = []
        for row in rows:
            if row[16]:  # if contact_type exists
                contacts.append({
                    'contact_type': row[16],
                    'contact_name': row[17],
                    'phone': row[18],
                    'email': row[19],
                    'fax': row[20],
                    'physical_address': row[21],
                    'mailing_address': row[22],
                    'contact_id': row[23]
                })
        
        # Structure the data
        consolidated_data = {
            'client': {
                'display_name': first_row[0],
                'full_name': first_row[1],
                'has_contract': first_row[2] is not None,
                'has_payments': first_row[10] is not None,
                'contact_count': len(contacts)
            },
            'active_contract': {
                'contract_id': first_row[2],
                'provider_name': first_row[3],
                'contract_number': first_row[4],
                'payment_schedule': first_row[5],
                'fee_type': first_row[6],
                'percent_rate': first_row[7],
                'flat_rate': first_row[8],
                'num_people': first_row[9]
            } if first_row[2] else None,
            'latest_payment': {
                'actual_fee': first_row[10],  # quarterly_total
                'received_date': first_row[11],  # last_payment_date
                'total_assets': first_row[12],  # latest_assets
                'quarter': first_row[13],
                'year': first_row[14],
                'yoy_growth': first_row[15]  # Added YoY growth
            } if first_row[10] else None,
            'contacts': contacts
        }
        
        return consolidated_data
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
            contact['contact_type'],
            contact['contact_name'],
            contact['phone'],
            contact['email'],
            contact['fax'],
            contact['physical_address'],
            contact['mailing_address'],
            contact['contact_id']
        )
        for contact in data['contacts']
        if contact['contact_type']  # Filter out null entries
    ] 
