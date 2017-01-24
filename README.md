# bibop_ircbot
IRC python simple bot 

A small project to command a bot, this version should allow you to modify the source file irctools.py on live.
This way, you can add new functions and triggers in the file without having to restart (providing a valid code).

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
