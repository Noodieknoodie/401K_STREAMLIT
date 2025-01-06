# CORE PRINCIPLES TO FOLLOW:
Use Streamlit's native form handling
Simple state management
Clear data flow
No complex UI manager
Use Streamlit forms properly
Keep state management simple
Let Streamlit handle reruns
Don't fight the framework
always use st.columns() inside containers rather than standalone
row containerization is cool
flexbox is your friend
equal sized things with extreme symmetry and balance is cool. seeing alligned sizes even between unlike components is cool. when looking left to right nothing should be too high, too low, not tall enough, not short enough, not the same and the component next to it in terms of where the edges are.
When looking at the layout vertically, the rule of thirds is your friend. if theres alot of content spanning the width, consider even width distribution. 
if you think that there isnt enough content to fill something width wise... then consider bringing in the left and right walls,,, having huge gaps is tacky. but also, the contrary is also true. having stuff crammed is also tacky. 
Consolidate section headers with their content by using styled containers, and use the row containerization to make it look nice. dont stack titles vertically. a subtitle that sits alone in a row is the biggest waste of space. put that shit next to the title horizontally. 


# Dynamically loads the database:
# 1. Primary: OneDrive for sync across users.
# 2. Fallback: Local "DATABASE" folder for backup/development.
# Includes error handling for unavailable paths.


# Technical Documentation for Main Summary Landing Dashboard Analytics

This is a 401k payment tracking system for a small financial advisory firm. They manage about 29 client companies' 401k plans and need to track incoming payments. The tricky part is that while they check things quarterly, clients pay in different ways - some monthly, some quarterly. 98% of the payments are directly applyying to the prior period 
The database is already set up and working - it tracks clients, their contracts, contacts, and most importantly, all their payments. Each client typically has one active contract at a time, and when one expires, it's immediately replaced with a new one. The payments can be either percentage-based (based on total assets) or flat-rate fees.
! PAYMENTS ARE IN AREERS !
The quarterly summary page you're building is part of a larger Streamlit app. The key thing users want to see is how payments are tracking quarter by quarter, (all payyments are aggregated in the database via a QUARTER system (1, 2, 3, 4) even if they have a MONTHLY payyment frequencyy. Pyython is used to calculate the database entries dyynamically.)  with the current quarter being the most important view. They need to easily spot who's paid, who hasn't, and what the totals look like.
Some quirks to keep in mind:
The expected_fee field is often empty (73% null), so don't rely on it too heavily... this is becasue its hard to find the assets under management alwaysy. the expected fee is auto calculated in the python code, and having it is a luxury. However, for fixed payment, its simple! the expected fee is their FIXED PAYYMENT HAHA
Clients can make multiple payments for the same quarter.
Payment dates don't match the quarter they yare for -- PAYMENTS ARE IN AREERS 
The main users are financial advisors who need to quickly check payment status and track quarterly totals. They're not tech experts, but they know their business well and need the information presented clearly and accurately.

NEEDS: to be flexible regarding the database but CLEAN ins and outs. 
I spent a LONG time asking chat GPT whats the most STANDARD PREFERRED WAY of setting up your database regarding formatting and stuff. So that being said - yoyu can ALWAYS assume the data in the database is formatted the "best practice" wayy. YYou can see exactly the setup in the database overview provided. 

regarding USER ENTRY... it’s gunna be flexible, require only a few required things... id reckon that the most important database interaction is the ADD PAYMENT and EDIT PAYMENT functionality. for the add payment, the user doesn’t have to enter a few things, such as client name and other obvious things considering the add payment button / form is accessible only while on an individual client’s specific dashboard, so the code knows a few fixed details by default – the keys and identification shit. Regarding LEGIT user inputs – we’re only requiring "date received" (since this should always be expected to have and it’s EASY and frankly doesn’t really affect jack shit if it’s perfect since payments are in arrears... yes, flexible... no complex validations regarding if date received is before or after stuff... who really cares...). Second required field for adding payment is the applied quarter, which is dynamic and jumps through a few hoops before hitting the DB... you see, in the DB there are 4 fields regarding the field application...

in the payments table you’ll find:
#     "applied_start_quarter" INTEGER,
#     "applied_start_year" INTEGER,
#     "applied_end_quarter" INTEGER,
#     "applied_end_year" INTEGER,

which is weird cause if you recall in the Contract Table there is:

#     "payment_schedule" TEXT,

which is either "quarterly" or "monthly".


the user openes the add payment form and see the current date in the "date received" field, which they can change as needed, but it’s the obvious default. the PRIOR QUARTER shows up in the "APPLIED QUARTER" dropdown, 

