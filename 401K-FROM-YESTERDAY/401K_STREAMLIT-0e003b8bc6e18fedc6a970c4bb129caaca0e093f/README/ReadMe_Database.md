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