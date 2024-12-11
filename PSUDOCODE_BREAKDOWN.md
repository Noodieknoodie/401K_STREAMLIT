CODESTACK = 
- Streamlit 
- Python 
- css / html / js as needed



>>>> DATABASE SNAPSHOT (DATABASE\401kDATABASE.db) --- START <<<<

**Database Overview**

1. Clients Table:
   - Stores information about each client.
   - Key fields: `client_id`, `display_name`, `full_name`, `ima_signed_date`, `file_path_*`.
   - One-to-Many relationship with:
       - `Contacts` (via `client_id`).
       - `Contracts` (via `client_id`).
       - `Payments` (via `client_id`).

2. Contacts Table:
   - Manages contact details for each client.
   - Key fields: `contact_id`, `client_id`, `contact_type`, `contact_name`, `phone`, `email`.
   - Relationships:
       - Linked to `Clients` via `client_id`.

3. Contracts Table:
   - Tracks contracts associated with each client.
   - Key fields: `contract_id`, `client_id`, `active`, `provider_name`, `fee_type`, `percent_rate`, `flat_rate`, `payment_schedule`.
   - Relationships:
       - Linked to `Clients` via `client_id`.
       - One-to-Many relationship with `Payments`.

4. Payments Table:
   - Stores payment history and financial details.
   - Key fields: `payment_id`, `contract_id`, `client_id`, `received_date`, `applied_start_quarter`, `applied_start_year`, `total_assets`, `expected_fee`, `actual_fee`.
   - Relationships:
       - Linked to `Contracts` via `contract_id`.
       - Linked to `Clients` via `client_id`.

**Indexes for Optimization**

- `client_id` is indexed across all tables for efficient lookups.
- `Contracts` and `Payments` include additional indexes for filtering by `active`, `provider`, and time periods (quarter/year).

**Formatting Guidelines**

1. Dates:
   - Format: `YYYY-MM-DD` (e.g., `2023-01-15`).
   - Relevant Columns:
     - `ima_signed_date`
     - `contract_start_date`
     - `received_date`

2. Currency:
   - Stored as decimal (REAL).
   - Relevant Columns:
     - `percent_rate` (e.g., `0.0007` for 0.07%).
     - `flat_rate`, `total_assets`, `expected_fee`, `actual_fee` (e.g., `1234.56`).
   - Display Format: `$1,234.56`.

3. Phone Numbers:
   - Stored as text (e.g., `206-555-1234`).
   - Display Format: `(206) 555-1234`.

4. Email Addresses:
   - Validate format before storing.
   - Stored as text, no additional formatting required.

5. Text Fields:
   - Store plain text without additional formatting.
   - Relevant Columns:
     - `notes`, `provider_name`, `contract_number`, `contact_name`.

6. Address Fields:
   - Store as plain text.
   - Relevant Columns:
     - `physical_address`, `mailing_address`.

>>>> DATABASE SNAPSHOT (DATABASE\401kDATABASE.db) --- END <<<<

>>> utils\client_data.py -- START <<<
```
**Performance Optimization for Client Data**

This module consolidates database queries to optimize performance and reduce redundant calls by caching results. The cache is valid for 5 seconds to balance freshness and efficiency.

---

**Cache Management**

- `_get_cached_client_data(client_id)`: 
  - Checks if client data exists in `_client_cache` and is within the TTL.
  - Logs cache hits, misses, and expirations.
  - Returns cached data or `None` if unavailable or expired.

- `_cache_client_data(client_id, data)`:
  - Stores `data` in `_client_cache` with a timestamp.
  - Logs the caching event.

---

**Database Query Optimization**

- `get_consolidated_client_data(client_id)`:
  - First checks `_get_cached_client_data`.
  - If not cached, queries the database using a consolidated SQL query:
    - Retrieves client information, active contract details, latest payment, and contact information.
    - Groups contact data into a JSON array.
  - Logs database call duration using `@log_db_call`.
  - Parses and structures query results into a dictionary:
    - `client`: Basic client information.
    - `active_contract`: Details of the active contract (if any).
    - `latest_payment`: Details of the latest payment (if any).
    - `contacts`: List of associated contacts.
  - Caches the result before returning a copy to prevent corruption.

---

**Optimized Wrapper Functions**

These functions replicate the functionality of the original API using the consolidated query for efficiency:

- `get_client_details_optimized(client_id)`:
  - Returns client’s `display_name` and `full_name`.

- `get_active_contract_optimized(client_id)`:
  - Returns active contract details, including:
    - `contract_id`, `provider_name`, `contract_number`, `payment_schedule`, `fee_type`, `percent_rate`, `flat_rate`, `num_people`.

- `get_latest_payment_optimized(client_id)`:
  - Returns the latest payment details:
    - `actual_fee`, `received_date`, `total_assets`, `quarter`, `year`.

- `get_contacts_optimized(client_id)`:
  - Returns a list of contacts as tuples, filtering out null entries.
  - Includes `type`, `name`, `phone`, `email`, `fax`, `physical_address`, `mailing_address`, `contact_id`.

---

**Caching and Query Efficiency**

- Cached data is refreshed after 5 seconds to balance accuracy and performance.
- Consolidated SQL query minimizes database load by replacing multiple calls with a single, optimized query.

```
>>> utils\client_data.py -- END <<<


