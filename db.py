import sqlite3
from sqlite3 import Error
import datetime
import time

sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
									id integer PRIMARY KEY,
									username text NOT NULL,
									email text NOT NULL,
									password text NOT NULL
	);"""


sql_create_blogs_table = """CREATE TABLE IF NOT EXISTS blogs (
									id integer PRIMARY KEY,
									title text NOT NULL,
									body text NOT NULL,
									user_id integer NOT NULL,
									claps integer DEFAULT 0,
									created_at text DEFAULT CURRENT_TIMESTAMP,
									FOREIGN KEY (user_id) REFERENCES users (id)
									ON DELETE CASCADE
								);"""

sql_create_followers_table = """CREATE TABLE IF NOT EXISTS followers (
									id integer PRIMARY KEY,
									follower_name text NOT NULL,
									user_id integer NOT NULL,
									FOREIGN KEY (user_id) REFERENCES users (id)
									ON DELETE CASCADE
);"""

sql_create_followings_table = """CREATE TABLE IF NOT EXISTS followings (
									id integer PRIMARY KEY,
									following_name text NOT NULL,
									user_id integer NOT NULL,
									FOREIGN KEY (user_id) REFERENCES users (id)
									ON DELETE CASCADE
);"""


class DB:


	def get_email_by_username(self, name):
		cur = self.conn.cursor()
		cur.execute("SELECT email FROM users WHERE username=?",(name,))
		rows = cur.fetchall()
		return rows[0][0]


	def get_followers(self, id):
		cur = self.conn.cursor()
		cur.execute("SELECT follower_name FROM followers WHERE user_id=?",(id,))
		rows = cur.fetchall()
		print(rows)
		return rows

	def get_followings(self, id):
		cur = self.conn.cursor()
		cur.execute("SELECT following_name FROM followings WHERE user_id==?",(id,))
		rows = cur.fetchall()
		print(rows)
		return rows


	def get_names(self, pattern):
		start = time.perf_counter()
		cur = self.conn.cursor()
		search = '%' + pattern + '%'
		cur.execute("SELECT username FROM users WHERE username LIKE ?",(search,))
		rows = cur.fetchall()
		print('time took to match:', time.perf_counter() - start)
		return rows

	def get_password_by_name(self, name):
		cur = self.conn.cursor()
		cur.execute("SELECT password FROM users WHERE username=?",(name,))
		rows = cur.fetchall()
		print(rows)
		return rows[0][0]

	def get_allblogs(self):
		cur = self.conn.cursor()
		cur.execute("SELECT created_at, title, body, claps, blogs.id, users.username FROM blogs, users WHERE blogs.user_id = users.id ORDER BY created_at DESC")
		rows = cur.fetchall()
		return rows

	def get_blog_by_id(self, id_):
		cur = self.conn.cursor()
		cur.execute("SELECT created_at, title, body, claps, blogs.id, users.username FROM blogs, users WHERE blogs.user_id = users.id AND blogs.id=?",(id_,))
		rows = cur.fetchall()
		print(rows)
		return rows

	def remove_follower(self, name, follower_name):
		cur = self.conn.cursor()
		sql = "SELECT id FROM users WHERE username=?"
		cur.execute(sql, (name,))
		rows = cur.fetchall()
		user_id = rows[0][0]
		sql = 'DELETE FROM followers WHERE user_id=? AND follower_name=?'
		cur = self.conn.cursor()
		cur.execute(sql, (user_id,follower_name))
		self.conn.commit()

	def remove_following(self, user_id, follower_name, following_name):
		sql = 'DELETE FROM followings WHERE user_id=? AND following_name=?'
		cur = self.conn.cursor()
		cur.execute(sql, (user_id, following_name))
		self.conn.commit()
		self.remove_follower(following_name, follower_name)
		
	def delete_user(self):
		sql = 'DELETE FROM users WHERE username=?'
		cur = self.conn.cursor()
		cur.execute(sql, ("akanksha1",))
		self.conn.commit()

	def delete_blog(self, details):
		sql = 'DELETE FROM blogs WHERE user_id=? AND id=?'
		cur = self.conn.cursor()
		cur.execute(sql, details)
		self.conn.commit()


	def get_userinfo(self, id):
		cur = self.conn.cursor()
		cur.execute("SELECT id, username FROM users WHERE id=?",(id,))
		rows = cur.fetchall()
		if len(rows) == 0:
			return None
		return rows[0]


	def get_blogs(self, username):
		cur = self.conn.cursor()
		cur.execute("SELECT id FROM users WHERE username=?",(username,))
		rows = cur.fetchall()
		row = rows[0][0]
		cur.execute("SELECT created_at, title, body, claps, id FROM blogs where blogs.user_id=? ORDER BY created_at DESC",(row,))
		rows = cur.fetchall()
		return rows



	def update_blog(self, id_, claps):
		sql = '''UPDATE blogs
				SET claps = ?
				WHERE id = ?
		'''
		blog = (claps, id_)
		cur = self.conn.cursor()
		cur.execute(sql, blog)
		self.conn.commit()

	def is_following(self, id, name):
		cur = self.conn.cursor()
		cur.execute("SELECT id FROM followings WHERE user_id=? AND following_name=?",(id, name))
		rows = cur.fetchall()
		print("rows are",rows)
		return rows

	def update_password(self, name, new_password):
		sql = '''UPDATE users
				SET password = ?
				WHERE username = ?
		'''
		info = (new_password, name)
		cur = self.conn.cursor()
		cur.execute(sql, info)
		self.conn.commit()
		print("updated")


	def add_blog(self, username, title, body):
		cur = self.conn.cursor()
		cur.execute("SELECT id FROM users WHERE username=?",(username,))
		rows = cur.fetchall()
		row = rows[0][0]
		sql = ''' INSERT INTO blogs(title, body, user_id)
						VALUES(?,?,?) '''
		blog = (title, body, row)
		cur.execute(sql, blog)
		self.conn.commit()
		return cur.lastrowid

	def add_follower(self, name, name_id, follows):
		cur = self.conn.cursor()
		cur.execute("SELECT id FROM users WHERE username=?",(follows,))
		rows = cur.fetchall()
		row = rows[0][0]
		print(row)
		sql = ''' INSERT INTO followers(follower_name, user_id)
						VALUES(?,?) '''
		print("in follower", name, row)
		info = (name, row)
		cur.execute(sql, info)
		self.conn.commit()
		print(self.add_following(follows, name_id))
		return cur.lastrowid

	def add_following(self, follows, name_id):
		print("in following", name_id, follows)
		cur = self.conn.cursor()
		sql = ''' INSERT INTO followings(following_name, user_id)
				VALUES(?,?)'''
		info = (follows, name_id)
		cur.execute(sql, info)
		self.conn.commit()
		return cur.lastrowid



	def user_exists(self, username, email):
		cur = self.conn.cursor()
		cur.execute("SELECT username FROM users WHERE username=? OR email=?",(username, email,))
		rows = cur.fetchall()
		if len(rows) == 0:
			return None
		return rows[0][0]

	def valid_login(self, email, password):
		cur = self.conn.cursor()
		cur.execute("SELECT username,id FROM users WHERE email=? AND password=?",(email, password,))
		rows = cur.fetchall()
		if len(rows) == 0:
			return None
		return rows[0]

	def add_user(self, user):
		if self.user_exists(user[0], user[1]) == None:
			sql = ''' INSERT INTO users(username, email, password)
						VALUES(?,?,?) '''
			c = self.conn.cursor()
			c.execute(sql, user)
			self.conn.commit()
			return c.lastrowid
		else:
			return -1

	def create_table(self, create_table):
		try:
			c = self.conn.cursor()
			c.execute(create_table)
		except Error as e:
			print(e)
		self.conn.commit()

	def __init__(self, db_file):
		self.conn = None
		try:
			self.conn = sqlite3.connect(db_file, check_same_thread=False)
			self.create_table(sql_create_users_table)
			self.create_table(sql_create_blogs_table)
			self.create_table(sql_create_followings_table)
			self.create_table(sql_create_followers_table)
		except Error as e:
			raise e
			print('err', e)

