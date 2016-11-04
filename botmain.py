#!/usr/bin/python
#-*-coding:utf-8-*-
#
# ////////////////// IMPORTS
import os,re,sys,time,ircbot,random,irctools as tools
from subprocess import check_output

# ////////////////// PROCESSING
def main():
	NICK = 'bibop_test'
	HOST = ('chat.freenode.net',6667)
	CHAN = ['#laphysique']
	
	ircbot.nonblocking_stdin()
	
	# CONNEXION
	bot = ircbot.IrcBot(NICK,HOST)
	bot.Connect()
	
	## AUTHENTICATION
	bot.Identify_NickUser('humanbot')
	bot.Identify_Password('********')
	#while not bot.hidden:
		#msg = tools.Get(bot)
		#if not msg or msg=="": continue
		#if bot.verbose: print msg
		#if msg.count('You are now identified for'):
			#bot.hidden = 1
	
	# JOIN MAIN CHANNEL
	bot.Join(CHAN)
	
	# CRONJOBS PARAMETERS
	bot.crontime = 60
	bot.cronprob = 1

	# CHECK ANY CHANGE IN irctools.py MODULE
	CHECKDATE = "ls -lc irctools.py | sed -e 's/.* [0-9{4,4}] //g'"
	date_0 = check_output(CHECKDATE,shell=1).strip()

	while True:
		# SOURCE CHECKING
		date = check_output(CHECKDATE,shell=1).strip()
		if date!=date_0:
			try:
				reload(tools)
				date_0 = date
			except: pass
			time.sleep(0.5)
		# CRONJOBS
		if ircbot.Uptime( bot ) % bot.crontime == 0 and random.random()<bot.cronprob:
			tools.Cronjob( bot )
		# READ FROM SOCKET
		msg = tools.Get(bot)
		if msg==None: sys.exit(0)
		elif msg=="" or msg.startswith('PING'): continue
		# PROCESS OUTPUT IN MAIN UPDATE
		tools.Update(bot,msg)

# ////////////////// MAIN CALL
if __name__=='__main__': main()
