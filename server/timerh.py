
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
  MAXDURATION=1800 #max. 30 minutes
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
    self.id=None

  @classmethod
  def parse(cls,map):
    ch=map.get('channel')
    if ch is None:
      raise Exception("missing parameter channel")
    wd=map.get('weekday')
    if wd is None:
      raise Exception("missing parameter weekday")
    if wd < 0 or wd > 6:
      raise Exception("invalid weekday %d, allowed: 0..6"%(wd))
    st=map.get('start')
    if st is None:
      raise Exception("missing parameter start")
    ts=cls.convertStartTime(st) #should raise an Exception
    dur=map.get('duration')
    if dur is None:
      raise Exception("missing parameter duration")
    if dur < 0 or dur > cls.MAXDURATION:
      raise Exception("invalid duration %d, allowed 0...%d"%(dur,cls.MAXDURATION))
    return cls(ch,wd,st,dur)

  def clone(self):
    rt=TimerEntry(self.channel,self.weekday,self.start,self.duration)
    return rt
  @classmethod
  def convertStartTime(cls,ts):
    hhmm = ts.split(':')
    startTime = datetime.time(hour=int(hhmm[0]), minute=int(hhmm[1]))
    return startTime
  def getStartTime(self):
    '''
    get the starttime as time
    :return: datetime.time
    '''
    return self.convertStartTime(self.start)

  def checkOverlap(self,other):
    if self.weekday != other.weekday:
      return False
    dummy=datetime.date(year=2018,month=1,day=1)
    selfstart=time.mktime(datetime.datetime.combine(dummy,self.getStartTime()).timetuple())
    otherstart=time.mktime(datetime.datetime.combine(dummy,other.getStartTime()).timetuple())
    selfend=selfstart+self.duration
    otherend=otherstart+other.duration
    if selfstart <= otherstart and selfend >= otherstart:
      return True
    if selfstart > otherstart and otherend >= selfstart:
      return True
    return False
  def nextFire(self,timestamp):
    '''datetime.timedelta(seconds=
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
      'duration':self.duration,
      'id':self.id if self.id is not None else 0
    }


class TimerHandler:
  def __init__(self, timerCallback,startThread=True):
    self.timerThread=threading.Thread(target=self.timerRun)
    self.timerThread.daemon=True
    if startThread:
      self.timerThread.start()
    self.timerlist=[]
    self.timerCallback=timerCallback
    self.running=True
    self.id=1
  def getNextId(self):
    self.id+=1
    return self.id
  def removeByChannel(self,channel,weekday=None,start=None):
    st=TimerEntry.convertStartTime(start) if start is not None else None
    for idx in xrange(len(self.timerlist)-1,-1,-1):
      timer=self.timerlist[idx]
      if timer.channel==channel:
        if ( weekday is None or weekday == timer.weekday) and (st is None or st == timer.getStartTime()):
          del self.timerlist[idx]
  def addTimer(self,timerEntry,deleteOther=False):
    if deleteOther:
      self.removeByChannel(timerEntry.channel)
    te=timerEntry.clone()
    te.id=self.getNextId()
    te.lastRun=None
    for timer in self.timerlist:
      if timer.checkOverlap(te):
        raise Exception("overlapping timer exists: %s"%(json.dumps(timer.info())))
    self.timerlist.append(te)

  def updateTimerWithId(self, timerEntry):
    if timerEntry.id is None:
      raise Exception("missing id in updateTimerWithid")
    for timer in self.timerlist:
      if timer.id != timerEntry.id and timer.checkOverlap(timerEntry):
        raise Exception("overlapping timer exists: %s" % (json.dumps(timer.info())))
    for timer in self.timerlist:
      if timer.id == timerEntry.id:
        timer.weekday=timerEntry.weekday
        timer.start=timerEntry.start
        timer.duration=timerEntry.duration
        return True
    self.addTimer(timerEntry)
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
        if self.running:
          self.checkAndRunTimer(time.time())
        time.sleep(1)
      except:
        print "Exception in timerloop"

  def info(self):
    return{
      'number':len(self.timerlist),
      'running':self.running,
      'entries':map(lambda e:e.info(),self.timerlist)
    }

  def readFromJson(self,cfgStr,clear=False):
    data=json.loads(cfgStr)
    if clear:
      self.clear()
    rmode=data.get('running')
    if rmode is not None:
      self.running=rmode
    for te in data['timer']:
      newTimer=TimerEntry.parse(te)
      self.addTimer(newTimer)

  def toJson(self):
    return json.dumps({
      'timer':map(lambda t:t.info(),self.timerlist),
      'running': self.running
    })
  def pause(self):
    self.running=False
  def unpause(self):
    self.running=True