# 401K_STREAMLIT.db
## THIS DATABASE ALREADY EXISTS: "DATABASE\401kDATABASE.db"
## THE INFORMATION BELOW IS ONLY SO YOU CAN UNDERSTAND HOW IT IS SETUP.
## YOU DO NOT NEED TO CREATE THE DATABASE 
## THIS IS FOR YOUR LEARNING 


---

# TABLE NAME: table: sqlite_sequence

SCHEMA (CREATE STATEMENT):
CREATE TABLE sqlite_sequence(name,seq)

---

# TABLE NAME: clients

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

# METIRCS: table: clients

Column,Null %,Unique,Is Diverse,Avg Length,Min Length,Max Length
client_id,0.0%,29,Yes,1.69,1,2
display_name,0.0%,29,Yes,12.966,5,27
full_name,0.0%,29,Yes,25.0,4,58
ima_signed_date,31.034%,19,Yes,10.0,10,10
file_path_account_documentation,100.0%,1,No,nan,nan,nan
file_path_consulting_fees,100.0%,1,No,nan,nan,nan
file_path_meetings,100.0%,1,No,nan,nan,nan

# SAMPLE: table: clients 

(1, 'AirSea America', 'THE TRUSTEES OF AIRSEA AMERICA INC 401K PLAN AND TRUST', '2020-07-31', NULL, NULL, NULL)
(2, 'Bumgardner Architects (ABC)', 'THE BUMGARDNER ARCHITECTS A WASHINGTON CORPORATION PROFIT', '2020-08-02', NULL, NULL, NULL)
(3, 'Amplero', 'AMPLERO INC 401K', '2019-03-15', NULL, NULL, NULL)
(4, 'Auction Edge', 'AUCTION EDGE Inc 401k Profit Sharing Plan', '2019-03-07', NULL, NULL, NULL)
(5, 'BDR Interactive', 'BUSINESS DEVELOPMENT RESOURCES & OPPORTUNITIES INTERACTIVE', '2021-02-23', NULL, NULL, NULL)
(6, 'Bellmont Cabinets', 'BELLMONT CABINETS', NULL, NULL, NULL, NULL)
(7, 'Corina Bakery', 'CORINA BAKERY', '2020-07-28', NULL, NULL, NULL)
(8, 'Dakota Creek', 'DAKOTA CREEK INDUSTRIES', NULL, NULL, NULL, NULL)
(9, 'CG Engineering', 'CG ENGINEERING PLLC', '2020-07-28', NULL, NULL, NULL)
(10, 'Fast Water Heater', 'FAST WATER HEATER CO', '2019-10-14', NULL, NULL, NULL)
(11, 'Floform', 'FLOFORM COUNTERTOPS', NULL, NULL, NULL, NULL)
(12, 'Hansen Bros', 'HANSEN BROS TRANSFER & STORAGE CO', '2019-03-18', NULL, NULL, NULL)
(13, 'Harper Engineering', 'HARPER ENGINEERING 401K PROFIT SHARING PLAN', '2020-08-06', NULL, NULL, NULL)
(14, 'Hos Bros', 'HOS BROS CONSTRUCTION INC', '2019-05-08', NULL, NULL, NULL)
(15, 'Lavle USA', 'LAVLE USA INC 401K', '2019-03-22', NULL, NULL, NULL)
(16, 'Lynnwood Honda', 'LYNNWOOD ENTERPRISES INC 401K', '2020-02-06', NULL, NULL, NULL)
(17, 'Nordic Museum', 'NATIONAL NORDIC MUSEUM', NULL, NULL, NULL, NULL)
(18, 'Marten Law', 'MARTEN LAW GROUP PLLC', '2019-03-26', NULL, NULL, NULL)
(19, 'Opportunity Interactive', 'OPPORTUNITY INTERACTIVE', '2021-01-29', NULL, NULL, NULL)
(20, 'MoxiWorks', 'MOXIWORKS', '2020-08-05', NULL, NULL, NULL)
(21, 'Mobile Focused', 'MOBILE FOCUSED MEDIA', NULL, NULL, NULL, NULL)
(22, 'PSWM Inc', 'PSWM INC 401K PLAN AND TRUST', '2019-03-18', NULL, NULL, NULL)
(23, 'Three Sigma', 'THREE SIGMA', '2020-09-22', NULL, NULL, NULL)
(24, "Tony's Coffee", 'TONYS COFFEE', NULL, NULL, NULL, NULL)
(25, 'United Way', 'UWKC', NULL, NULL, NULL, NULL)
(26, 'Urban Renaissance', 'URBAN RENAISSANCE 401K AND TRUST', '2020-07-29', NULL, NULL, NULL)
(27, 'XFire', 'XFIRE INDUSTRIES INC 401K PLAN', NULL, NULL, NULL, NULL)
(28, 'Younker Motors', 'YOUNKER MOTORS', '2020-07-30', NULL, NULL, NULL)
(29, 'Youth Dynamics', 'YOUTH DYNAMICS', NULL, NULL, NULL, NULL)

