**FIXME Document - 401(k) Payment Tracker Application**

---

**FIXME (FALSE POSITIVE -- IGNORE THIS): Incorrect Monthly Period Storage**

*   **Issue:** Monthly payment periods are incorrectly stored as zero-based quarters (0-11) instead of month numbers (1-12). This creates inconsistencies throughout the application.
*   **Evidence:** The code consistently subtracts 1 from the month number when storing monthly payments, treating them as if they were quarters. This leads to incorrect calculations, display issues, and validation problems. The database schema intends applied_start_quarter and applied_end_quarter to represent quarters (1-4), not zero-indexed months.
*   **Affected Components:**
    *   client_payments.py
    *   utils.py
    *   client_payment_utils.py
    *   payments table (database schema)
    *   All summary calculations and triggers related to periods.
*   **Fix:**
    1.  **Modify add_payment (in utils.py):**
        *   Remove the incorrect - 1 conversion for monthly schedules:
        
python
            if schedule == 'monthly':
                start_quarter = payment_data['applied_start_period']  # Remove - 1
                end_quarter = payment_data['applied_end_period']  # Remove - 1
            else:
                start_quarter = payment_data['applied_start_period']
                end_quarter = payment_data['applied_end_period']


    2.  **Modify update_payment (in utils.py):**  Make the same change as in add_payment.
    3.  **Modify get_payment_by_id (in utils.py):** Remove the incorrect conversion when loading payment data for editing:
    
python
          if schedule == "monthly":
              # Convert quarters back to months
              start_period = payment_data[1] # Remove: (payment_data[1] - 1) * 3 + 1
              end_period = payment_data[3] # Remove: (payment_data[3] - 1) * 3 + 3


    4. **Modify validate_payment_data (in utils.py):** Correct the current_quarter calculation:
    
python
        current_quarter = current_month if is_monthly else (current_month - 1) // 3 + 1


    5.  **Modify get_period_options (in client_payment_utils.py):**  Adjust to return month numbers, not quarter-like strings, for monthly schedules.
    6. **Modify parse_period_option (in client_payment_utils.py):** Adjust to handle month numbers correctly for monthly.
    7. **Modify format_payment_data (in client_payments.py):** Remove the flawed conversion logic. Use format_period_display directly.
    8.  **Database Migration:**
        *   Write a database migration script to update existing data in the payments table.  For all rows where the payment_schedule (in the related contracts table) is 'monthly', update applied_start_quarter and applied_end_quarter by adding 1.  This will convert the stored zero-based values to the correct month numbers.
        *   Update the summary tables (quarterly_summaries, yearly_summaries, client_metrics) after correcting the payments table. The easiest way to do this is to call populate_all_summaries() *after* the data migration.
    9. **Update Triggers:** Update all triggers that use applied_start_quarter and applied_end_quarter to reflect the change to month numbers for monthly payments.

---

**FIXME: Broken Payment Versioning**

*   **Issue:** The version_payments trigger is broken and does not create versions of updated payments.
*   **Evidence:** The trigger uses the incorrect column name id instead of payment_id. It also attempts to update valid_from and valid_to incorrectly.
*   **Affected Components:**
    *   triggers.py (version_payments trigger)
    *   payments table
*   **Fix:**
    1.  **Correct the trigger definition in triggers.py:**
    
sql
        CREATE TRIGGER version_payments
        BEFORE UPDATE ON payments
        FOR EACH ROW
        BEGIN
            INSERT INTO payments (
                payment_id, contract_id, client_id, received_date,
                applied_start_quarter, applied_start_year,
                applied_end_quarter, applied_end_year,
                total_assets, expected_fee, actual_fee,
                method, notes, valid_from, valid_to
            ) VALUES (
                OLD.payment_id, OLD.contract_id, OLD.client_id, OLD.received_date,
                OLD.applied_start_quarter, OLD.applied_start_year,
                OLD.applied_end_quarter, OLD.applied_end_year,
                OLD.total_assets, OLD.expected_fee, OLD.actual_fee,
                OLD.method, OLD.notes, OLD.valid_from, DATETIME('now')
            );
            UPDATE payments SET valid_from = DATETIME('now'), valid_to = NULL
            WHERE payment_id = OLD.payment_id;
        END;


        *   Change WHERE id = OLD.id to WHERE payment_id = OLD.payment_id.
        *   Move the UPDATE payments SET valid_from ... statement to *before* the main UPDATE operation.
        *   The INSERT INTO statement should explicitly list all columns to avoid issues if the table schema changes.
    2. **Recreate the trigger:** Drop and recreate the corrected trigger in the database.

