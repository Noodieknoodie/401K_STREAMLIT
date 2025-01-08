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
 For the common case where a payment applies to just one specific quarter, the user doesn’t need to enter anything for the "end" quarter or year. The system automatically copies the start selection into these fields since the payment only covers that one quarter.

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

# 401K_STREAMLIT


## THIS DATABASE ALREADY EXISTS: "DATABASE\401kDATABASE.db"
## THE INFORMATION BELOW IS ONLY SO YOU CAN UNDERSTAND HOW IT IS SETUP.
## YOU DO NOT NEED TO CREATE THE DATABASE 
## THIS IS FOR YOUR LEARNING 




TABLE NAME:
clients

SCHEMA (CREATE STATEMENT):
CREATE TABLE "clients" (
	"client_id"	INTEGER NOT NULL,
	"display_name"	TEXT NOT NULL,
	"full_name"	TEXT,
	"ima_signed_date"	TEXT,
	"file_path_account_documentation"	TEXT,
	"file_path_consulting_fees"	TEXT,
	"file_path_meetings"	INTEGER,
	PRIMARY KEY("client_id" AUTOINCREMENT)
)

SAMPLE:
(1, 'AirSea America', 'THE TRUSTEES OF AIRSEA AMERICA INC 401K PLAN AND TRUST', '2020-07-31', None, None, None)
(2, 'Bumgardner Architects (ABC)', 'THE BUMGARDNER ARCHITECTS A WASHINGTON CORPORATION PROFIT', '2020-08-02', None, None, None)
(3, 'Amplero', 'AMPLERO INC 401K', '2019-03-15', None, None, None)
(4, 'Auction Edge', 'AUCTION EDGE Inc 401k Profit Sharing Plan', '2019-03-07', None, None, None)
(5, 'BDR Interactive', 'BUSINESS DEVELOPMENT RESOURCES & OPPORTUNITIES INTERACTIVE', '2021-02-23', None, None, None)
(6, 'Bellmont Cabinets', 'BELLMONT CABINETS', None, None, None, None)
(7, 'Corina Bakery', 'CORINA BAKERY', '2020-07-28', None, None, None)
(8, 'Dakota Creek', 'DAKOTA CREEK INDUSTRIES', None, None, None, None)
(9, 'CG Engineering', 'CG ENGINEERING PLLC', '2020-07-28', None, None, None)
(10, 'Fast Water Heater', 'FAST WATER HEATER CO', '2019-10-14', None, None, None)
(11, 'Floform', 'FLOFORM COUNTERTOPS', None, None, None, None)
(12, 'Hansen Bros', 'HANSEN BROS TRANSFER & STORAGE CO', '2019-03-18', None, None, None)
(13, 'Harper Engineering', 'HARPER ENGINEERING 401K PROFIT SHARING PLAN', '2020-08-06', None, None, None)
(14, 'Hos Bros', 'HOS BROS CONSTRUCTION INC', '2019-05-08', None, None, None)
(15, 'Lavle USA', 'LAVLE USA INC 401K', '2019-03-22', None, None, None)
(16, 'Lynnwood Honda', 'LYNNWOOD ENTERPRISES INC 401K', '2020-02-06', None, None, None)
(17, 'Nordic Museum', 'NATIONAL NORDIC MUSEUM', None, None, None, None)
(18, 'Marten Law', 'MARTEN LAW GROUP PLLC', '2019-03-26', None, None, None)
(19, 'Opportunity Interactive', 'OPPORTUNITY INTERACTIVE', '2021-01-29', None, None, None)
(20, 'MoxiWorks', 'MOXIWORKS', '2020-08-05', None, None, None)
(21, 'Mobile Focused', 'MOBILE FOCUSED MEDIA', None, None, None, None)
(22, 'PSWM Inc', 'PSWM INC 401K PLAN AND TRUST', '2019-03-18', None, None, None)
(23, 'Three Sigma', 'THREE SIGMA', '2020-09-22', None, None, None)
(24, "Tony's Coffee", 'TONYS COFFEE', None, None, None, None)
(25, 'United Way', 'UWKC', None, None, None, None)
(26, 'Urban Renaissance', 'URBAN RENAISSANCE 401K AND TRUST', '2020-07-29', None, None, None)
(27, 'XFire', 'XFIRE INDUSTRIES INC 401K PLAN', None, None, None, None)
(28, 'Younker Motors', 'YOUNKER MOTORS', '2020-07-30', None, None, None)
(29, 'Youth Dynamics', 'YOUTH DYNAMICS', None, None, None, None)


