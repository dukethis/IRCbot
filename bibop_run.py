#!/usr/bin/python
# coding: UTF-8

import os,sys,re,time,ircbot
from subprocess import check_output

# IRC PARAMETERS
NICK = 'bibop'
HOST = 'chat.freenode.org'
PORT = 6697
CHAN = '#laphysique'

try:    ison = check_output("/bin/is ircbot | grep -v '/bin/is'",shell=1).strip()
except: ison = None
if ison:
	print "Instance detected, shut it down"
	print ison
	sys.exit(1)

time.sleep(1)

# NEW BOT INSTANCE
bot = ircbot.IRCBOT(HOST,PORT,NICK)

bot.output = open('/home/duke/bot/ircs/output','w')
bot.input  = open('/home/duke/bot/ircs/input','r')

bot.connect()
bot.identify()

bot.send("JOIN %s"%CHAN)

CHECKDATE = "ls -lc ircbot.py | awk '{ print $8 }'"
date_0 = check_output(CHECKDATE,shell=1).strip()

# BOT JOB
while True:
	ircbot.update( bot )
	date = check_output(CHECKDATE,shell=1).strip()
	if date != date_0:
		try:
			reload(ircbot)
			time.sleep(1)
			date_0 = date
		except: print "Source is corrupted"
del bot

