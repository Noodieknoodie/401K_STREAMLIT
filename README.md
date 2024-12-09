# 401K Payment Tracker

A Streamlit-based application for tracking and managing 401K plan payments, client relationships, and contract details.

## 🏗️ Project Structure

```
401K_Payment_Tracker/
├── app.py                 # Main application entry point
├── sidebar.py            # Global navigation sidebar
├── DATABASE/             # SQLite database directory
│   └── 401kDATABASE.db  # Main database file
├── pages/               # Application pages
│   ├── client_dashboard/     # Main dashboard functionality
│   │   ├── dashboard.py         # Dashboard entry point
│   │   ├── client_selection.py  # Client selector component
│   │   ├── dashboard_metrics.py # Client metrics display
│   │   ├── payment_management.py# Payment history and notes
│   │   ├── contact_management.py# Contact CRUD operations
│   │   └── contact_layout.py    # Contact display components
│   ├── quarterly_summary/   # Quarterly reporting (placeholder)
│   ├── manage_clients/      # Client management (placeholder)
│   └── bulk_payment/        # Bulk payment entry (placeholder)
├── utils/               # Utility functions
│   ├── database/           # Database operations
│   │   ├── connection.py      # Database connection handling
│   │   ├── client_queries.py  # Client-related queries
│   │   ├── contact_queries.py # Contact-related queries
│   │   ├── contract_queries.py# Contract-related queries
│   │   ├── payment_queries.py # Payment-related queries
│   │   └── pagination.py      # Pagination utilities
│   ├── formatters/         # Data formatting utilities
│   │   ├── phone.py          # Phone number formatting
│   │   └── rate.py           # Rate calculations
│   └── validators/         # Input validation
│       └── input.py          # Input validation utilities
└── shared/              # Shared components and constants
    ├── components/         # Reusable UI components
    ├── constants/          # Application constants
    └── state/             # Session state management
```

## 🗄️ Database Schema

### Key Tables and Relationships

1. **clients**
   - Primary table for client information
   - Key fields: `client_id`, `display_name`, `full_name`
   - Referenced by: contacts, contracts, payments

2. **contacts**
   - Stores client contact information
   - Types: Primary, Authorized, Provider
   - Key fields: `contact_id`, `client_id`, `contact_type`
   - Foreign key: `client_id` → clients

3. **contracts**
   - Manages client contracts and fee structures
   - Key fields: `contract_id`, `client_id`, `active`, `fee_type`
   - Fee types: percentage, flat
   - Foreign key: `client_id` → clients

4. **payments**
   - Tracks all payment transactions
   - Key fields: `payment_id`, `contract_id`, `client_id`, `received_date`
   - Foreign keys: `client_id` → clients, `contract_id` → contracts

## 🔑 Key Features

### Client Dashboard
- **Client Selection**: Dropdown with search functionality
- **Metrics Display**: Shows active contract details, latest payment info
- **Contact Management**: CRUD operations for three contact types
- **Payment History**: 
  - Paginated display (25 rows per page)
  - Filterable by year/quarter
  - Note management for each payment

### Session State Management
- Client selection persistence
- Payment history pagination state
- Contact form state management
- Filter state preservation

### Data Caching
- Client list caching
- Active contract caching
- Payment history caching
- Contact list caching

## 🔄 Common Patterns

### Database Operations
```python
@st.cache_data
def get_something(param):
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ... WHERE ... = ?", (param,))
        return cursor.fetchall()
    finally:
        conn.close()
```

### Component Layout
```python
def show_component():
    col1, col2 = st.columns([ratio1, ratio2])
    with col1:
        # Left column content
    with col2:
        # Right column content
```

### Form Handling
```python
if 'form_state' not in st.session_state:
    st.session_state.form_state = {
        'is_open': False,
        'mode': 'add',  # or 'edit'
        'data': {}
    }
```

## 📱 UI/UX Patterns

### Consistent Metrics Display
- Four-column layout for metrics
- Currency formatting: `f"${value:,.2f}"`
- Date formatting: `date_obj.strftime('%b %d, %Y')`

### Interactive Elements
- Collapsible sections using `st.expander`
- Modal dialogs using `@st.dialog`
- Tooltips on action buttons
- Confirmation dialogs for destructive actions

## 🚀 Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Pagination for large datasets
- Connection handling in try-finally blocks

### Caching Strategy
- Read operations cached with `@st.cache_data`
- Cache cleared on relevant write operations
- Selective cache invalidation

## 🔒 Data Validation

### Input Validation
- Phone number format: (XXX) XXX-XXXX
- Required field checking
- Type-specific validation (dates, currency)

### Error Handling
- Graceful error display
- User-friendly error messages
- State preservation on error

## 🎯 Future Development Areas

1. Quarterly Summary Implementation
2. Bulk Payment Entry System
3. Client Management Interface
4. Enhanced Reporting Features

## 📝 Notes

- Database file location is fixed: `DATABASE/401kDATABASE.db`
- All monetary values stored as REAL in database
- Dates stored in 'YYYY-MM-DD' format
- Quarter/Year combinations used for payment tracking