>>> utils\utils.py -- START <<<
```
**Utility Functions for Database Operations and UI Integration**

This module provides helper functions for interacting with the database, formatting data for display, and managing client-related information. 

---

### **Database Connection**

- `get_database_connection()`:
  - Establishes and returns a connection to the SQLite database.

---

### **Cached Data Retrieval Functions**

- `@st.cache_data get_clients()`:
  - Fetches all clients sorted by `display_name`.

- `@st.cache_data get_active_contract(client_id)`:
  - Retrieves the active contract for a specific client.

- `@st.cache_data get_latest_payment(client_id)`:
  - Retrieves the latest payment details for a client, ordered by `received_date`.

- `@st.cache_data get_client_details(client_id)`:
  - Fetches the `display_name` and `full_name` of a specific client.

- `@st.cache_data get_contacts(client_id)`:
  - Retrieves and orders contacts based on type and name for a client.

- `@st.cache_data get_all_contracts(client_id)`:
  - Returns all contracts associated with a client, ordered by active status and start date.

- `@st.cache_data get_payment_history(client_id, years=None, quarters=None)`:
  - Fetches payment history with optional filters for years and quarters.

---

### **Data Formatting and Validation**

- `calculate_rate_conversions(rate_value, fee_type, schedule)`:
  - Converts rates (percentage or flat) to equivalent values based on payment schedule.

- `format_phone_number_ui(number)`:
  - Formats a phone number for user interface as `(XXX) XXX-XXXX`.

- `format_phone_number_db(number)`:
  - Formats a phone number for database storage as `XXX-XXX-XXXX`.

- `validate_phone_number(number)`:
  - Validates whether a phone number contains exactly 10 digits.

---

### **Data Update and Management**

- `add_contact(client_id, contact_type, contact_data)`:
  - Adds a new contact to the database for a specific client.

- `delete_contact(contact_id)`:
  - Deletes a contact by its ID.

- `update_contact(contact_id, contact_data)`:
  - Updates the details of an existing contact.

- `update_payment_note(payment_id, new_note)`:
  - Updates the note for a specific payment record.

---

### **Specialized Queries**

- `get_total_payment_count(client_id)`:
  - Counts the total number of payments associated with a client.

- `get_payment_year_quarters(client_id)`:
  - Fetches distinct year and quarter combinations for a client’s payments.

- `get_paginated_payment_history(client_id, offset=0, limit=None, years=None, quarters=None)`:
  - Retrieves paginated payment history with optional year and quarter filters.

---

### **Implementation Details**

- **Error Handling**:
  - Each function uses `try-finally` to ensure database connections are properly closed.
  
- **Caching**:
  - `@st.cache_data` ensures frequently accessed data is stored for efficiency.

- **Ordering**:
  - Results are consistently ordered for predictable display in UI.


### **Payment Formatting**

- `format_payment_data(payments)`:
  - Formats payment data into a consistent structure for UI display, including:
    - Provider name, payment period, frequency, received date, currency fields, discrepancies, and notes.
  - Includes helper functions for currency formatting and discrepancy calculation.

---

### **Active Contract Management**

- `get_active_contracts_for_client(client_id)`:
  - Fetches all active contracts for a client, ordered by start date.

---

### **Currency Handling**

- `format_currency_db(amount)`:
  - Converts user-entered currency values to decimal format for database storage.

- `format_currency_ui(amount)`:
  - Formats currency values for UI as `$X,XXX.XX`.

---

### **Payment Data Validation**

- `validate_payment_data(data)`:
  - Ensures all required payment fields are valid.
  - Checks payment periods against the current date to confirm they are in arrears.
  - Validates logical consistency between start and end periods.

---

### **Payment Management**

- `add_payment(client_id, payment_data)`:
  - Inserts a new payment into the database, converting periods (months/quarters) as needed.
  - Associates the payment with an active contract for the client.

- `get_payment_by_id(payment_id)`:
  - Retrieves complete payment details for a specific payment record.

---

### **Comprehensive Client Dashboard Data**

- `@st.cache_data(ttl=300) get_client_dashboard_data(client_id)`:
  - Retrieves all relevant client data in a single database query:
    - Contacts as a JSON array.
    - Active contract details as a JSON object.
    - Recent payments as a JSON array (up to 50 records).

---

### **Database Query Best Practices**

- **Efficiency**:
  - Consolidated queries reduce the number of database calls.
  - Recent payments and related data are fetched using SQL `WITH` statements for clarity and performance.

- **Error Handling**:
  - Database connections are managed with `try-finally` to ensure proper closure.

- **Caching**:
  - Cached queries improve performance for frequently accessed data (e.g., dashboard components).


```
>>> utils\utils.py -- END <<<