TABLE NAME:
contacts

SCHEMA (CREATE STATEMENT):
CREATE TABLE "contacts" (
	"contact_id"	INTEGER NOT NULL,
	"client_id"	INTEGER NOT NULL,
	"contact_type"	TEXT NOT NULL,
	"contact_name"	TEXT,
	"phone"	TEXT,
	"email"	TEXT,
	"fax"	TEXT,
	"physical_address"	TEXT,
	"mailing_address"	TEXT,
	PRIMARY KEY("contact_id" AUTOINCREMENT),
	FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
)

SAMPLE:
(1, 1, 'Primary', 'Donald Jay', '253-395-9551', 'djay@asamerica.com', None, '3500 West Vally HWY, Ste B-106, Auburn, WA 98001', '3500 West Vally HWY, Ste B-106, Auburn, WA 98001')
(2, 2, 'Primary', 'Mark Simpson', '206-223-1361', 'marks@bumgardner.biz', None, '2111 Third Ave, Seattle, WA 98121', '2111 Third Ave, Seattle, WA 98121')
(3, 3, 'Primary', 'Doug Gelfand', '206-816-3700', 'dgelfand@amplero.com', None, '1218 3rd Ave #900, Seattle, WA 98101', None)
(4, 4, 'Primary', 'Robert Copeland', '206-858-4800', 'robertc@auctionedge.com', None, '1424 4th Ave Suite 920, Seattle, WA 98101', '1424 4th Ave Suite 920, Seattle, WA 98101')
(5, 5, 'Primary', 'Bruce Wiseman', '206-870-1880', 'brucewiseman@bdrco.com', None, '19604 International Blvd Ste 200, SeaTac, WA 98188', None)
(6, 6, 'Primary', None, None, None, None, None, None)
(7, 7, 'Primary', 'Mike Ott', '253-839-4968', 'mott56@aol.com', None, '602 Fawcett Ave, Tacoma, WA 98402', '602 Fawcett Ave, Tacoma, WA 98402')
(8, 8, 'Primary', None, '360-293-9575', None, None, '820 4th St, Anacortes WA 98221', None)
//truncated...
(31, 2, 'Authorized', 'Nick Simpson', None, 'nicks@bumgardner.biz', None, None, None)
(32, 5, 'Authorized', 'Aaron Schuh', None, None, None, None, None)
(33, 5, 'Authorized', 'Sarwesh Kumar', None, 'sarweshkumar@bdrco.com', None, None, None)
(34, 8, 'Authorized', 'Katie Duran', None, 'kdurantnuno@dakotacreek.com', None, None, None)
(35, 8, 'Authorized', 'Nancy Loftis', None, 'nancyl@dakotacreek.com', None, None, None)
(36, 8, 'Authorized', 'Mike Nelson', None, 'mike@dakotacreek.com', None, None, None)
(37, 9, 'Authorized', 'Beth Campbell', '425-778-8500', 'beth@cgengineering.com', None, None, None)
(38, 9, 'Authorized', 'Greg Guillen', '425-778-8500', None, None, None, None)
//truncated...
(61, 15, 'Provider', 'Paul Brachvogel', '866-498-4557', None, None, '15809 Preston Place, Burlington, WA 98233', None)
(62, 17, 'Provider', 'Brett Lundgren', '866-421-4137', 'Brett.Lundgren@capgroup.com', None, None, None)
(63, 20, 'Provider', 'Chris Gledhill', '800-333-0963', None, None, None, None)
(64, 21, 'Provider', 'Austin Del Prado', '800-333-0963', 'delprau@jhancock.com', None, '601 Congress St, Boston, MA 02210', None)
(65, 25, 'Provider', 'Jeff Harvey', '206-624-3790', None, None, '520 Pike Street Suite 1450 Seattle WA 98101', None)
(66, 26, 'Provider', 'Austin Del Prado', '800-333-0963', 'delprau@jhancock.com', None, '601 Congress St, Boston, MA 02210', None)
(67, 27, 'Provider', 'Brett Lundgren', '866-421-2137', 'Brett.Lundgren@capgroup.com', None, None, None)
(68, 29, 'Provider', 'Maria Viala-Wood', None, 'maria.vialawood@transamerica.com', None, None, None)


