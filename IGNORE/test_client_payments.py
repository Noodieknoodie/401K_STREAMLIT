import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from freezegun import freeze_time
from datetime import datetime
import traceback
import sys
import warnings

# Suppress specific warnings from Streamlit
warnings.filterwarnings("ignore", category=UserWarning, message=".*ScriptRunContext.*")

# Debug function to help identify test issues
def debug_test(func):
    def wrapper(*args, **kwargs):
        try:
            print(f"\nExecuting test: {func.__name__}")
            print("=" * 50)
            # Check if session state is properly initialized
            if not hasattr(st, 'session_state'):
                raise Exception("ERROR: st.session_state not initialized")
            
            # Print current session state for debugging
            print("Current session state variables:")
            for key, value in st.session_state.items():
                print(f"  {key}: {value}")
            
            result = func(*args, **kwargs)
            print(f"Test {func.__name__} completed successfully")
            return result
        except Exception as e:
            print(f"\nERROR in test {func.__name__}:")
            print("-" * 50)
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            print("-" * 50)
            raise  # Re-raise the exception after printing debug info
    return wrapper

try:
    from pages_new.client_display_and_forms.client_payments import (
        init_payment_state,
        reset_payment_form,
        show_payment_form,
        validate_payment_data
    )
except ImportError as e:
    print("\nERROR: Failed to import required modules")
    print(f"Import Error: {str(e)}")
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

