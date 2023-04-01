import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()


cur.execute("DELETE FROM authorization WHERE auth_id=2;")
