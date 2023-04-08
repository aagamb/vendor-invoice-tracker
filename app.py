from flask import Flask, render_template, request, url_for, redirect, session, send_file, flash
from flask_mail import Mail, Message
import sqlite3
import sys
import time
import os
from werkzeug.utils import secure_filename
from uuid import uuid4
import io

uname = None
company_name = None
company_id = None
user_id = None
vendor_id = None

d = {"approver":2, "accounts":3, "vendor":4}

def getdbConnection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def validate_passwords(pwd1, pwd2):
    if pwd1 != pwd2:
        return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


app = Flask(__name__)
app.secret_key = "my_secret_key"

app.config['UPLOAD_FOLDER'] = 'invoices'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vendorinvoicetracker2023@gmail.com'
app.config['MAIL_PASSWORD'] = 'ptnqecwxleiqtgew'
app.config['MAIL_DEFAULT_SENDER'] = 'vendorinvoicetracker2023@gmail.com'

mail = Mail(app)

def sendEmail(rec, company_name, invoice_no, invoice_amt, invoice_date,  status):

    body = '''The invoice to {company_name} dated {invoice_date} of amount {invoice_amt} has a change of status.
    It's status is updated to '{status}'.
    
    Please Do not respond to this email. It is autogenerated.
    '''
    subject = "{company_name} Invoice status update"
    
    msg = Message(subject, recipients=[rec])
    msg.body = body
    mail.send(msg)

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
    contact = request.form.get("contact")
    pwd = request.form.get("pwd1")
    
    # company_name    = request.form.get("company_name")
    company_addr    = request.form.get("company_addr")
    gstno           = request.form.get("gstno")
    company_contact = request.form.get("company_contact")
    
    conn = getdbConnection()
    cur = conn.cursor()

    cur.execute("INSERT INTO authorization(user_email, pwd) VALUES (?, ?)", (email, pwd))
    conn.commit()
    auth_id = cur.lastrowid
    print("auth_id: ", auth_id)
    cur.execute("INSERT INTO company(company_name) VALUES (?);", (cname, ))
    conn.commit()
    company_id = cur.lastrowid
    print("company_id: ", company_id)

    cur.execute('''INSERT INTO users(user_id, first_name, last_name, contact, company_id, user_role)
                    VALUES (?, ?, ?, ?, ?, ?);''', (auth_id, fname, lname, contact, company_id, 1))
    conn.commit()

    conn.close()
    
    return render_template("login.html", message="Account created successfully! Please login to continue")

@app.route("/forgotPassword")
def forgotPassword():
    # recipient = request.form['recipient']
    # subject = request.form['subject']
    # body = request.form['body']

    flash('Email sent successfully!', 'success')
    return render_template('index.html')