TABLE NAME:
contracts

SCHEMA (CREATE STATEMENT):
CREATE TABLE "contracts" (
	"contract_id"	INTEGER NOT NULL,
	"client_id"	INTEGER NOT NULL,
	"active"	TEXT,
	"contract_number"	TEXT,
	"provider_name"	TEXT,
	"contract_start_date"	TEXT,
	"fee_type"	TEXT,
	"percent_rate"	REAL,
	"flat_rate"	REAL,
	"payment_schedule"	TEXT,
	"num_people"	INTEGER,
	"notes"	TEXT,
	PRIMARY KEY("contract_id" AUTOINCREMENT),
	FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
)

SAMPLE:
(1, 1, 'TRUE', '134565', 'John Hancock', '2018-03-22', 'percentage', 0.0007, None, 'monthly',  18, 'Phone: 800-333-0963 Option 1 with Contract # or Option 2, ext 154617\r\nFax: General Info 866-377-9577  Enrollment Forms 866-377-8846 \r\n')
(2, 2, 'TRUE', None, 'Voya', '2019-04-19', 'percentage', 0.041667, None, 'monthly',  35, '')
(3, 3, 'TRUE', '551296', 'Voya', None, 'flat', '', 666.66, 'monthly',  None, None)
(4, 4, 'FALSE', '684021', 'ADP', None, 'percentage', 0.00125, None, 'quarterly',  139, None)
(5, 5, 'TRUE', '231393', 'Ascensus Trust Company', '2019-05-2019', 'flat', '', 3000.0, 'quarterly',  93, None)
(6, 6, 'TRUE', '29366', 'John Hancock', None, 'percentage', 0.00125, None, 'monthly',  289, None)
(7, 7, 'FALSE', '15880157', 'Nationwide', None, 'percentage', 0.041667, None, 'monthly', '', 15, None)
(8, 8, 'TRUE', '273504', 'Ascensus', None, 'percentage', 0.003446, None, 'quarterly', '', 177, None)
(9, 9, 'TRUE', '134019', 'Direct from CG Engineering', None, 'flat', '', 2500.0, 'quarterly', 'Invoice - Check', 42, None)
(10, 10, 'TRUE', None, 'Empower', None, 'percentage', 0.000667, None, 'monthly', '', 208, None)
(11, 11, 'TRUE', '147266', 'John Hancock', None, 'percentage', 0.000208, None, 'monthly', '', 531, None)
(12, 12, 'TRUE', '222908', 'Ascensus Trust Company', None, 'flat', '', 2500.0, 'quarterly',  80, None)
(13, 13, 'TRUE', '41909', 'Fidelity', None, 'flat', '', 1250.0, 'monthly',  80, None)
(14, 14, 'TRUE', '34283', 'Fidelity', None, 'flat', '', 3750.0, 'quarterly',  24, None)
(15, 15, 'TRUE', '809872', 'Transamerica', None, 'percentage', 0.000417, None, 'monthly',  None, None)
//truncated...
(32, 7, 'TRUE', '', 'Voya', None, 'percentage', 0.041667, None, 'monthly', '', 15, None)
(33, 16, 'TRUE', '', 'Empower', None, 'flat', '', 3500.0, 'quarterly',  None, None)
(34, 28, 'TRUE', None, 'Empower', None, 'percentage', 0.000667, None, 'monthly',  43, None)
(35, 29, 'TRUE', None, 'Principal', None, 'percentage', 0.001875, None, 'quarterly', '', 15, None)


TABLE NAME:
payments

