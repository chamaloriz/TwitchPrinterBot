from escpos.printer import Serial
from twitchio.ext import commands
from tinydb import TinyDB, Query
import asyncio
import time
import json

db = TinyDB('twitch_users.json')
users = db.table('users')
admins = db.table('admins')
oauthkey = db.table('oauthkey')

simple_printer = Serial(devfile='/dev/cu.BlueToothPrinter-SPPsla',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True)

sticky_printer = Serial(devfile='/dev/cu.BlueToothPrinter-SPPsla-1',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True)

def checkIfGoodColor(color):
	try:
		color = int(color)
		if(type(color) == int and color <= 255 and color >= 0):
			return True
		else:
			return False
	except:
		return False

def ChangeColor(uid, r, g, b):
	User = Query()
	users.update({'color': {"r":r,"g":g,"b":b} }, User.id == uid)

def ResetActivity(uid):
	User = Query()
	users.update({'activity': 100 }, User.id == uid)

def DeductPrint(uid):
	User = Query()
	prints_left = users.search(User.id == uid)[0]["prints_left"]
	prints_left -= 1
	users.update({'prints_left': prints_left }, User.id == uid)

def PrintMessage(name,message=None, sticky=False):
	if(not sticky):
		simple_printer.charcode(code='AUTO')
		simple_printer.set(custom_size=True, width=2, height=2, invert=True, smooth=True)
		simple_printer.text(f"{name}\n")
		simple_printer.set(custom_size=False, font="b", width=2, height=2, invert=False)
		simple_printer.text(message + "\n\n\n\n\n")
	else:
		sticky_printer.charcode(code='AUTO')
		sticky_printer.set(custom_size=True, width=2, height=2, invert=True, smooth=True)
		sticky_printer.text(f"{name}\n")
		sticky_printer.set(custom_size=False, font="b", width=2, height=2, invert=True)
		sticky_printer.text("Welcome to the stream !!!" + "\n\n\n\n\n")

def CheckOrAddUser(uid,username):
	User = Query()
	found_users = users.search(User.id == uid)

	if(uid == 0):
		return {"new_user":False, "prints_left":0}

	ResetActivity(uid)

	if(len(found_users) != 0):
		return {"uid":uid, "color":found_users[0]['color'], "new_user":False, "prints_left":found_users[0]['prints_left'], "printed_total":found_users[0]['printed_total']}
	else:
		print(f"Creating User | {username}")
		users.insert({
			'username': username,
			'id': uid,
			'printed_total': 0,
			'prints_left': 5,
			'color': {"r":100,"g":65,"b":165},
			'activity': 0,
		})
		return {"uid":uid, "color":{"r":100,"g":65,"b":165}, "new_user":True, "prints_left":2, "printed_total":0}

def CheckIfAdmin(uid):
	User = Query()
	found_admins = admins.search(User.id == uid)
	if(len(found_admins) != 0):
		return True
	else:
		return False

def AddToTotal(uid):
	User = Query()
	printed_total = users.search(User.id == uid)[0]["printed_total"]
	printed_total += 1
	users.update({'printed_total': printed_total }, User.id == uid)

def DeductPrint(uid):
	User = Query()
	prints_left = users.search(User.id == uid)[0]["prints_left"]
	prints_left -= 1
	users.update({'prints_left': prints_left }, User.id == uid)

def AddPrintsToUser(username, print_quantity):
	User = Query()
	prints_left = users.search(User.username == username)[0]["prints_left"]
	prints_left += int(print_quantity)
	users.update({'prints_left': prints_left }, User.username == username)
	print(f"Refill | {username} has {prints_left}")

class Bot(commands.Bot):

	def __init__(self):
		super().__init__(
			irc_token=oauthkey.all()[0]["key"],
			client_id='chamaloriz',
			nick='chamaloriz',
			prefix='!',
			initial_channels=['chamaloriz']
		)

	async def event_command_error(self, ctx, error):
		pass

	async def event_ready(self):
		print(f'Ready | {self.nick}')

	async def event_message(self, message):
		status = CheckOrAddUser(message.author.id, message.author.name)
		if(status["new_user"] == True):
			print(f"NewUser message | {message.author.name} joined the chat")
			PrintMessage(message.author.name,sticky=True)
		await self.handle_commands(message)

	@commands.command(name='print')
	async def print(self, ctx):
		message = ctx.message.content[7:]
		user = CheckOrAddUser(ctx.author.id, ctx.author.name)

		if(user["prints_left"] != 0):
			if(len(message) < 100):
				prints_left = user["prints_left"] - 1
				print(f"Printing | {len(message)} char message from {ctx.author.name}")
				if(message == ""):
					await ctx.send(f"{ctx.author.name} you need to add a text to print after the command (!print bla bla)")
				else: 
					DeductPrint(ctx.author.id)
					AddToTotal(ctx.author.id)
					PrintMessage(ctx.author.name, message)
					await ctx.send(f"{ctx.author.name} I'll print that ! you have {prints_left} left")
			else:
				await ctx.send(f"{ctx.author.name} you can only print 100 chars")
		else:
			await ctx.send(f"{ctx.author.name} you can't print anymore wait for a refill :p")

	@commands.command(name='refill')
	async def refill(self, ctx):
		if(CheckIfAdmin(ctx.author.id)):
			data = ctx.message.content[8:].split(' ')
			user = data[0]
			amount = data[1]
			AddPrintsToUser(user, amount)
		else:
			print(f"Not Admin {ctx.author.name} : {ctx.author.id}")

	@commands.command(name='color')
	async def changeColor(self, ctx):
		data = ctx.message.content[7:].split(' ')
		r = data[0]
		g = data[1]
		b = data[2]
		if(checkIfGoodColor(r) and checkIfGoodColor(g) and checkIfGoodColor(b)):
			if(ctx.author.id != 0):
				print(f"Changing Color | to {r}/{g}/{b} for {ctx.author.name}")
				await ctx.send(f"{ctx.author.name} I'll do that for sure !")
				ChangeColor(uid=ctx.author.id, r=r, g=g, b=b)
		else:
			await ctx.send(f"{ctx.author.name} you can't change to that it should be in this format !color 255 255 255 each color can be from 0 to 255")

	@commands.command(name='test')
	async def test(self, ctx):
		if(CheckIfAdmin(ctx.author.id)):
			PrintMessage(ctx.author.name,sticky=True)
		else:
			print(f"Not Admin {ctx.author.name} : {ctx.author.id}")

	@commands.command(name='help')
	async def help(self, ctx):
		await ctx.send(f"{ctx.author.name} you can !print to show your message on the printer")

bot = Bot()
bot.run()