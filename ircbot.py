#!/usr/bin/python
# coding: UTF-8

import os,sys,re,time,socket,ssl
from random import random,choice
from subprocess import check_output

class IRCBOT:
	def __init__(self,HOST,PORT,NICK='bibop'):
		self.nick = NICK
		self.host = HOST
		self.port = PORT
		self.output = None
		self.input  = None

		# CLEAR VIEW SOCKET
		socket_0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# TLSv1 WRAPPED SOCKET
		self.socket = ssl.wrap_socket(socket_0, ssl_version=ssl.PROTOCOL_TLSv1)

	def send(self,msg):
		self.socket.send("%s\r\n"%msg)

	def read(self,bytes=1024):
		try: msg = self.socket.recv(bytes).strip()
		except Exception as this:
			err = this.args[0]
			if err == 'The read operation timed out': return
			# FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
			else:
				print >> self.output, "Stopped: %s"%(err)
				sys.exit(1)
		else:
			# BOT SHUTDOWN
			if len(msg) == 0:
				print >> self.output, '%s %s orderly shutdown.'%(self.nick)
				sys.exit(0)
			else:
				# AUTO RESPONSE TO ANY PING
				if msg.startswith('PING '):
					host = msg.split()[1]
					self.send('PONG %s'%host)
		return msg

	def connect(self,d=1):
		# CONNECT AND DO HANDSHAKE (CF TLS)
		print >> self.output, "connecting..."
		self.socket.connect((self.host,self.port))
		print >> self.output, "handshaking..."
		self.socket.do_handshake()
		self.socket.settimeout(10)
		if d: time.sleep(d)

	def identify(self,d=1):
		# IDENTIFYING AS USUAL
		self.send("USER %s * * :%s"%(self.nick,self.nick))
		self.send("NICK %s"%self.nick)
		if d: time.sleep(d)		
		print >> self.output, self.read(1024)		

	def __del__(self):
		# QUIT HOST CONNEXION
		self.socket.send("QUIT\r\n")
		# CLOSE SOCKET CONNEXION
		self.socket.close()

def update(bot):
	data = bot.read()
	if not data: return
	MSGS = re.findall('^.*PRIVMSG.*$',data)
	for msg in MSGS:
		USER = re.sub('^:','', re.sub('!.*','',msg) )
		MESG = re.sub('.*PRIVMSG','',msg)
		DEST = MESG.split(':')[0]
		MESG = ":".join(MESG.split(':')[1:])
		if re.findall(bot.nick,MESG):
			if re.findall('\?',MESG):
				p = choice([0,1])
				ans = 'oui peut-être' * p + (1-p) * 'non je crois pas'
				bot.send("PRIVMSG %s :%s"%(DEST,ans))
			else: bot.send("PRIVMSG %s :C'est moi"%DEST)
		URL = re.findall('(?i)https?:\/\/[^ ]*',MESG)
		if URL:
			URL = URL[0]		
			try:    title = check_output('spyder %s'%URL,shell=1).strip()
			except: title = None
			if title: bot.send("PRIVMSG %s :%s"%(DEST,title))
	print >> bot.output,data

