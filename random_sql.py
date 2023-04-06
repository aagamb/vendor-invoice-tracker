import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()


cur.execute("DELETE FROM authorization where user_email = 'ff';")
data = cur.fetchall()
print(data)
conn.commit()
conn.close()
