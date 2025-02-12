import sqlite3
from datetime import datetime

def test_payment_versioning():
    """Test to verify payment versioning functionality"""
    conn = sqlite3.connect('DATABASE/401kDATABASE.db')
    cursor = conn.cursor()
    
    try:
        # 1. Create test client
        print("\nStep 1: Creating test client...")
        cursor.execute('''
            INSERT INTO clients (display_name, full_name)
            VALUES (?, ?)
        ''', ('TEST_VERSION_CLIENT', 'Test Version Client'))
        client_id = cursor.lastrowid
        print(f"Created client with ID: {client_id}")

        # 2. Create contract
        print("\nStep 2: Creating contract...")
        cursor.execute('''
            INSERT INTO contracts (
                client_id, active, provider_name,
                payment_schedule, fee_type, percent_rate
            )
            VALUES (?, 'TRUE', 'TEST_PROVIDER', 'monthly', 'percentage', 0.5)
        ''', (client_id,))
        contract_id = cursor.lastrowid
        print(f"Created contract with ID: {contract_id}")

        # 3. Add initial payment
        print("\nStep 3: Adding initial payment...")
        cursor.execute('''
            INSERT INTO payments (
                client_id, contract_id, received_date,
                applied_start_quarter, applied_start_year,
                applied_end_quarter, applied_end_year,
                total_assets, actual_fee, method,
                valid_from
            )
            VALUES (?, ?, '2024-01-15', 1, 2024, 1, 2024, 100000, 1000, 'TEST', datetime('now'))
        ''', (client_id, contract_id))
        payment_id = cursor.lastrowid
        print(f"Created payment with ID: {payment_id}")

        # Commit initial data
        conn.commit()

        # 4. Update the payment
        print("\nStep 4: Updating payment...")
        cursor.execute('''
            UPDATE payments 
            SET actual_fee = 2000
            WHERE payment_id = ?
        ''', (payment_id,))
        conn.commit()

        # 5. Check versions
        print("\nStep 5: Checking payment versions...")
        cursor.execute('''
            SELECT payment_id, actual_fee, valid_from, valid_to
            FROM payments 
            WHERE client_id = ?
            ORDER BY valid_from DESC
        ''', (client_id,))
        versions = cursor.fetchall()
        
        print("\nPayment Versions:")
        for version in versions:
            print(f"Payment ID: {version[0]}")
            print(f"Amount: ${version[1]}")
            print(f"Valid From: {version[2]}")
            print(f"Valid To: {version[3]}")
            print("---")

    except Exception as e:
        print(f"Error during test: {str(e)}")
        conn.rollback()
    finally:
        # Clean up test data
        print("\nCleaning up test data...")
        cursor.execute("DELETE FROM payments WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM contracts WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    test_payment_versioning() 