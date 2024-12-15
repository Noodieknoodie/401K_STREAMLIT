# utils\ui_state_manager.py

from typing import Optional, Literal, TypedDict, List, Dict, Any, Union
import streamlit as st
from utils.debug_logger import debug

class BaseDialogState(TypedDict):
    """Base state structure shared by all dialogs"""
    is_open: bool
    mode: Literal['add', 'edit']
    validation_errors: List[str]
    show_cancel_confirm: bool
    form_data: Dict[str, Any]

class PaymentDialogState(BaseDialogState):
    """Payment dialog specific state"""
    client_id: Optional[int]
    expected_fee: Optional[float]

class ContactDialogState(BaseDialogState):
    """Contact dialog specific state"""
    contact_type: Optional[str]
    contact_id: Optional[int]

class UIStateManager:
    """
    Central manager for dialog (modal) states in Streamlit applications.
    
    This manager provides a standardized way to handle dialog states while working
    with Streamlit's native dialog behavior. It handles the complete lifecycle of
    dialogs including:
    - Dialog visibility
    - Form data management
    - Validation states
    - Confirmation dialogs
    
    Usage:
        ui_manager = UIStateManager()
        
        # Open dialog with initial data
        ui_manager.open_payment_dialog(
            client_id=123,
            mode='edit',
            initial_data={'amount': 1000}
        )
        
        # Update form data
        ui_manager.update_payment_form_data({'amount': 2000})
        
        # Handle validation
        ui_manager.set_payment_validation_errors(['Invalid amount'])
        
        # Handle cancel confirmation
        if ui_manager.show_payment_cancel_confirm():
            ui_manager.close_payment_dialog()
    """
    
    def __init__(self) -> None:
        """Initialize the UI state manager with standard dialog states."""
        if 'ui_state' not in st.session_state:
            initial_state = {
                'payment_dialog': PaymentDialogState(
                    is_open=False,
                    mode='add',
                    client_id=None,
                    expected_fee=None,
                    validation_errors=[],
                    show_cancel_confirm=False,
                    form_data={}
                ),
                'contact_dialog': ContactDialogState(
                    is_open=False,
                    mode='add',
                    contact_type=None,
                    contact_id=None,
                    validation_errors=[],
                    show_cancel_confirm=False,
                    form_data={}
                )
            }
            st.session_state.ui_state = initial_state
            debug.log_state_change(
                component='ui_state_manager',
                old_value=None,
                new_value=initial_state,
                context={'action': 'initialize'}
            )

    def open_payment_dialog(
        self,
        client_id: Optional[int] = None,
        mode: Literal['add', 'edit'] = 'add',
        initial_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Open the payment dialog with specified parameters and optional initial data."""
        state = self._get_dialog_state('payment')
        old_state = state.copy()
        
        state['is_open'] = True
        state['mode'] = mode
        state['client_id'] = client_id
        state['validation_errors'] = []
        state['show_cancel_confirm'] = False
        state['form_data'] = initial_data or {}
        
        debug.log_state_change(
            component='payment_dialog',
            old_value=old_state,
            new_value=state,
            context={'action': 'open', 'client_id': client_id, 'mode': mode}
        )

    def update_payment_form_data(self, data: Dict[str, Any]) -> None:
        """Update payment form data, preserving existing values."""
        state = self._get_dialog_state('payment')
        old_data = state['form_data'].copy()
        state['form_data'].update(data)
        
        debug.log_state_change(
            component='payment_form_data',
            old_value=old_data,
            new_value=state['form_data'],
            context={'action': 'update'}
        )

    def set_payment_validation_errors(self, errors: List[str]) -> None:
        """Set validation errors for the payment dialog."""
        state = self._get_dialog_state('payment')
        old_errors = state['validation_errors']
        state['validation_errors'] = errors
        
        debug.log_state_change(
            component='payment_validation',
            old_value=old_errors,
            new_value=errors,
            context={'action': 'set_errors'}
        )

    def clear_payment_validation_errors(self) -> None:
        """Clear all validation errors from the payment dialog."""
        state = self._get_dialog_state('payment')
        old_errors = state['validation_errors']
        state['validation_errors'] = []
        
        debug.log_state_change(
            component='payment_validation',
            old_value=old_errors,
            new_value=[],
            context={'action': 'clear_errors'}
        )

    def close_payment_dialog(self, clear_data: bool = True) -> None:
        """Close the payment dialog and optionally clear its data."""
        state = self._get_dialog_state('payment')
        old_state = state.copy()
        
        state['is_open'] = False
        state['show_cancel_confirm'] = False
        if clear_data:
            state['form_data'] = {}
            state['validation_errors'] = []
        
        debug.log_state_change(
            component='payment_dialog',
            old_value=old_state,
            new_value=state,
            context={'action': 'close', 'clear_data': clear_data}
        )

    def open_contact_dialog(
        self,
        contact_type: Optional[str] = None,
        mode: Literal['add', 'edit'] = 'add',
        contact_id: Optional[int] = None,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Open the contact dialog with specified parameters and optional initial data."""
        state = self._get_dialog_state('contact')
        old_state = state.copy()
        
        state['is_open'] = True
        state['mode'] = mode
        state['contact_type'] = contact_type
        state['contact_id'] = contact_id
        state['validation_errors'] = []
        state['show_cancel_confirm'] = False
        state['form_data'] = initial_data or {}
        
        debug.log_state_change(
            component='contact_dialog',
            old_value=old_state,
            new_value=state,
            context={
                'action': 'open',
                'contact_type': contact_type,
                'contact_id': contact_id,
                'mode': mode
            }
        )

    def update_contact_form_data(self, data: Dict[str, Any]) -> None:
        """Update contact form data, preserving existing values."""
        state = self._get_dialog_state('contact')
        old_data = state['form_data'].copy()
        state['form_data'].update(data)
        
        debug.log_state_change(
            component='contact_form_data',
            old_value=old_data,
            new_value=state['form_data'],
            context={'action': 'update'}
        )

    def set_contact_validation_errors(self, errors: List[str]) -> None:
        """Set validation errors for the contact dialog."""
        state = self._get_dialog_state('contact')
        old_errors = state['validation_errors']
        state['validation_errors'] = errors
        
        debug.log_state_change(
            component='contact_validation',
            old_value=old_errors,
            new_value=errors,
            context={'action': 'set_errors'}
        )

    def clear_contact_validation_errors(self) -> None:
        """Clear all validation errors from the contact dialog."""
        state = self._get_dialog_state('contact')
        old_errors = state['validation_errors']
        state['validation_errors'] = []
        
        debug.log_state_change(
            component='contact_validation',
            old_value=old_errors,
            new_value=[],
            context={'action': 'clear_errors'}
        )

    def close_contact_dialog(self, clear_data: bool = True) -> None:
        """Close the contact dialog and optionally clear its data."""
        state = self._get_dialog_state('contact')
        old_state = state.copy()
        
        state['is_open'] = False
        state['show_cancel_confirm'] = False
        if clear_data:
            state['form_data'] = {}
            state['validation_errors'] = []
        
        debug.log_state_change(
            component='contact_dialog',
            old_value=old_state,
            new_value=state,
            context={'action': 'close', 'clear_data': clear_data}
        )

    def close_all_dialogs(self) -> None:
        """Close all managed dialogs and clear their data."""
        old_states = {
            'payment': self._get_dialog_state('payment').copy(),
            'contact': self._get_dialog_state('contact').copy()
        }
        
        for dialog_type in ['payment', 'contact']:
            state = self._get_dialog_state(dialog_type)
            state['is_open'] = False
            state['show_cancel_confirm'] = False
            state['form_data'] = {}
            state['validation_errors'] = []
        
        debug.log_state_change(
            component='all_dialogs',
            old_value=old_states,
            new_value={
                'payment': self._get_dialog_state('payment'),
                'contact': self._get_dialog_state('contact')
            },
            context={'action': 'close_all'}
        )

    # Properties for state checking
    @property
    def is_payment_dialog_open(self) -> bool:
        """Check if payment dialog is open."""
        return self._get_dialog_state('payment')['is_open']
    
    @property
    def payment_dialog_has_errors(self) -> bool:
        """Check if payment dialog has validation errors."""
        return bool(self._get_dialog_state('payment')['validation_errors'])
    
    @property
    def payment_validation_errors(self) -> List[str]:
        """Get current payment dialog validation errors."""
        return self._get_dialog_state('payment')['validation_errors']
    
    @property
    def payment_form_data(self) -> Dict[str, Any]:
        """Get current payment form data."""
        return self._get_dialog_state('payment')['form_data']
    
    @property
    def is_contact_dialog_open(self) -> bool:
        """Check if contact dialog is open."""
        return self._get_dialog_state('contact')['is_open']
    
    @property
    def contact_dialog_has_errors(self) -> bool:
        """Check if contact dialog has validation errors."""
        return bool(self._get_dialog_state('contact')['validation_errors'])
    
    @property
    def contact_validation_errors(self) -> List[str]:
        """Get current contact dialog validation errors."""
        return self._get_dialog_state('contact')['validation_errors']
    
    @property
    def contact_form_data(self) -> Dict[str, Any]:
        """Get current contact form data."""
        return self._get_dialog_state('contact')['form_data']

    def _get_dialog_state(self, dialog_type: Literal['payment', 'contact']) -> Union[PaymentDialogState, ContactDialogState]:
        """Get the state for a specific dialog type.
        
        Args:
            dialog_type: The type of dialog to get state for ('payment' or 'contact')
            
        Returns:
            The dialog state dictionary
        """
        return st.session_state.ui_state[f'{dialog_type}_dialog'] 