# importing the modules
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
from passlib.hash import pbkdf2_sha256
import config

# app config
app = Flask(__name__)
app.config['MYSQL_HOST'] = config.sql_server
app.config['MYSQL_USER'] = config.mysql_username
app.config['MYSQL_PASSWORD'] = config.sql_password
app.config['MYSQL_DB'] = config.mysql_username
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = config.email
app.config['MAIL_PASSWORD'] = config.password
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False

mysql = MySQL(app)
app.secret_key = 'returnzero'
mail = Mail(app)


# routes

# home
@app.route("/",methods=['GET',"POST"])
def home():
    if ('user' not in session.keys()) or (session['user'] == None):
        return redirect(url_for('login'))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM User WHERE id = % s",[session['user']])
        userdetails = cursor.fetchone()
        if userdetails[3] == 2:
            return render_template("home.html",user=userdetails)
        elif userdetails[3] == 1:
            cursor.execute("SELECT * FROM Tickets WHERE agent=%s",[session['user']])
            tickets = cursor.fetchall()
            return render_template("home.html",user=userdetails,tickets=tickets)
        else:
            if request.method == "POST":
                title = request.form['title']
                description = request.form['description']
                cust_id = session['user']
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO Tickets(customer,title,description) VALUES(%s,%s,%s)",(cust_id,title,description))
                mysql.connection.commit()
                cursor.execute("SELECT * FROM User WHERE id = % s",[session['user']])
                userdetails = cursor.fetchone()
                cursor.execute("SELECT * FROM Tickets WHERE customer = %s",[session['user']])
                tickets = cursor.fetchall()
                return render_template("home.html",msg="Ticket Filed",user=userdetails,tickets=tickets)
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM User WHERE id = % s",[session['user']])
            userdetails = cursor.fetchone()
            cursor.execute("SELECT * FROM Tickets WHERE customer = %s",[session['user']])
            tickets = cursor.fetchall()
            return render_template("home.html",user=userdetails,tickets=tickets)

# user account registration
@app.route("/register",methods=["GET","POST"])
def register_account():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = pbkdf2_sha256.hash(password)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO User(username,email,password,role) VALUES(%s,%s,%s,%s)",(username,email,hashed_password,0))
        mysql.connection.commit()
        msg = Message('registration customer care',sender=config.email,
            recipients=[email]
        )
        msg.body = '''
            Account creation in customer care registry was successful.
            for raising tickets, login with your email id and password.
            Thank You
        '''
        mail.send(msg)
        return redirect(url_for("login"))
    return render_template("register.html")

# login
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM User WHERE email = % s",[email])
        userdetails = cursor.fetchone()
        if userdetails:
            if pbkdf2_sha256.verify(password,userdetails[2]):
                session['user'] = userdetails[4]
                return redirect(url_for("home"))
            else:
                msg = "Incorrect Password"
        else:
            msg = "User does not exist"
        return render_template("login.html",msg=msg)
    return render_template("login.html")

# logout
@app.route("/logout")
def logout():
    session['user'] = None
    return redirect(url_for("home"))


