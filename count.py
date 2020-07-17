from tinydb import TinyDB, Query

db = TinyDB('twitch_users.json')
users = db.table('users')

print(len(users.all()))