---

**FIXME (COMPLETELY FIXED): Missing Unique Constraint on Active Contracts**

*   **Issue:** There is no database constraint to prevent multiple active contracts for a single client.
*   **Evidence:** The contracts table schema lacks a unique constraint on (client_id, active). The application relies on LIMIT 1 in get_active_contract, which is a workaround, not a solution.
*   **Affected Components:**
    *   contracts table (database schema)
    *   utils.py (get_active_contract, save_contract)
*   **Fix:**
    1.  **Add a unique constraint:**
        *   Create a database migration to add a unique constraint to the contracts table:
        
sql
            ALTER TABLE contracts ADD CONSTRAINT unique_active_contract UNIQUE (client_id, active);


        *   **Important:** Before adding this constraint, ensure that there are no existing violations (multiple active contracts for the same client). If violations exist, you'll need to manually resolve them (e.g., by setting active = 'FALSE' for all but one contract per client) before adding the constraint.
    2.  **Modify save_contract (in utils.py):** Wrap the UPDATE and INSERT operations in an explicit transaction:
    
python
        conn = get_database_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")  # Start transaction
            if mode == 'add':
                cursor.execute("""
                    UPDATE contracts
                    SET active = 'FALSE'
                    WHERE client_id = ? AND active = 'TRUE'
                """, (client_id,))

            # ... (rest of the save_contract logic) ...

            conn.commit()  # Commit transaction
        except Exception as e:
            conn.rollback()
            # ... (handle error) ...
        finally:
            conn.close()


    3.  **Remove LIMIT 1 (Optional):** Once the unique constraint is in place, the LIMIT 1 in get_active_contract is no longer strictly necessary (although it doesn't hurt to leave it as a safety measure).

---

**FIXME: Redundant Summary Updates**

*   **Issue:** Summary tables are updated twice: once by triggers and again by manual calls to update_all_summaries.
*   **Evidence:** The add_payment and update_payment functions in client_payments.py call update_all_summaries after the database operations that trigger the summary updates.
*   **Affected Components:**
    *   client_payments.py (add_payment, update_payment)
    *   summaries.py (update_all_summaries, and the individual update functions)
    *   triggers.py (all summary update triggers)
*   **Fix:**
    1.  **Remove the calls to update_all_summaries from add_payment and update_payment (in utils.py).**  The triggers should handle all summary updates.

---

**FIXME: Missing Yearly Summary Update on Quarter Update**

*   **Issue:** The YoY growth in yearly_summaries is not recalculated when quarterly data is updated.
*   **Evidence:** The update_yearly_after_quarterly_change trigger only fires on INSERT to quarterly_summaries, not on UPDATE.
*   **Affected Components:**
    *   triggers.py (update_yearly_after_quarterly_change trigger)
    *   yearly_summaries table
*   **Fix:**
    1.  **Modify the trigger:** Change the trigger to fire AFTER INSERT OR UPDATE:

    
sql
        CREATE TRIGGER IF NOT EXISTS update_yearly_after_quarterly_change
        AFTER INSERT OR UPDATE ON quarterly_summaries  -- Change this line
        BEGIN
            -- ... (rest of the trigger logic remains the same) ...
        END;


    2. **Recreate the trigger:** Drop and recreate the modified trigger.

---
**FIXME: Potential Data Loss Due to Missing Concurrency Control**

*  **Issue:** The application lacks any mechanism to prevent data loss from concurrent modifications (e.g., two users editing the same payment simultaneously).
*  **Evidence:**  There's no version checking or locking implemented in the update_payment function.
*   **Affected Components:**
    *   utils.py (update_payment)
    *   payments table (potentially add a version column)
*   **Fix:**
    1.  **Implement Optimistic Locking:**
        *   **Add a version column (INTEGER) to the payments table.**  This column will store a version number that is incremented on each update.
        *   **Modify get_payment_by_id (in utils.py):**  Include the version in the data returned.
        *   **Modify update_payment (in utils.py):**
            *   Include the version in the WHERE clause of the UPDATE statement:
            
sql
                UPDATE payments
                SET ...
                WHERE payment_id = ? AND version = ?
                """, (..., payment_id, original_version))


            *   Increment the version in the SET clause: version = version + 1.
            *   Check the number of rows affected by the UPDATE. If no rows were affected (meaning the version didn't match), it indicates that another user modified the payment concurrently.  Raise an exception or return an error to the user.
        * **Example Implementation (in update_payment):**
        
python
            cursor.execute("SELECT version FROM payments WHERE payment_id = ?", (payment_id,))
            original_version = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE payments
                SET ..., version = version + 1
                WHERE payment_id = ? AND version = ?
            """, (..., payment_id, original_version))

            if cursor.rowcount == 0:
                conn.rollback()
                raise Exception("Concurrent modification detected. Please refresh and try again.")



