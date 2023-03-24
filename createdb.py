import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()

conn.execute('''CREATE TABLE IF NOT EXISTS approver
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                cname TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                pwd TEXT NOT NULL);''')

conn.execute('''CREATE TABLE IF NOT EXISTS accounts
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                cname TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                pwd TEXT NOT NULL);''')

conn.execute('''CREATE TABLE IF NOT EXISTS vendor
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                vname TEXT NOT NULL UNIQUE,
                vmail TEXT NOT NULL UNIQUE,
                pwd TEXT NOT NULL);''')