---

# TABLE NAME: contacts

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

# METIRCS: Table: contacts

Column,Null %,Unique,Is Diverse,Avg Length,Min Length,Max Length
contact_id,0.0%,71,Yes,1.873,1,2
client_id,0.0%,29,Yes,1.62,1,2
contact_type,0.0%,3,Yes,8.352,7,10
contact_name,7.042%,61,Yes,12.242,4,20
phone,42.254%,34,Yes,12.0,12,12
email,25.352%,50,Yes,22.132,13,35
fax,94.366%,6,Yes,12.25,12,13
physical_address,52.113%,32,Yes,37.294,20,52
mailing_address,73.239%,21,Yes,37.842,30,52


# SAMPLE: table: contacts

(1, 1, 'Primary', 'Donald Jay', '253-395-9551', 'djay@asamerica.com', NULL, '3500 West Vally HWY, Ste B-106, Auburn, WA 98001', '3500 West Vally HWY, Ste B-106, Auburn, WA 98001')
(2, 2, 'Primary', 'Mark Simpson', '206-223-1361', 'marks@bumgardner.biz', NULL, '2111 Third Ave, Seattle, WA 98121', '2111 Third Ave, Seattle, WA 98121')
(3, 3, 'Primary', 'Doug Gelfand', '206-816-3700', 'dgelfand@amplero.com', NULL, '1218 3rd Ave #900, Seattle, WA 98101', NULL)
(4, 4, 'Primary', 'Robert Copeland', '206-858-4800', 'robertc@auctionedge.com', NULL, '1424 4th Ave Suite 920, Seattle, WA 98101', '1424 4th Ave Suite 920, Seattle, WA 98101')
(5, 5, 'Primary', 'Bruce Wiseman', '206-870-1880', 'brucewiseman@bdrco.com', NULL, '19604 International Blvd Ste 200, SeaTac, WA 98188', NULL)
(6, 6, 'Primary', NULL, NULL, NULL, NULL, NULL, NULL)
(7, 7, 'Primary', 'Mike Ott', '253-839-4968', 'mott56@aol.com', NULL, '602 Fawcett Ave, Tacoma, WA 98402', '602 Fawcett Ave, Tacoma, WA 98402')
(8, 8, 'Primary', NULL, '360-293-9575', NULL, NULL, '820 4th St, Anacortes WA 98221', NULL)
//truncated...
(32, 5, 'Authorized', 'Aaron Schuh', NULL, NULL, NULL, NULL, NULL)
(33, 5, 'Authorized', 'Sarwesh Kumar', NULL, 'sarweshkumar@bdrco.com', NULL, NULL, NULL)
(34, 8, 'Authorized', 'Katie Duran', NULL, 'kdurantnuno@dakotacreek.com', NULL, NULL, NULL)
(35, 8, 'Authorized', 'Nancy Loftis', NULL, 'nancyl@dakotacreek.com', NULL, NULL, NULL)
(36, 8, 'Authorized', 'Mike Nelson', NULL, 'mike@dakotacreek.com', NULL, NULL, NULL)
(37, 9, 'Authorized', 'Beth Campbell', '425-778-8500', 'beth@cgengineering.com', NULL, NULL, NULL)
(38, 9, 'Authorized', 'Greg Guillen', '425-778-8500', NULL, NULL, NULL, NULL)
(39, 13, 'Authorized', 'Sarina Perera', NULL, 's.perera@harperengineering.com', NULL, NULL, NULL)
//truncated...
(64, 21, 'Provider', 'Austin Del Prado', '800-333-0963', 'delprau@jhancock.com', NULL, '601 Congress St, Boston, MA 02210', NULL)
(65, 25, 'Provider', 'Jeff Harvey', '206-624-3790', NULL, NULL, '520 Pike Street Suite 1450 Seattle WA 98101', NULL)
(66, 26, 'Provider', 'Austin Del Prado', '800-333-0963', 'delprau@jhancock.com', NULL, '601 Congress St, Boston, MA 02210', NULL)
(67, 27, 'Provider', 'Brett Lundgren', '866-421-2137', 'Brett.Lundgren@capgroup.com', NULL, NULL, NULL)
(68, 29, 'Provider', 'Maria Viala-Wood', NULL, 'maria.vialawood@transamerica.com', NULL, NULL, NULL)
(70, 5, 'Authorized', 'ERIK TEST', '', '', '', '', '')
(72, 1, 'Primary', 'Joe Dirt', '425-985-1184', 'joedirttheman@gmail.com', '488-299-2929', '402 Windor Dr SE, Sammamish WA 98004', '929 203th ave E, Welmington TX 91020')
(73, 1, 'Primary', 'Cunky Boy', '293-299-2932', 'chunkythemonkey@monkey.com', '102-932-3223', '123 123th st E, 3333', '92832 19th ct, Massive MA 01929')

