from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
from flask_jsglue import JSGlue
from functools import wraps, update_wrapper
import hashlib
from .utils import make_hash, check_db, convert_datetime
from .db import DB
import json
import flask
from .types import UserClass

DB_FILE = r"/home/akanksha/flask/app/pythonsqlite.db"
db = DB(DB_FILE)
login_manager = LoginManager()
app = Flask(__name__)
fujs = JSGlue(app)
login_manager.init_app(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@login_manager.user_loader
def load_user(user_id):
	return check_db(user_id)


def my_decorator():
	def decorator(function):
		def wrapper(*args, **kwargs):
			print("hello", function, kwargs)
			if kwargs['name'] != current_user.get_name():
				flask.abort(400)
			return function(*args, **kwargs)
		return update_wrapper(wrapper, function)
	return decorator




@app.route('/')
def my_blog():
	return render_template('home.html')


@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		data = db.valid_login(request.form['email'], make_hash(request.form['password']))
		username = None
		id_ = None
		if data != None:
			username = data[0]
			id_ = data[1]
		User = UserClass(id_, username, active = True)
		if username != None:
			login_user(User)
			return redirect(url_for('profile', name = username))
		else:
			error = 'Invalid Email/Password , Please try again.'
	return render_template('login.html', error = error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	error = None
	if request.method == 'POST':
		if request.form['password'] != request.form['confirmPassword']:
			error = "Passwords doesn't match."
		else:
			x = db.add_user((request.form['username'], request.form['email'], make_hash(request.form['password'])))
			if x == -1:
				error = "Email/Username already registered. Try using another username/email."
			else:
				flask.flash("Account created succesfully.")
				return redirect(url_for('index'))
	return render_template('signup.html', error = error)


@app.route('/index')
def index():
	return render_template('index.html')


@app.route('/profile/<name>', methods=['GET', 'POST'])
@login_required
@my_decorator()
def profile(name):
	details = db.get_allblogs()
	details = convert_datetime(details)
	return render_template('profile.html', name = name, details = details, current_user = current_user.get_name())


@app.route('/profile/<name>/myblogs', methods=['GET', 'POST'])
@login_required
def myblogs(name):
	if request.method == 'POST':	
		if len(request.json) == 2:
			db.update_blog(request.json['id'], request.json['claps'])
			return jsonify("changes saved.")
		elif len(request.json) == 1 and 'id' in request.json:
			db.delete_blog((current_user.id, request.json['id']))
			return jsonify("Blog deleted.")
		else:
			if request.json['follows'] == 1:
				db.add_follower(current_user.get_name(), current_user.id, name)
				return jsonify("starting following.")
			else:
				db.remove_following(current_user.id, current_user.get_name(), name)
				return jsonify("unfollowed.")
	x = 0
	if current_user.name != name:
		result = db.is_following(current_user.id, name)
		print("result is", result)
		if len(result) != 0:
			x = 1
	details = db.get_blogs(name)
	details = convert_datetime(details)
	return render_template('blogs.html', details = details, name = name, current_user = current_user.get_name(), result = x)


@app.route('/profile/<name>/settings', methods=['GET', 'POST'])
@login_required
@my_decorator()
def settings(name):
	if request.method == 'POST':
		if db.get_password_by_name(name) != make_hash(request.form['old_password']):
			flask.flash('old password doesnt match.', category ='danger')
		elif request.form['new_password'] != request.form['confirm_password']:
			flask.flash('new password and confirmPassword doesnt match.',category ='danger')
		else:
			db.update_password(name, make_hash(request.form['new_password']))
			flask.flash('Password changed', category='success')
	followers = db.get_followers(current_user.id)
	followings = db.get_followings(current_user.id)
	email = db.get_email_by_username(name)
	print(email)
	return render_template('settings.html', name = name , followers = followers, followings = followings, email = email)


@app.route("/logout")
@login_required
def logout():
	obj = current_user
	logout_user()
	obj.active = False
	return redirect ('/login')


@app.route("/profile/<name>/search/<pattern>", methods=['GET', 'POST'])
@login_required
@my_decorator()
def search(name, pattern):
	profiles = db.get_names(pattern)
	return render_template('helper.html',users=profiles, name=name, val = pattern)

@app.route("/profile/<name>/create-blog", methods=['GET', 'POST'])
@login_required
@my_decorator()
def createBlog(name):
	if request.method == 'POST':
		if request.form:
			index = db.add_blog(name, request.form['title'], request.form['body'])
			print("came here.")
			flask.flash("blogs posted")
			return redirect(url_for('blog', name = name, id = index))
	return render_template('createBlog.html', name=name)

@app.route("/profile/<name>/blog/<id>", methods=['GET','POST'])
@login_required
def blog(name, id):
	print("hello g")
	detail = db.get_blog_by_id(id)
	print(detail)
	return render_template('specific_blog.html', name=name, id = id, details = detail, current_user = current_user.get_name())



if __name__ == '__main__':
	app.run()



