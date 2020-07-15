import sys
from tinydb import TinyDB, Query

db = TinyDB('twitch_users.json')
admins = db.table('admins')

uid = sys.argv[1]

admins.insert({"id":int(uid)})