---

# TABLE NAME: payments

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


# METIRCS: table: payments

Column,Null %,Unique,Is Diverse,Avg Length,Min Length,Max Length
payment_id,0.0%,924,Yes,2.883,1,3
contract_id,0.0%,35,Yes,1.692,1,2
client_id,0.0%,29,Yes,1.641,1,2
received_date,0.0%,360,Yes,10.0,10,10
applied_start_quarter,0.0%,4,Yes,1.0,1,1
applied_start_year,0.0%,8,Yes,4.0,4,4
applied_end_quarter,0.0%,4,Yes,1.0,1,1
applied_end_year,0.0%,8,Yes,4.0,4,4
total_assets,51.299%,444,Yes,6.527,1,8
expected_fee,73.485%,149,Yes,6.082,3,7
actual_fee,0.108%,675,Yes,6.151,4,8
method,27.922%,4,Yes,11.476,10,15
notes,82.468%,114,Yes,42.951,3,138

# SAMPLE: table: payments 

(1, 1, 1, '2019-05-03', 2, 2019, 2, 2019, 824305, 542.01, 547.51, 'Auto - Check', 'waiting on how John Hancock calculates fee payments')
(2, 1, 1, '2019-06-07', 1, 2019, 1, 2019, 805477, 547.28, 535.03, 'Auto - Check', NULL)
(3, 1, 1, '2019-07-05', 3, 2019, 3, 2019, 839288, 551.86, 557.54, 'Auto - Check', NULL)
(4, 1, 1, '2019-08-02', 3, 2019, 3, 2019, 842294, 572.3, 559.45, 'Auto - Check', NULL)
//truncated...
(83, 2, 2, '2020-09-21', 3, 2020, 3, 2020, 2902855, NULL, 1209.52, 'Auto - ACH', NULL)
(84, 2, 2, '2020-10-20', 3, 2020, 3, 2020, 2849170, 1187.15, 1187.15, 'Auto - ACH', NULL)
(85, 2, 2, '2020-11-20', 4, 2020, 4, 2020, NULL, NULL, 1174.52, 'Auto - ACH', NULL)
(86, 2, 2, '2020-12-18', 4, 2020, 4, 2020, NULL, NULL, 1295.02, 'Auto - ACH', NULL)
(87, 2, 2, '2021-01-15', 4, 2020, 4, 2020, 3247119, 1352.96, 1352.96, 'Auto - ACH', NULL)
(88, 2, 2, '2021-02-19', 1, 2021, 1, 2021, NULL, 1357.24, 1357.24, 'Auto - ACH', NULL)
(89, 2, 2, '2021-03-19', 1, 2021, 1, 2021, NULL, 1388.36, 1388.36, 'Auto - ACH', NULL)
(90, 2, 2, '2021-04-16', 1, 2021, 1, 2021, NULL, 1417.82, 1417.82, 'Auto - ACH', NULL)
//truncated...
(155, 3, 3, '2021-07-22', 2, 2021, 2, 2021, NULL, NULL, 666.66, 'Auto - Check', 'per RIA comp statement rcvd from Max 7..21.21')
(156, 3, 3, '2021-08-23', 3, 2021, 3, 2021, NULL, NULL, 666.66, 'Auto - Check', 'per RIA comp statement rcvd from Max 8.23.21')
(157, 3, 3, '2021-09-17', 3, 2021, 3, 2021, NULL, NULL, 666.66, 'Auto - Check', 'per RIA comp statement rcvd')
(158, 3, 3, '2021-10-15', 3, 2021, 3, 2021, NULL, NULL, 666.66, 'Auto - Check', 'per RIA comp statement rcvd')
(159, 3, 3, '2021-11-20', 4, 2021, 4, 2021, NULL, NULL, 666.66, 'Auto - Check', 'per RIA comp statement rcvd')
(160, 3, 3, '2021-12-17', 4, 2021, 4, 2021, NULL, NULL, 666.66, 'Auto - Check', NULL)
//truncated...
(263, 6, 6, '2024-08-20', 3, 2024, 3, 2024, 14710457, NULL, 1837.19, 'Auto - Check', NULL)
(264, 6, 6, '2024-09-23', 3, 2024, 3, 2024, 15130036, NULL, 1889.7, 'Auto - Check', '')
(265, 6, 6, '2024-10-17', 3, 2024, 3, 2024, 15426229, NULL, 1926.67, 'Auto - Check', NULL)
(266, 6, 6, '2024-11-19', 3, 2024, 3, 2024, 15397306, NULL, 1923.0, 'Auto - Check', '')
(267, 7, 7, '2019-10-01', 3, 2019, 3, 2019, NULL, NULL, 655.54, '', 'Partial Payment for 9/14/2019-9/30/2019')
(268, 7, 7, '2020-01-01', 4, 2019, 4, 2019, NULL, NULL, 547.12, '', '12/14 - 12/31/2019')
(269, 7, 7, '2020-04-01', 1, 2020, 1, 2020, NULL, NULL, 472.5, '', '3/14/20 - 3/31/20')
(270, 7, 7, '2020-07-13', 2, 2020, 2, 2020, NULL, NULL, 551.67, '', 'Per email from TB 7/14/2020')
//truncated...
(271, 7, 7, '2020-10-13', 3, 2020, 3, 2020, NULL, NULL, 594.92, '', '9/16 - 9/30')
(272, 7, 7, '2021-01-11', 4, 2020, 4, 2020, NULL, NULL, 651.62, '', 'ACH notice via mail.')
(273, 7, 7, '2021-01-29', 4, 2020, 4, 2020, NULL, NULL, 78.04, '', 'ACH notice via mail.')
(274, 32, 7, '2021-08-23', 3, 2021, 3, 2021, NULL, NULL, 1596.68, '', NULL)
(275, 32, 7, '2021-09-17', 3, 2021, 3, 2021, NULL, NULL, 247.34, '', 'per RIA comp statement rcvd from Max 8.23.21')
(276, 32, 7, '2021-10-15', 3, 2021, 3, 2021, NULL, NULL, 243.1, '', 'per RIA comp statement')
(277, 32, 7, '2021-11-19', 4, 2021, 4, 2021, NULL, NULL, 251.32, '', 'per RIA comp statement')
(278, 32, 7, '2021-12-17', 4, 2021, 4, 2021, NULL, NULL, 250.66, '', 'per RIA comp statement')
(279, 32, 7, '2022-01-21', 4, 2021, 4, 2021, NULL, NULL, 258.23, '', NULL)
//truncated...
(919, 29, 29, '2023-06-12', 2, 2023, 2, 2023, 307387, NULL, 192.12, '', NULL)
(920, 35, 29, '2023-10-19', 3, 2023, 3, 2023, NULL, NULL, 665.49, '', 'Newly established at Principal; amount will be posted on 10.27.23')
(921, 35, 29, '2024-01-17', 4, 2023, 4, 2023, NULL, NULL, 748.16, '', NULL)
(922, 35, 29, '2024-04-15', 1, 2024, 1, 2024, NULL, NULL, 915.53, '', NULL)
(923, 35, 29, '2024-07-16', 2, 2024, 2, 2024, NULL, NULL, 946.32, '', NULL)
(924, 35, 29, '2024-10-14', 3, 2024, 3, 2024, NULL, NULL, 1043.09, '', NULL)