# ticket detail
@app.route("/ticket/<int:id>",methods=["GET","POST"])
def ticket_detail(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Tickets WHERE id=%s",[id])
    ticket = cursor.fetchone()
    cursor.execute("SELECT * FROM User WHERE id=%s",[ticket[1]])
    customer = cursor.fetchone()
    cursor.execute("SELECT * FROM User WHERE id=%s",[session['user']])
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM User WHERE role=1")
    all_users = cursor.fetchall()
    cursor.execute("SELECT * FROM User WHERE id=%s",[ticket[2]])
    agent = cursor.fetchone()
    if agent is None:
        agent = [None,None]
    if user is None:
        return redirect(url_for("login"))
    if request.method == "POST":
        agent = request.form['agent']
        cursor.execute("UPDATE Tickets SET agent= %s WHERE id = %s",(agent,id))
        cursor.execute("UPDATE Tickets SET progress='assigned' WHERE id = %s",[id])
        mysql.connection.commit()
        cursor.execute("SELECT email FROM User WHERE id=%s",[agent])
        agent_mail = cursor.fetchone()[0]
        msg = Message('Assigned Ticket',sender=config.email,
            recipients=[agent_mail]
        )

        # send mail to agent
        msg = Message('Assigned Ticket',sender=config.email,
            recipients=[agent_mail]
        )
        cursor.execute("SELECT email FROM User WHERE id=%s",[ticket[1]])
        customer = cursor.fetchone()[0]
        msg.body = f'''
            You have been assigned a ticket.
            Ticket Title: {ticket[3]}
            posted by: {customer}
        '''
        mail.send(msg)

        # send mail to customer
        msg = Message('Ticked Progress',sender=config.email,
            recipients=[customer]
        )
        msg.body = f'''
            Dear Customer,
            Your Ticket progress has been Updated and
            Assigned to an Agent of ours.
            Agent : {agent_mail}
        '''
        mail.send(msg)
        return redirect(url_for("panel"))
    return render_template("details.html",ticket=ticket,agent=agent,customer=customer,user=user,all_users=all_users)


# admin register
@app.route("/admin/register",methods=["GET","POST"])
def admin_register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        secret_key = request.form['secret']
        if secret_key == "12345":
            hashed_password = pbkdf2_sha256.hash(password)
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO User(username,email,password,role) VALUES(%s,%s,%s,%s)",(username,email,hashed_password,2))
            mysql.connection.commit()
            return redirect(url_for("login"))
        else:
            return render_template("admin_register.html",msg="Invlaid Secret")

    return render_template("admin_register.html")

# promote agent
@app.route("/panel",methods=['GET','POST'])
def panel():
    id = session['user']
    if id is None:
        return redirect("login")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM User WHERE id=%s",[id])
    user_details = cursor.fetchone()
    if user_details[3] != 2:
        return "You do not have administrator privileges"
    else:
        cursor.execute("SELECT * FROM User WHERE role=0")
        all_users = cursor.fetchall()
        cursor.execute("SELECT * FROM Tickets WHERE progress IS NULL")
        tickets = cursor.fetchall()
        if request.method == "POST":
            user_id = request.form['admin-candidate']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE User SET role=1 WHERE id = %s",[user_id])
            mysql.connection.commit()
            cursor.execute("SELECT * FROM User WHERE id = %s",[user_id])
            promoted_agent = cursor.fetchone()
            msg = Message('Promoted to Agent',sender=config.email,recipients=[promoted_agent[1]])
            msg.body = """
                Dear User,
                You have been promoted to an Agent in the Customer-Care-Registry.
                You will be able to handle tickets for the customer from now on.
                Congratulations.
            """
            mail.send(msg)
            return redirect(url_for("panel"))
        return render_template("panel.html",all_users=all_users,user=user_details,tickets=tickets)

# accept ticket
@app.route("/accept/<int:ticket_id>/<int:user_id>")
def accept(ticket_id,user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM User WHERE id = %s",[user_id])
    agent = cursor.fetchone()
    cursor.execute("SELECT * FROM Tickets WHERE id=%s",[ticket_id])
    ticket = cursor.fetchone()
    cursor.execute("SELECT email FROM User WHERE id=%s",[ticket[1]])
    customer = cursor.fetchone()
    if agent[4] == ticket[2]:
        cursor.execute("UPDATE Tickets SET progress='accepted' WHERE id=%s",[ticket_id])
        mysql.connection.commit()
        msg = Message('Ticket Progress',sender=config.email,recipients=[customer[0]])
        msg.body = f"""
            Dear User,
            Your Ticket has been accepted by {agent[1]}
        """
        mail.send(msg)
    return redirect(url_for("home"))

# close ticket
@app.route("/delete/<int:ticket_id>/<int:user_id>")
def delete(ticket_id,user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM User WHERE id = %s",[user_id])
    agent = cursor.fetchone()
    cursor.execute("SELECT * FROM Tickets WHERE id=%s",[ticket_id])
    ticket = cursor.fetchone()
    if agent[4] == ticket[2]:
        cursor.execute("DELETE FROM Tickets WHERE id=%s",[ticket_id])
        mysql.connection.commit()
        cursor.execute("SELECT * FROM User WHERE id=%s",[ticket[1]])
        customer = cursor.fetchone()
        msg = Message('Ticket Progress',sender=config.email,recipients=[customer[1]])
        msg.body = f"""
            Dear User,
            Your Ticket has been Closed by {agent[1]}
            Thanks For using Customer Care Registry.
        """
        mail.send(msg)
    return redirect(url_for("home"))


# run server
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port='8080')

