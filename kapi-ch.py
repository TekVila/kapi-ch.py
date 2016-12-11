#!/usr/bin/python
import ch
import random
from threading import Thread
import urllib.request
import subprocess
from subprocess import check_output
import re
import os
import getpass
import datetime

def unspace_sup(msg):
  msg = msg.replace("&#39;","'")
  return msg

def termform_message(time, name, mess):
  txt = "[" + time.strftime("%H:%M") + "] " + "\x1b[1;31m<" + name + ">\x1b[0m " + unspace_sup(mess) 
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
      msgU = input("> ")
      if msgU.lower().startswith("!who"):
        for u in self.getRoom(room)._userlist:
          print(u)
      elif msgU.lower().startswith("!lastpic"):
        if picURL != "":
          urllib.request.urlretrieve(picURL, "tmppic")
          subprocess.Popen(["cacaview", "tmppic"])
      elif msgU.lower().startswith("!last"):
        lsm = msgU.split(" ");
        if len(lsm) > 1:
          print(" ** " + lsm[1] + " : " + unspace_sup(self.getRoom(room).getLastMessage(self.getRoom(room).findUser(lsm[1])).body))
      elif msgU.lower().startswith("!clean"):
        #recap history
        subprocess.call(["killall", "cacaview"])
        subprocess.call(["clear"])
        for ms in self.getRoom(room)._history:
          print(termform_message(datetime.datetime.utcfromtimestamp(ms.time), ms.user.name,  ms.body))
      else:
        self.getRoom(room).message("" + msgU)  
  
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
    #thread = Thread(target = TestBot.inputer, args = (self.getRoom(room),) )
    thread = Thread(target = self.main, args = ())
    thread.start()
    #self.main()
    self.inputer(roomC)
  
  def onConnect(self, room):
    curRoom = room
    print("Connected to "+room.name)

  def onReconnect(self, room):
    print("Reconnected to "+room.name)

  def onDisconnect(self, room):
    print("Disconnected from "+room.name)

  def onMessage(self, room, user, message):
    # Use with PsyfrBot framework? :3
    print(termform_message(datetime.datetime.utcfromtimestamp(message.time), user.name, message.body))

    if message.body.lower().startswith("!+-"):
      room.message("Bot : On joue entre 0 et 5000")
      global valML
      valML = random.randint(0, 5000)
      print(valML)
    elif message.body.lower().startswith("!val"):
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
    elif ".jpg" in message.body.lower() or ".png" in message.body.lower():
      global picURL
      urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.body.lower())
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
    print( datetime.datetime.now().strftime("%H:%M:%S")  + " ** " + user.name + " est là !");

  def onLeave(self, room, user, puid):
    print( datetime.datetime.now().strftime("%H:%M:%S")  + " ** " + user.name + " est gone !");

  def onHistoryMessage(self, room, user, message):
    print(termform_message(datetime.datetime.utcfromtimestamp(message.time),user.name, message.body))
    #print( "** " + datetime.datetime.utcfromtimestamp(message.time).strftime("%H:%M:%S")  + " ** " + user.name + " : " + unspace_sup(message.body)) 
    
    

if __name__ == "__main__":
  pppid = os.popen("ps -p %d -oppid=" % os.getppid()).read().strip()
  global lterm
  lterm = os.popen("ps -p %s -o comm=" % pppid).read().strip()
  print(lterm)
  Kapich.the_start()
