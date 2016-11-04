#!/usr/bin/python
#-*-coding:utf-8-*-
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// IMPORTS
import os,sys,re,time,socket,ircbot
from random import random,choice
from subprocess import check_output
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// FUNCTIONS

# GET 'CALL' FROM OUTPUT (PRIVMSG,JOIN,...)
def GetCall(line):
	res = re.findall(' *[A-Z]{4,8} *',line)
	if len(res)>0: res = res[0].strip()
	else: res = None
	return res

def Cronjob(bot):
	if ircbot.Uptime(bot) < 10: return
	bot.Send('privmsg #laphysique :cronjob text ^o^')
	time.sleep(0.050)

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// GET METHOD

def Get(bot,nb=2048,input_delay=0):
	# WE CHECK TIME FOR SCHEDULED JOBS
	act_time = check_output('date "+%H%M %S"',shell=1).strip()
	if act_time and SCHEDULE:
		hm,s = act_time.split() ; s = int(s)
		# CHECK FOR SCHEDULED JOBS
		for k,v in SCHEDULE.iteritems():
			if hm==k and 0<=s<=30:
				bot.Send('privmsg #laphysique :%s'%v)
				time.sleep(30-s)
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
			if inline: bot.Send(inline)
			return ""
		# FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
		else:
			if bot.verbose: print "bot stopped:%s"%e
			sys.exit(1)
	# FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
	except socket.error, e:
		if bot.verbose: print "bot stopped:%s"%e
		sys.exit(1)
	else:
		# BOT SHUTDOWN
		if len(msg) == 0:
			if bot.verbose: print '• %s orderly shutdown.\n'%bot.nick
			bot.connected = 0
			return
		else:
			# AUTO RESPONSE TO ANY PING
			if msg.startswith('PING '):
				host = msg.split()[1]
				bot.Send('PONG %s'%host,reason='PONG')
			# JUST A CACHE (USELESS AFTER A PROPER START)
			bot.data += msg
			if len(bot.data)>1024*10: bot.data = bot.data[-1024*10:]
			return msg

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// MAIN UPDATE

def Update(bot,msg):
	if bot.connected:
		lines = msg.splitlines()
		# FOR EACH LINE IN MESSAGE
		for line in lines:
			line = line.strip()
			# WHAT DO WE HAVE
			CALL = GetCall(line)
			if not CALL: continue
			# GET USER/CHAN FROM OUTPUT
			user = line.split(CALL)[0][1:]
			user = re.sub('!.*','',user)
			chan = re.findall('#[^ ]+',line)
			if len(chan)>0: chan=chan[0]
			elif not chan and user: chan=user
			else: chan = ""
			# FOR A PRIVATE MESSAGE (EXCLUDING 'anotherbot' ;-)
			if CALL=='PRIVMSG' and user not in ['anotherbot']:
				msg = line.split(CALL)[1]
				if chan.count('#'): msg = line.split(chan+' :')[1]
				else: msg = line.split(bot.nick+' :')[1]
				# CUT MESSAGES THAT CONTAIN '|' OR '&' (SAFETY FOR EXECUTING SCRIPT)
				msg = re.sub('[|&].*','',msg)
				# AUTOMATED MESSAGES
				if msg.count('music'):
					MUSIC = '♩ ♪ ♫ ♬ ♭'.split()
					song = ' '.join([choice(MUSIC) for i in range(5)])
					bot.Send('privmsg %s :%s'%(chan,song))
				elif msg.count(bot.nick):
					if any([msg.lower().count(x) for x in GREETINGS]):
						x = choice(GREETINGS)+' %s'%user
					bot.Send('privmsg %s :%s'%(chan,x))
				elif any([msg.lower().count(x) for x in QUOTES_KEYS]):
					for k,v in QUOTES.iteritems():
						if msg.lower().count(k):
							bot.Send('privmsg %s :%s'%(chan,v))

# DATA
GREETINGS = ['yo','salut','bonjour','hello','ola','salam alekoum','buon giorno']
SCHEDULE  = {"1337":"|\|0w 15 7h3 71m3"}
QUOTES    = { "shake":" ♩ ᕕ(ᐛ)ᕗ  ♬ ♩  " }
QUOTES_KEYS = QUOTES.keys()