# This is used to determine which dashboard page should be loaded after authentication
@app.route('/loginDashboard', methods=['POST'])
def loginDashboard():
    global uname
    uname = request.form.get("uname")
    pwd = request.form.get("pwd")
    # role = request.form.get("role")
    
    print("USERNAME AND PASSWORD: ", uname, pwd, file=sys.stderr)
    
     # Create a new database or connect to an existing one
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()


    cur.execute(f"SELECT * FROM authorization WHERE user_email= ?", (uname,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    #username does not exist in the table
    if not row:
        print(f"No row found with uname = {uname}")
        print("Login Unsuccessful", file=sys.stderr)
        return render_template("login.html", errmsg="Authentication failed")
        
    #The username has been found in the table, password does not match  
    if row[-1] != pwd:
        print("Login Unsuccessful", file=sys.stderr)
        return render_template("login.html", errmsg="Authentication failed", usrname=uname)
    
    #Authentication successful
    print("Login Successful", file=sys.stderr)
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute(f"select * from authorization a JOIN users on a.auth_id = users.user_id where user_email= ?", (uname,))
    row = cur.fetchone()
    print(row, file=sys.stderr)
    
    cur.execute(f'''select company_name from (select * from authorization a JOIN users on a.auth_id = users.user_id)
                    NATURAL JOIN company  where user_email= ?''', (uname,))
    cname = cur.fetchone()
    session["cname"] = cname[0]
    global company_name
    company_name = cname[0]
    
    cur.execute(f'''select company_id from (select * from authorization a JOIN users on a.auth_id = users.user_id)
                    NATURAL JOIN company  where user_email= ?''', (uname,))
    cid = cur.fetchone()
    session["company_id"] = cid[0]
    global company_id
    company_id = cid[0]
    print("\ncompany_id: ", company_id, file = sys.stderr)
    
    
    
    cur.close()
    conn.close()
    
    if row[-1] == 1:
        print("\nADMIN LOGIN ENTERED\n")
        return redirect(url_for("dashboard_admin"))
    elif row[-1] == 2:
        print("\nApprover LOGIN ENTERED\n")
        return redirect(url_for("dashboard_approver"))
    elif row[-1] == 3:
        print("\nAccounts LOGIN ENTERED\n")
        return redirect(url_for("dashboard_accounts"))
    else:
        print("\nVendor LOGIN ENTERED\n")
        return redirect(url_for("dashboard_vendor"))
    

#ADMIN DASHBOARD NESTED PAGES --------------------------------
@app.route('/dashboard_admin')
def dashboard_admin():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Add column names to the cursor
    column_names = ["User Id", "First Name", "Last Name", "Contact", "User Role"]

    # Read the entire table
    cursor.execute("""SELECT u.user_id, u.first_name, u.last_name, u.contact, r.role FROM users u JOIN role r ON u.user_role = r.role_id WHERE u.company_id=?""", (company_id,))
    data = cursor.fetchall()
    print(data)
    
    # cursor.close()
    conn.close()
    return render_template('dashboard_admin.html', column_names=column_names, data=data)

@app.route('/adminAddUser')
def create_user():    
    return render_template("adminAddUser.html")

@app.route('/adminAddUser',  methods=['POST'])
def storeAdminAccountData():
    
    print("COMPANY NAME IS: ", session.get("cname"), "\n", file = sys.stderr)
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    cname = request.form.get("cname")
    email = request.form.get("email")
    contact = request.form.get("contact")
    pwd = request.form.get("pwd1")
    role = request.form.get("options")
    
    print("ROLE: ", role, sys.stderr)
    
    conn = getdbConnection()
    cur = conn.cursor()

    ret = cur.execute("INSERT INTO authorization(user_email, pwd) VALUES (?, ?)", (email, pwd))
    print(ret)
    conn.commit()
    auth_id = cur.lastrowid
    print("auth_id: ", auth_id)
    cur.execute("select * from company where company_name = ?;", (session["cname"], ))
    # company_id = cur.lastrowid
    print("company_id: ", company_id, sys.stderr)

    cur.execute('''INSERT INTO users(user_id, first_name, last_name, contact, company_id, user_role)
                    VALUES (?, ?, ?, ?, ?, ?);''', (auth_id, fname, lname, contact, company_id, d[role]))
    
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard_admin"))

@app.route('/adminListVendors')
def list_vendors():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Add column names to the cursor
    column_names = ["Company ID", "Company Name", "Company Address", "GST No.", "Company Email"]

    # Read the entire table
    cursor.execute('''select vr.vendor_id, c.company_name, c.company_addr, c.gstno, c.company_contact  from vendor_company_rel vr join company c on vr.vendor_id = c.company_id where vr.client_id = ?''', (company_id,))
    data = cursor.fetchall()
    print(data)
    
    # cursor.close()
    cursor.close()
    conn.close()
    return render_template('adminListVendors.html', column_names=column_names, data=data)

@app.route('/adminRegisterVendor')
def create_vendor():    
    return render_template("adminRegisterVendor.html")

@app.route('/adminRegisterVendor',  methods=['POST'])
def storeVendorAccountData():
    
    print("COMPANY NAME IS (Inside vendor): ", session.get("cname"), "\n", file = sys.stderr)
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    contact = request.form.get("contact")
    company_name = request.form.get("company_name")
    company_addr = request.form.get("company_addr")
    company_contact = request.form.get("company_contact")
    gstno = request.form.get("gstno")
    
    email = request.form.get("email")
    contact = request.form.get("contact")
    pwd = request.form.get("pwd1")
    role = "vendor"
    
    print("ROLE: ", role)
    
    conn = getdbConnection()
    cur = conn.cursor()

    ret = cur.execute("INSERT INTO authorization(user_email, pwd) VALUES (?, ?)", (email, pwd))
    print(ret)
    conn.commit()
    auth_id = cur.lastrowid
    print("auth_id: ", auth_id)
    cur.execute("""INSERT INTO company(company_name, company_addr, gstno, company_contact) 
                    VALUES (?, ?, ?, ?);""", (company_name, company_addr, gstno, company_contact))
    conn.commit()
    company_id = cur.lastrowid
    print("company_id: ", company_id)

    cur.execute('''INSERT INTO users(user_id, first_name, last_name, contact, company_id, user_role)
                    VALUES (?, ?, ?, ?, ?, ?);''', (auth_id, fname, lname, contact, company_id, d[role]))
    conn.commit()

    cur.execute("""INSERT INTO vendor_company_rel(vendor_id, client_id) VALUES(?, ?)""", (auth_id, session["company_id"]))
    conn.commit()

    conn.close()

    return redirect(url_for("dashboard_admin"))

@app.route('/adminDeleteUser', methods=['POST'])
def adminDeleteUser():
    row_id = request.form['data-row-id']
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    print("deleting user", row_id)
    cur.execute(f"DELETE FROM users WHERE user_id=?", (row_id,))
    cur.execute(f"DELETE FROM authorization WHERE auth_id=?", (row_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard_admin"))

@app.route("/adminModifyUser")
def adminModifyUser():
    return render_template("adminModifyUser.html")

@app.route("/adminModifyUser", methods=['POST'])
def adminModifyUserForm():
    global user_id
    user_id = request.form.get("user_id")
    print("user id: ", user_id, file = sys.stderr)
    
    conn = getdbConnection()
    cur = conn.cursor()
    
    # Add column names to the cursor
    cur.execute("PRAGMA table_info(users)")
    column_names = [col[1] for col in cur.fetchall()]

    # Read the entire table
    cur.execute("select * from users where user_id=?", (user_id,))
    data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("adminModifyUserDetails.html", data = data, column_names = column_names)

@app.route("/adminModifyUserAction", methods = ['POST'])
def adminModifyUserAction():
    # user_id = request.form.get("user_id")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    contact = request.form.get("contact")
    role = request.form.get("role")
    pwd = request.form.get("pwd")
    
    print("user id is: ", user_id,  "\n" , file = sys.stderr)

    conn = getdbConnection()
    cur = conn.cursor()

    cur.execute("select * from users where user_id=?", (user_id,))
    row = cur.fetchall()
    print(row[0], file=sys.stderr)

    cur.execute('''
        UPDATE users
        SET first_name = ?,
            last_name = ?,
            user_role =?,
            contact = ?
        WHERE user_id = ?;
        ''', (first_name, last_name, role, contact, user_id))
    conn.commit()
    
    cur.execute('''
        UPDATE authorization
        SET user_email = ?,
        pwd = ?
        WHERE auth_id = ?;
        ''', (contact, pwd, user_id))
    conn.commit()

    cur.close()
    conn.close()

    
    
    return redirect(url_for("dashboard_admin"))
    
#ADMIN DASHBOARD NESTED PAGES ENDS--------------------------------

#APPROVER DASHBOARD NESTED PAGES --------------------------------
@app.route('/dashboard_approver')
def dashboard_approver():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Add column names to the cursor
    cursor.execute("PRAGMA table_info(invoice)")
    column_names = [col[1] for col in cursor.fetchall()]
    column_names = ["Invoice Id", "Invoice Date", "Invoice Amount", "Invoiced By (invoice_vendor)"]

    # Read the entire table
    cursor.execute("SELECT invoice_id, invoice_date, invoice_amt, invoice_vendor FROM invoice WHERE invoice_client=? AND invoice_status=3", (company_id,))
    data = cursor.fetchall()

    conn.close()
    return render_template('dashboard_approver.html', column_names= column_names, data = data)

@app.route('/downloadFile', methods = ['POST'])
def download_file():
    row_id = request.form['data-row-id']
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("SELECT invoice_file FROM invoice WHERE invoice_id = ?", (row_id,))
    data = cur.fetchone()[0]

    cur.close()
    conn.close()
    return send_file(data, as_attachment=True)

@app.route("/approverApproved", methods=['POST'])
def approverApprovedAction():
    row_id = request.form['data-row-id']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
        UPDATE invoice
        SET invoice_status = 2
        WHERE invoice_id = ?;
        ''', (row_id,))
    conn.commit()
    
    print(row_id, file = sys.stderr)


    cur.close()
    conn.close()
    
    return redirect(url_for("dashboard_approver"))
    
@app.route("/approverRejected", methods=['POST'])
def approverRejectedAction():
    row_id = request.form['data-row-id']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
        UPDATE invoice
        SET invoice_status = 4
        WHERE invoice_id = ?;
        ''', (row_id,))
    conn.commit()
    
    print(row_id, file = sys.stderr)


    cur.close()
    conn.close()
    
    return redirect(url_for("dashboard_approver"))
    

#APPROVER DASHBOARD NESTED PAGES ENDS--------------------------------

#VENDOR DASHBOARD NESTED PAGES --------------------------------

@app.route('/dashboard_vendor')
def dashboard_vendor():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Add column names to the cursor
    cursor.execute("PRAGMA table_info(invoice)")
    column_names = [col[1] for col in cursor.fetchall()]
    column_names = ["Invoice Date", "Invoice Amount", "Company Invoiced ID", "Invoice Status"]

    cursor.execute("select company_name from company where company_id = ?", (company_id,))
    cname = cursor.fetchall()[0]
    # Read the entire table
    cursor.execute("select invoice_date, invoice_amt, invoice_client, invoice_status from invoice join (select * from company where company_id=?)", (company_id,))
    data = cursor.fetchall()
    
    print(data, file = sys.stderr)

    # cursor.close()
    conn.close()
    return render_template("dashboard_vendor.html", column_names = column_names, data = data )

@app.route('/vendorAddInvoice')
def vendorAddInvoice():
    return render_template("vendorAddInvoice.html")

@app.route('/vendorAddInvoice', methods=['POST'])
def vendorAddInvoiceAction():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # invoice_no = request.form['invoice_no']
        invoice_date = request.form['invoice_date']
        invoice_amt = request.form['invoice_amt']
        invoice_client = request.form['invoice_client']

        # Save the file path and other invoice details in the database
        conn = getdbConnection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO invoice (invoice_date, invoice_amt, invoice_vendor ,invoice_client, invoice_status, invoice_file) VALUES (?, ?, ?, ?, ?, ?)",
            (invoice_date, invoice_amt, company_id, invoice_client, 3, file_path)
        )
        conn.commit()
        
        # cursor.execute('select c.company_contact, c.company_name, i.invoice_no from company c join invoice i on i.invoice_client=?', (company_id,))
        # company_email , company_name, invoice_no = cursor.fetchone()[0]
        
        # sendEmail(company_email, company_name, invoice_no, invoice_amt, invoice_date, "Pending Approval")

        cursor.close()
        conn.close()

        
        
        return redirect(url_for("dashboard_vendor"))

    return "File type not allowed", 400

@app.route('/vendorDeleteInvoice', methods=['POST'])
def vendorDeleteInvoice():
    row_id = request.form['data-row-id']
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    print("deleting user", row_id, file = sys.stderr)
    cur.execute(f"DELETE FROM invoice WHERE invoice_date=?", (row_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard_vendor"))
    
#VENDOR DASHBOARD NESTED PAGES ENDS--------------------------------

#ACCOUNTS DASHBOARD NESTED PAGES--------------------------------
@app.route("/dashboard_accounts")
def dashboard_accounts():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Add column names to the cursor
    cursor.execute("PRAGMA table_info(invoice)")
    column_names = [col[1] for col in cursor.fetchall()]
    column_names = ["Invoice Id", "Invoice Date", "Invoice Amount", "Company Invoiced ID", "Invoice Status"]

    cursor.execute("select company_name from company where company_id = ?", (company_id,))
    cname = cursor.fetchall()[0]
    # Read the entire table
    cursor.execute("select invoice_id, invoice_date, invoice_amt, invoice_client, invoice_status from invoice join (select * from company where company_id=?) where invoice_status=2", (company_id,))
    data = cursor.fetchall()
    
    print(data, file = sys.stderr)

    # cursor.close()
    conn.close()
    return render_template("dashboard_accounts.html", column_names = column_names, data = data )

@app.route("/accountsApproved", methods=['POST'])
def accountsApprovedAction():
    row_id = request.form['data-row-id']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
        UPDATE invoice
        SET invoice_status = 1
        WHERE invoice_id = ?;
        ''', (row_id,))
    conn.commit()
    
    print(row_id, file = sys.stderr)


    cur.close()
    conn.close()
    
    return redirect(url_for("dashboard_accounts"))
    
@app.route("/accountsRejected", methods=['POST'])
def accountsRejectedAction():
    row_id = request.form['data-row-id']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
        UPDATE invoice
        SET invoice_status = 4
        WHERE invoice_id = ?;
        ''', (row_id,))
    conn.commit()

    cur.close()
    conn.close()
    
    return redirect(url_for("dashboard_accounts"))
    

#ACCOUNTS DASHBOARD NESTED PAGES ENDS--------------------------------



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
