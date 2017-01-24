#!/usr/bin/python
# coding: UTF-8
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// IMPORTS
import os,sys,re,time,socket,ircbot
from random import random,choice
from subprocess import check_output

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// DATA

GREETINGS = ['yo','salut','bonjour','hello','ola','salam alekoum','buon giorno']
SCHEDULE  = { "1212":"J'ai faim"}
QUOTES    = { "shake":" ♩ ᕕ(ᐛ)ᕗ  ♬ ♩ ." , "uptime":"bot.uptime" }
QUOTES_KEYS = QUOTES.keys()

# SYSTEM COMMAND TRIGGERS
TRIGGERS = { "define":"/home/duke/bin/define %s" }

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// FUNCTIONS

def cronJob(bot):
	if bot.uptime < 10: return
	bot.send('privmsg #laphysique :cronjob text example ^o^')
	bot.crontime = 3600
	bot.cronprob = 1
	#time.sleep(0.050)
	
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// GET METHOD

def recv(bot,nb=2048,input_delay=0):
	# WE CHECK TIME FOR SCHEDULED JOBS
	t = check_output('date "+%H:%M:%S"',shell=1).strip()
	# TRY TO READ FROM SOCKET
	try: msg = bot.socket.recv(nb)
	# EXCEPT FOR TIMEOUT
	except socket.timeout, e:
		err = e.args[0]
		if err == 'timed out':
			# GET STDIN INPUT HERE (ADJUST DELAY)
			time.sleep(input_delay)
			try:    inline = sys.stdin.readline().strip()
			except: inline = None
			if inline: bot.send(inline)
			return ""
		# FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
		else:
			print "%s bot stopped: %s"%(t,e)
			sys.exit(1)
	# FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
	except socket.error, e:
		print "%s bot stopped: %s"%(t,e)
		sys.exit(1)
	else:
		# BOT SHUTDOWN
		if len(msg) == 0:
			if bot.connected:
				print '%s %s orderly shutdown.'%(t,bot.nick)
				bot.connected = 0
			sys.exit(0)
		else:
			# AUTO RESPONSE TO ANY PING
			if msg.startswith('PING '):
				host = msg.split()[1]
				bot.send('PONG %s'%host,reason='PONG')
			else: print '\rrecv [%d bytes] %s'%(len(msg),re.sub('\n|\r','',msg))
			return msg

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// MAIN UPDATE

def update(bot,msg):
	if bot.connected:
		lines = msg.splitlines()
		# FOR EACH LINE IN MESSAGE
		for line in lines:
			line = line.strip()
			# WHAT DO WE HAVE
			CALL = re.findall(' *[A-Z]{4,8} *',line)
			CALL = CALL[0].strip() if CALL else CALL
			if not CALL: continue
			# GET USER/CHAN FROM OUTPUT
			user = line.split(CALL)[0][1:]
			user = re.sub('!.*','',user)
			chan = re.findall('#[^ ]+',line)
			if len(chan)>0: chan=chan[0]
			elif not chan and user: chan=user
			else: chan = ""
			# FOR A PRIVATE MESSAGE (EXCLUDING 'anotherbot')
			if CALL=='PRIVMSG' and user not in ['anotherbot']:
				msg = line.split(CALL)[1]
				if chan.count('#'): msg = line.split(chan+' :')[1]
				else: msg = line.split(bot.nick+' :')[1]
				# CUT MESSAGES THAT CONTAIN '|' OR '&' (SAFETY FOR EXECUTING SCRIPT)
				msg = re.sub('[|&].*','',msg)
				# AUTOMATED TRIGGERS
				for k,v in TRIGGERS.iteritems():
					if msg.startswith(k):
						arg = re.sub('%s *'%k,'',msg)
						cmd = TRIGGERS[k]%arg
						try:    ans=check_output(cmd,shell=1).strip()
						except: ans=None
						if ans:
							lines = ans.splitlines()
							output = []
							output = [x for x in lines if x not in output]
							if k=='define': output = output[:4]
							for line in output:
								bot.send('privmsg %s :%s'%(chan,line))
				# AUTOMATED MESSAGES
				if msg.count('music'):
					MUSIC = '♩ ♪ ♫ ♬ ♭'.split()
					song = ' '.join([choice(MUSIC) for i in range(5)])
					bot.send('privmsg %s :%s'%(chan,song))
				elif msg.count(bot.nick):
					if any([msg.lower().count(x) for x in GREETINGS]):
						x = choice(GREETINGS)+' %s'%user
					elif msg.count('?'):
						x = 'oui' if random()<0.5 else 'non'
					bot.send('privmsg %s :%s'%(chan,x))
				elif any([msg.lower().count(x) for x in QUOTES_KEYS]):
					for k,v in QUOTES.iteritems():
						if msg.lower().count(k):
							bot.send('privmsg %s :%s'%(chan,eval(v)))
