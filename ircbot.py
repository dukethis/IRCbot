#!/usr/bin/python3 -B
# coding: UTF-8
""" Simple IRCbot Class definition
"""
import os,sys,re,time,datetime,socket,ssl,urllib3
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup

#//////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////// Internet Relay Chat RobOT

class Ircbot:
    def __init__(self,HOST,PORT,NICK,PATH="."):
        self.nick = NICK
        self.host = HOST
        self.port = PORT
        self.chan = []
        self.output = "%s/output"%PATH
        self.input  = "%s/input"%PATH

        # CLEAR VIEW SOCKET
        socket_0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TLSv1_2 WRAPPED SOCKET
        self.socket = ssl.wrap_socket(socket_0, ssl_version=ssl.PROTOCOL_TLSv1_2)
        
    def send(self,msg):
        msg = re.sub("'","",msg)
        print("Send: %s"%msg,flush=1)
        msg = bytes(msg+'\r\n','UTF-8')
        self.socket.send(msg)

    def read_input(self):
        # READ ALL LINES
        with open(self.input,'r') as fd:
            data = fd.readlines()
        # WRITE ALL MINUS FIRST LINE
        with open(self.input,'w') as fd:
            fd.write( '\n'.join( data[1:] ) )
        # RETURN THE FIRST LINE AS THE CURRENT LINE
        return data[0].strip() if len(data)>0 else None

    def read(self,bytes=1024):
        msg = ""
        try: msg = self.socket.recv(bytes)
        except Exception as this:
            err = this.args[0]
            if err == 'The read operation timed out': return
            # FOR AN ERROR EXCEPT TIMEOUT, WE SHOULD STOP
            else:
                print("Stopped: %s"%(err),file=open(self.output, 'a'))
                sys.exit(1)
        else:
            # BOT SHUTDOWN
            if len(msg) == 0:
                print('%s orderly shutdown.'%(self.nick),file=open(self.output, 'a'))
                sys.exit(0)
        msg = msg.decode('utf8')
        msg = re.sub("^b[\'\"]","", msg)[:-1]
        msg = re.sub(r'\\r\\n','', msg)
        # AUTO RESPONSE TO ANY PING
        if re.match("PING ",msg):
            host = re.sub("^:","",msg.split()[1])
            self.send("PONG %s"%host)
        print( msg, file=open(self.output,'a'), flush=1)
        return msg

    def connect(self, delay=1):
        # CONNECT AND DO HANDSHAKE (CF TLS)
        print( "connecting...", file=open(self.output,'w'))
        self.socket.connect((self.host,self.port))
        print( "handshaking...", file=open(self.output,'a'))
        self.socket.do_handshake()
        self.socket.settimeout(10)
        time.sleep(delay)
        if os.path.isfile("timestamp"):
            with open("timestamp","r") as fd:
                self.timestamp = float(fd.read().strip())
                print( "Last:",self.datetime( self.timestamp ) )
        print( time.time(), file=open("timestamp","w") )
        print( "Conn:",self.datetime( time.time() ) )
        print( self.read(1024), file=open(self.output,'a'))

    def identify(self,delay=1):
        # IDENTIFYING AS USUAL
        self.send("USER %s * * :%s"%(self.nick,self.nick))
        self.send("NICK %s"%self.nick)
        time.sleep(delay)
        print(self.read(1024),file=open(self.output,'a'))

    def datetime(self, t ):
        return datetime.datetime.fromtimestamp( t ).strftime( "%Y-%m-%d %H:%M" )
        
    def __del__(self):
        # QUIT HOST CONNEXION
        try:    self.socket.send("QUIT \\[o.o]\r\n")
        except: pass	
        # CLOSE SOCKET CONNEXION
        self.socket.close()

#//////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////// UPDATE ROBOT HAPPENS HERE: READ / ANALYZE / ACT

USERS  = {}
QUOTES = { "test":"test ok" }

def chatbot(bot,user,msg,dest):
    n = USERS[user][1] if user in USERS.keys() else 1
    print("Recv: %s [%s/%d]"%(msg,user,n))
    if user in USERS.keys() and USERS[user][0]==msg:
        n = n+1
        if n > 2:
            USERS.update( {user:[msg,n]} )
            if n < 5: bot.send("PRIVMSG %s :ok %s"%(dest,user))
            return
    USERS.update( {user:[msg,n]} )
    for k,v in QUOTES.items():
        if re.findall(k, msg, re.I|re.M):
            if v.count('%s'): v = v%(re.sub(k+' *','',msg))
            bot.send("PRIVMSG %s :%s"%(dest,v))
            return
    else:
        url = re.findall("https?:\/\/[^ ,;]*",msg)
        if url:
            url = url[0]
            print(url)
            try:
                url    = urllib3.util.parse_url( url )
                host   = '://'.join([url.scheme,url.host])
                req    = Request( url, headers={"User-Agent":"WebCake/url-title"} )
                req    = urlopen( req, timeout=5 )
                if req:
                  html = BeautifulSoup( req.read().decode('utf-8'), 'lxml' )
                  data = [ u.get_text() for u in html.find_all("title") ]
                  data = data[0] if len(data)>0 else None
                  bot.send( f"PRIVMSG {dest} :{data}" )
                req.close()
            except Exception as e:
                if str(e).count("CERTIFICATE_VERIFY_FAILED"):
                  try:
                    req    = Request( url.replace("https","http"), headers={"User-Agent":"WebCake/url-title"} )
                    req    = urlopen( req, timeout=5 )
                    if req:
                      html = BeautifulSoup( req.read().decode('utf-8'), 'lxml' )
                      data = [ u.get_text() for u in html.find_all("title") ]
                      data = data[0] if len(data)>0 else None
                      bot.send( f"PRIVMSG {dest} :{data}" )
                    req.close()
                  except: print(e)
                print(e)
    
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
    
