#!/usr/bin/python3 -B
# coding: UTF-8
""" IRC ROBOT RUN SCRIPT
"""
import os,sys,re,time,ircbot
from importlib import reload
from subprocess import check_output

# IRC PARAMETERS
PATH = "/home/duke/bot/irc/freenode/"
NICK = 'bibop'
HOST = 'chat.freenode.org'
PORT = 6697
CHAN = ["#laphysique"]

os.chdir( PATH )

# NEW BOT INSTANCE
bot = ircbot.Ircbot(HOST,PORT,NICK,PATH)

bot.connect()
bot.identify()

for chan in CHAN:
    bot.send("JOIN %s"%chan)
    bot.chan.append( chan )

CHECKDATE = "ls -lc ircbot.py | awk '{ print $8 }'"
date_0 = check_output(CHECKDATE,shell=1).strip()

# BOT JOB
while True:
    INPUT = bot.read_input()
    if INPUT: bot.send(INPUT)
    ircbot.update( bot )
    date = check_output(CHECKDATE,shell=1).strip()
    if date != date_0:
        try:
            reload(ircbot)
            time.sleep(1)
            date_0 = date
        except Exception as this:
            print( "Source is corrupted: %s"%' '.join(this.args) )
            sys.exit(1)
