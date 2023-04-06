import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()

conn.execute('''
                CREATE TABLE IF NOT EXISTS role (
                    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role    TEXT
                );
            ''')
conn.execute("INSERT INTO role (role) VALUES (?)", ("Admin", ));
conn.execute("INSERT INTO role (role) VALUES (?)", ("Approver", ));
conn.execute("INSERT INTO role (role) VALUES (?)", ("Accounts", ));
conn.execute("INSERT INTO role (role) VALUES (?)", ("Vendor", ));


conn.execute('''
                CREATE TABLE IF NOT EXISTS company (
                    company_id      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    company_name    TEXT NOT NULL,
                    company_addr    TEXT,
                    gstno           TEXT,
                    company_contact TEXT
                );
            ''')

conn.execute('''
                CREATE TABLE IF NOT EXISTS authorization (
                    auth_id     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    user_email  TEXT UNIQUE NOT NULL,
                    pwd         TEXT
                );
            ''')

conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id     INTEGER,
                    first_name  TEXT NOT NULL,
                    last_name   TEXT,
                    contact     TEXT,
                    company_id  INTEGER,
                    user_role   INTEGER NOT NULL,
                    FOREIGN KEY(user_id) 
                        REFERENCES authorization(auth_id),
                    FOREIGN KEY(company_id) 
                        REFERENCES company(company_id),
                    FOREIGN KEY(user_role) 
                        REFERENCES role(role_id)
                );
            ''')

conn.execute('''
                CREATE TABLE IF NOT EXISTS invoice_status (
                    invoice_status_id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    invoice_status     TEXT
                );
            ''')

conn.execute("INSERT INTO invoice_status (invoice_status) VALUES (?)", ("Approved", ));
conn.execute("INSERT INTO invoice_status (invoice_status) VALUES (?)", ("Rejected", ));
conn.execute("INSERT INTO invoice_status (invoice_status) VALUES (?)", ("Pending Approval", ));
conn.execute("INSERT INTO invoice_status (invoice_status) VALUES (?)", ("Payment Complete", ));
conn.execute("INSERT INTO invoice_status (invoice_status) VALUES (?)", ("Payment Rejected", ));

conn.execute('''
                CREATE TABLE IF NOT EXISTS invoice (
                    invoice_id          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    invoice_no          TEXT,
                    invoice_date        TEXT,
                    invoice_amt         TEXT,
                    invoice_vendor      INTEGER,
                    invoice_client      INTEGER,
                    invoice_status_id   INTEGER,
                    invoice_file        TEXT,
                    FOREIGN KEY(invoice_vendor) 
                        REFERENCES company(company_id),
                    FOREIGN KEY(invoice_client) 
                        REFERENCES company(company_id),
                    FOREIGN KEY(invoice_status) 
                        REFERENCES invoice_status(invoice_status_id)
                );
            ''')

conn.execute('''
                CREATE TABLE IF NOT EXISTS invoice_state (
                    invoice_id          INTEGER ,
                    log_date            TEXT,
                    invoice_status_id   INTEGER,
                    FOREIGN KEY(invoice_id) 
                        REFERENCES invoice(invoice_id),
                    FOREIGN KEY(invoice_status) 
                        REFERENCES invoice_status(invoice_status_id)
                );
            ''')

conn.execute('''
                CREATE TABLE IF NOT EXISTS vendor_company_rel (
                    vendor_id   INTEGER ,
                    client_id   INTEGER,
                    FOREIGN KEY(vendor_id) 
                        REFERENCES company(company_id),
                    FOREIGN KEY(client_id) 
                        REFERENCES company(company_id)
                );
            ''')

conn.commit()
conn.close()
