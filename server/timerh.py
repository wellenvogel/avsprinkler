
import time
import json
import os
import time
import threading
import datetime

DEFAULT_RUNTIME=15*60

basedir=os.path.dirname(os.path.relpath(__file__))

class TimerEntry:
  def __init__(self,channel,weekday,start,duration):
    '''

    :param channel: the channel id to start
    :param weekday: the day of the week (0...6), 0 is monday
    :param start: the start time in hh:mm
    :param duration: is seconds
    '''
    self.channel=channel
    self.weekday=weekday
    self.start=start
    self.duration=duration
    self.lastRun=None

  def clone(self):
    rt=TimerEntry(self.channel,self.weekday,self.start,self.duration)
    return rt

  def getStartTime(self):
    '''
    get the starttime as time
    :return: datetime.time
    '''
    hhmm = self.start.split(':')
    startTime = datetime.time(hour=int(hhmm[0]), minute=int(hhmm[1]))
    return startTime

  def nextFire(self,timestamp):
    '''
    return a timestamp for the next fire if there is one
    between lastRun and timestamp
    :param timestamp:
    :return:
    '''
    if self.lastRun is not None and timestamp <= self.lastRun:
      return
    last=self.lastRun
    if last is None:
      last=time.time()-1
    startTime=self.getStartTime()
    dt=datetime.datetime.fromtimestamp(last)
    if dt.weekday() == self.weekday and startTime < dt.time():
      #wee need to start the next day...
      dt+=datetime.timedelta(days=1)
    loopmax=7
    while dt.weekday() != self.weekday and loopmax > 0:
      dt+=datetime.timedelta(days=1)
      loopmax-=1
    if dt.weekday() != self.weekday:
      #strange - invalid weekday
      return
    nextStart=datetime.datetime.combine(dt.date(),startTime)
    rt=time.mktime(nextStart.timetuple())
    if rt > timestamp:
      return None
    return rt



class TimerHandler:
  def __init__(self, timerCallback,startThread=True):
    self.timerThread=threading.Thread(target=self.timerRun)
    self.timerThread.daemon=True
    if startThread:
      self.timerThread.start()
    self.timerlist=[]
    self.timerCallback=timerCallback
  def removeByChannel(self,channel):
    for idx in xrange(len(self.timerlist)-1,-1,-1):
      timer=self.timerlist[idx]
      if timer.channel==channel:
        del self.timerlist[idx]
  def addTimer(self,timerEntry,deleteOther=False):
    if deleteOther:
      self.removeByChannel(timerEntry.channel)
    te=timerEntry.clone()
    te.lastRun=None
    self.timerlist.append(te)

  def clear(self):
    self.timerlist=[]

  def findNextTimer(self,now):
    '''
    find a timer where the next matching entry is greater then lastRun
    :return: TimerEntry
    '''
    nextTimer=None
    nextFire=None
    for timer in self.timerlist:
      next=timer.nextFire(now)
      if next is not None:
        if nextTimer is None:
          nextFire=next
          nextTimer=timer
        else:
          if nextTimer > next:
            nextTimer=timer
            nextFire=next
    return nextTimer

  def checkAndRunTimer(self,now):
    timerEntry = self.findNextTimer(now)
    if timerEntry is not None:
      timerEntry.lastRun = now
      self.timerCallback(timerEntry)

  def timerRun(self):
    while True:
      try:
        self.checkAndRunTimer(time.time())
        time.sleep(1)
      except:
        print "Exception in timerloop"
