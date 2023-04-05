from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from jinja2 import Template
# from flask_socketio import SocketIO
# from flask_socketio import emit, send
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime
app = Flask(__name__)
app.secret_key = 'shankh'

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# socketio = SocketIO(app, cors_allowed_origins="*")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shankh'
app.config['MYSQL_DB'] = 'user'
mysql = MySQL(app)


def insert_profile(first_name,last_name,username,email,password):
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   check=cursor.execute('SELECT * FROM profile WHERE username = (% s) ', (username,))
   report=tuple(cursor.fetchall())
   check_mail=cursor.execute('SELECT * FROM profile WHERE email = (% s) ', (email,))
   report_mail=tuple(cursor.fetchall())
   if (report != ()): 
       return 0
   elif (report_mail != ()): return 2
   else:  
        cursor.execute('create table chat.{} (user_id VARCHAR(100), sender_id VARCHAR(100), message VARCHAR(1000), date DATE, time TIME)'.format(username))
        cursor.execute('INSERT INTO profile VALUES (% s,% s,% s ,% s,% s);', (first_name,last_name,username, email, password))
        mysql.connection.commit()
   cursor.close()
   return(1)
def insert_chat(user_id_1, user_id_2,sender_id, message, date, time):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('USE chat;')
    cursor.execute('INSERT INTO {} VALUES (% s,% s ,% s,% s, % s);'.format(user_id_1), (user_id_2, sender_id, message, date, time))
    mysql.connection.commit()
    cursor.execute('INSERT INTO {} VALUES (% s,% s ,% s,% s, % s);'.format(user_id_2), (user_id_1, sender_id, message, date, time))
    mysql.connection.commit()
    cursor.execute('use user;')
    cursor.close()
    
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login.html/register', methods = ['GET', 'POST'])
def register_user():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        user_mail = request.form.get("email")
        password = request.form.get("pwd")
        username = request.form.get("Username")
        check = insert_profile(first_name, last_name, username, user_mail, password)
        if check == 0 : 
            return "<script> alert('Username already exists!') </script>"
        elif check == 2 : 
            return "<script> alert('Email id already registered!') </script>"
        session['username'] = username
        return redirect(url_for('welcome_user'))
    return render_template('login.html')

@app.route('/login.html/login', methods = ['GET', 'POST'])
def user_login():
    if request.method == "POST":
        username = request.form.get("login_username")
        user_pwd = request.form.get("login_pwd")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        check=cursor.execute('SELECT password FROM profile WHERE username = (% s) ', (username,))
        report=tuple(cursor.fetchall())

        if (report == ()):
            return "<script> alert('Unauthorized User') </script>"
        elif (user_pwd!=report[0]['password']) : 
            return "<script> alert('Incorrect Login ID or Password!') </script>"
        else :
            session['username'] = username
            print(session['username'],"tfyguhgfhjhk")
            return redirect(url_for('welcome_user'))
    return render_template("login.html")

@app.route('/landing_page.html', methods = ['GET', 'POST'])
def welcome_user():
    print(session.get('username'), 11111111111111111111111111111111111111111111111111111)
    return render_template("landing_page.html")

@app.route('/chatbox.html')
def sessions():
    user_id2 = request.args.get('user_id2')
    print(user_id2)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('USE chat;')
    user_id = session.get('username')
    print(user_id,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
    cursor.execute('select * from {} where user_id="{}";'.format(user_id,user_id2))
    report=tuple(cursor.fetchall())
    # print(report)
    # for chat in report:
    #     sender_id = chat['sender_id']
    #     if (sender_id == user_id): direction = "right"
    #     else : direction = "left"
    cursor.execute('USE user;')
    cursor.close()
    return render_template("chat.html", report = report, user_id2=user_id2, user_id=user_id)


# @socketio.on('message')
# def handle_message(message):
#     user_id = session.get('username')
#     print(user_id,"hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
#     now=datetime.datetime.now()
#     date,time=now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
#     print(date,time)
#     send(message, broadcast=True)
#     insert_chat(user_id,seller_id,user_id,message,date,time)

@app.route("/chatbox.html", methods = ['GET', 'POST'])
def handle_message():
    if request.method == "POST" : 
        user_id2 = request.args.get('user_id2')
        print(user_id2,"gfkjlhgjfcvghmbjhgvhjkggggggggggggggggggggggggggggggggggggg")
        user_id = session.get('username')
        message = request.form.get("message")
        now=datetime.datetime.now()
        date,time=now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
        insert_chat(user_id,user_id2,user_id, message,date,time)
        return render_template("chat.html")
    else: return render_template("chat.html")


@app.route('/chats.html')
def select_chat():
    user_id = session.get('username')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('USE chat;')
    cursor.execute('select distinct user_id from {}'.format(user_id))
    report=cursor.fetchall()
    return render_template("chat_app.html",report = report)

if __name__ == "__main__":
    app.run(debug = True)