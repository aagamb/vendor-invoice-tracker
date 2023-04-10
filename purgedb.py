import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS approver;")
cur.execute("DROP TABLE IF EXISTS accounts;")
cur.execute("DROP TABLE IF EXISTS vendor;")
cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("DROP TABLE IF EXISTS role;")
cur.execute("DROP TABLE IF EXISTS company;")
cur.execute("DROP TABLE IF EXISTS authorization;")
cur.execute("DROP TABLE IF EXISTS vendor_company_rel;")
cur.execute("DROP TABLE IF EXISTS invoice;")
cur.execute("DROP TABLE IF EXISTS invoice_state;")