SCHEMA (CREATE STATEMENT):
CREATE TABLE "payments" (
	"payment_id"	INTEGER NOT NULL,
	"contract_id"	INTEGER NOT NULL,
	"client_id"	INTEGER NOT NULL,
	"received_date"	TEXT,
	"applied_start_quarter"	INTEGER,
	"applied_start_year"	INTEGER,
	"applied_end_quarter"	INTEGER,
	"applied_end_year"	INTEGER,
	"total_assets"	INTEGER,
	"expected_fee"	REAL,
	"actual_fee"	REAL,
	"method"	TEXT,
	"notes"	TEXT,
	PRIMARY KEY("payment_id" AUTOINCREMENT),
	FOREIGN KEY("client_id") REFERENCES "clients"("client_id"),
	FOREIGN KEY("contract_id") REFERENCES "contracts"("contract_id")
)

SAMPLE:
(1, 1, 1, '2019-05-03', 2, 2019, 2, 2019, 824305, 542.01, 547.51, 'Auto - Check', 'waiting on how John Hancock calculates fee payments')
(2, 1, 1, '2019-06-07', 1, 2019, 1, 2019, 805477, 547.28, 535.03, 'Auto - Check', None)
(3, 1, 1, '2019-07-05', 3, 2019, 3, 2019, 839288, 551.86, 557.54, 'Auto - Check', None)
(4, 1, 1, '2019-08-02', 3, 2019, 3, 2019, 842294, 572.3, 559.45, 'Auto - Check', None)
(5, 1, 1, '2019-09-06', 3, 2019, 3, 2019, 842118, 572.18, 559.37, 'Auto - Check', None)
(6, 1, 1, '2019-10-04', 3, 2019, 3, 2019, 849739, 0.0, 564.44, 'Auto - Check', None)
(7, 1, 1, '2019-10-31', 4, 2019, 4, 2019, 863024, None, 573.23, 'Auto - Check', None)
(8, 1, 1, '2019-11-12', 4, 2019, 4, 2019, 863024, 573.23, 573.23, 'Auto - Check', None)
(9, 1, 1, '2019-12-16', 4, 2019, 4, 2019, 876458, None, 582.15, 'Auto - Check', None)
(10, 1, 1, '2020-01-13', 1, 2020, 1, 2020, None, 609.54, 609.54, 'Auto - Check', None)
(11, 1, 1, '2020-02-19', 1, 2020, 1, 2020, 919435, 610.73, 610.73, 'Auto - Check', None)
(12, 1, 1, '2020-03-17', 1, 2020, 1, 2020, 889926, 591.11, 591.11, 'Auto - Check', None)
(13, 1, 1, '2020-04-13', 1, 2020, 1, 2020, None, 544.01, 544.01, 'Auto - Check', None)
(14, 1, 1, '2020-05-13', 1, 2020, 1, 2020, 872685, 592.95, 579.66, 'Auto - Check', None)
(15, 1, 1, '2020-06-22', 2, 2020, 2, 2020, 898969, 610.81, 597.14, 'Auto - Check', None)
//truncated...
(456, 13, 13, '2022-10-10', 3, 2022, 3, 2022, None, None, 5000.01, 'Auto - Check', 'Per fee statement payment (July, August, September)')
(457, 13, 13, '2023-01-24', 4, 2022, 4, 2022, None, None, 4999.97, 'Auto - Check', 'Per fee statement payment (October, November December )')
(458, 13, 13, '2023-04-13', 1, 2023, 1, 2023, None, None, 4999.97, 'Auto - Check', 'Per fee statement payment (January, February March )')
(459, 13, 13, '2023-07-15', 2, 2023, 2, 2023, None, None, 5000.0, 'Auto - Check', 'Per fee statement payment (April, May, June )')
(460, 13, 13, '2023-10-15', 3, 2023, 3, 2023, None, None, 5000.01, 'Auto - Check', 'Per fee statement payment (July, August, September)')
(461, 13, 13, '2024-01-09', 4, 2023, 4, 2023, None, None, 5000.01, 'Auto - Check', 'Per fee statement payment (October, November December )')
(462, 13, 13, '2024-04-08', 1, 2024, 1, 2024, None, None, 5000.01, 'Auto - Check', 'Per fee statement payment (January, February March )')
(463, 13, 13, '2024-07-18', 2, 2024, 2, 2024, None, None, 5000.01, 'Auto - Check', 'Per fee statement payment (April, May, June )')
(464, 13, 13, '2024-10-16', 3, 2024, 3, 2024, None, None, 5000.01, 'Auto - Check', 'Per fee statement payment (July, Aug, Sept )')
(465, 14, 14, '2019-07-09', 2, 2019, 2, 2019, None, 2500.0, 2500.0, 'Auto - ACH', 'For May and June only. No Partial April')
(466, 14, 14, '2019-10-08', 3, 2019, 3, 2019, None, 3750.0, 3750.0, 'Auto - ACH', None)
(467, 14, 14, '2020-01-13', 4, 2019, 4, 2019, None, 3750.0, 3750.0, 'Auto - ACH', 'Emailed received from Tom RE: this fee payment 1/15/2020 (Oct. Nov. Dec.)')
(468, 14, 14, '2020-04-13', 1, 2020, 1, 2020, None, 3750.0, 3750.0, 'Auto - ACH', 'Per statement received 4/13/2020')
(469, 14, 14, '2020-07-13', 2, 2020, 2, 2020, None, 3750.0, 3750.0, 'Auto - ACH', 'Per email 7/13/2020 from DH/TB')
(470, 14, 14, '2020-10-15', 3, 2020, 3, 2020, None, 3750.0, 3750.0, 'Auto - ACH', None)
//truncated...
(910, 29, 29, '2022-09-13', 3, 2022, 3, 2022, 151793, None, 94.87, '', None)
(911, 29, 29, '2022-10-12', 3, 2022, 3, 2022, 150139, None, 93.84, '', None)
(912, 29, 29, '2022-11-15', 4, 2022, 4, 2022, 150139, None, 107.25, '', None)
(913, 29, 29, '2022-12-13', 4, 2022, 4, 2022, 214112, None, 133.82, '', None)
(914, 29, 29, '2023-01-12', 4, 2022, 4, 2022, 218423, None, 136.51, '', None)
(915, 29, 29, '2023-02-08', 1, 2023, 1, 2023, 247368, None, 154.6, '', None)
(916, 29, 29, '2023-03-17', 1, 2023, 1, 2023, 255278, None, 159.55, '', None)
(917, 29, 29, '2023-04-10', 1, 2023, 1, 2023, 276062, None, 172.54, '', None)
(918, 29, 29, '2023-05-10', 2, 2023, 2, 2023, 293667, None, 183.54, '', None)
(919, 29, 29, '2023-06-12', 2, 2023, 2, 2023, 307387, None, 192.12, '', None)
(920, 35, 29, '2023-10-19', 3, 2023, 3, 2023, None, None, 665.49, '', 'Newly established at Principal; amount will be posted on 10.27.23')
(921, 35, 29, '2024-01-17', 4, 2023, 4, 2023, None, None, 748.16, '', None)
(922, 35, 29, '2024-04-15', 1, 2024, 1, 2024, None, None, 915.53, '', None)
(923, 35, 29, '2024-07-16', 2, 2024, 2, 2024, None, None, 946.32, '', None)
(924, 35, 29, '2024-10-14', 3, 2024, 3, 2024, None, None, 1043.09, '', None)




