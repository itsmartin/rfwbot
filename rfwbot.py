#!/usr/bin/env python3
import discord, configparser, random, re, requests

class InvalidDieException(Exception):
	def __init__(self, die):
		self.die = die
	def __str__(self):
		return "Invalid die description: " + self.die


class DiscordBot:
	def __init__(self, configFile):
		self._loadConfig(configFile)
		self.cReload()

	def _loadConfig(self, configFile):
		self.config = configparser.ConfigParser()
		self.config.read(configFile)
		self.commandString = self.config.get(
			'settings', 'commandString', fallback='!'
		)
        
	def cReload(self):
		self.loadCommands()
		self.loadChannels()
		self.loadAdmins()
		self.loadIgnore()
        
        
	def loadCommands(self):
		self.commands = {}
		commandsFile = self.config.get(
			'files', 'commands', fallback='commands.txt'
		)

		f = open(commandsFile, 'r')

		commandGroup = ''
		
		for line in f:
			# Detect beginning of new commandGroup, "[[name]]"
			m = re.match('\[\[(.*)\]\]', line)
			if m:
				commandGroup = m.group(1)
				self.commands[commandGroup] = {}
				continue
			
			# If no current commandGroup is set, ignore this line
			if not commandGroup:
				continue
				
			(command, response) = line.split("\t", 1)
			if command in self.commands[commandGroup]:
				self.commands[commandGroup][command].append(response.strip())
				
			else:
				self.commands[commandGroup][command]=[response.strip()]
				
		f.close()


	def loadChannels(self):
		channelsFile = self.config.get(
			'files', 'channels', fallback='channels.txt'
		)
		f = open(channelsFile, 'r')
		
		self.commandGroups = {}
		
		for line in f:
			(channelId, commandGroups) = line.split("\t", 1)
			self.commandGroups[channelId] = commandGroups.strip().split(",")

		f.close()


	def loadAdmins(self):
		self.admins=[]
		
		adminsFile = self.config.get(
			'files', 'admins', fallback='admins.txt'
		)
		f = open(adminsFile, 'r')
		
		for line in f:
			id = line.strip()
			if id != '': self.admins.append(id)
			
		
		f.close()
	
	def loadIgnore(self):
		self.ignore=[]
		
		ignoreFile = self.config.get(
			'files', 'ignore', fallback='ignore.txt'
		)
		f = open(ignoreFile, 'r')
		
		for line in f:
			id = line.strip()
			if id != '': self.ignore.append(id)
			
		
		f.close()

	def handleLogin(self, user):
		print('Logged in as {}'.format(user.name))
		self.user = user


	def connect(self):
		self.client = discord.Client()
		self.client.login(
			self.config['authentication']['username'],
			self.config['authentication']['password']
		)
		return self.client


	def isAdmin(self, user):
		return user.id in self.admins


	def isIgnored(self, user):
		return (user.id in self.ignore or user == self.user)
		

	def say(self, channel, message):
		self.client.send_message(channel, message)


	def handleCommand(self, channel, message, sender):
		# Are we listening in this channel?
		if channel.id not in self.commandGroups:
			return
		
		# Get the list of commandGroups for this channel
		commandGroups = self.commandGroups[channel.id]
		
		# Working backwards from the end of the string, remove
		# words until a command is found
		cmd = message.strip()
		params = ''
		response = False
		while True:
			rawResponse = self.getRawCommandResponse(commandGroups, cmd.strip(), params.strip())
			if rawResponse != False:
				break
			
			spl = cmd.rsplit(' ',1)
			if len(spl) == 1: 
				break
			cmd = spl[0]
			params = spl[1] + ' ' + params

		if rawResponse != False:
			self.processCommandResponse(channel, rawResponse, sender, params.strip())
		

	def getRawCommandResponse(self, commandGroups, cmd, params):
		# Single-spacify the command
		cmd = ' '.join(cmd.split()).lower()
		
		# Iterate over all commandGroups for the current channel
		for g in commandGroups:
			if g in self.commands:
				if cmd in self.commands[g] and params == '':
					# Exact command match with no params
					return random.choice(self.commands[g][cmd])
				
				elif (cmd + ' *') in self.commands[g] and params != '':
					return random.choice(self.commands[g][cmd + ' *'])

		# We got to here with no result, so there is no matching command
		return False


	def processCommandResponse(self, channel, response, sender, params):
		if "%LIST%" in response:
			# Need to get a list of subkeys. Out of scope right now.
			response = response.replace(
				"%LIST%", "This function is not yet implemented"
			)
		
		if "%SENDER%" in response:
			response = response.replace("%SENDER%", sender.name)
			
		if "%INPUT%" in response:
			response = response.replace("%INPUT%", params)
		
		if "%CHOICE%" in response:
			response = response.replace(
				"%CHOICE%",
				random.choice(params.split(',')).strip()
			)
		
		if "%ROLL%" in response:
			try:
				response = response.replace(
					"%ROLL%",
					self.diceRoll(params)
				)
			except InvalidDieException as e:
				response = str(e)

		if "%XKCD%" in response:
			response = response.replace("%XKCD%", self.getXkcd(params))

		if "%RANDOM_XKCD%" in response:
			response = response.replace("%RANDOM_XKCD%", self.getRandomXkcd())


		self.say(channel, response)


	def diceRoll(self, dice):
		dice = dice.split()
		rolls = []
		for die in dice:
			dieDef = die.lower().split('d')
			if len(dieDef) != 2:
				raise InvalidDieException(die)
			try:
				if dieDef[0] == '':
					number = 1
				else:
					number = int(dieDef[0])

				sides = int(dieDef[1])
			except ValueError:
				raise InvalidDieException(die)
			
			if number > 20 or number < 1 or sides > 1000 or sides < 1:
				raise InvalidDieException(die)

			for i in range(number):
				rolls.append(random.randint(1,sides))

		return " + ".join(str(n) for n in rolls) + (" = " + str(sum(rolls)) if len(rolls) > 1 else '')


	def getXkcd(self,number):
		try:
			r = requests.get("http://xkcd.com/{}/info.0.json".format(number))
		except:
			return "Sorry, I couldn't reach XKCD"

		try:
			title = r.json()['safe_title']
		except:
			return("Comic {} not found".format(number))

		return("http://xkcd.com/{} (\"{}\")".format(number, title))


	def getRandomXkcd(self):
		try:
			r = requests.get("http://xkcd.com/info.0.json")
			latest = r.json()['num']
		except:
			return "Sorry, I couldn't reach XKCD"

		return self.getXkcd(random.randint(1, latest))

		
	def handleSystemCommand(self, channel, message, sender):
		if not channel.is_private: return
		
		(cmd, params) = (message.strip() + ' ').split(' ', 1)
		cmd = cmd.lower()
		
		# General commands

		if cmd == 'whoami':
			self.say(channel, 'Your name is {} and your id is {}'
				.format(sender.name, sender.id))

		# Admin commands
		
		if not self.isAdmin(sender): return

		if cmd == 'reload':
			self.cReload()
			self.say(channel, 'Reloaded!')
		if cmd == 'stop':
			self.say(channel, 'Shutting down.')
			self.client.logout()
		if cmd == 'channels':
			r = ''
			for s in self.client.servers:
				r += "Server: {}\n".format(s.name)
				for c in s.channels:
					r += "-- {} [{}] (id: {})\n".format(
						c.name, c.type, c.id
					)
					if c.id in self.commandGroups:
						r += "---- In groups: {}\n".format(
							', '.join(self.commandGroups[c.id])
						)
					else:
						r += "---- (Channel not monitored)\n"
			self.say(channel, r)
		


rfwbot = DiscordBot('config/rfwbot.conf')
client = rfwbot.connect();

@client.event
def on_message(message):
	if not rfwbot.isIgnored(message.author):
		if message.content.startswith(rfwbot.commandString):
			command = message.content[len(rfwbot.commandString):]
			if command.startswith(rfwbot.commandString):
				# System commands start with !!
				command = command[len(rfwbot.commandString):]
				rfwbot.handleSystemCommand(message.channel, command, message.author)
			else:
				rfwbot.handleCommand(message.channel, command, message.author)

@client.event
def on_ready():
	rfwbot.handleLogin(client.user)



client.run()
