CREATE TABLE sqlite_sequence(name,seq)
CREATE TABLE "contacts" (
	"contact_id"	INTEGER NOT NULL,
	"client_id"	INTEGER NOT NULL,
	"contact_type"	TEXT NOT NULL,
	"contact_name"	TEXT,
	"phone"	TEXT,
	"email"	TEXT,
	"fax"	TEXT,
	"physical_address"	TEXT,
	"mailing_address"	TEXT, valid_from DATETIME, valid_to DATETIME,
	PRIMARY KEY("contact_id" AUTOINCREMENT),
	FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
)
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
	"notes"	TEXT, valid_from DATETIME, valid_to DATETIME,
	PRIMARY KEY("payment_id" AUTOINCREMENT),
	FOREIGN KEY("client_id") REFERENCES "clients"("client_id"),
	FOREIGN KEY("contract_id") REFERENCES "contracts"("contract_id")
)
CREATE INDEX idx_contacts_client_id ON contacts(client_id)
CREATE INDEX idx_payments_client_id ON payments(client_id)
CREATE INDEX idx_payments_contract_id ON payments(contract_id)
CREATE INDEX idx_payments_date ON payments(client_id, received_date DESC)
CREATE INDEX idx_contacts_type ON contacts(client_id, contact_type)
CREATE INDEX idx_payments_quarter_year ON payments(client_id, applied_start_quarter, applied_start_year)
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
	"notes"	TEXT, valid_from DATETIME, valid_to DATETIME,
	PRIMARY KEY("contract_id" AUTOINCREMENT),
	FOREIGN KEY("client_id") REFERENCES "clients"("client_id")
)
CREATE INDEX idx_contracts_active ON contracts(client_id, active)
CREATE INDEX idx_contracts_client_id ON contracts(client_id)
CREATE INDEX idx_contracts_provider ON contracts(provider_name)
CREATE TABLE "clients" (
	"client_id"	INTEGER NOT NULL,
	"display_name"	TEXT NOT NULL,
	"full_name"	TEXT,
	"ima_signed_date"	TEXT,
	"file_path_account_documentation"	TEXT,
	"file_path_consulting_fees"	TEXT,
	"file_path_meetings"	TEXT, valid_from DATETIME, valid_to DATETIME,
	PRIMARY KEY("client_id" AUTOINCREMENT)
)
CREATE INDEX idx_contracts_provider_active 
ON contracts(provider_name, active)
CREATE TABLE quarterly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    total_payments REAL,
    total_assets REAL,
    payment_count INTEGER,
    avg_payment REAL,
    expected_total REAL,
    last_updated TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(client_id),
    UNIQUE(client_id, year, quarter)
)
CREATE TABLE yearly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    total_payments REAL,
    total_assets REAL,
    payment_count INTEGER,
    avg_payment REAL,
    yoy_growth REAL,
    last_updated TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(client_id),
    UNIQUE(client_id, year)
)
CREATE TABLE client_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    last_payment_date TEXT,
    last_payment_amount REAL,
    last_payment_quarter INTEGER,
    last_payment_year INTEGER,
    total_ytd_payments REAL,
    avg_quarterly_payment REAL,
    last_recorded_assets REAL,
    last_updated TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(client_id),
    UNIQUE(client_id)
)
CREATE INDEX idx_quarterly_lookup ON quarterly_summaries(client_id, year, quarter)
CREATE INDEX idx_yearly_lookup ON yearly_summaries(client_id, year)
CREATE INDEX idx_client_metrics_lookup ON client_metrics(client_id)
CREATE TRIGGER update_quarterly_after_insert
            AFTER INSERT ON payments
            BEGIN
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    NEW.client_id,
                    NEW.applied_start_year,
                    NEW.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = NEW.client_id
                AND applied_start_year = NEW.applied_start_year
                AND applied_start_quarter = NEW.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;
            END
CREATE TRIGGER update_quarterly_after_update
            AFTER UPDATE ON payments
            BEGIN
                -- Update old quarter summary
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    OLD.client_id,
                    OLD.applied_start_year,
                    OLD.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = OLD.client_id
                AND applied_start_year = OLD.applied_start_year
                AND applied_start_quarter = OLD.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;

                -- Update new quarter summary
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    NEW.client_id,
                    NEW.applied_start_year,
                    NEW.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = NEW.client_id
                AND applied_start_year = NEW.applied_start_year
                AND applied_start_quarter = NEW.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;
            END
CREATE TRIGGER update_quarterly_after_delete
            AFTER DELETE ON payments
            BEGIN
                INSERT INTO quarterly_summaries (
                    client_id, year, quarter, total_payments,
                    total_assets, payment_count, avg_payment,
                    expected_total, last_updated
                )
                SELECT 
                    OLD.client_id,
                    OLD.applied_start_year,
                    OLD.applied_start_quarter,
                    COALESCE(SUM(actual_fee), 0),
                    AVG(total_assets),
                    COUNT(*),
                    CASE 
                        WHEN COUNT(*) > 0 THEN COALESCE(SUM(actual_fee), 0) / COUNT(*)
                        ELSE 0
                    END,
                    MAX(expected_fee),
                    datetime('now')
                FROM payments
                WHERE client_id = OLD.client_id
                AND applied_start_year = OLD.applied_start_year
                AND applied_start_quarter = OLD.applied_start_quarter
                ON CONFLICT(client_id, year, quarter) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    expected_total = excluded.expected_total,
                    last_updated = excluded.last_updated;

                -- Remove empty summaries
                DELETE FROM quarterly_summaries
                WHERE payment_count = 0;
            END