>>> pages\client_dashboard\client_contact_layout.py -- START <<<<
```
import streamlit as st
from utils.utils import get_contacts
from .client_contact_management import render_contact_section, render_contact_card
**Contact Section Display**

- `show_contact_sections(client_id)`: Renders contact sections for a given client in a three-column layout.
  - Fetches contact data for the given `client_id` using `get_contacts`.
  - Categorizes contacts into three types: `Primary`, `Authorized`, and `Provider`, grouping contacts by their type.
  - Divides the UI into three equal-width columns:
    - **Column 1**: Displays `Primary` contacts using `render_contact_section`.
    - **Column 2**: Displays `Authorized` contacts using `render_contact_section`.
    - **Column 3**: Displays `Provider` contacts using `render_contact_section`.


```
>>> pages\client_dashboard\client_contact_layout.py -- END <<<<


>>> pages\client_dashboard\client_contact_management.py -- START <<<<
```
import streamlit as st
from utils.utils import (
    get_contacts, add_contact, format_phone_number_ui, format_phone_number_db,
    validate_phone_number, delete_contact, update_contact, get_clients
)

**Contact Form Management**

- `init_contact_form_state()`: Initializes the contact form state in `st.session_state` with:
  - Fields for `is_open`, `mode` (`add` or `edit`), `contact_type`, `contact_id`, and flags for validation errors and cancellation confirmations.
  - Defaults for `form_data` including `contact_name`, `phone`, `fax`, `email`, `physical_address`, and `mailing_address`.
  - Initializes `delete_contact_id` and `show_delete_confirm` if not present.

- `clear_form()`: Resets the `form_data` fields to defaults, closes the form, clears validation errors, and resets the `show_cancel_confirm` state. Clears cached contacts.

**Form Validation and Input Formatting**

- `validate_form_data(form_data)`: Returns `True` if at least one field in `form_data` has a value.
- `has_unsaved_changes(form_data)`: Returns `True` if any field in `form_data` is non-empty.
- `clear_validation_error()`: Resets the `has_validation_error` flag in the form state.
- `format_phone_on_change()` and `format_fax_on_change()`: Formats the respective phone or fax number in the form state based on user input.

**Contact Form Display**

- `show_contact_form()`:
  - Displays a modal dialog with a title based on the form's `mode` (`Add` or `Edit`) and `contact_type`.
  - Includes inputs for `contact_name`, `phone`, `fax`, `email`, `physical_address`, and `mailing_address`.
  - Validates `phone` and `fax` input using `validate_phone_number` and converts them for database storage.
  - Handles form submission:
    - Validates `form_data` and either adds or updates the contact using `add_contact` or `update_contact`.
    - Clears the form and refreshes the contact list cache upon success.
  - Handles cancellation:
    - If changes are present, prompts for confirmation; otherwise, resets the form.

**Contact Rendering**

- `render_contact_card(contact)`:
  - Displays a contact's details in a two-column layout (info and actions).
  - Shows confirmation for delete actions with `Yes` and `No` options.
  - Provides buttons for editing (`✏️`) or deleting (`🗑️`) a contact:
    - Editing pre-populates the form fields and switches to `edit` mode.
    - Deleting sets up confirmation for the selected contact.

- `render_contact_section(contact_type, contacts)`:
  - Displays an expandable section for each `contact_type`, listing all contacts in the section.
  - Allows adding a new contact via a button, opening the form in `add` mode.

```
>>> pages\client_dashboard\client_contact_management.py -- END <<<<

>>> pages\client_dashboard\client_dashboard_metrics.py -- START <<<<
```
import streamlit as st
from utils.client_data import (
    get_consolidated_client_data,  
    get_client_details_optimized as get_client_details,  
    get_active_contract_optimized as get_active_contract,
    get_latest_payment_optimized as get_latest_payment
)
from utils.utils import calculate_rate_conversions  


**Client Metrics Display**

- **Function Overview**:
  - `show_client_metrics(client_id)`: Displays a metrics section with key client information based on consolidated data.

**Data Retrieval and Validation**

- **Data Query**:
  - Retrieves all client data using `get_consolidated_client_data(client_id)`.

- **Empty Data Handling**:
  - If no data is returned, exits early.

**Metrics Display**

- **Container Layout**:
  - Uses a Streamlit container and two rows of four columns each for metrics.

- **First Row Metrics**:
  - **Client Name**:
    - Shows `display_name` with `full_name` as delta (if available).
  - **Provider**:
    - Shows `provider_name` from `active_contract`, or "N/A" if unavailable.
  - **Contract #**:
    - Displays `contract_number` from `active_contract`, or "N/A" if not present.
  - **Participants**:
    - Displays `num_people` from `active_contract`, or "N/A" if missing.

- **Second Row Metrics**:
  - **Rate**:
    - Defaults to "N/A" with optional `rate_type` and `rate_conversions`.
    - Calculates rate based on `fee_type` (`percentage` or `flat_rate`) in `active_contract`:
      - Converts percentage rates to formatted strings (e.g., `3.000%`).
      - Converts flat rates to currency format (e.g., `$1,000.00`).
    - Optionally applies `calculate_rate_conversions` if rate data and schedule are available.
  - **Payment Schedule**:
    - Displays `payment_schedule` title-cased from `active_contract`, or "N/A" if unavailable.
  - **Last Payment**:
    - Defaults to "No payments".
    - Shows `actual_fee` formatted as currency, with `received_date` if available in `latest_payment`.
  - **Last Recorded AUM**:
    - Defaults to "Not available".
    - Displays `total_assets` from `latest_payment` formatted as currency and associated with quarter/year if present.

**Utility Integration**

- Uses `calculate_rate_conversions` for rate conversion based on the contract's fee type and schedule.

**Dynamic Conditional Logic**

- Adapts metrics to available data fields (`active_contract`, `latest_payment`).
- Ensures robust fallback values ("N/A", "No payments", etc.) for missing data.


```
>>> pages\client_dashboard\client_dashboard_metrics.py -- END <<<<


