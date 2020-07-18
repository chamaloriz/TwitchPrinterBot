from tinydb import TinyDB, Query
import asyncio
import serial
import time
import json
import numpy

db = TinyDB('twitch_users.json')
users = db.table('users')

led_wall = serial.Serial("/dev/cu.usbmodem14101", baudrate=115200)

async def ColorFrameUpdater():
	while True:
		#time.sleep(0)
		User = Query()
		data_to_send = []
		active_users = users.search(User["activity"] > 0)
		print(f"LED wall | il y a {len(active_users)} utilisateurs actifs")
		for user in active_users:
			# remove 1 activity point
			print(f"         | {user['username']}")
			user_activity = users.search(User.id == user["id"])[0]["activity"]
			user_activity -= 1
			users.update({'activity': user_activity }, User.id == user["id"])
	
			data = {"color":user["color"],"activity":user["activity"]}
			data_to_send.append(data)
	
		#chuck an array into arrays of max 5
		chuncked_data = numpy.array_split(numpy.array(data_to_send),10)
		position = 0
	
		for data in chuncked_data:
			time.sleep(2)
	
			status = ""
			if(position == 0):
				status = "start"
	
			if(position + len(data) == len(data_to_send)):
				status = "end"
	
			current_data = {"position":position,"data":data.tolist(),"status":status}
			position += len(data)
			encoded_data = json.dumps(current_data).encode()
			led_wall.write(encoded_data)
		
asyncio.run(ColorFrameUpdater())
