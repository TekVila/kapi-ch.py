#!/usr/bin/python

"""
kapi-ch.py : A simple terminal client for public Chatango(e)s
  Extends ch.py's RoomManager https://github.com/Nullspeaker/ch.py

bidouilled by TekVila
"""
import ch
import random
from threading import Thread
import urllib.request
import subprocess
import re
import os
import getpass
import datetime
import sys

def unspace_sup(msg):
  msg = msg.replace("&#39;","'")
  return msg

def termform_message(time, name, mess, level = 0):
  end = "\x1b[0m"
  if level == 0:
    dec = ""
    nameCol = "\x1b[1;31m"
  elif level == 1:
    dec = "@"
    nameCol = "\x1b[2;31m"
  else:
    dec = "~"
    nameCol = "\x1b[3;31m"
  txt = "\x1b[3;36m[" + time.strftime("%H:%M") + "] " + end + nameCol  + "<" + dec + name + "> " + end  + unspace_sup(mess)
  return txt

class Kapich(ch.RoomManager):
  valML = 0
  picURL = ""
  
  def onInit(self):
    self.setNameColor("000000")
    self.setFontColor("993300")
    self.setFontFace("Arial")
    self.setFontSize(14)
    global valML
    valML = 0
    global picURL
    picURL = ""
  
  def inputer(self, room):
    while True:
      try:
        msgU = input("> ").lower()
        if msgU.lower().startswith("!who"):
          for u in self.getRoom(room)._userlist:
            print(u)
        elif msgU.lower().startswith("!lastpic"):
          if picURL != "":
            urllib.request.urlretrieve(picURL, "tmppic")
            subprocess.Popen(["cacaview", "tmppic"])
            #print("\033[?1049h\033[H")
            #subprocess.call(["cacaview", "tmppic"])
            #print("\033[?1049l")
        elif msgU.lower().startswith("!last"):
          lsm = msgU.split(" ");
          if len(lsm) > 1:
            usL = self.getRoom(room).findUser(lsm[1])
            msL = self.getRoom(room).getLastMessage(usL)
            print("** " + termform_message(datetime.datetime.utcfromtimestamp(msL.time) ,lsm[1], msL.body, self.getRoom(room).getLevel(usL)))
        elif msgU.lower().startswith("!clean"):
          #recap history
          subprocess.call(["killall", "cacaview"])
          subprocess.call(["clear"])
          for ms in self.getRoom(room)._history:
            print(termform_message(datetime.datetime.utcfromtimestamp(ms.time), ms.user.name,  ms.body, self.getRoom(room).getLevel(ms.user)))
        else:
          self.getRoom(room).message("" + msgU)  
      except KeyboardInterrupt:
        break;
        
  @classmethod
  def the_start(cl, rooms = None, name = None, password = None, pm = True):
    """
    Prompts the user for missing info, then starts.

    @type rooms: list
    @param room: rooms to join
    @type name: str
    @param name: name to join as ("" = None, None = unspecified)
    @type password: str
    @param password: password to join with ("" = None, None = unspecified)
    """
    if not rooms: rooms = str(input("Room name : ")).split(";")
    if len(rooms) == 1 and rooms[0] == "": rooms = []
    if not name: name = str(input("User name: "))
    if name == "": name = None
    if not password: password = str(getpass.getpass("User password: "))
    if password == "": password = None
    self = cl(name, password, pm = pm)
    for room in rooms:
      self.joinRoom(room)
    print(rooms[0])
    roomC = rooms[0]
    thread = Thread(target = self.main, args = ())
    thread.start()
    self.inputer(roomC)
  
  def onConnect(self, room):
    curRoom = room
    print("Connected to "+room.name)

  def onReconnect(self, room):
    print("Reconnected to "+room.name)

  def onDisconnect(self, room):
    print("Disconnected from "+room.name)

  def onMessage(self, room, user, message):
    #print("\033[?1049l")
    print(termform_message(datetime.datetime.utcfromtimestamp(message.time), user.name, message.body, room.getLevel(user)))

    lowmess = message.body.lower()
    if lowmess.startswith("!+-"):
      room.message("Bot : On joue entre 0 et 5000")
      global valML
      valML = random.randint(0, 5000)
      print(valML)
    elif lowmess.startswith("!val"):
      mparts = message.body.split(" ")
      if len(mparts) > 1:
        valtest = int(mparts[1])
        if valtest == valML:
          room.message("Bot : Bingo " + user.name + " !!!")
        elif valtest < valML:
          room.message("Bot : C'est plus !")
        else:
          room.message("Bot : C'est moins !")
      else:
        room.message("Bot : Fail "+ user.name  + " !!!")
    elif ".jpg" in lowmess or ".png" in lowmess:
      global picURL
      urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', lowmess)
      if len(urls) > 0:
        for url in urls:
          if ".jpg" in url or ".png" in url:
            picURL = url           
            #break
      else:
        picURL = ""        

  def onFloodBan(self, room):
    print("You are flood banned in "+room.name)

  def onPMMessage(self, pm, user, body):
    self.safePrint('PM: ' + user.name + ': ' + body)
    pm.message(user, body) # echo

  def onJoin(self, room, user, puid):
    print(termform_message(datetime.datetime.now(), user.name, "\x1b[3;32m is here !\x1b[0m", room.getLevel(user)))

  def onLeave(self, room, user, puid):
    print(termform_message(datetime.datetime.now(), user.name, "\x1b[3;31m is gone !\x1b[0m", room.getLevel(user)))

  def onHistoryMessage(self, room, user, message):
    print(termform_message(datetime.datetime.utcfromtimestamp(message.time),user.name, message.body, room.getLevel(user)))
    
    

if __name__ == "__main__":
  global lterm
  lterm = os.environ["TERM"]
  print(lterm)
  Kapich.the_start()
  print("")
  os._exit(1)
