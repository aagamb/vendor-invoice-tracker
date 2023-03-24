from flask import Flask, render_template, redirect, url_for, request
import math
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import numpy as np
from itertools import product
import math
from math import pi
import pandas as pd
import time
import os
import sqlite3
matplotlib.use('Agg') 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/createAccount')
def createAccount():
    return render_template("createAccount.html")

@app.route('/createAccount', methods=['POST'])
def storeAccountData():
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    cname = request.form.get("cname")
    email = request.form.get("email")
    pwd = request.form.get("pwd")
    role = request.form.get("role")

    if role == 0:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('''INSERT INTO approver 
                    (fname, lname, cname, email, pwd) 
                    VALUES (?,?,?,?,?)''', 
                    (fname, lname, cname, email, pwd))
        cur.close()
        conn.close()
    elif role == 1:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('''INSERT INTO accounts 
                    (fname, lname, cname, email, pwd) 
                    VALUES (?,?,?,?,?)''', 
                    (fname, lname, cname, email, pwd))
        cur.close()
        conn.close()
    elif role == 2:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('''INSERT INTO vendor 
                    (fname, lname, vname, vmail, pwd) 
                    VALUES (?,?,?,?,?)''', 
                    (fname, lname, cname, email, pwd))
        cur.close()
        conn.close()
    else:
        print("Error in POST form", file=sys.stderr)
        return render_template("createAccount.html")
    
    return render_template("login.html")


@app.route('/loginDashboard', methods=['POST'])
def loginDashboard():
    uname = request.form.get("uname")
    pwd = request.form.get("pwd")
    role = request.form.get("role")
    
    print("USERNAME AND PASSWORD: ", uname, pwd, file=sys.stderr)
    
     # Create a new database or connect to an existing one
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    # Create a table for storing user credentials
    if role == 0:
        conn.execute('''CREATE TABLE IF NOT EXISTS approver
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    cname TEXT NOT NULL UNIQUE,
                    uname TEXT NOT NULL UNIQUE,
                    pwd TEXT NOT NULL);''')
    elif role == 1:
        conn.execute('''CREATE TABLE IF NOT EXISTS accounts
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    cname TEXT NOT NULL UNIQUE,
                    uname TEXT NOT NULL UNIQUE,
                    pwd TEXT NOT NULL);''')
    elif role == 2:
        conn.execute('''CREATE TABLE IF NOT EXISTS vendor
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    cname TEXT NOT NULL UNIQUE,
                    vname TEXT NOT NULL UNIQUE,
                    vmail TEXT NOT NULL UNIQUE,
                    pwd TEXT NOT NULL);''')
    cur.execute(f"SELECT * FROM users WHERE uname= ?", (uname,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if row:
        if row[-1] == pwd:
            print("Login Successful", file=sys.stderr)
            return render_template("dashboard.html")
        else:
            print("Login Unsuccessful", file=sys.stderr)
            return render_template("login.html")
            
    else:
        print(f"No row found with uname = {uname}")
        print("Login Unsuccessful", file=sys.stderr)
        return render_template("login.html")


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    
    if request.method != 'POST':
        return render_template("index.html")
        
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    cname = request.form.get("cname")
    uname = request.form.get("uname")
    pwd = request.form.get("pwd")
    
    print("USERNAME AND PASSWORD: ", uname, pwd, file=sys.stderr)

    # Create a new database or connect to an existing one
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    # Create a table for storing user credentials
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                cname TEXT NOT NULL UNIQUE,
                uname TEXT NOT NULL UNIQUE,
                pwd TEXT NOT NULL);''')

    # Execute a SQL SELECT statement to search for the string in the database
    cur.execute('SELECT * FROM users WHERE uname LIKE ?', ('%' + uname + '%',))

    # Fetch the results of the SELECT statement
    result = cur.fetchall()

    if len(result)>0:
        print("already in db", file = sys.stderr)
        cur.close()
        conn.close()
        return render_template("createAccount.html", err="true")
    
    # Execute a SQL SELECT statement to search for the string in the database
    cur.execute('SELECT * FROM users WHERE uname LIKE ?', ('%' + cname + '%',))

    # Fetch the results of the SELECT statement
    result = cur.fetchall()
    
    
    if len(result)>0:
        print("already in db", file = sys.stderr)
        cur.close()
        conn.close()
        return render_template("createAccount.html", err="true")
    
    
    

    conn.execute("INSERT INTO users (fname, lname, cname, uname, pwd) VALUES (?,?,?,?,?)", (fname, lname, cname, uname, pwd))
    conn.commit()
    conn.close()

    print("NEW USER ADDED", file = sys.stderr)    
    
    return render_template("dashboard.html")
    



if __name__ == "__main__":
    app.run(debug=True, port=5001)
