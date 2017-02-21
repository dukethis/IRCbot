#!/usr/bin/python -B
# coding: UTF-8

import os,sys,re,time,socket,ssl,ircbot
from random import random,choice
from subprocess import check_output

GREETINGS = ['yo','salut','bonjour','hello','ola','salam alekoum','buon giorno']
SCHEDULE  = { "1212":"J'ai faim" , "1750":"scheduled job" }
QUOTES    = {
"shake":" ♩ ᕕ(ᐛ)ᕗ  ♬ ♩ .",
"ping":"pong",
"vulgaire":"vulgaire ? oui, mais pas seulement..."
}
QUOTES_KEYS = QUOTES.keys()

# SYSTEM COMMAND TRIGGERS
TRIGGERS = {
"define":"/home/duke/bin/define %s -l en",
"definir":"/home/duke/bin/define %s -l fr",
"définir":"/home/duke/bin/define %s -l fr"
}

HELPMSG = [
"I am a bot. I name url for you, just share it.",
"I have other functions: %s"%(';'.join(TRIGGERS.keys()))
]

# ////////////////// FUNCTIONS

def now(): return check_output('date "+%H:%M:%S"',shell=1).strip()
def echo(line): os.system('echo "%s"'%line)

def GetTrigger(msg,bot,chan,user):
	# AUTOMATED URL NAMING
	urls = re.findall('https?://[^ ,;]+',msg)
	for url in urls:
		title = check_output('spider %s'%url,shell=1).strip()
		if title and not title.startswith('Content-Type'): bot.send('privmsg %s :%s'%(chan,title))
	if msg.count('help'):
		if msg.count(bot.nick) or random()<0.25:
			for h in HELPMSG: bot.send('privmsg %s :%s'%(chan,h))
	# GET TRIGGER
	elif any([ re.findall('%s *'%k,msg,flags=re.I) for k in TRIGGERS.keys() ]):
		trig = msg.split()[0]
		args = tuple(msg.split()[1:])
		comm = TRIGGERS[trig]%args
		try:    output = check_output("%s"%comm,shell=1).strip()
		except: output = None
		if output:
			for line in output.splitlines():
				bot.send('privmsg %s :%s'%(chan,line))
	# AUTOMATED MESSAGES
	elif msg.count('uptime'):
		ut = bot.uptime
		ut = "%.3f h"%(ut/3600.) if ut > 1000 else "%d s"%(ut)
		bot.send('privmsg %s :%s'%(chan,ut))
	elif msg.count(bot.nick):
		if re.findall('merci|thank you|thanks|ty',msg):
			x = 'de rien %s'%user
		elif msg.count('?'):
			x = 'oui' if random()<0.5 else 'non'
		else: x = '%s toi-même'%(re.sub(' ?%s[:]? ?'%bot.nick,'',msg))
		bot.send('privmsg %s :%s'%(chan,x))
	elif any([re.findall(x,msg.lower()) for x in QUOTES_KEYS]):
		for k,v in QUOTES.iteritems():
			if msg.lower().count(k):
				bot.send('privmsg %s :%s'%(chan,v))

# ////////////////// RECEIVE METHOD

def recv(bot,nb=2048):
	# ACTUAL TIME
	t = now()
	# EXEC SCHEDULED JOBS
	if SCHEDULE:
		hms = t.split(':')
		hm = ''.join(hms[:2])
		if hm in SCHEDULE.keys():
			bot.send('privmsg %s :%s'%(bot.chan[0],SCHEDULE[hm]),'scheduled job')
			time.sleep(60-int(hms[2]))
	m = None
	# TRY TO READ FROM SOCKET
	try: m = str(bot.socket.recv(nb))
	except Exception as e:
		try: INPUT = sys.stdin.readline().strip()
		except: time.sleep(0.1)
		if INPUT: bot.send(INPUT,reason="input")
	# BOT SHUTDOWN
	if m:
		if m.count('Closing Link'):
			echo('%s %s orderly shutdown.'%(t,bot.nick))
			sys.exit(0)
		else:
			# AUTO RESPONSE TO ANY PING
			if m.startswith('PING'):
				host = m.split()[1]
				bot.send('PONG %s'%host,'PING')
			else: echo('\r%s recv [%d bytes] %s'%(t,len(m),re.sub('\n|\r','',m)))
			return m

# ////////////////// MAIN UPDATE

def update(bot,msg):
	# PARSE RECEIVED MESSAGE
	if msg:
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
			# FOR A PRIVATE MESSAGE
			if CALL=='PRIVMSG':
				# GET MESSAGE
				msg = line.split(CALL)[1]
				if chan.count('#'): msg = line.split(chan+' :')[1]
				else: msg = line.split(bot.nick+' :')[1]
				# CUT OUT '|' OR '&' (MORE SAFE WHEN CALLING SCRIPT)
				msg = re.sub('[|&].*$','',msg)
				# AUTOMATED TRIGGERS
				try:    GetTrigger(msg,bot,chan,user)
				except: pass
	
