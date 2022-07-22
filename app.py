from base64 import encode
from fileinput import filename
from webbrowser import get
from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import pytz
import os
import random
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from io import StringIO
import csv
import urllib.request


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PreGuest.db'
app.config['SECRET_KEY'] = os.urandom(24) #必ず必要

app.config [ 'DEBUG' ] = True
app.config [ 'MAIL_SERVER' ] = 'smtp.gmail.com' 
app.config [ 'MAIL_PORT' ] = 465
app.config [ 'MAIL_USERNAME' ] = 'j.ibwf.opuioh.opx.1415.2005@gmail.com'
app.config [ 'MAIL_PASSWORD' ] = 'xxhhcsqfxpjrazfy'
app.config [ 'MAIL_USE_TLS' ] = False
app.config [ 'MAIL_USE_SSL' ] = True
#app.config [ 'MAIL_DEBUG' ] = True
#app.config [ 'MAIL_DEFAULT_SENDER' ] = None
#app.config [ 'MAIL_MAX_EMAILS' ] = None
#app.config [ 'MAIL_SUPPRESS_SEND' ] = False
#app.config [ 'MAIL_ASCII_ATTACHEMENTS' ] = True

db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

class PreGuest(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_token = db.Column(db.String(24), unique=True,nullable=False)
    m_address = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    #status = db.Column(db.String(10), nullable=True)

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Lname_k = db.Column(db.String(10),nullable=True)
    Fname_k = db.Column(db.String(10),nullable=True)
    Lname_r = db.Column(db.String(30),nullable=False)
    Fname_r = db.Column(db.String(30),nullable=False)
    m_address = db.Column(db.String(100),nullable=False,unique=True)
    attendance = db.Column(db.String(10),nullable=False)
    gift_money = db.Column(db.Integer, nullable=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET"])
def top():
    return render_template('top.html')

@app.route("/create", methods=["GET","POST"])
def create():
    return render_template('create.html')

@app.route("/create_check", methods=["GET","POST"])
def create_check():
    if request.method =='POST':
        mail_address = request.form.get('m_address')
        return render_template('create_check.html', mail_address=mail_address)
    else:
        return render_template('create.html')

@app.route("/create_done", methods=["GET","POST"])
def create_done():
    if request.method == 'POST':
        token = generate_token(24)
        mail_address = request.form.get('m_address')
        msg = Message("仮登録ありがとうございます。", sender="j.ibwf.opuioh.opx.1415.2005@google.com", recipients=[mail_address])
        #msg.body = "testing"
        #msg.html = "<b>testing</b>"
        msg.body = "この度は**家・**家の結婚式出欠入力フォームにご登録いただきありがとうございます。\r\n下記のURLから出欠情報をご入力下さい。\r\nよろしくお願いいたします。\r\nhttp://127.0.0.1:5000/{}/form".format(token)  
        mail.send(msg)

        post = PreGuest(m_address=mail_address,url_token=token)
        db.session.add(post)
        db.session.commit()
        return render_template('create_done.html')
    else:    
        return render_template('create.html')

#仮登録用のtoken作成
def generate_token(length):
    approvals = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvbwxyz'
    applen = len(approvals)
    token = ''
    for i in range(length):
        r = random.randrange(applen)
        token = token + approvals[r]
    return token

#url_token付きのURLからform.htmlへのルーティング
@app.route("/<url_token>/form",methods=["GET","POST"])
def form(url_token):
    token = PreGuest.query.get(url_token)
    if request.method == 'GET':
        return render_template('form.html')
    else:
        return render_template('top.html')

@app.route("/<url_token>/form_check",methods=["GET","POST"])
def form_check(url_token):
    token = PreGuest.query.get(url_token)
    if request.method =='POST':
        Lname_k = request.form.get('Lname_k')
        Fname_k = request.form.get('Fname_k')
        Lname_r = request.form.get('Lname_r')
        Fname_r = request.form.get('Fname_r')
        m_address = request.form.get('m_address')
        attendance = request.form.get('attendance')
        return render_template('form_check.html', Lname_k=Lname_k, Fname_k=Fname_k,Lname_r=Lname_r, Fname_r=Fname_r,m_address=m_address,attendance=attendance)
    else:
        return render_template('create.html')
    

@app.route("/<url_token>/form_done",methods=["GET", "POST"])
def form_done(url_token):
    token = PreGuest.query.get(url_token)
    if request.method == 'POST':
        Lname_k = request.form.get('Lname_k')
        Fname_k = request.form.get('Fname_k')
        Lname_r = request.form.get('Lname_r')
        Fname_r = request.form.get('Fname_r')
        m_address = request.form.get('m_address')
        attendance = request.form.get('attendance')

        posts = Guest(Lname_k=Lname_k,Fname_k=Fname_k, Lname_r=Lname_r,Fname_r=Fname_r, m_address=m_address,attendance=attendance)
        db.session.add(posts)
        db.session.commit()
        return render_template('form_done.html')
    else:    
        return render_template('create.html')

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('owner-signup.html')


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first() #usernameがない場合の処理は後で追加する
        if check_password_hash(user.password, password):
            login_user(user) 
            return redirect('/list')
    else:
        return render_template('owner-top.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route("/list",methods=["GET","POST"])
@login_required
def list():
    if request.method == "GET":
        posts = Guest.query.all()
        return render_template('owner-list.html',posts=posts)    

@app.route("/<int:id>/edit",methods=["GET","POST"])
@login_required
def owner_edit(id):
    posts = Guest.query.get(id)
    if request.method == "GET":
        return render_template('owner-edit.html',posts=posts)
    else:
        posts.Lname_k = request.form.get('Lname_k')
        posts.Fname_k = request.form.get('Fname_k')
        posts.Lname_r = request.form.get('Lname_r')
        posts.Fname_r = request.form.get('Fname_r')
        posts.m_address = request.form.get('m_address')
        posts.attendance = request.form.get('attendance')
        posts.gift_money = request.form.get('gift_money')
        db.session.commit()
        return redirect('/list')

@app.route("/<int:id>/delete",methods=["GET"])
@login_required
def owner_delete(id):
    posts = Guest.query.get(id)

    db.session.delete(posts)
    db.session.commit()
    return redirect("/list")

@app.route('/export/<obj>')
def export(obj):

    f = StringIO()
    writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator="\n")

    if obj == 'Guest':
        writer.writerow([ "id","Lname_k","Fname_k","Lname_r","Fname_r","m_address","attendance","gift_money"])
        for u in Guest.query.all():
            writer.writerow([u.id, u.Lname_k, u.Fname_k, u.Lname_r, u.Fname_r, u.m_address, u.attendance, u.gift_money])
    
    res = make_response()
    res.data = f.getvalue()
    res.headers['Content-Type'] = 'text/csv'
    res.headers['Content-Disposition'] = 'attachment; filename='+ obj +'.csv'
    return res

if __name__ == "__main__":
    app.run(debug=True)