import datetime
import pprint
from unittest import TestCase
import timerh
import time


class TestTimerHandler(TestCase):
  def _createList(self):
    rt=[]
    rt.append(timerh.TimerEntry(1,0,"7:55",30))
    rt.append(timerh.TimerEntry(2,1, "7:55", 30))
    return rt
  def _cb(self,timerEntry):
    self._lastCb=timerEntry
    print "callback",timerEntry
  def test_removeByChannel(self):
    tl=timerh.TimerHandler(self._cb,False)
    li=self._createList()
    tl.addTimer(li[0])
    tl.addTimer(li[1])
    assert len(tl.timerlist) == 2
    tl.removeByChannel(1)
    assert len(tl.timerlist) == 1


  def test_addTimer(self):
    tl = timerh.TimerHandler(self._cb,False)
    li = self._createList()
    tl.addTimer(li[0])
    tl.addTimer(li[1])
    assert len(tl.timerlist) == 2


  def test_clear(self):
    tl = timerh.TimerHandler(self._cb,False)
    li = self._createList()
    tl.addTimer(li[0])
    tl.addTimer(li[1])
    assert len(tl.timerlist) == 2
    tl.clear()
    assert len(tl.timerlist) == 0
    assert tl.findNextTimer(time.time()) is None

  def test_checkAndRunTimer(self):
    tl = timerh.TimerHandler(self._cb,False)
    li = self._createList()
    # monday, 25.6.2018
    last = time.mktime(datetime.datetime(year=2018, month=6, day=25, hour=6).timetuple())
    tl.addTimer(li[0])
    tl.addTimer(li[1])
    tl.timerlist[0].lastRun = last
    tl.timerlist[1].lastRun = last
    assert len(tl.timerlist) == 2
    #first
    now = time.mktime(datetime.datetime(year=2018, month=6, day=25, hour=8).timetuple())
    self._lastCb=None
    tl.checkAndRunTimer(now)
    assert self._lastCb is not None
    assert self._lastCb.channel == 1 #we should see this timer first as already on monday
    self._lastCb = None
    tl.checkAndRunTimer(now)
    assert self._lastCb is None
    now = time.mktime(datetime.datetime(year=2018, month=6, day=26, hour=8).timetuple())
    tl.checkAndRunTimer(now)
    assert self._lastCb is not None
    assert self._lastCb.channel == 2 #we should now see the other timer fire
    self._lastCb = None
    tl.checkAndRunTimer(now)
    assert self._lastCb is None
    #do not fire if we are outside of tolerance
    now = time.mktime(datetime.datetime(year=2018, month=7, day=2, hour=10).timetuple())
    tl.checkAndRunTimer(now)
    assert self._lastCb is None

  def test_info(self):
    tl = timerh.TimerHandler(self._cb,False)
    li = self._createList()
    tl.addTimer(li[0])
    tl.addTimer(li[1])
    i=tl.info()
    assert i is not None
    pprint.pprint(i)

  def test_loadJson(self):
    json='''
    {"timer":[{"channel": 1, "duration": 30, "start": "7:55", "weekday": 0},
    {"channel": 2, "duration": 30, "start": "7:55", "weekday": 1}]}
    '''
    tl = timerh.TimerHandler(self._cb, False)
    tl.readFromJson(json)
    assert len(tl.timerlist) == 2