# INDEXES MADE IF NEEDED: 
-- Primary keys (automatically indexed by SQLite)

-- Indexes for Foreign Keys
CREATE INDEX idx_contacts_client_id ON contacts(client_id);
CREATE INDEX idx_contracts_client_id ON contracts(client_id);
CREATE INDEX idx_payments_client_id ON payments(client_id);
CREATE INDEX idx_payments_contract_id ON payments(contract_id);

-- Index for Active Contracts Lookup
CREATE INDEX idx_contracts_active ON contracts(client_id, active);

-- Index for Payment Sorting by Date
CREATE INDEX idx_payments_date ON payments(client_id, received_date DESC);

-- Index for Contacts Filtering by Type
CREATE INDEX idx_contacts_type ON contacts(client_id, contact_type);

-- Optional Composite Index for Payments by Quarter/Year
CREATE INDEX idx_payments_quarter_year ON payments(client_id, applied_start_quarter, applied_start_year);

-- Optional Index for Contracts by Provider
CREATE INDEX idx_contracts_provider ON contracts(provider_name);


---



Table: sqlite_sequence
  Column: name
    % Nulls: 0.00%
    Unique Values: 4
    Diverse: No
    Average Length: 8.00 characters
    Length Range: {'min': 7, 'max': 9}
  Column: seq
    % Nulls: 0.00%
    Unique Values: 4
    Diverse: No
    Average Length: 2.25 characters
    Length Range: {'min': 2, 'max': 3}

