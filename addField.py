from tinydb import TinyDB, Query
#adds a field to all the db
db = TinyDB('twitch_users.json')
users = db.table('users')

User = Query()
users.update({'activity': 0 })