>>>> pages\client_dashboard\client_dashboard.py -- START <<<<
```
import streamlit as st
from .client_contact_management import init_contact_form_state, show_contact_form
from .client_payment_management import show_payment_history, clear_client_specific_states, init_payment_form_state
from .client_dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .client_contact_layout import show_contact_sections
from .client_payment_form import show_payment_form
from utils.client_data import (  # New optimized queries
    get_consolidated_client_data,
    get_client_details_optimized as get_client_details,
    get_contacts_optimized as get_contacts
)
from utils.perf_

**Client Dashboard Initialization**

- **Dashboard Entry Point**:
  - Function: `show_client_dashboard()` is decorated with `@log_ui_action("show_dashboard")` to log its invocation.
  - Displays "👥 Client Dashboard" as the main title.

- **State Initialization**:
  - Calls `init_contact_form_state()` and `init_payment_form_state()` to set up initial states for contact and payment forms.

**Client Selection and State Management**

- **Client Selection**:
  - Retrieves `client_id` and `selected_client_name` from `get_selected_client()`.
  - Logs the event `'client_selected'` if a valid client is selected (not `"Select a client..."`).

- **State Management**:
  - Initializes `st.session_state.previous_client` if not present.
  - Calls `clear_client_specific_states()` to reset specific states when switching between clients, updating `st.session_state.previous_client` accordingly.

**Dialog Display**

- **Contact Form**:
  - Checks if `contact_form['is_open']` in `st.session_state` is `True`.
  - Logs the event `'contact_form_opened'` with the form's `contact_type`.
  - Displays the contact form using `show_contact_form()`.

- **Payment Form**:
  - Checks if `payment_form['is_visible']` in `st.session_state` is `True`.
  - Logs the event `'payment_form_opened'` with the `client_id`.
  - Displays the payment form using `show_payment_form(client_id)`.

**Client Data Handling**

- **Data Retrieval**:
  - If `client_id` is valid, retrieves consolidated client data using `get_consolidated_client_data(client_id)`.

- **Data Logging**:
  - Logs the event `'client_data_loaded'` with details about:
    - Client name, active contract status, payment status, and contact count.
    - Duration of the data loading process.

**Dashboard Components**

- **Metrics Section**:
  - Displays client-specific metrics using `show_client_metrics(client_id)`.

- **Contacts Section**:
  - Adds spacing before showing contact sections.
  - Displays contacts using `show_contact_sections(client_id)`.

- **Payment History Section**:
  - Adds spacing before showing payment history.
  - Displays a header "### Payment History".
  - Shows payment history using `show_payment_history(client_id)`.


>>>> pages\client_dashboard\client_dashboard.py -- END <<<<

>>>>> pages\client_dashboard\client_payment_management.py -- START <<<<<
```
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history, update_payment_note,
    get_clients, get_contacts,
    get_client_details, add_contact, update_contact,
    delete_contact, get_payment_year_quarters, get_payment_by_id, format_currency_ui,
    get_client_dashboard_data,
)
from utils.perf_logging import log_event
from .client_payment_form import (
    show_payment_form,
    populate_payment_form_for_edit
)


**Contact Form State Management**

- `init_contact_form_state()`: Initializes `st.session_state.contact_form` with:
  - `is_open`, `mode` ('add' or 'edit'), `contact_type`, `contact_id`, `has_validation_error`, `show_cancel_confirm`.
  - Default `form_data` fields: `contact_name`, `phone`, `fax`, `email`, `physical_address`, `mailing_address`.
  - Also initializes `delete_contact_id` and `show_delete_confirm` if missing.

- `clear_contact_form()`: Resets `contact_form` fields to defaults, closes the form, clears errors, cancels state, and clears the `get_contacts` cache.

**Contact Form Display (`@st.dialog`)**