---

# TABLE NAME: contracts

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

# METIRCS: table: contracts

Column,Null %,Unique,Is Diverse,Avg Length,Min Length,Max Length
contract_id,0.0%,35,Yes,1.743,1,2
client_id,0.0%,29,Yes,1.657,1,2
active,0.0%,2,Yes,4.171,4,5
contract_number,28.571%,27,Yes,6.12,5,8
provider_name,0.0%,15,Yes,11.486,3,30
contract_start_date,91.429%,4,Yes,10.667,10,12
fee_type,2.857%,3,Yes,7.706,4,10
percent_rate,40.0%,15,Yes,7.429,5,8
flat_rate,62.857%,11,Yes,6.077,6,7
payment_schedule,2.857%,3,Yes,8.059,7,9
num_people,14.286%,21,Yes,2.233,1,3
notes,97.143%,3,Yes,134.0,134,134

## SAMPLE: table: contracts

(1, 1, 'TRUE', '134565', 'John Hancock', '2018-03-22', 'percentage', 0.0007, NULL, 'monthly', 18, 'Phone: 800-333-0963 Option 1 with Contract # or Option 2, ext 154617\r\nFax: General Info 866-377-9577  Enrollment Forms 866-377-8846 \r\n')
(2, 2, 'TRUE', NULL, 'Voya', '2019-04-19', 'percentage', 0.000416, NULL, 'monthly', 35, '')
(3, 3, 'TRUE', '551296', 'Voya', NULL, 'flat', '', 666.66, 'monthly', NULL, NULL)
(4, 4, 'FALSE', '684021', 'ADP', NULL, 'percentage', 0.00125, NULL, 'quarterly', 139, NULL)
(5, 5, 'TRUE', '231393', 'Ascensus Trust Company', '2019-05-2019', 'flat', '', 3000.0, 'quarterly', 93, NULL)
(6, 6, 'TRUE', '29366', 'John Hancock', NULL, 'percentage', 0.00125, NULL, 'monthly', 289, NULL)
(7, 7, 'FALSE', '15880157', 'Nationwide', NULL, 'percentage', 0.041667, NULL, 'monthly', 15, NULL)
(8, 8, 'TRUE', '273504', 'Ascensus', NULL, 'percentage', 0.003446, NULL, 'quarterly', 177, NULL)
(9, 9, 'TRUE', '134019', 'Direct from CG Engineering', NULL, 'flat', '', 2500.0, 'quarterly', 42, NULL)
(10, 10, 'TRUE', NULL, 'Empower', NULL, 'percentage', 0.000667, NULL, 'monthly', 208, NULL)
(11, 11, 'TRUE', '147266', 'John Hancock', NULL, 'percentage', 0.000208, NULL, 'monthly', 531, NULL)
(12, 12, 'TRUE', '222908', 'Ascensus Trust Company', NULL, 'flat', '', 2500.0, 'quarterly', 80, NULL)
(13, 13, 'TRUE', '41909', 'Fidelity', NULL, 'flat', '', 1250.0, 'monthly', 80, NULL)
(14, 14, 'TRUE', '34283', 'Fidelity', NULL, 'flat', '', 3750.0, 'quarterly', 24, NULL)
(15, 15, 'TRUE', '809872', 'Transamerica', NULL, 'percentage', 0.000417, NULL, 'monthly', NULL, NULL)
//truncated...
(32, 7, 'TRUE', '', 'Voya', NULL, 'percentage', 0.000417, NULL, 'monthly', 15, NULL)
(33, 16, 'TRUE', '', 'Empower', NULL, 'flat', '', 3500.0, 'quarterly', NULL, NULL)
(34, 28, 'TRUE', NULL, 'Empower', NULL, 'percentage', 0.000667, NULL, 'monthly', 43, NULL)
(35, 29, 'TRUE', NULL, 'Principal', NULL, 'percentage', 0.001875, NULL, 'quarterly', 15, NULL)

---

# INDEXES MADE IF NEEDED:

CREATE INDEX idx_contacts_client_id ON contacts(client_id)
CREATE INDEX idx_payments_client_id ON payments(client_id)
CREATE INDEX idx_payments_contract_id ON payments(contract_id)
CREATE INDEX idx_payments_date ON payments(client_id, received_date DESC)
CREATE INDEX idx_contacts_type ON contacts(client_id, contact_type)
CREATE INDEX idx_payments_quarter_year ON payments(client_id, applied_start_quarter, applied_start_year)
CREATE INDEX idx_contracts_active ON contracts(client_id, active)
CREATE INDEX idx_contracts_client_id ON contracts(client_id)
CREATE INDEX idx_contracts_provider ON contracts(provider_name)
