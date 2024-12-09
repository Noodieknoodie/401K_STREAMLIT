- Many Streamlit commands prefixed with 'experimental' are outdated. For example, `st.experimental.rerun` is deprecated—use `st.rerun` instead.
- ALL PAYMENTS ARE IN ARREARS. 

# State Transitions & User Paths

## Client Selection Flow
When I first load the dashboard:
1. I see a dropdown to select a client
2. No forms or data are visible yet
3. The previous_client state is None

When I select a client:
1. The client_id and name are stored
2. ALL previous states are cleared (payment form, contact form, notes, filters)
3. Then new states are initialized
4. The dashboard loads with client's data

## Payment Form States
When I click "Add Payment":
1. The payment_form['is_visible'] becomes True
2. The payment_form['client_id'] is set to current client
3. The form appears with default values (current date, previous quarter)
4. The form stays visible until I:
   - Save the payment (clears form)
   - Cancel the form (clears form)
   - Switch clients (form auto-clears)

## Contact Form States
When I click any "Add Contact" button:
1. The contact_form['is_open'] becomes True
2. The contact_form['contact_type'] is set (Primary/Authorized/Provider)
3. The form appears empty
4. The form stays open until I:
   - Save the contact (clears form)
   - Cancel without changes (clears form)
   - Cancel with changes (shows confirmation)
   - Switch clients (form auto-clears)

## Notes States
When I click a note button:
1. If no note is active:
   - That note becomes active
   - Text area appears
2. If another note is active:
   - Previous note auto-saves
   - New note becomes active
3. Notes clear when:
   - I click the note button again
   - I switch clients
   - I save the note

## Filter States
When I change payment history filters:
1. The filter_state updates
2. Payment data resets to empty
3. New filtered data loads
4. Filters reset when:
   - I switch clients
   - I select "All Time"

## Important State Rules
1. Client changes ALWAYS clear ALL states first
2. Forms can't be open simultaneously (Streamlit limitation)
3. Payment form visibility is tied to current client_id
4. Contact form type is set when opening, not after
5. Notes auto-save when switching between them
6. ALL states are managed in session_state
7. ALL states have proper initialization
8. ALL states clear properly on client change

## Common Issues to Watch For
1. If a form appears when switching clients:
   - The clear_client_specific_states() might be running after state initialization
   - The form's client_id might not be checked
2. If states don't clear properly:
   - Check the order of operations in show_client_dashboard()
   - Verify all states are included in clear_client_specific_states()
3. If forms conflict:
   - Remember only one dialog can be open
   - Check if states are properly resetting