class TestClientPayments(unittest.TestCase):
    def setUp(self):
        print("\nSetting up test environment...")
        try:
            # Initialize complete session state
            if not hasattr(st, 'session_state'):
                st.session_state = {}
            
            # Initialize all required session state variables
            required_states = {
                'payment_edit_id': None,
                'show_payment_form': False,
                'payment_form_data': {},
                'client_id': 1,
                'client_selector_dashboard': None,
                'show_contract_form': False,
                'contract_form_data': {},
                'contract_edit_id': None,
                'selected_client': None,
                'previous_client': None,
                'show_delete_confirm': False,
                'current_page': '👥 Client Dashboard'
            }
            
            for key, value in required_states.items():
                st.session_state[key] = value
                if key not in st.session_state:
                    raise Exception(f"Failed to initialize session state: {key}")
            
            # Mock st.rerun
            self.original_rerun = getattr(st, 'rerun', None)
            st.rerun = MagicMock()
            print("Session state and rerun mock initialized successfully")
            
        except Exception as e:
            print("\nERROR in setUp:")
            print(f"Exception: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            raise
            
    def tearDown(self):
        print("\nCleaning up test environment...")
        try:
            # Restore original st.rerun if it existed
            if self.original_rerun:
                st.rerun = self.original_rerun
            print("Test environment cleanup completed successfully")
        except Exception as e:
            print("\nERROR in tearDown:")
            print(f"Exception: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    def test_init_payment_state(self):
        """Test payment state initialization"""
        try:
            print("\nTesting payment state initialization...")
            
            # Clear session state
            st.session_state.clear()
            print("Session state cleared")
            
            # Initialize state
            init_payment_state()
            print("Payment state initialized")
            
            # Verify all required state variables are initialized
            required_states = {
                'show_payment_form': False,
                'payment_form_data': {},
                'payment_edit_id': None,
                'show_delete_confirm': False
            }
            
            for key, expected_value in required_states.items():
                print(f"Checking state variable: {key}")
                self.assertIn(key, st.session_state, f"Missing state variable: {key}")
                actual_value = st.session_state[key]
                self.assertEqual(
                    actual_value,
                    expected_value,
                    f"Incorrect value for {key}. Expected: {expected_value}, Got: {actual_value}"
                )
            
            print("All state variables verified successfully")
            
        except Exception as e:
            print("\nError in test_init_payment_state:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    def test_reset_payment_form(self):
        """Test payment form reset"""
        try:
            print("\nTesting payment form reset...")
            
            # Set up initial state
            print("Setting up test state...")
            initial_states = {
                'show_payment_form': True,
                'payment_form_data': {'test': 'data'},
                'payment_edit_id': 1
            }
            
            for key, value in initial_states.items():
                st.session_state[key] = value
                print(f"Set {key} to {value}")
            
            # Reset form
            print("Calling reset_payment_form...")
            reset_payment_form()
            
            # Verify state is reset
            print("Verifying state reset...")
            verification_items = [
                ('show_payment_form', False, "Form should be hidden"),
                ('payment_form_data', {}, "Form data should be empty"),
                ('payment_edit_id', None, "Edit ID should be None")
            ]
            
            for key, expected, message in verification_items:
                actual = st.session_state[key]
                print(f"Checking {key}: Expected={expected}, Actual={actual}")
                self.assertEqual(actual, expected, message)
            
            print("Form reset verification completed successfully")
            
        except Exception as e:
            print("\nError in test_reset_payment_form:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    @freeze_time("2024-03-15")
    @patch('pages_new.client_display_and_forms.client_payments.get_active_contract')
    @patch('pages_new.client_display_and_forms.client_payments.get_period_options')
    @patch('utils.utils.get_database_connection')
    def test_show_payment_form(self, mock_db, mock_period_options, mock_active_contract):
        """Test payment form display with different scenarios"""
        try:
            print("\nTesting payment form display...")
            
            # Setup database mock
            print("Setting up database mock...")
            try:
                mock_cursor = MagicMock()
                mock_db.return_value.cursor.return_value = mock_cursor
                mock_cursor.fetchone.return_value = (1, 'Test Client')
                print("Database mock setup complete")
            except Exception as e:
                print("Error setting up database mock:")
                print(str(e))
                raise
            
            # Test valid contract with monthly schedule
            print("\nTesting valid monthly contract scenario...")
            try:
                valid_contract = (
                    1,              # contract_id
                    'Provider',     # provider_name
                    '12345',       # contract_number
                    'monthly',      # payment_schedule
                    'percentage',   # fee_type
                    0.015,         # percent_rate
                    None,          # flat_rate
                    100           # num_people
                )
                mock_active_contract.return_value = valid_contract
                
                period_options = ['Feb 2024', 'Jan 2024', 'Dec 2023']
                mock_period_options.return_value = period_options
                
                with patch('streamlit.form') as mock_form, \
                    patch('streamlit.selectbox') as mock_selectbox, \
                    patch('streamlit.date_input') as mock_date, \
                    patch('streamlit.number_input') as mock_number, \
                    patch('streamlit.text_input') as mock_text, \
                    patch('streamlit.text_area') as mock_textarea:
                    
                    # Setup mock returns
                    print("Setting up Streamlit component mocks...")
                    mock_selectbox.return_value = 'Feb 2024'
                    mock_date.return_value = datetime(2024, 3, 1).date()
                    mock_number.return_value = 1000000
                    mock_text.return_value = '1500.00'
                    mock_textarea.return_value = 'Test payment'
                    
                    print("Calling show_payment_form...")
                    show_payment_form(st.session_state.client_id, valid_contract)
                    
                    # Verify form components were rendered
                    print("Verifying form components...")
                    mock_form.assert_called()
                    mock_selectbox.assert_called()
                    mock_date.assert_called()
                    mock_number.assert_called()
                    mock_text.assert_called()
                    mock_textarea.assert_called()
                    print("Valid contract scenario verified successfully")
                    
            except Exception as e:
                print("Error in valid contract scenario:")
                print(str(e))
                raise
            
            # Test contract without payment schedule
            print("\nTesting contract without payment schedule...")
            try:
                invalid_contract = (
                    2,              # contract_id
                    'Provider',     # provider_name
                    '12345',       # contract_number
                    None,          # payment_schedule
                    'percentage',   # fee_type
                    0.015,         # percent_rate
                    None,          # flat_rate
                    100           # num_people
                )
                mock_active_contract.return_value = invalid_contract
                
                with patch('streamlit.warning') as mock_warning:
                    show_payment_form(st.session_state.client_id, invalid_contract)
                    mock_warning.assert_called()
                    print("Missing schedule warning verified")
            except Exception as e:
                print("Error in invalid contract scenario:")
                print(str(e))
                raise
            
            # Test no active contract
            print("\nTesting no active contract scenario...")
            try:
                mock_active_contract.return_value = None
                with patch('streamlit.error') as mock_error:
                    show_payment_form(st.session_state.client_id, None)
                    mock_error.assert_called()
                    print("Missing contract error verified")
            except Exception as e:
                print("Error in no contract scenario:")
                print(str(e))
                raise
                
        except Exception as e:
            print("\nError in test_show_payment_form:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise
            
    @debug_test
    @freeze_time("2024-03-15")
    @patch('utils.utils.get_database_connection')
    def test_validate_payment_data(self, mock_db):
        """Test payment data validation with different scenarios"""
        try:
            print("\nTesting payment data validation...")
            
            # Setup database mock
            print("Setting up database mock...")
            mock_cursor = MagicMock()
            mock_db.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1, 'Test Client')
            
            # Test valid payment data (in arrears)
            print("\nTesting valid payment data...")
            try:
                valid_data = {
                    'applied_start_period': 2,  # February
                    'applied_start_year': 2024,
                    'applied_end_period': 2,    # February
                    'applied_end_year': 2024,
                    'received_date': '2024-03-01',
                    'actual_fee': '1500.00',
                    'total_assets': '1000000',
                    'notes': 'Test payment',
                    'payment_schedule': 'monthly'
                }
                
                errors = validate_payment_data(valid_data)
                self.assertEqual(errors, [], "Valid data should not produce errors")
                print("Valid data validation successful")
            except Exception as e:
                print("Error in valid data validation:")
                print(str(e))
                raise
            
            # Test missing required fields
            print("\nTesting missing required fields...")
            try:
                invalid_data = {
                    'applied_start_period': 2,
                    'applied_start_year': 2024,
                    'applied_end_period': 2,
                    'applied_end_year': 2024,
                    'notes': 'Test payment',
                    'payment_schedule': 'monthly'
                }
                
                errors = validate_payment_data(invalid_data)
                self.assertTrue(len(errors) > 0, "Missing fields should produce errors")
                self.assertTrue(
                    any('received_date' in err.lower() for err in errors),
                    "Should have received_date error"
                )
                self.assertTrue(
                    any('actual_fee' in err.lower() for err in errors),
                    "Should have actual_fee error"
                )
                print("Missing fields validation successful")
            except Exception as e:
                print("Error in missing fields validation:")
                print(str(e))
                raise
            
            # Test invalid period range
            print("\nTesting invalid period range...")
            try:
                invalid_period_data = {
                    'applied_start_period': 3,  # March (current month)
                    'applied_start_year': 2024,
                    'applied_end_period': 2,    # February
                    'applied_end_year': 2024,
                    'received_date': '2024-03-01',
                    'actual_fee': '1500.00',
                    'total_assets': '1000000',
                    'notes': 'Test payment',
                    'payment_schedule': 'monthly'
                }
                
                errors = validate_payment_data(invalid_period_data)
                self.assertTrue(len(errors) > 0, "Invalid period should produce errors")
                self.assertTrue(
                    any('arrears' in err.lower() for err in errors),
                    "Should have arrears-related error"
                )
                print("Invalid period validation successful")
            except Exception as e:
                print("Error in invalid period validation:")
                print(str(e))
                raise
            
            # Test quarterly payment
            print("\nTesting quarterly payment...")
            try:
                quarterly_data = {
                    'applied_start_period': 4,  # Q4
                    'applied_start_year': 2023,
                    'applied_end_period': 4,    # Q4
                    'applied_end_year': 2023,
                    'received_date': '2024-03-01',
                    'actual_fee': '1500.00',
                    'total_assets': '1000000',
                    'notes': 'Test payment',
                    'payment_schedule': 'quarterly'
                }
                
                errors = validate_payment_data(quarterly_data)
                self.assertEqual(errors, [], "Valid quarterly data should not produce errors")
                print("Quarterly payment validation successful")
            except Exception as e:
                print("Error in quarterly payment validation:")
                print(str(e))
                raise
                
        except Exception as e:
            print("\nError in test_validate_payment_data:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

if __name__ == '__main__':
    unittest.main()