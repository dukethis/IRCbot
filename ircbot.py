#!/usr/bin/python -B
# coding: UTF-8
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// IMPORTS
import os,re,sys,time,socket,ssl,fcntl,irctools as tools

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// HOSTS
"""
('irc.freenode.org',6667)
('fdn.geeknode.org',6667)
('fantasya.europnet.org',6667)
('roubaix-fr.pirateirc.net',6697)
('bulbizarre.swordarmor.fr',6697)
('kaiminus.swordarmor.fr',6697)
"""

# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// OBJECT
class IRCBOT:

	def __init__(self,nick,host):
		self.nick = nick
		self.host = host
		self.chan = []
		self.time = time.localtime()
		self.socket = ssl.wrap_socket( socket.socket(socket.AF_INET,socket.SOCK_STREAM), ssl_version=ssl.PROTOCOL_TLSv1)
	
	@property
	def uptime(self): return int( round(time.mktime(time.localtime())-time.mktime(self.time),0) )
	
	def send(self,line,reason=None):
		t = tools.now()
		nbs = self.socket.send('%s\r\n'%line)
		if line and reason!='PONG':
			tools.echo('\r%s sent [%d bytes] %s (%s)'%(t,nbs,line,reason))
		self.last = line
		return nbs

	def connect(self,timeout=10):
		tools.echo("• connecting...")
		self.socket.connect(self.host)
		tools.echo("• handshaking...")
		self.socket.do_handshake()
		tools.echo("• handshake done.")
		self.socket.settimeout(float(timeout))
		
	def id_user(self):
		tools.echo("• identifying as %s"%(self.nick))
		self.send("user %s * * :%s"%(self.nick,self.nick),reason='user command')
		self.send("nick "+self.nick,reason='nick command')
		msg = tools.recv(self,1024)
		tools.echo(msg)
		time.sleep(0.5)
	
	def id_pass(self,password,nb=4096):
		self.send("privmsg nickserv :identify %s %s"%(self.nick,password),reason='identify command')
		msg = tools.recv(self,nb)
		tools.echo(msg)
		time.sleep(1)
	
	def join(self,chan,nb=4096):
		tools.echo("• joining %s"%chan)
		self.send("join "+chan,reason="join command")
		msg = tools.recv(self,nb)
		if chan not in self.chan: self.chan.append( chan )
		tools.echo(msg)
		time.sleep(1)
	
	def __del__(self):
		try:    self.socket.send('quit\r\n')
		except: pass
		self.socket.close()
	
