"""
Client Display and Forms Package
==============================

This package implements the client management interface of the 401K Payment Tracker.
All components use Streamlit's native patterns for state management and form handling.

Component Structure
-----------------
- client_dashboard.py: Main entry point and layout manager
- client_metrics.py: Key performance indicators and metrics display
- client_contacts.py: Contact management (Primary/Authorized/Provider)
- client_contracts.py: Contract lifecycle management
- client_payments.py: Payment processing and history
- client_payment_utils.py: Shared payment processing utilities

State Management
--------------
Each component maintains its own state using st.session_state:
- Dashboard: Client selection and layout state
- Contacts: Form visibility and validation state
- Contracts: Edit mode and form data
- Payments: Period selection and validation

Database Tables
-------------
Shared across components:
- clients: Core client information
- contacts: Contact details with type classification
- contracts: Fee structures and payment schedules
- payments: Payment history and processing

Key Workflows
-----------
1. Client Selection (dashboard.py)
   → Loads client data
   → Updates all component views

2. Payment Processing (payments.py + payment_utils.py)
   → Validates contract terms
   → Handles period calculations
   → Processes payments in arrears

3. Contact Management (contacts.py)
   → Enforces contact type rules
   → Manages required fields
   → Handles address formatting

4. Contract Lifecycle (contracts.py)
   → Manages active/inactive states
   → Handles fee calculations
   → Validates payment schedules

Note: All components assume payments are processed in arrears.
""" 