from flask_login import login_required, LoginManager, UserMixin
class UserClass(UserMixin):
	def  __init__(self, id_, name, active = True):
		self.id = id_
		self.name = name
		self.active = active
	
	def is_active(self):
		return self.active

	def get_id(self):
		return self.id

	def get_name(self):
		return self.name

