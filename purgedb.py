import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS approver;")
cur.execute("DROP TABLE IF EXISTS accounts;")
cur.execute("DROP TABLE IF EXISTS vendor;")