- If `contact_form['is_open']` is `False`, return early.
- Display form with title based on `mode` (`Add` or `Edit`).
- Input fields for `contact_name`, `phone`, `fax`, `email`, `physical_address`, `mailing_address` are prefilled with `form_data` values.
- Validation:
  - If `has_validation_error`, show an error message.
  - If `show_cancel_confirm`, display a confirmation warning with "Yes" to discard changes (calls `clear_contact_form()` and reruns) or "No" to return to the form.
- Save button:
  - Validates `form_data` by checking any non-empty field.
  - For "edit" mode, updates the contact and clears form state.
  - For "add" mode, retrieves `client_id`, adds the contact, and clears the form.
  - If validation fails, sets `has_validation_error` and reruns.
- Cancel button:
  - If changes are present, sets `show_cancel_confirm` to `True` and reruns.
  - Otherwise, clears form state and reruns.


**State Management Initialization**

- `init_payment_form_state()`: 
  - Initializes `payment_form` in `st.session_state` if not already present.
  - Sets default visibility, client identification, mode (`add`), validation error states, cancel confirmation, and form lock.
  - Pre-fills form data with the current date, last quarter and year, and default financial and method fields.
  - Ensures `client_id` is added if not present in an existing `payment_form`.

- `init_notes_state()`:
  - Creates a centralized `notes_state` in `st.session_state` with placeholders for active notes, edited notes, and temporary unsaved changes.

- `init_filter_state()`:
  - Groups payment filter state into `filter_state` in `st.session_state` with year, quarter, and applied filters.

**Client-Specific State Clearing**

- `clear_client_specific_states()`:
  - Resets `filter_state` to default empty filters.
  - Clears `notes_state` by removing active notes and temporary edits.
  - Resets the visibility, mode, validation, and form data of `payment_form`.

**Payment Data Formatting**

- `format_payment_data(payments)`:
  - Processes a list of payment tuples into a standardized format for display.
  - Handles currency formatting, calculates fee discrepancies, and formats periods based on payment frequency (monthly or quarterly).
  - Converts received dates to a human-readable format and ensures all values have defaults (e.g., "N/A").
  - Constructs a list of dictionaries containing formatted payment details for display.

**Note Editing**

- `handle_note_edit(payment_id, new_note)`:
  - Logs the note update event and persists the new note to storage.
  - Clears the `active_note` in `notes_state` after update.

- `format_note_display(note)`:
  - Returns a tuple with note presence (`True`/`False`), an indicator icon ("🟢" for present, "◯" for absent), and the note content or placeholder text.

- `initialize_notes_state()`:
  - Ensures `notes_state` exists in `st.session_state` with default fields for active and edited notes.

**Note Rendering**

- `render_note_cell(payment_id, note, provider=None, period=None)`:
  - Displays a clickable note cell with an icon indicating note presence.
  - Allows toggling of note editing mode via a unique key, automatically saving prior notes when switching.
  - Provides a form for editing or adding notes, with changes saved in `notes_state`.

**Utilities**

- Clickable icons and JavaScript are embedded in `render_note_cell` for toggling note states, styled via inline CSS.
- Payment periods and financial values are dynamically formatted for consistent user display.
- Note interactions are logged for analytics and state tracking.


**Payment History Display and Navigation**

- `show_payment_history(client_id)`:
  - **State Initialization**:
    - Initializes payment form, notes, filter states, and delete confirmation states if not already in `st.session_state`.
  - **Data Retrieval**:
    - Fetches available year-quarter combinations (`get_payment_year_quarters`) for the client and derives available years.
    - Displays an info message if no payment history is found.
  - **Filter and Navigation UI**:
    - Displays a time filter with options: "All Time," "This Year," and "Custom" (year and quarter selection).
    - Customizes displayed text based on filter selection and stores filter criteria in `filter_state`.
    - Adds an "Add Payment" button to show the payment form.
  - **Filter Application**:
    - Determines year and quarter filters based on user selection.
  - **Payment Table Display**:
    - Formats payment data (`format_payment_data`) into a DataFrame and renders rows with columns for provider, period, frequency, received date, financial details, and actions (notes and edit/delete).
    - Custom CSS ensures compact and styled table layout.
  - **Row Actions**:
    - Notes:
      - Displays a note icon (green or empty circle) for each payment.
      - Allows toggling note edit mode and saving changes dynamically.
    - Actions:
      - Edit: Opens the payment form in edit mode with pre-filled data.
      - Delete: Shows a confirmation dialog to delete the payment.
  - **Note Editing and Rendering**:
    - Displays editable text areas for notes and auto-saves changes upon modification.

**Client Dashboard Overview**

- `display_client_dashboard()`:
  - **State Initialization**:
    - Ensures all relevant states (contact form, payment form, notes, filters) are initialized.
  - **Client Selection and Data Loading**:
    - Retrieves the selected client from a session key.
    - Loads client-specific data into `st.session_state` if not already loaded or if the selected client has changed.
  - **Dashboard Layout**:
    - Two-column layout:
      - Left column: Displays the "Payment History" section by invoking `display_payments_section`.
      - Right column: Displays "Contacts" with an "Add Contact" button for each contact type.
  - **Conditional Form Display**:
    - Displays the payment or contact form based on visibility state, ensuring only one form is shown at a time.
	````
