#!/usr/bin/python3 -B
# coding: UTF-8

import os,sys,re,time,socket,ssl
from random import random,choice
from subprocess import check_output

#//////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////// Internet Relay Chat roBOT

class Ircbot:
    def __init__(self,HOST,PORT,NICK,PATH):
        self.nick = NICK
        self.host = HOST
        self.port = PORT
        self.chan = []
        self.output = "%s/output"%PATH
        self.input  = "%s/input"%PATH

        # CLEAR VIEW SOCKET
        socket_0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TLSv1 WRAPPED SOCKET
        self.socket = ssl.wrap_socket(socket_0, ssl_version=ssl.PROTOCOL_TLSv1)
        
    def send(self,msg):
        msg = re.sub("'","",msg)
        print("\033[0;0;42mSend\033[0;0;0m: %s"%msg,flush=1)
        msg = bytes(msg+'\r\n','UTF-8')
        self.socket.send(msg)

    def read_input(self):
        with open(self.input,'r') as f:
            data = f.read().strip()
            return str(data)

    def read(self,bytes=1024):
        msg = ""
        try: msg = self.socket.recv(bytes)
        except Exception as this:
            err = this.args[0]
            if err == 'The read operation timed out': return
            # FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
            else:
                print("Stopped: %s"%(err),file=open(self.output,'a'))
                sys.exit(1)
        else:
            # BOT SHUTDOWN
            if len(msg) == 0:
                print('%s orderly shutdown.'%(self.nick),file=open(self.output,'a'))
                sys.exit(0)
        msg = msg.decode('utf8')
        msg = str(msg)
        msg = re.sub("^b[\'\"]","",msg)
        msg = msg[:-1]
        msg = re.sub(r'\\r\\n','',msg)
        # AUTO RESPONSE TO ANY PING
        if re.match("PING ",msg):
            host = re.sub("^:","",msg.split()[1])
            self.send("PONG %s"%host)
        print(msg,file=open(self.output,'a'),flush=1)
        return msg

    def connect(self,d=1):
        # CONNECT AND DO HANDSHAKE (CF TLS)
        print("connecting...",file=open(self.output,'w'))
        self.socket.connect((self.host,self.port))
        print("handshaking...",file=open(self.output,'a'))
        self.socket.do_handshake()
        self.socket.settimeout(10)
        time.sleep(d)
        print(self.read(1024),file=open(self.output,'a'))

    def identify(self,d=1):
        # IDENTIFYING AS USUAL
        self.send("USER %s * * :%s"%(self.nick,self.nick))
        self.send("NICK %s"%self.nick)
        time.sleep(d)
        print(self.read(1024),file=open(self.output,'a'))

    def __del__(self):
        # QUIT HOST CONNEXION
        try:    self.socket.send("QUIT\r\n")
        except: pass	
        # CLOSE SOCKET CONNEXION
        self.socket.close()

#//////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////// UPDATE ROBOT HAPPENS HERE: READ / ANALYZE / ACT

USERS  = {}
QUOTES = {
"combien .*\??":"42",
"say":"%s",
"héhéhé":u"C'est drôle ?"
}

def chatbot(bot,user,msg,dest):
    n = USERS[user][1] if user in USERS.keys() else 1
    print("\033[1;1;43mRecv\033[0;0;0m: %s [%s/%d]"%(msg,user,n))
    if user in USERS.keys() and USERS[user][0]==msg:
        n = n+1
        if n > 3:
            USERS.update( {user:[msg,n]} )
            if n < 5: bot.send("PRIVMSG %s :ouai j'ai compris %s"%(dest,user))
            return
    USERS.update( {user:[msg,n]} )
    for k,v in QUOTES.items():
        if re.findall(k,msg,flags=re.I):
            if v.count('%s'): v = v%(re.sub(k+' *','',msg))
            if k=='do':
                print("Doing: '%s'"%v)
                bot.send( v )
            else:
                bot.send("PRIVMSG %s :%s"%(dest,v))
            return
    
def update(bot):
    data = bot.read()
    if not data: return
    LINES = re.findall('^.*PRIVMSG.*$',data)
    LINES = [str(x) for x in LINES if not x.startswith(':%s'%bot.nick)]
    for line in LINES:
        USER = re.sub('!.*','',line)
        USER = re.sub("^:","", USER )
        MESG = re.sub(".*PRIVMSG","",line)
        DEST = MESG.split(':')[0].strip()
        DEST = USER if DEST==bot.nick else DEST
        MESG = ":".join( MESG.split(':')[1:] ).strip()
        MESG = re.sub("\'$",'',MESG)
        if DEST in bot.chan or DEST==USER:
            chatbot(bot,USER,MESG,DEST)
        # NAME FIRST URL
        URL = re.findall('(?i)https?:\/\/[^ ]*',MESG)
        if URL:
            URL = URL[0]		
            try:    title = check_output(['/home/duke/bin/spyder %s'%URL],stderr=STDOUT)
            except: title = None
            if title:
                title = re.sub("b'","",title.strip())
                title = re.sub("'$","",title).strip()
                bot.send("PRIVMSG %s :%s"%(DEST,title))
	

