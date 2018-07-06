
import time
import json
import os
import time
import threading
import datetime

DEFAULT_RUNTIME=15*60

basedir=os.path.dirname(os.path.relpath(__file__))

class TimerEntry:
  TOLERANCE=3600 #at maximum we start timers from one hour back
  def __init__(self,channel,weekday,start,duration):
    '''

    :param channel: the channel id to start
    :param weekday: the day of the week (0...6), 0 is monday
    :param start: the start time in hh:mm
    :param duration: is minutes
    '''
    self.channel=channel
    self.weekday=weekday
    self.start=start
    self.duration=duration
    self.lastRun=None

  @classmethod
  def parse(cls,map):
    return cls(map['channel'],map['weekday'],map['start'],map['duration'])

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
    startTime=self.getStartTime()
    dt=datetime.datetime.fromtimestamp(timestamp)
    tol=datetime.datetime.fromtimestamp(timestamp-TimerEntry.TOLERANCE)
    #at most we have 2 weekdays (TOLERANCE < 1 day!)
    if dt.weekday() != self.weekday and tol.weekday() != self.weekday:
      return
    next=None
    if dt.weekday() == self.weekday:
      next=datetime.datetime.combine(dt.date(),startTime)
    else:
      next=datetime.datetime.combine(tol.date(),startTime)
    nextts=time.mktime(next.timetuple())
    #next is now our candidate
    #check that it is above lastRun but before/equal now
    if self.lastRun is not None and nextts <= self.lastRun:
      return
    if nextts > timestamp or nextts < (timestamp - TimerEntry.TOLERANCE):
      return
    return nextts

  def info(self):
    return {
      'channel':self.channel,
      'weekday':self.weekday,
      'start':self.start,
      'duration':self.duration
    }


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
          if nextFire > next:
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

  def info(self):
    return{
      'number':len(self.timerlist),
      'entries':map(lambda e:e.info(),self.timerlist)
    }

  def readFromJson(self,cfgStr,clear=False):
    data=json.loads(cfgStr)
    if clear:
      self.clear()
    for te in data['timer']:
      newTimer=TimerEntry.parse(te)
      self.addTimer(newTimer)