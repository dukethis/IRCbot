#!/usr/bin/python
#-*-coding:utf-8-*-
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// IMPORTS
import os,sys,re,time,socket,ircbot,random
from subprocess import check_output
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// FUNCTIONS

# GET 'CALL' FROM OUTPUT (PRIVMSG,JOIN,...)
def GetCall(line):
	res = re.findall(' *[A-Z]{4,8} *',line)
	if len(res)>0: res = res[0].strip()
	else: res = None
	return res

# CRONJOB (EACH bot.crontime SECONDS)
def Cronjob(bot):
	# YOU MAY NEED TO ADJUST THE SETTING
	r = ircbot.Uptime( bot ) % bot.crontime
	t = ircbot.Uptime( bot ) < 10
	if t or r > 4 or random.random()>bot.cronprob: return
	bot.Send('privmsg #laphysique :shake test ^^','cronjob')
	bot.crontime = 600
	bot.cronprob = 1
	time.sleep(4)

# SCHEDULED JOBS {'HHMM':'something to remind or announce'}
def Scheduledjob(bot):
	act_time = check_output('date "+%H%M %S"',shell=1).strip()
	if act_time and SCHEDULE:
		hm,s = act_time.split() ; s = int(s)
		# CHECK FOR SCHEDULED JOBS
		for k,v in SCHEDULE.iteritems():
			if hm==k and 0<=s<=30:
				bot.Send('privmsg %s :%s'%(bot.chan[0],v),'scheduledjob')
				time.sleep(30-s)

# TRIGGERS { keyword:command }
def GetTrigger(line):
	if any([line.lower().startswith(x) for x in TRIGGERS.keys()]):
		key = re.sub(' .*','',line)
		arg = line.split(key)[1].strip()
		cmd = TRIGGERS[key]
		arg = re.sub('[|&].*$','',arg)
		try:    out = check_output('%s %s'%(cmd,arg),shell=1).strip()
		except: out = None
		return out

# URL DECODER (USING SPIDER BOT)
def GetTitle(line):
	url = re.findall('https?://[^ ]+',line)
	if url:
		try:    title = check_output('$BOTSRC/spider -c %s'%url[0],shell=1).strip()
		except: title = None
		return title

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// GET METHOD

def Get(bot,nb=2048,input_delay=0):
	# CRONJOBS
	Cronjob(bot)
	# WE CHECK TIME FOR SCHEDULED JOBS
	Scheduledjob(bot)
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
	if not bot.connected: return
	# PROCESS OUTPUT
	lines = msg.splitlines()
	for line in lines:
		line = line.strip()
		# WHAT DO WE HAVE (PRIVMSG,JOIN,...)
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
			# BOT CAN BE USED BOTH IN PUBLIC AND PRIVATE
			if chan.count('#'): msg = line.split(chan+' :')[1]
			else: msg = line.split(bot.nick+' :')[1]
			# CUT MESSAGES THAT CONTAIN '|' OR '&' (SAFETY FOR EXECUTING SCRIPT)
			msg = re.sub('[|&].*','',msg)
			# NAME URL BY DEFAULT
			title = GetTitle(msg)
			if title: bot.Send('privmsg %s :%s'%(chan,title),'title')
			# CHECK FOR TRIGGERS FIRST
			x = GetTrigger(msg)
			if x: bot.Send('privmsg %s :%s'%(chan,x))
			# ELSE SOME AUTOMATED MESSAGES
			elif msg.count(' %s'%bot.nick) or msg.count('%s '%bot.nick):
				x = '◯¬(ᐛ)ᕗ ..' if random.random()<0.5 else 'ᕕ(ᐛ)−◯ ..'
				bot.Send('privmsg %s :%s'%(chan,x))
			elif msg.count('music'):
				MUSIC = '♩ ♪ ♫ ♬ ♭'.split()
				song = ' '.join([random.choice(MUSIC) for i in range(5)])
				bot.Send('privmsg %s :%s'%(chan,song))
			elif any([msg.lower().count(x) for x in QUOTES_KEYS]):
				for k,v in QUOTES.iteritems():
					if msg.lower().count(k):
						bot.Send('privmsg %s :%s'%(chan,v))

# DATA
TRIGGERS  = {"uptime":"/usr/bin/uptime"}
GREETINGS = ['yo','salut','bonjour','hello','ola','salam alekoum','buon giorno']
SCHEDULE  = {"1100":"schedule job success" , "1337":"|\|0w 15 7h3 71m3"}
QUOTES    = {
'vulgaire':'Vulgaire ? Oui... Mais pas seulement',
'suicide collectif':'✔ ☣ suicide collectif activé ☢ ☠',
'datalove':'datagueule le datalove ♥',
'< *3':'♥',
'shake':' ♩ ᕕ(ᐛ)ᕗ  ♬ ♩    ',
'dtc':'ça chatouille',
'fucking a':'★★★★★★',
'yeah':'★★★★★☆',
'joli':'★★★★☆☆',
'mouai':'★★☆☆☆☆',
'haha':'lol'
}
QUOTES_KEYS = QUOTES.keys()