>>>>> pages\client_dashboard\client_payment_management.py -- END <<<<<


>>>> pages\client_dashboard\client_payment_table.py -- START <<<<
````
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import update_payment_note
from utils.perf_logging import log_event
from .client_payment_form import set_payment_form_edit_mode 


**Payment Table Formatting and Display**

- **Utility Functions**:
  - `format_currency(value)`:
    - Converts a numeric value to a currency format (`$X,XXX.XX`), returning "N/A" for invalid or empty inputs.
  - `format_payment_data(payments)`:
    - Transforms raw payment data into a standardized format for display.
    - Formats periods based on frequency (monthly or quarterly).
    - Handles received date formatting, currency formatting for financial values, and calculates fee discrepancies.
    - Returns a list of dictionaries containing processed payment data.

- **State Management**:
  - `init_notes_state()`:
    - Initializes `notes_state` in `st.session_state` for managing active notes, edited notes, and unsaved changes.

- **Payment Table Display**:
  - `display_payment_table(client_id, payments)`:
    - **Prerequisites**:
      - Initializes `notes_state`, delete confirmation states, and formats the `payments` data using `format_payment_data`.
    - **Custom CSS**:
      - Styles payment table rows, headers, notes, and actions for a compact and user-friendly UI.
    - **Header Display**:
      - Creates headers for columns such as Provider, Period, Frequency, Received, Financial Details, Notes, and Actions.
    - **Row Rendering**:
      - Iterates over the formatted payment data (`DataFrame` rows).
      - Displays each payment row with columns for all key details, including:
        - Provider name.
        - Period (single quarter or range).
        - Payment frequency and received date.
        - Financial details like total assets, expected fee, actual fee, and discrepancy.
        - Notes with an interactive button (`🟢` for existing, `◯` for absent).
        - Action buttons:
          - Delete (`🗑️`): Triggers delete confirmation for the payment.
    - **Delete Confirmation**:
      - Displays a warning and "Yes/No" options for confirming or canceling the deletion of a payment.
    - **Note Editing**:
      - Shows an editable text area for notes when the note button is clicked.
      - Saves updates dynamically and resets the active note state.

- **Overall Interaction**:
  - Provides a user-friendly interface for viewing, editing, and deleting payments with interactive elements like buttons and confirmation dialogs.
  - Ensures robust state management for handling notes and payment actions dynamically.

````
>>>> pages\client_dashboard\client_payment_table.py -- END <<<<