---

**FIXME: Unnecessary Summary Recreation on Startup**

*   **Issue:** The application recreates all summary tables on every startup, which is inefficient and potentially dangerous.
*   **Evidence:** ensure_summaries_initialized calls populate_all_summaries (which deletes and recreates all summaries) if the summary tables are empty. ensure_summaries_initialized is called in multiple places.
*   **Affected Components:**
    *   utils.py (ensure_summaries_initialized)
    *   summaries.py (populate_all_summaries)
*   **Fix:**
    1.  **Modify ensure_summaries_initialized (in utils.py):** Remove the call to populate_all_summaries(). The summary tables should only be populated once, during initial setup, or manually if needed. The triggers should maintain the summaries after that.  The function should *only* ensure the triggers exist.
    2.  **Provide a manual way to rebuild summaries:** Add a function (perhaps in a separate admin module) that allows an administrator to manually rebuild the summary tables if necessary (e.g., after a database schema change or data corruption).

---

**FIXME: Payments Missing from History Due to INNER JOIN**
* **Issue:** Payments may not appear in the payment history if the corresponding entry in quarterly_summaries is missing.
* **Evidence:** The get_payment_history function in utils.py uses an INNER JOIN with the quarterly_summaries table.
* **Affected Components:**
    * utils.py (get_payment_history)
* **Fix:**
    1. **Change the INNER JOIN to a LEFT JOIN:**
    
sql
        FROM payments p
        JOIN contracts c ON p.contract_id = c.contract_id
        LEFT JOIN quarterly_summaries qs ON  -- Change this line
            p.client_id = qs.client_id AND
            p.applied_start_year = qs.year AND
            p.applied_start_quarter = qs.quarter


---
**FIXME: Inconsistent Trigger Logic**
* **Issue:** The after update trigger for quarterly_summaries updates both the old and the new quarters.
* **Evidence:** The update_quarterly_after_update trigger in triggers.py has two insert statements.
* **Affected Components:**
	* triggers.py
* **Fix:**
	1. Rewrite the trigger to only update the new quarter, and to correctly recalculate the old quarter.

sql
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

    -- Delete the old quarterly summary if no payments exist anymore.
     DELETE FROM quarterly_summaries
                WHERE payment_count = 0 and client_id = OLD.client_id
                AND applied_start_year = OLD.applied_start_year
                AND applied_start_quarter = OLD.applied_start_quarter;

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


2. **Recreate the trigger:** Drop and recreate the modified trigger.

---

These FIXME items represent the most critical issues that need to be addressed to improve the data integrity, reliability, and maintainability of the 401(k) Payment Tracker application. Addressing these issues will significantly enhance the application's robustness and correctness.