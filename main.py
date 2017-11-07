from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import random, datetime, time



app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mugnovel:mugnovel@localhost:8889/mugnovel'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = "#someSecretString"


#classes for user and posts

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(120), unique = True)
	f_name = db.Column(db.String(120))
	l_name = db.Column(db.String(120))
	pw_hash = db.Column(db.String(120))
	posts = db.relationship("Posts", backref = "owner")

	def __init__(self, email, f_name, l_name, password):
		self.email = email
		self.f_name = f_name
		self.l_name = l_name
		self.pw_hash = make_pw_hash(password)


class Posts(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	message = db.Column(db.String(99999))
	time = db.Column(db.String(100))
	owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

	def __init__(self, message, time, owner):
		self.message = message
		self.time = time
		self.owner = owner


def getAllPosts():
	return Posts.query.all()

def getAllUsers():
	return User.query.all()


#before request actions

@app.before_request
def require_login():
	allowed_routes = ["logon", "signup"]
	if request.endpoint not in allowed_routes and "email" not in session:
		return redirect("/logon")



#logon page handler

@app.route("/logon", methods=["POST", "GET"])
def logon():
	if request.method == "POST":
		email = request.form["email"]
		password = request.form["password"]
		user = User.query.filter_by(email=email).first()

		email_ph = ""
		password_ph = ""

		if user and check_pw_hash(password, user.pw_hash):
			session["email"] = email
			return redirect("/")

		if email == "":
			email_ph = "Please enter a username"


		elif not user:
			email = ""
			email_ph = "Username does not exist"


		if password == "":
			password_ph = "Please enter a password"

		return render_template("logon.html", email=email, email_ph=email_ph, password="", password_ph=password_ph)

	return render_template("logon.html", email="", email_ph="Email", password="", password_ph="Password")



# signup page handlers


@app.route("/signup", methods=["POST", "GET"])
def signup():
	if request.method == "POST":
		f_name = request.form["f_name"]
		l_name = request.form["l_name"]
		email = request.form["email"]
		password = request.form["password"]
		v_password = request.form["v_password"]
		user = User.query.filter_by(email=email).first()

		f_name_ph = ""
		l_name_ph = ""
		email_ph = ""
		password_ph = ""
		v_password_ph = ""

		if f_name == "":
			f_name_ph = "Please enter your first name"

		if l_name == "":
			l_name_ph = "Please enter your last name"

		if email == "":
			email = ""
			email_ph = "Please enter an email"

		elif user:
			email = ""
			email_ph = "Username taken"

		elif "@" not in email and "." not in email:
			email = ""
			email_ph = "Please enter a valid email"

		if password == "":
			password = ""
			password_ph = "Please enter a password"

		if v_password == "":
			v_password = ""
			v_password_ph = "Verify password"

		if password != v_password:
			password = ""
			v_password = ""
			password_ph = "Enter password again"
			v_password_ph = "Verify password"

		if not user and len(password) > 1 and password == v_password:
			new_user = User(email, f_name, l_name, password)
			db.session.add(new_user)
			db.session.commit()
			session["email"] = email

			return redirect("/")

		return render_template("signup.html", f_name=f_name, f_name_ph=f_name_ph, l_name=l_name, l_name_ph=l_name_ph, email=email, email_ph=email_ph, password=password, password_ph=password_ph, v_password=v_password, v_password_ph=v_password_ph)

	return render_template("signup.html", f_name="", f_name_ph="First name",l_name="", l_name_ph="Last name", email="", email_ph="Email", password="", password_ph="Password", v_password="", v_password_ph="Verify password")


#log out page handler

@app.route("/logout")
def logout():
	del session["email"]
	return redirect("/logon")


#home page handler

@app.route("/", methods=["POST", "GET"])
def index():
	name = User.query.filter_by(email=session["email"]).first()
	name = name.f_name
	quote = ["Let us know how you're doing today.", "How are you doing today?", "What do you have on your mind?", "Do squirrels feel joy?", "It's a beautiful day, isn't it?", "Do you really believe the Zodiac killer is dead?"]

	if request.method == "POST":
		message = request.form["message"]

		owner = User.query.filter_by(email=session["email"]).first()
		if message == "":
			return redirect("/")

		time = datetime.datetime.now().strftime("%B %#d, %Y, %#I:%M")
		def amOrPm():
			hour = datetime.datetime.now().strftime("%H")
			hour = int(hour)
			if hour > 11:
				return "p.m."
			return "a.m."

		time = time + " " + amOrPm()
		entry = Posts(message, time, owner)
		db.session.add(entry)
		db.session.commit()
		return redirect("/")


	return render_template("home.html", name = name, quote = random.choice(quote), messages = reversed(getAllPosts()), users = getAllUsers())

if __name__ == "__main__":
	app.run()
