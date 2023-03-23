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
    return render_template("index.html")

@app.route('/landingPage', methods=['POST', 'GET'])
def report():
    if request.method != 'POST':
        return render_template("index.html")
        
    username = request.form.get("user")
    password = request.form.get("pwd")
    
    print("USERNAME AND PASSWORD: ", username, password, file=sys.stderr)
    
    if username is None:
        return 

    # Create a new database or connect to an existing one
    conn = sqlite3.connect('users.db')

    # Create a table for storing user credentials
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL);''')

    # Insert the new username and password into the table
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

    print("New user added successfully!")

    # Close the database connection
    conn.close()
    
    return render_template("landingPage.html")

@app.route('/createDB')
def createDB():
    return render_template("createDB.html")

@app.route('/databaseReport',methods=['POST', 'GET'])
def databaseReport():
    if request.method == "POST":
        report = request.form
        Dstart  = float(report['Dstart'])    

        return render_template("databaseReport.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
