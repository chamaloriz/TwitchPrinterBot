from escpos.printer import Serial
from twitchio.ext import commands
from tinydb import TinyDB, Query

db = TinyDB('twitch_users.json')
users = db.table('users')
admins = db.table('admins')

p = Serial(devfile='/dev/cu.BlueToothPrinter-SPPsla',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True)

def PrintMessage(name,message="welcome to the stream"):
	p.charcode(code='WEST_EUROPE')
	p.set(width=2, height=2, invert=True)
	p.text(f"{name}\n\n")
	p.set(width=1, height=1, invert=False)
	p.text(message)
	p.cut()

def CheckOrAddUser(uid,username):
	User = Query()
	found_users = users.search(User.id == uid)

	if(uid == 0):
		return {"new_user":False, "prints_left":0}

	if(len(found_users) != 0):
		return {"new_user":False, "prints_left":found_users[0]['prints_left']}
	else:
		print(f"Creating User | {username}")
		users.insert({
			'username': username,
			'id': uid,
			'printed_total': 0,
			'prints_left': 2,
		})
		return {"new_user":True, "prints_left":2}

def CheckIfAdmin(uid):
	User = Query()
	found_admins = admins.search(User.id == uid)
	if(len(found_admins) != 0):
		return True
	else:
		return False

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
			irc_token='oauth:ryv23uregfmhvw7t883mvi9ebz1f6g',
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
			PrintMessage(message.author.name)
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
					PrintMessage(ctx.author.name, message)
					await ctx.send(f"{ctx.author.name} I'll print that ! you have {prints_left} left")
			else:
				await ctx.send(f"{ctx.author.name} you can only print 250 chars")
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

	@commands.command(name='help')
	async def help(self, ctx):
		await ctx.send(f"{ctx.author.name} you can !print to show your message on the printer")

bot = Bot()
bot.run()