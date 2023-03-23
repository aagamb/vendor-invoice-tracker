from flask import Flask, render_template, redirect, url_for, request
import math
import matplotlib
matplotlib.use('Agg') 
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


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/report', methods=['POST', 'GET'])
def report():
    if request.method == 'POST':
        
        # D = float(request.form.get('D'))
        
        return render_template("report.html", report=report, figs = figs)
    

    
    
    else:
        D = request.args.get('D')
        return render_template("index.html")
        # return redirect(url_for('showVar', varName =D))

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