there really isn’t a WAY for the user to submit the form without selecting something in this field... it’s a dropdown with no option for "NOTHING." once they select the applied period, the backend uses python to convert that into:
#     "applied_start_quarter" INTEGER,
#     "applied_start_year" INTEGER,

so if we received a check from the example mock client we’ve been discussing in january 2025, the default would be "Q4 2024" for arrears, and the backend would store:
#     applied_start_quarter = 4
#     applied_start_year = 2024

for ADD PAYMENTS the monthly vs quarterly distinction is purely presentational.
Looking at the form logic:
For monthly clients:
Shows months in dropdown (e.g. "Jan 2024")
But converts to quarters before saving (start_quarter = (payment_data['applied_start_period'] - 1) // 3 + 1)
2. For quarterly clients:
Shows quarters directly (e.g. "Q1 2024")
Saves directly as quarters
The database ALWAYS stores quarters. The only difference is how we display the options to the user based on their payment frequency.
So no, there's no fundamental need for the "period" abstraction. We could:
Keep the UI display logic (showing months vs quarters)
But internally always work with quarters
Have clear conversion functions for monthly->quarterly
Name everything consistently with "quarter" since that's what we're actually storing
Almost all payments directly apply to a single quarter, which is why the `applied_end_quarter` and `applied_end_year` fields have such a large number of NULL values. For the common case where a payment applies to just one specific quarter, the user doesn’t need to enter anything for the "end" quarter or year. The system automatically copies the start selection into these fields since the payment only covers that one quarter.

HOWEVER, for rare multi-quarter scenarios (like backpayments or other unusual situations), the payment form includes a checkbox dropdown labeled "Payment covers multiple quarters." Clicking this gives the user the ability to select both a START QUARTER and an END QUARTER. These selections populate the database appropriately with the specified range.

There’s PYTHON CODE elsewhere in the app that dynamically splits these multi-payments into equitable portions, applying them evenly across the stated quarters. This ensures that the quarterly summary report reflects the truth of the payment distribution and avoids any large spikes. For example, if a payment spans three quarters, each quarter receives 1/3 of the total payment for reporting purposes.

From the user’s perspective, all applied quarter data is displayed concatenated as "Q1 2022" or "Q4 2024." For a multi-quarter payment, such as one covering Q1 2022 through Q3 2022, the database would store:

applied_start_quarter    applied_start_year    applied_end_quarter    applied_end_year
1                        2022                  1                      2022
2                        2022                  2                      2022
3                        2022                  3                      2022

In this case, the total received payment would be evenly split into thirds, with each quarter's `actual_fee` reflecting 1/3 of the payment.

----
# DATABASE INFO YOU WILL NEED 
----
## Database Structure
**Location:** `DATABASE/401kDATABASE.db`

### Tables and Fields

1. **clients**
```sql
CREATE TABLE "clients" (
    "client_id"      INTEGER PRIMARY KEY AUTOINCREMENT,
    "display_name"   TEXT NOT NULL,      -- Short name for display
    "full_name"      TEXT,               -- Complete legal name
    "ima_signed_date" TEXT,              -- Format: YYYY-MM-DD
    "file_path_account_documentation" TEXT,
    "file_path_consulting_fees" TEXT,
    "file_path_meetings" TEXT
)
```

2. **contacts**
```sql
CREATE TABLE "contacts" (
    "contact_id"         INTEGER PRIMARY KEY AUTOINCREMENT,
    "client_id"         INTEGER NOT NULL,
    "contact_type"      TEXT NOT NULL,    -- Values: Primary, Authorized, Provider
    "contact_name"      TEXT,
    "phone"             TEXT,
    "email"             TEXT,
    "fax"               TEXT,
    "physical_address"  TEXT,
    "mailing_address"   TEXT,
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
)
```

3. **contracts**
```sql
CREATE TABLE "contracts" (
    "contract_id"        INTEGER PRIMARY KEY AUTOINCREMENT,
    "client_id"         INTEGER NOT NULL,
    "active"            TEXT,             -- Values: TRUE, FALSE
    "contract_number"   TEXT,
    "provider_name"     TEXT,
    "contract_start_date" TEXT,           -- Format: YYYY-MM-DD
    "fee_type"          TEXT,             -- Values: percentage, flat
    "percent_rate"      REAL,
    "flat_rate"         REAL,
    "payment_schedule"  TEXT,             -- Values: monthly, quarterly
    "num_people"        INTEGER,
    "notes"             TEXT,
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
)
```

4. **payments**
```sql
CREATE TABLE "payments" (
    "payment_id"            INTEGER PRIMARY KEY AUTOINCREMENT,
    "contract_id"          INTEGER NOT NULL,
    "client_id"           INTEGER NOT NULL,
    "received_date"       TEXT,            -- Format: YYYY-MM-DD
    "applied_start_quarter" INTEGER,        -- Values: 1-4
    "applied_start_year"   INTEGER,         -- Format: YYYY
    "applied_end_quarter"  INTEGER,         -- Values: 1-4
    "applied_end_year"    INTEGER,         -- Format: YYYY
    "total_assets"        INTEGER,
    "expected_fee"        REAL,
    "actual_fee"          REAL,
    "method"             TEXT,             -- Values: Auto - Check, Auto - ACH, etc.
    "notes"              TEXT,
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id"),
    FOREIGN KEY("contract_id") REFERENCES "contracts"("contract_id")
)
```
## Available Indexes
```sql
CREATE INDEX idx_contacts_client_id ON contacts(client_id);
CREATE INDEX idx_contracts_client_id ON contracts(client_id);
CREATE INDEX idx_payments_client_id ON payments(client_id);
CREATE INDEX idx_payments_contract_id ON payments(contract_id);
CREATE INDEX idx_payments_date ON payments(client_id, received_date DESC);
CREATE INDEX idx_contacts_type ON contacts(client_id, contact_type);
CREATE INDEX idx_payments_quarter_year ON payments(client_id, applied_start_quarter, applied_start_year);
CREATE INDEX idx_contracts_provider ON contracts(provider_name);
```

# CHECK IT OUT! HELPFUL SHIT HERE!
## This was compiled a while ago, take it with a grain of salt. 

sqlite_sequence:
name: 0% nulls, 4 unique, average length 8 (7–9).
seq: 0% nulls, 4 unique, average length 2.25 (2–3).

clients:
client_id: 0% nulls, 29 unique, diverse, avg length 1.69 (1–2).
display_name: 0% nulls, 29 unique, diverse, avg length 12.97 (5–27).
full_name: 0% nulls, 29 unique, diverse, avg length 25 (4–58).
ima_signed_date: 31.03% nulls, 18 unique, avg length 10.
file_path_*: 100% nulls, no data.

contacts:
contact_id: 0% nulls, 68 unique, diverse, avg length 1.87 (1–2).
client_id: 0% nulls, 29 unique, avg length 1.65.
contact_type: 0% nulls, 3 unique, avg length 8.37 (7–10).
contact_name: 7.35% nulls, 57 unique, diverse, avg length 12.41 (4–20).
phone: 42.65% nulls, 30 unique, avg length 12.
email: 25% nulls, 46 unique, avg length 22.04 (13–35).
fax: 97.06% nulls, 2 unique, avg length 12.5.
physical_address: 52.94% nulls, 28 unique, avg length 37.88 (30–52).
mailing_address: 75% nulls, 17 unique, avg length 38.35.

contracts:
contract_id: 0% nulls, 35 unique, avg length 1.74.
client_id: 0% nulls, avg length 1.66.
active: 0% nulls, 2 unique, avg length 4.17.
contract_number: 20% nulls, 26 unique, avg length 5.46.
provider_name: 0% nulls, 15 unique, avg length 11.49.
contract_start_date: 91.43% nulls, 3 unique, avg length 10.67.
fee_type: 2.86% nulls, 2 unique, avg length 7.71.
percent_rate: 40% nulls, 14 unique, avg length 4.59.
flat_rate: 60% nulls, 10 unique, avg length 6.08.
payment_schedule: 2.86% nulls, 2 unique, avg length 8.06.
num_people: 14.29% nulls, 20 unique, avg length 4.23.
notes: 94.29% nulls, 2 unique, avg length 67.

payments:
payment_id: 0% nulls, 924 unique, avg length 2.88.
contract_id: 0% nulls, avg length 1.69.
client_id: 0% nulls, avg length 1.64.
received_date: 0% nulls, 360 unique, avg length 10.
applied_start_quarter and applied_end_quarter: 0% nulls, 4/8 unique, avg length 1/4.
applied_start_year and applied_end_year: same as quarter but for year 
total_assets: 51.3% nulls, 443 unique, avg length 6.53.
expected_fee: 73.48% nulls, 148 unique, avg length 6.08.
actual_fee: 0.11% nulls, 674 unique, avg length 6.15.
method: 0% nulls, 4 unique, avg length 8.1.
notes: 81.6% nulls, 113 unique, avg length 40.93.


----

## MORE HELPFUL INFO?

## Data Relationships
- Each client can have multiple contracts (one-to-many)
- Each contract can have multiple payments (one-to-many)
- Each client can have multiple contacts of different types (one-to-many)

## Important Notes
1. Contracts are continuous - when one expires, it's immediately replaced
2. Payment schedules vary between monthly and quarterly
3. Fee types can be either percentage-based or flat rate
4. All monetary values are stored as REAL in the database
5. Dates are stored as TEXT in YYYY-MM-DD format

## Data Quality Considerations
- `expected_fee` is NULL in ~73% of payment records
- `total_assets` is NULL in ~51% of payment records
- Contract dates have some gaps
- Some clients have missing IMA signed dates

** FLEXIBILITY IS A MUST! &


Let me add crucial additional technical details:

## Streamlit Environment & Integration

### Page Structure
- File is part of multi-page Streamlit app
- Located in `pages/main_summary/summary.py`
- Must include `show_main_summary()` function (this is called by the main app)
- Page appears in sidebar navigation automatically

### Fee Calculation Logic
```python
# For percentage-based fees
fee = total_assets * percent_rate

# For flat-rate fees
fee = flat_rate  # per payment schedule
```


## UI/UX Context

### Display Requirements
1. Currency formatting: `${:,.2f}`
2. Date formatting: `YYYY-MM-DD`
3. Quarter notation: `Q1, Q2, Q3, Q4`
4. Provider names should match exactly
5. Client names use `display_name`
```

## Error Handling / Validation 

FOR PAYMENT ENTRY: basics like showing error to the user if their required inputs for payment is attempted submitted without providing at a minimum: when payment was recieved, the quarter it applies to, and the amount. All others optional. also showing warning confirmation if the user hits CANCEL after they have entered anything in... in other words if the form is added to in any way from its default state (defaulkt or placeholders dont count obviously... any NEW entry like ENTERED BY THE PERSON). Gotta consider the basics using COMMON SENSE... if they get this cancel message and the hit NO (they dont want to cancel) then the form should stay there exactly like it did before not clearing anything (duh they arent finished they mightve hit cancle on accident you never know). but if they DO want to cancle and they hit YES on the cacle coinfirmation then the form collapses or clears, doesnt matter. 

FOR CONTRACTS: required inputs we need to know: IF ITS ACTIVE OR NOT. PROVIDER NAME. fee type, EITHER percent rate or flat rate (one or the other), payment schedual. 
-- HOWEVER THIS SHOULD NOT BE VALIDATED IN THE DATABASE OR WHEN BEING FETCHED FROM THE DATABASE. ONLY VERIFICATION IS WHEN CREATING A NEW CONTRACT. NOT EDITING OR ANYTHING. ONLY WHEN ENTERING NEW ONE.
-- ENTERING NEW CONTRACT THE USER CAN SELECT IF THE CONTRACT IS ACTIVE OR NOT. If the new contract is set to ACTIVE, then the user should get a confirmation message that the new contract will make the old contract unactive and the entry will be the new active one. The user rarely gives a shit about unactive contracts since they are a thing of the past... but figured we can have a discrete way of seeing them. 

# FOR CONTACTS:
- very fucking flexible. FOR THE ENTRY FORM = minimum required field is literally ONE field... literally any field. think about why... sometimes you have a phone number and no other information or an email address or something. its still good to enter that in. its stupid to punish them for not having more information lol. very flexible. See dataabse info for how its set up. 

*** SEE THE DATABASE SAMPLES AND THE PERCENTS NULL AND DEDUCE THE APPROPRIATE AND NON RESTRICTIVE MEASURES. DONT FIGHT THE DATA ***
SIMPLE AND COMMON SENSE FLEXIBLE.. 

NEVER ANY ERRORS FOR USER ENTERING SHIT IN THE WRONG FORMAT... WERE KEEPING IT EASY AND FLEXIBLE... NO WORRIES JUST TYPE IT IN BUCKAROO. the database will look perfect regardless! 
TRY TO AVOID TESTING CONTENT AS IT COMES INTO THE APP FROM THE DATABASE. REMEMBER WE CANT CHANGE THE DATABASE ITS JUST THE WAY IT IS. AT LEAST ITS CLEANED UP WELL AND ALL VALUES ARE FORMATTED IN THE BEST-PRACTICE WAY!





# Core design philosophy, architecture and layout:

### WE WANT A CONSISTENT VERTICAL RHYTHM BETWEEN SECTIONS.
### WRAP SECTIONS PROPERLY WITH CONTAINERS.
### THE SPACING SHOULD CREATE A GENTLE VISUAL GROUPING WHILE MAINTAINING A CONSISTENT RHYTHM DOWN THE PAGE.

### USE FIXED HEIGHT OR MIN-HEIGHT WHEN SUITABLE
### USE FLEX LAYOUT WITH CONSISTENT SPACING WHEN SUITABLE
### ENSURE THE DELTA SPACE IS RESERVED EVEN WHEN EMPTY WHEN NEEDED


Layout Hierarchy Principles
Always use st.columns() inside containers rather than standalone
Maintain a consistent grid system (prefer [2,2,2,2] or [3,3,3] over irregular splits)
Use streamlit-extras grid/row when you need precise vertical alignment
Minimize empty vertical space - if spacing is needed, use add_vertical_space with intention


Component Best Practices
Favor native Streamlit components over custom CSS whenever possible
Use streamlit-extras metric_cards instead of raw st.metric() for better visual consistency
Place related interactive elements (buttons, inputs) in the same container/grid cell
Keep form layouts symmetrical with consistent widths
Looking left to right, all similar content like TEXT or buttons or similar things that would look best vertically aligned. Consider the components and the defaults padding and whatnot. for instance buttons will place the text in the middle with padding so adding st.write("") will not aline the text with the buttons text. How will you make this sort of thing not happen? This kinda of mindset is what we need to have.
I prefer equal sized things with extreme symmetry. and balance. *****containers nested with flexbox is your friend***** (pst... did you know Streamlit-Extras has things like "Row: Insert a multi-element, horizontal container into your app.") and (grid: Insert a multi-element, grid container into your app.) and so much more? 
If you have to consider EXOTIC CSS/HTML/JS... then you are doing it wrong. 


Styling Philosophy
Start with native Streamlit styling before adding custom CSS
When CSS is needed, peep streamlit-extras {Library_Documentation_Latest\README_SL-EXTRAS_DOCS.md} to see if there is a low-code solution before immediatly going to the CSS.
*** ALWAYS MAKE SURE THERE ARE NO CSS CONFLICTS BETWEEN APP PAGES, NO OVERLAPING STYLES, NO STYLING ON ONE PAGE FOR A COMPONENT THAT EFFECTS THAT SAME TYPE OF COMPONENT ON ANOTHER PAGE. MAKE SURE TO USE UNIQUE CLASSES FOR EACH COMPONENT. AND VERIFY IT IS INFACT UNIQUE. ***
Maintain consistent padding/margins (0.5rem, 1rem) across similar components
Keep the headers and labels tight to the content
Use border-radius and subtle shadows to create visual hierarchy without heaviness


Space Optimization
Combine logically related headers/controls into single row containers
Use expanders strategically for secondary information
Leverage multi-column layouts to reduce vertical scrolling
Maintain minimum 2-3 lines between major sections, but eliminate unnecessary gaps


Interaction Patterns
Keep primary actions visible without scrolling
Group related controls together in logical containers
Maintain consistent button/input sizing within sections
Use progressive disclosure (show/hide) rather than multiple pages when possible

The goal is intentional, clean layouts that guide users naturally through workflows while maximizing screen real estate and minimizing custom styling needs.

__ Remove unnecessary st.write("") spacing calls - these take up vertical space
___ Use add_vertical_space from streamlit-extras for precise spacing control when needed
____ Consolidate section headers with their content by using styled containers

** Dont LAYER headers vertically. instead put them horizontally so that vertical space is not wasted.


### Row Structure
Each payment row is contained within its own container, ensuring:
- Consistent spacing and alignment
- Proper note expansion behavior
- Clean separation between rows
- Predictable layout scaling

- Row containers provide structural integrity

### Note System
Notes use a single, consistent implementation that:
- Toggles between green (🟢) and hollow (◯) icons based on content
- Expands smoothly below the row
- Spans partial row width for clean visual hierarchy
- Maintains state within row containers



### Filter Handling
Filters are processed separately from display logic:
- Time period selections (All Time, This Year, Custom)
- Proper handling of both monthly and quarterly frequencies
- Clean separation between filter logic and display code


----


## NOTE!! 

- Many Streamlit commands prefixed with 'experimental' are outdated. For example, `st.experimental.rerun` is deprecated—use `st.rerun` instead.
- ALL PAYMENTS ARE IN ARREARS. 



## PLEASE READ:
Library_Documentation_Latest\Architecture_and_Execution_SL_README.md
Library_Documentation_Latest\Concepts_SL.ReadME.md
Library_Documentation_Latest\FUNDEMENTALS_SL.ReadME.md
Library_Documentation_Latest\SLEXTRAS_README.md
Library_Documentation_Latest\Streamlit-docs-2024.md
Library_Documentation_Latest\streamlitextras_docs.md