CREATE TRIGGER update_yearly_after_quarterly_change
            AFTER INSERT ON quarterly_summaries
            BEGIN
                INSERT INTO yearly_summaries (
                    client_id, year, total_payments, total_assets,
                    payment_count, avg_payment, yoy_growth, last_updated
                )
                SELECT 
                    NEW.client_id,
                    NEW.year,
                    COALESCE(SUM(total_payments), 0),
                    AVG(total_assets),
                    SUM(payment_count),
                    CASE 
                        WHEN SUM(payment_count) > 0 
                        THEN COALESCE(SUM(total_payments), 0) / SUM(payment_count)
                        ELSE 0
                    END,
                    CASE
                        WHEN (SELECT total_payments FROM yearly_summaries 
                              WHERE client_id = NEW.client_id 
                              AND year = NEW.year - 1) > 0
                        THEN ((COALESCE(SUM(total_payments), 0) - 
                              (SELECT total_payments FROM yearly_summaries 
                               WHERE client_id = NEW.client_id 
                               AND year = NEW.year - 1)) /
                              (SELECT total_payments FROM yearly_summaries 
                               WHERE client_id = NEW.client_id 
                               AND year = NEW.year - 1)) * 100
                        ELSE NULL
                    END,
                    datetime('now')
                FROM quarterly_summaries
                WHERE client_id = NEW.client_id AND year = NEW.year
                GROUP BY client_id, year
                ON CONFLICT(client_id, year) DO UPDATE SET
                    total_payments = excluded.total_payments,
                    total_assets = excluded.total_assets,
                    payment_count = excluded.payment_count,
                    avg_payment = excluded.avg_payment,
                    yoy_growth = excluded.yoy_growth,
                    last_updated = excluded.last_updated;
            END
CREATE TRIGGER update_client_metrics_after_payment_change
            AFTER INSERT ON payments
            BEGIN
                INSERT INTO client_metrics (
                    client_id, last_payment_date, last_payment_amount,
                    last_payment_quarter, last_payment_year,
                    total_ytd_payments, avg_quarterly_payment,
                    last_recorded_assets, last_updated
                )
                SELECT 
                    p.client_id,
                    p.received_date,
                    p.actual_fee,
                    p.applied_start_quarter,
                    p.applied_start_year,
                    (SELECT COALESCE(SUM(actual_fee), 0)
                     FROM payments 
                     WHERE client_id = p.client_id 
                     AND applied_start_year = strftime('%Y', 'now')),
                    (SELECT AVG(total_payments)
                     FROM quarterly_summaries
                     WHERE client_id = p.client_id
                     AND total_payments > 0
                     ORDER BY year DESC, quarter DESC
                     LIMIT 4),
                    p.total_assets,
                    datetime('now')
                FROM payments p
                WHERE p.payment_id = NEW.payment_id
                ON CONFLICT(client_id) DO UPDATE SET
                    last_payment_date = excluded.last_payment_date,
                    last_payment_amount = excluded.last_payment_amount,
                    last_payment_quarter = excluded.last_payment_quarter,
                    last_payment_year = excluded.last_payment_year,
                    total_ytd_payments = excluded.total_ytd_payments,
                    avg_quarterly_payment = excluded.avg_quarterly_payment,
                    last_recorded_assets = excluded.last_recorded_assets,
                    last_updated = excluded.last_updated;
            END
CREATE TRIGGER version_clients
BEFORE UPDATE ON clients
FOR EACH ROW
BEGIN
    INSERT INTO clients SELECT *, OLD.valid_from, DATETIME('now') 
    FROM clients WHERE id = OLD.id;
    
    UPDATE clients 
    SET valid_from = DATETIME('now'),
        valid_to = NULL
    WHERE id = OLD.id;
END
CREATE TRIGGER version_contracts
BEFORE UPDATE ON contracts
FOR EACH ROW
BEGIN
    INSERT INTO contracts SELECT *, OLD.valid_from, DATETIME('now') 
    FROM contracts WHERE id = OLD.id;
    
    UPDATE contracts 
    SET valid_from = DATETIME('now'),
        valid_to = NULL
    WHERE id = OLD.id;
END
CREATE TRIGGER version_payments
BEFORE UPDATE ON payments
FOR EACH ROW
BEGIN
    INSERT INTO payments SELECT *, OLD.valid_from, DATETIME('now') 
    FROM payments WHERE id = OLD.id;
    
    UPDATE payments 
    SET valid_from = DATETIME('now'),
        valid_to = NULL
    WHERE id = OLD.id;
END