>>>> pages\client_dashboard\client_payment_form.py -- START <<<<
```
import streamlit as st
from datetime import datetime
from utils.utils import (
    get_active_contract,
    format_currency_ui,
    format_currency_db,
    validate_payment_data,
    add_payment
)
from .client_payment_utils import (
    get_current_period,
    get_period_options,
    validate_period_range,
    format_period_display,
    calculate_expected_fee,
    parse_period_option,
    get_current_quarter,
    get_previous_quarter,
    get_quarter_month_range
)
**Payment Management and Validation**

### **Caching Contract Data**
- **`get_cached_contract(client_id)`**:
  - Retrieves contract data for a given client, using caching for improved performance (5-minute TTL).

### **Initialization and State Management**
- **`init_payment_form()`**:
  - Initializes `st.session_state.payment_form` with defaults if not already present.
  - Defaults include `is_visible`, `mode`, validation states, and prefilled form fields like `received_date`, `total_assets`, and `method`.

- **`clear_payment_form()`**:
  - Resets `payment_form` to its default state, closing visibility, clearing validation errors, and resetting all form fields.

- **`populate_payment_form_for_edit(payment_data)`**:
  - Populates `payment_form` fields with `payment_data` for editing, formatting fields like `total_assets` and `actual_fee` as needed.

- **`has_unsaved_changes(form_data)`**:
  - Compares `form_data` to its default state to detect any unsaved changes.

- **`clear_validation_error()`**:
  - Resets the `has_validation_error` flag in `payment_form`.

### **Input Formatting and Validation**
- **`format_amount_on_change(field_key)`**:
  - Formats currency input fields dynamically, updating the `expected_fee` and `actual_fee` fields when `total_assets` changes.

- **`get_period_from_date(date_str, schedule)`**:
  - Derives a period (month/quarter) based on a given `date_str` and payment schedule (monthly/quarterly).

- **`on_date_change()`**:
  - Updates the payment period fields (`applied_start_period`, `applied_start_year`) when the payment date changes, based on the contract’s payment schedule.

- **`validate_quarter_range(start_quarter, start_year, end_quarter, end_year)`**:
  - Ensures a valid chronological range for quarters when custom ranges are selected.

### **Payment Form Display and Interaction**
- **`show_payment_form(client_id)`**:
  - Displays the payment form dialog with:
    - Contract details (`fee_type`, `rate`, `schedule`, `provider`) fetched via `get_cached_contract`.
    - Inputs for payment date, period selection (monthly/quarterly), and custom ranges.
    - Form validation and error handling for missing/invalid inputs.
  - Updates `payment_form` with selected options or exits early if conditions (e.g., missing contract) are not met.

- **`get_previous_payment_defaults(client_id)`**:
  - Fetches the most recent payment’s defaults (e.g., `method`, `total_assets`) for a client.

### **Utility Functions**
- **`get_previous_quarter(quarter, year)`**:
  - Determines the previous quarter and year based on the current quarter.

- **`get_quarter_options()`**:
  - Generates a list of quarter options for the last five years, excluding the current quarter.

### **Default Values from Previous Payment**
- Retrieves default values for `method` and `total_assets` from the most recent payment for the client.
- Uses these defaults if `payment_form` fields are not already populated.

### **Form Fields and User Inputs**
- **Assets Under Management**:
  - Text input for `total_assets` with a placeholder and on-change formatting via `format_amount_on_change`.

- **Payment Amount**:
  - Text input for `actual_fee`, also with a placeholder and on-change formatting.

- **Expected Fee**:
  - Displays `expected_fee` dynamically if calculated.
  - Checks for discrepancies between payment periods and contract start dates, showing a warning if the payment quarter predates the contract.

- **Payment Method**:
  - Dropdown to select `method` with a default from `payment_form` or previous payment.
  - Displays an additional text input if the selected method is "Other".

- **Notes**:
  - Text area for additional notes, with a conditional placeholder message depending on whether a multi-quarter range is selected.

### **Form Data Capture**
- Consolidates all user input fields into a `form_data` dictionary:
  - Includes fields like `received_date`, `applied_start_period`, `total_assets`, `actual_fee`, and `method`.
  - Adds `payment_schedule` from the contract for validation.

### **Validation and Error Handling**
- **Validation Errors**:
  - If `has_validation_error` is set, calls `validate_payment_data` to display all errors.

- **Cancel Confirmation**:
  - If unsaved changes are detected, prompts the user with a warning.
  - Options:
    - Discard changes (`clear_payment_form()` and rerun).
    - Keep editing (removes `show_cancel_confirm` state).

### **Save and Cancel Actions**
- **Save Button**:
  - Validates `form_data` and attempts to save payment data using `add_payment`.
  - Displays success or failure messages accordingly.
  - On success, clears the form and reruns the script.

- **Cancel Button**:
  - If unsaved changes are detected, triggers `show_cancel_confirm`.
  - Otherwise, clears the form state and reruns.

```
>>>> pages\client_dashboard\client_payment_form.py -- END <<<<



>>>>> pages\client_dashboard\client_payment_utils.py -- START <<<< 
```
from datetime import datetime

**Period Management Utilities**

- `get_current_period(schedule)`:
  - Determines the current period based on the provided schedule:
    - Monthly: Returns the current month.
    - Quarterly: Returns the current quarter.

- `get_period_options(schedule)`:
  - Generates a list of past period options (months or quarters) based on the provided schedule.
  - Monthly: Includes the last 24 months.
  - Quarterly: Includes the last 8 quarters.

- `parse_period_option(period_option, schedule)`:
  - Parses a string period option (e.g., "Jan 2024" for monthly, "Q1 2024" for quarterly) into a period and year.

- `validate_period_range(start_period, start_year, end_period, end_year, schedule)`:
  - Ensures the period range is valid:
    - Both start and end periods must be in arrears (before the current period).
    - The end period cannot precede the start period.

- `format_period_display(period, year, schedule)`:
  - Formats a period and year for display:
    - Monthly: Displays as "MMM YYYY" (e.g., "Jan 2024").
    - Quarterly: Displays as "Q1 YYYY" (e.g., "Q1 2024").

**Fee Calculation**

- `calculate_expected_fee(contract_data, total_assets)`:
  - Computes the expected fee based on contract terms:
    - Percentage-based: Multiplies `total_assets` by the `percentage_rate`.
    - Flat rate: Returns the `flat_rate` directly.



**Quarter Management**

- `get_current_quarter()`:
  - Determines the current quarter based on the current month.

- `get_previous_quarter(current_quarter, current_year)`:
  - Calculates the previous quarter and year:
    - Returns `(4, previous_year)` if the current quarter is 1.
    - Otherwise, decrements the quarter.

- `get_quarter_month_range(quarter, year)`:
  - Returns the start and end months for a given quarter.

**Key Features and Behavior**

- Ensures proper formatting and validation for periods across both monthly and quarterly schedules.
- Provides robust utilities for calculating, formatting, and validating periods and fees.
- Adapts functionality to handle various contract and schedule requirements dynamically.
```
>>>>> pages\client_dashboard\client_payment_utils.py -- END <<<<