Table: clients
  Column: client_id
    % Nulls: 0.00%
    Unique Values: 29
    Diverse: Yes
    Average Length: 1.69 characters
    Length Range: {'min': 1, 'max': 2}
  Column: display_name
    % Nulls: 0.00%
    Unique Values: 29
    Diverse: Yes
    Average Length: 12.97 characters
    Length Range: {'min': 5, 'max': 27}
  Column: full_name
    % Nulls: 0.00%
    Unique Values: 29
    Diverse: Yes
    Average Length: 25.00 characters
    Length Range: {'min': 4, 'max': 58}
  Column: ima_signed_date
    % Nulls: 31.03%
    Unique Values: 18
    Diverse: Yes
    Average Length: 10.00 characters
    Length Range: {'min': 10, 'max': 10}
  Column: file_path_account_documentation
    % Nulls: 100.00%
    Unique Values: 0
    Diverse: No
    Average Length: nan characters
    Length Range: {'min': nan, 'max': nan}
  Column: file_path_consulting_fees
    % Nulls: 100.00%
    Unique Values: 0
    Diverse: No
    Average Length: nan characters
    Length Range: {'min': nan, 'max': nan}
  Column: file_path_meetings
    % Nulls: 100.00%
    Unique Values: 0
    Diverse: No
    Average Length: nan characters
    Length Range: {'min': nan, 'max': nan}

Table: contacts
  Column: contact_id
    % Nulls: 0.00%
    Unique Values: 68
    Diverse: Yes
    Average Length: 1.87 characters
    Length Range: {'min': 1, 'max': 2}
  Column: client_id
    % Nulls: 0.00%
    Unique Values: 29
    Diverse: Yes
    Average Length: 1.65 characters
    Length Range: {'min': 1, 'max': 2}
  Column: contact_type
    % Nulls: 0.00%
    Unique Values: 3
    Diverse: No
    Average Length: 8.37 characters
    Length Range: {'min': 7, 'max': 10}
  Column: contact_name
    % Nulls: 7.35%
    Unique Values: 57
    Diverse: Yes
    Average Length: 12.41 characters
    Length Range: {'min': 4, 'max': 20}
  Column: phone
    % Nulls: 42.65%
    Unique Values: 30
    Diverse: Yes
    Average Length: 12.00 characters
    Length Range: {'min': 12, 'max': 12}
  Column: email
    % Nulls: 25.00%
    Unique Values: 46
    Diverse: Yes
    Average Length: 22.04 characters
    Length Range: {'min': 13, 'max': 35}
  Column: fax
    % Nulls: 97.06%
    Unique Values: 2
    Diverse: No
    Average Length: 12.50 characters
    Length Range: {'min': 12, 'max': 13}
  Column: physical_address
    % Nulls: 52.94%
    Unique Values: 28
    Diverse: Yes
    Average Length: 37.88 characters
    Length Range: {'min': 30, 'max': 52}
  Column: mailing_address
    % Nulls: 75.00%
    Unique Values: 17
    Diverse: Yes
    Average Length: 38.35 characters
    Length Range: {'min': 30, 'max': 52}

