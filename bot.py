#!/usr/bin/python3 -B
# coding: UTF-8
""" Simple IRCbot run
chat.freenode.org/6697
irc.geeknode.org/6697
"""
import os,sys,re,time,IRCbot

#-----------------
# IRC PARAMETERS -
#-----------------

PATH = "."
NICK = 'bebop'
HOST = 'irc.geeknode.org'
PORT = 6697
CHAN = ["#arn"]

os.chdir( PATH )

#---------------
# BOT INSTANCE -
#---------------

bot = IRCbot.IRCbot(HOST,PORT,NICK,PATH)

bot.connect()
bot.identify()

for i in range(3):
    msg = bot.read()
    
def send_input( line ):
    print(line,file=open("input","w"))

for chan in CHAN:
    bot.send("JOIN %s"%chan)
    bot.chan.append( chan )
    if time.time()-bot.timestamp > 1800:
        send_input(f"PRIVMSG {chan} :01001000 01100101 01101100 01101100 01101111 [o.o]/")

#----------
# BOT JOB -
#----------

while True:
    INPUT = bot.read_input()
    if INPUT:
        bot.send(INPUT)
    IRCbot.update( bot )

