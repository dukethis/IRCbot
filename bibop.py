#!/usr/bin/python3 -B
# coding: UTF-8
""" Simple IRCbot script:
1. Create your ircbot script: mybot.py
2. Instantiate with HOST , PORT , NICK (, optionnal PATH)
3. Connect to specified HOST/PORT

"""
import os,sys,re,time,ircbot

#-----------------
# IRC PARAMETERS -
#-----------------

PATH = "."
NICK = 'bibop'
HOST = 'chat.freenode.org'
PORT = 6697
CHAN = ["#laphysique"]

os.chdir( PATH )

#---------------
# BOT INSTANCE -
#---------------

bot = ircbot.Ircbot(HOST,PORT,NICK,PATH)

bot.connect()
bot.identify()

def send_input( line ):
    print(line,file=open("input","w"))

for chan in CHAN:
    bot.send("JOIN %s"%chan)
    bot.chan.append( chan )
    time.sleep(1)
    if time.time()-bot.timestamp > 1800:
        send_input(f"PRIVMSG {chan} :01001000 01100101 01101100 01101100 01101111 [o.o]/")

#----------
# BOT JOB -
#----------
while True:
    INPUT = bot.read_input()
    if INPUT:
        bot.send(INPUT)
    ircbot.update( bot )

