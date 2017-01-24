#!/usr/bin/python
# coding: UTF-8
# //////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////// IMPORTS
import os,re,sys,time,socket,fcntl,irctools as tools

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
		self.data = ""
		self.time = time.localtime()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.hidden = 0
		self.connected = 0
		# USE NON BLOCKING STDIN (GOOD ENOUGH ?)
		fd = sys.stdin.fileno()
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
	
	@property
	def uptime(self): return int( round(time.mktime(time.localtime())-time.mktime(self.time),0) )
	
	def send(self,line,reason=None):
		line = line.strip()
		nbs = self.socket.send('%s\r\n'%line)
		if line and reason!='PONG':
			print '\rsent [%d bytes] %s (%s)'%(nbs,line,reason)
		self.last = line
		return nbs

	def connect(self,timeout=5):
		if self.connected: return
		print "• connecting..."
		self.socket.connect(self.host)
		self.socket.settimeout(float(timeout))
		msg = tools.recv(self)
		if msg.startswith(':'):
			host = re.sub(' .*$','',msg)[1:]
			server = host.strip()
			self.host = (server,self.host[1])
			self.connected = 1
			print "• hosted by %s"%server
		print msg
		time.sleep(0.25)
	
	def id_user(self,ident='botnet'):
		self.ident = ident
		print "• identifying as %s (%s)"%(self.nick,self.ident)
		self.send("nick "+self.nick,reason='nick command')
		self.send("user "+self.nick+" "+self.host[0]+" bla "+self.ident,reason='user command')
		msg = tools.recv(self)
		print msg
		time.sleep(0.25)
	
	def id_pass(self,password):
		self.send("privmsg nickserv :identify %s %s"%(self.nick,password),reason='identify command')
		msg = tools.recv(self)
		print msg
		time.sleep(0.25)

	def join(self,chan):
		print "• joining %s"%chan
		self.send("join "+chan,reason="join command")
		msg = tools.recv(self)
		if chan not in self.chan: self.chan.append( chan )
		print msg
		time.sleep(0.25)
		
	def __del__(self):
		self.socket.send('quit\r\n')
		self.socket.close()
