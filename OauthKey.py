import sys
from tinydb import TinyDB, Query

db = TinyDB('twitch_users.json')
oauthkey = db.table('oauthkey')

key = sys.argv[1]

oauthkey.insert({"key":key})

