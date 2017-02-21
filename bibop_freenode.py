#!/usr/bin/python
# coding: UTF-8
# ////////////////// IMPORTS
import time,ircbot,irctools as tools

bot = ircbot.IRCBOT('bibop',('chat.freenode.org',6697))

bot.connect()
bot.id_user()

bot.join('#laphysique')

# RELOAD SOURCE MODULE EVERY X SECONDS
TIME_RELOAD = 60
TIME_0 = time.time()

while True:
	if time.time()-TIME_0 > TIME_RELOAD:
		try:
			reload(tools)
			tools.echo("INFO source up to date")
			TIME_0 = time.time()
		except:
			tools.echo("WARNING source update failed")
	msg = tools.recv(bot)
	tools.update(bot,msg)
	time.sleep(0.25)

