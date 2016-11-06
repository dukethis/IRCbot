#!/usr/bin/python
#-*-coding:utf-8-*-
#
# ////////////////// IMPORTS
import os,re,sys,time,socket,fcntl,irctools as tools

# ////////////////// FUNCTIONS

# ///////// NETWORK
# make a socket ready
def makeSocket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# make stdin a non-blocking file
def nonblocking_stdin():
    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

# make stdin a blocking file
def blocking_stdin():
    fd = sys.stdin.fileno()
    fcntl.fcntl(fd, fcntl.F_SETFL, os.O_RDONLY)

# ///////// BASE/BOT UTILITIES

def splitline(line):
    rs = line.split()
    r1 = ' '.join( rs[:len(rs)//2] )
    r2 = ' '.join( rs[len(rs)//2:] )
    return [r1,r2]

# uptime from Unit().time
def Uptime(unit):
    return int( round(time.mktime(time.localtime())-time.mktime(unit.time),0) )

# ////////////////// OBJECT

class IrcBot:

	def __init__(self,nick,host=('irc.freenode.org',6667),verbose=1):
		self.nick = nick
		self.host = host
		self.chan = []
		self.data = ""
		self.time = time.localtime()
		self.socket = makeSocket()
		self.hidden = 0
		self.connected = 0
		self.verbose = verbose
		self.crontime = 60
		self.cronprob = 1
	
	def Send(self,line,reason='msg'):
		line = line.strip()
		nbs = self.socket.send('%s\r\n'%line)
		if line and self.verbose and reason!='PONG':
			print '\rrecv [%d bytes] (%s)'%(len(line),line)
			print '\rsent [%d bytes] (%s)'%(nbs,reason)
		self.last = line
		return nbs

	def Connect(self,timeout=5):
		if self.connected: return
		if self.verbose: print "• connecting..."
		self.socket.connect(self.host)
		self.socket.settimeout(float(timeout))
		msg = tools.Get(self)
		if self.verbose: print msg,
		if msg.startswith(':'):
			host = re.sub(' .*$','',msg)[1:]
			server = host.strip()
			if self.verbose: print "• hosted by %s"%server
			self.host = (server,self.host[1])
			self.connected = 1
	
	def Identify_NickUser(self,ident):
		self.ident = ident
		if self.verbose: print "• identifying as %s (%s)"%(self.nick,self.ident)
		self.Send("nick "+self.nick,reason='nick command')
		self.Send("user "+self.nick+" "+self.host[0]+" bla "+self.ident,reason='user command')
		msg = tools.Get(self)
		if self.verbose: print msg
	
	def Identify_Password(self,password):
		self.Send("privmsg nickserv :identify %s %s"%(self.nick,password),reason='identify command')
		msg = tools.Get(self)
		if self.verbose: print msg

	def Join(self,chans):
		for chan in chans:
			if self.verbose: print "• joining %s"%chan
			self.Send("join "+chan,reason="join command")
			msg = tools.Get(self)
			if self.verbose: print msg
			if chan not in self.chan: self.chan.append( chan )
