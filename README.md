# bibop_ircbot
IRC python simple bot 

A small project to run a bot on IRC.
A bot can connect one server and join multiple channels at once.

Requirements : 
- python

No installation : 
- With all files in the same directory, just execute botmain.py file :
  - Live session (you can use all IRC commands directly through the bot) :
      - $ python bibop_freenode
      - $ python -B bibop_freenode
  - Automated session (it will run in background and will process IRC commands reading the 'input' file) :
      - $ python -B bibop_freenode < input &> output &

Enjoy :-)