Table: contracts
  Column: contract_id
    % Nulls: 0.00%
    Unique Values: 35
    Diverse: Yes
    Average Length: 1.74 characters
    Length Range: {'min': 1, 'max': 2}
  Column: client_id
    % Nulls: 0.00%
    Unique Values: 29
    Diverse: Yes
    Average Length: 1.66 characters
    Length Range: {'min': 1, 'max': 2}
  Column: active
    % Nulls: 0.00%
    Unique Values: 2
    Diverse: No
    Average Length: 4.17 characters
    Length Range: {'min': 4, 'max': 5}
  Column: contract_number
    % Nulls: 20.00%
    Unique Values: 26
    Diverse: Yes
    Average Length: 5.46 characters
    Length Range: {'min': 0, 'max': 8}
  Column: provider_name
    % Nulls: 0.00%
    Unique Values: 15
    Diverse: Yes
    Average Length: 11.49 characters
    Length Range: {'min': 3, 'max': 30}
  Column: contract_start_date
    % Nulls: 91.43%
    Unique Values: 3
    Diverse: No
    Average Length: 10.67 characters
    Length Range: {'min': 10, 'max': 12}
  Column: fee_type
    % Nulls: 2.86%
    Unique Values: 2
    Diverse: No
    Average Length: 7.71 characters
    Length Range: {'min': 4, 'max': 10}
  Column: percent_rate
    % Nulls: 2.86%
    Unique Values: 14
    Diverse: Yes
    Average Length: 4.59 characters
    Length Range: {'min': 0, 'max': 8}
  Column: flat_rate
    % Nulls: 62.86%
    Unique Values: 10
    Diverse: No
    Average Length: 6.08 characters
    Length Range: {'min': 6, 'max': 7}
  Column: payment_schedule
    % Nulls: 2.86%
    Unique Values: 2
    Diverse: No
    Average Length: 8.06 characters
    Length Range: {'min': 7, 'max': 9}
  Column: num_people
    % Nulls: 14.29%
    Unique Values: 20
    Diverse: Yes
    Average Length: 4.23 characters
    Length Range: {'min': 3, 'max': 5}
  Column: notes
    % Nulls: 94.29%
    Unique Values: 2
    Diverse: No
    Average Length: 67.00 characters
    Length Range: {'min': 0, 'max': 134}

Table: payments
  Column: payment_id
    % Nulls: 0.00%
    Unique Values: 924
    Diverse: Yes
    Average Length: 2.88 characters
    Length Range: {'min': 1, 'max': 3}
  Column: contract_id
    % Nulls: 0.00%
    Unique Values: 35
    Diverse: Yes
    Average Length: 1.69 characters
    Length Range: {'min': 1, 'max': 2}
  Column: client_id
    % Nulls: 0.00%
    Unique Values: 29
    Diverse: Yes
    Average Length: 1.64 characters
    Length Range: {'min': 1, 'max': 2}
  Column: received_date
    % Nulls: 0.00%
    Unique Values: 360
    Diverse: Yes
    Average Length: 10.00 characters
    Length Range: {'min': 10, 'max': 10}
  Column: applied_start_quarter
    % Nulls: 0.00%
    Unique Values: 4
    Diverse: No
    Average Length: 1.00 characters
    Length Range: {'min': 1, 'max': 1}
  Column: applied_start_year
    % Nulls: 0.00%
    Unique Values: 8
    Diverse: No
    Average Length: 4.00 characters
    Length Range: {'min': 4, 'max': 4}
  Column: applied_end_quarter
    % Nulls: 0.00%
    Unique Values: 4
    Diverse: No
    Average Length: 1.00 characters
    Length Range: {'min': 1, 'max': 1}
  Column: applied_end_year
    % Nulls: 0.00%
    Unique Values: 8
    Diverse: No
    Average Length: 4.00 characters
    Length Range: {'min': 4, 'max': 4}
  Column: total_assets
    % Nulls: 51.30%
    Unique Values: 443
    Diverse: Yes
    Average Length: 6.53 characters
    Length Range: {'min': 1, 'max': 8}
  Column: expected_fee
    % Nulls: 73.48%
    Unique Values: 148
    Diverse: Yes
    Average Length: 6.08 characters
    Length Range: {'min': 3, 'max': 7}
  Column: actual_fee
    % Nulls: 0.11%
    Unique Values: 674
    Diverse: Yes
    Average Length: 6.15 characters
    Length Range: {'min': 4, 'max': 8}
  Column: method
    % Nulls: 0.00%
    Unique Values: 4
    Diverse: No
    Average Length: 8.10 characters
    Length Range: {'min': 0, 'max': 15}
  Column: notes
    % Nulls: 81.60%
    Unique Values: 113
    Diverse: Yes
    Average Length: 40.93 characters
    Length Range: {'min': 0, 'max': 138}

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

