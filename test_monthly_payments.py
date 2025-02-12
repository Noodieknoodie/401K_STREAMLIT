import sqlite3
from datetime import datetime
import os

def test_monthly_payment_storage():
    """Test to verify how monthly payments are stored and retrieved"""
    db_path = 'DATABASE/401kDATABASE.db'
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        print("Current directory:", os.getcwd())
        print("Available files:", os.listdir())
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create test client
        print("\nStep 1: Creating test client...")
        cursor.execute('''
            INSERT INTO clients (display_name, full_name)
            VALUES (?, ?)
        ''', ('TEST_MONTHLY_CLIENT', 'Test Monthly Client'))
        client_id = cursor.lastrowid
        print(f"Created client with ID: {client_id}")

        # 2. Create monthly contract
        print("\nStep 2: Creating monthly contract...")
        cursor.execute('''
            INSERT INTO contracts (
                client_id, active, provider_name,
                payment_schedule, fee_type, percent_rate
            )
            VALUES (?, 'TRUE', 'TEST_PROVIDER', 'monthly', 'percentage', 0.5)
        ''', (client_id,))
        contract_id = cursor.lastrowid
        print(f"Created contract with ID: {contract_id}")

        # 3. Add January 2024 payment
        print("\nStep 3: Adding January 2024 payment...")
        cursor.execute('''
            INSERT INTO payments (
                client_id, contract_id, received_date,
                applied_start_quarter, applied_start_year,
                applied_end_quarter, applied_end_year,
                total_assets, actual_fee, method
            )
            VALUES (?, ?, '2024-01-15', 1, 2024, 1, 2024, 100000, 1000, 'TEST')
        ''', (client_id, contract_id))
        payment_id = cursor.lastrowid
        print(f"Created payment with ID: {payment_id}")

        # Commit the changes
        conn.commit()

        # 4. Verify the data
        print("\nStep 4: Verifying stored data...")
        
        # Check client
        cursor.execute('SELECT * FROM clients WHERE client_id = ?', (client_id,))
        client = cursor.fetchone()
        print(f"\nClient Data:")
        print(f"ID: {client[0]}")
        print(f"Name: {client[1]}")

        # Check contract
        cursor.execute('SELECT * FROM contracts WHERE contract_id = ?', (contract_id,))
        contract = cursor.fetchone()
        print(f"\nContract Data:")
        print(f"ID: {contract[0]}")
        print(f"Client ID: {contract[1]}")
        print(f"Active: {contract[2]}")
        print(f"Provider: {contract[4]}")
        print(f"Schedule: {contract[9]}")  # payment_schedule column

        # Check payment
        cursor.execute('''
            SELECT 
                p.payment_id,
                p.received_date,
                p.applied_start_quarter,
                p.applied_start_year,
                p.applied_end_quarter,
                p.applied_end_year,
                p.actual_fee,
                c.payment_schedule,
                p.total_assets
            FROM payments p
            JOIN contracts c ON p.contract_id = c.contract_id
            WHERE p.payment_id = ?
        ''', (payment_id,))
        payment = cursor.fetchone()
        print(f"\nPayment Data:")
        print(f"ID: {payment[0]}")
        print(f"Received Date: {payment[1]}")
        print(f"Start Quarter/Month: {payment[2]}")  # This should be 1 for January
        print(f"Start Year: {payment[3]}")
        print(f"End Quarter/Month: {payment[4]}")    # This should be 1 for January
        print(f"End Year: {payment[5]}")
        print(f"Amount: ${payment[6]}")
        print(f"Schedule Type: {payment[7]}")
        print(f"Total Assets: ${payment[8]}")

        # 5. Check how it's displayed in the UI
        print("\nStep 5: Checking how payment would be displayed...")
        cursor.execute('''
            SELECT 
                c.provider_name,
                p.applied_start_quarter,
                p.applied_start_year,
                p.applied_end_quarter,
                p.applied_end_year,
                c.payment_schedule,
                p.received_date,
                p.total_assets,
                p.actual_fee
            FROM payments p
            JOIN contracts c ON p.contract_id = c.contract_id
            WHERE p.payment_id = ?
        ''', (payment_id,))
        display_data = cursor.fetchone()
        
        # This mimics the format_payment_data function's logic
        if display_data[5].lower() == 'monthly':
            start_month = ((display_data[1] - 1) * 3) + 1
            end_month = ((display_data[3] - 1) * 3) + 3
            start_date = datetime.strptime(f'2000-{start_month}-1', '%Y-%m-%d')
            end_date = datetime.strptime(f'2000-{end_month}-1', '%Y-%m-%d')
            if display_data[2] == display_data[4]:
                period_display = f"{start_date.strftime('%b')} {display_data[2]}"
            else:
                period_display = f"{start_date.strftime('%b')} {display_data[2]} - {end_date.strftime('%b')} {display_data[4]}"
        else:
            if display_data[1] == display_data[3] and display_data[2] == display_data[4]:
                period_display = f"Q{display_data[1]} {display_data[2]}"
            else:
                period_display = f"Q{display_data[1]} {display_data[2]} - Q{display_data[3]} {display_data[4]}"

        print("\nUI Display Data:")
        print(f"Provider: {display_data[0]}")
        print(f"Period Display: {period_display}")
        print(f"Received Date: {datetime.strptime(display_data[6], '%Y-%m-%d').strftime('%b %d, %Y')}")
        print(f"Total Assets: ${display_data[7]:,.2f}")
        print(f"Amount: ${display_data[8]:,.2f}")

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
    test_monthly_payment_storage() 