import hashlib
from time import strptime, sleep
from .db import DB
from datetime import datetime
from dateutil import tz
from .types import UserClass
DB_FILE = r"/home/akanksha/flask/app/pythonsqlite.db"
db = DB(DB_FILE)


def convert_datetime(details):
	m = {
        '01':'jan',
        '02':'feb',
        '03':'mar',
        '04':'apr',
        '05':'may',
        '06':'jun',
        '07':'jul',
        '08':'aug',
        '09':'sep',
        '10':'oct',
        '11':'nov',
        '12':'dec'
        }
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('Asia/kolkata')
	arr = []
	for i, detail in enumerate(details):
		arr.append(list(detail))
		utc = datetime.strptime(detail[0], '%Y-%m-%d %H:%M:%S')
		utc = utc.replace(tzinfo = from_zone)
		central = utc.astimezone(to_zone)
		x = utc.astimezone(to_zone)
		central = str(central)
		arr[i][0] = central[8:10]+' '+ m[central[5:7]] + ' ' + central[0:4] + ' ' + x.strftime("%I: %M %p")
	return arr



def make_hash(string):
	return hashlib.sha1(string.encode('utf-8')).hexdigest()


def check_db(user_id):
	db_check = db.get_userinfo(user_id)
	if db_check is None:
		return None
	UserObject = UserClass(user_id, db_check[1], active = True)
	return UserObject