>>>> pages\client_dashboard\client_selection.py --- START <<<<
```
import streamlit as st
from utils.utils import get_clients

**Client State Management**

- `reset_client_state()`:
  - Resets session state variables related to client data:
    - Clears `payment_data` and resets `payment_offset`.
    - Removes `current_year` and `current_quarter` from session state if present.

**Client Selection**

- `get_selected_client()`:
  - **Initialization**:
    - Ensures `previous_client` exists in `st.session_state`.
  - **Client Selector UI**:
    - Displays a dropdown to search or select a client from the available options.
    - Returns `None, None` if no client is selected.
  - **State Reset on Client Change**:
    - Compares the newly selected client with the `previous_client`.
    - Calls `reset_client_state()` and updates `previous_client` when a new client is selected.
  - **Client ID and Name Retrieval**:
    - Matches the selected client name to its corresponding `client_id` from the list of clients.
    - Returns the `client_id` and selected client name.

**Key Features and Behavior**

- Automatically resets relevant state variables when switching clients to ensure a clean slate for new client data.
- Provides a user-friendly client selection interface with dynamic state updates.
- Efficiently retrieves and maps selected client information for further processing.

```
>>>> pages\client_dashboard\client_selection.py -- END <<<<

>>>> pages\client_dashboard.py -- START <<<<
```
import streamlit as st
from .client_contact_management import init_contact_form_state, show_contact_form
from .client_payment_management import show_payment_history, clear_client_specific_states, init_payment_form_state
from .client_dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .client_contact_layout import show_contact_sections
from .client_payment_form import show_payment_form
from utils.client_data import (  # New optimized queries
    get_consolidated_client_data,
    get_client_details_optimized as get_client_details,
    get_contacts_optimized as get_contacts
)
from utils.perf_logging import log_ui_action, log_event
import time

**Client Dashboard Display**

- `show_client_dashboard()`:
  - **Initialization**:
    - Displays a dashboard title ("👥 Client Dashboard").
    - Initializes contact form and payment form states.
  - **Client Selection**:
    - Retrieves the selected client ID and name using `get_selected_client`.
    - Logs the client selection if a valid client is chosen.
  - **Client State Management**:
    - Initializes `previous_client` in session state if not already present.
    - Resets client-specific states via `clear_client_specific_states` when switching clients.
  - **Dialogs**:
    - Opens the contact form if `contact_form['is_open']` is `True`.
    - Opens the payment form if `payment_form['is_visible']` is `True`.
  - **Client Data Loading**:
    - Fetches consolidated client data using `get_consolidated_client_data`.
    - Logs metrics such as contract presence, payment history, and contact count, along with data load duration.
  - **Metrics and Sections**:
    - Displays client metrics using `show_client_metrics`.
    - Adds spacing between sections using styled markdown.
    - Shows contact sections via `show_contact_sections`.
    - Displays the "Payment History" section with relevant data.

**Key Features and Behavior**

- Modular and efficient: Integrates reusable components like contact and payment forms, client metrics, and payment history.
- Dynamically adjusts displayed content based on selected client and their associated data.
- Logs UI interactions and client-specific metrics for performance tracking and analytics.
- Provides clean UI transitions when switching clients or interacting with forms.


>>>> pages\client_dashboard.py -- END <<<<
```
**Client Metrics Display**

- **Fetch Client Data**
  - Use `get_consolidated_client_data(client_id)` to retrieve client data.
  - Return early if no data is found.

- **Metrics Layout**
  - Display metrics in two rows of 4 columns each within a Streamlit container.

- **First Row Metrics**
  - **Column 1**: Show "Client Name" as `data['client']['display_name']`, with the difference from `data['client']['full_name']` if available.
  - **Column 2**: Show "Provider" as `data['active_contract']['provider_name']` or "N/A" if no active contract.
  - **Column 3**: Show "Contract #" as `data['active_contract']['contract_number']` or "N/A" if no active contract.
  - **Column 4**: Show "Participants" as `data['active_contract']['num_people']` or "N/A" if no active contract.

- **Second Row Metrics**
  - **Column 1**: Show "Rate" with:
    - Default to "N/A".
    - If `data['active_contract']['fee_type']` is "percentage", show percentage rate if available.
    - If `data['active_contract']['fee_type']` is "flat", show flat rate if available.
    - Use `calculate_rate_conversions()` to adjust the rate value for display along with conversion details if applicable.
  - **Column 2**: Show "Payment Schedule" as the title-cased `data['active_contract']['payment_schedule']` or "N/A" if not available.
  - **Column 3**: Show "Last Payment" with:
    - Default to "No payments".
    - Display `actual_fee` and `received_date` from `data['latest_payment']` if available.
  - **Column 4**: Show "Last Recorded AUM" with:
    - Default to "Not available".
    - Use `total_assets`, `quarter`, and `year` from `data['latest_payment']` to calculate AUM value and date if present.

**Dependencies**
- Utilizes optimized functions for client data (`get_consolidated_client_data`, `get_client_details`, etc.).
- Uses `calculate_rate_conversions()` for rate calculations and adjustments.

```



