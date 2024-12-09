<!-- Cusor_MUST_REMEMBER.md
>> This file is for Cursor Ai's personal use and self

# Cursor, this is your memory cheat sheet to avoid retracing the same missteps and to remind yourself of the best way to tackle similar challenges in the future. 
Use this document as a personal memory bank where you jot down:  
 Mistakes or inefficiencies you’ve encountered and how you eventually figured out the right solutions.  
- Clarifications for outdated or misunderstood concepts (e.g., deprecated commands and their updated counterparts).  
- The little details you tend to forget, like handling edge cases or managing session state properly.  
- Workflow adjustments or shortcuts you discovered through trial and error.  


# **WHEN, HOW and WHY** TO UTILIZE THIS DOCUMENT:
When: Add to this document any time you solve a problem, uncover a key detail, or figure out a solution that could have prevented wasted time or frustration if it had been documented here earlier. Focus on capturing anything you didn’t do **by default** but should have, to make future work smoother and more efficient.  
Why: Future agents (including you) working on this project will encounter the same challenges due to shared training and approaches. This document acts as a LIVING RECORD of lessons learned, helping agents progressively avoid errors and become more tailored to the specific needs of the project. It ensures growth through shared knowledge and avoids repeating the same mistakes.  
How: Write entries as concise bullet points using `-` (dash) syntax. Keep them clear and to the point, framed as if talking to a future version of yourself. Add only new and important insights or solutions to maintain the document’s value.  


-->

# MEMORY BANK BEGIN BELOW

- Many Streamlit commands prefixed with 'experimental' are outdated. For example, `st.experimental.rerun` is deprecated—use `st.rerun` instead.
- ALL PAYMENTS ARE IN ARREARS. 
- When accessing contract data from get_active_contract(), the field indices are:
  - 0: contract_id
  - 1: provider_name
  - 2: contract_number
  - 3: payment_schedule
  - 4: fee_type
  - 5: percent_rate
  - 6: flat_rate
  - 7: num_people
- Payments must ALWAYS be for previous quarters (in arrears). This needs to be enforced at:
  - UI level (quarter selection)
  - Validation level (payment data validation)
  - Business logic level (quarter range validation)
- Streamlit can only have ONE dialog open at a time using st.dialog. When designing forms:
  - Never try to open multiple dialogs
  - Use inline forms or containers when additional UI elements need to appear/disappear
  - Avoid nested dialogs or dialog triggers within dialogs
- Never use empty strings for Streamlit input labels. Instead:
  - Always provide a meaningful label that describes the input
  - If you want to hide the label, use label_visibility="collapsed"
  - This prevents accessibility warnings and future compatibility issues
- Payment schedules are a FIXED CONTRACT PROPERTY, not a user input:
  - Can be 'monthly', 'quarterly', or NULL
  - Affects period selection, validation, and display
  - Must be handled gracefully when NULL (grey out period selection)
  - Period calculations must respect the schedule type
- Period selection must ALWAYS be in arrears regardless of schedule:
  - Monthly: Can't select current or future months
  - Quarterly: Can't select current or future quarters
  - Multi-period selections must also be in arrears
