from unittest import TestCase
import timerh
import datetime
import time


class TestTimerEntry(TestCase):
  def _createTe(self):
    return timerh.TimerEntry(1,0,"7:55",30)
  def test_clone(self):
    te=self._createTe()
    cl=te.clone()
    assert cl.channel==1
    assert cl.weekday ==0
    assert cl.start == "7:55"
    assert cl.duration == 30

  def test_getStartTime(self):
    te=self._createTe()
    st=te.getStartTime()
    assert st==datetime.time(hour=7,minute=55)
  def test_nextFireToday(self):
    te=self._createTe()
    #monday, 25.6.2018
    last=datetime.datetime(year=2018,month=6,day=25,hour=6)
    print "starting at ",last
    #should be 25.6.2018, 07:55
    te.lastRun=time.mktime(last.timetuple())
    now=datetime.datetime(year=2018,month=6,day=25,hour=8)
    next=te.nextFire(time.mktime(now.timetuple()))
    assert next is not None
    nextDt=datetime.datetime.fromtimestamp(next)
    print nextDt
    assert nextDt.weekday()==0
    assert nextDt.day==25
    assert nextDt.year==2018
    assert nextDt.month==6
    assert nextDt.hour==7
    assert nextDt.minute==55

  def test_nextFireNextWeek(self):
    te=self._createTe()
    #monday, 25.6.2018
    last=datetime.datetime(year=2018,month=6,day=26,hour=6)
    print "starting at ",last
    #should be 2.7.2018, 07:55
    te.lastRun=time.mktime(last.timetuple())
    now=datetime.datetime(year=2018,month=7,day=2,hour=8)
    next=te.nextFire(time.mktime(now.timetuple()))
    assert next is not None
    nextDt=datetime.datetime.fromtimestamp(next)
    print nextDt
    assert nextDt.weekday()==0
    assert nextDt.day==2
    assert nextDt.year==2018
    assert nextDt.month==7
    assert nextDt.hour==7
    assert nextDt.minute==55

  def test_nextFireNotYetSameDay(self):
    te=self._createTe()
    #monday, 25.6.2018
    last=datetime.datetime(year=2018,month=6,day=26,hour=6)
    print "starting at ",last
    #should be 2.7.2018, 07:55
    te.lastRun=time.mktime(last.timetuple())
    now=datetime.datetime(year=2018,month=6,day=26,hour=7)
    next=te.nextFire(time.mktime(now.timetuple()))
    assert next is None

  def test_nextFireNotYet(self):
    te=self._createTe()
    #monday, 25.6.2018
    last=datetime.datetime(year=2018,month=6,day=26,hour=6)
    print "starting at ",last
    #should be 2.7.2018, 07:55
    te.lastRun=time.mktime(last.timetuple())
    now=datetime.datetime(year=2018,month=7,day=1,hour=8)
    next=te.nextFire(time.mktime(now.timetuple()))
    assert next is  None

  def test_parse(self):
    map={'channel':1,'weekday':0,'start':'09:40','duration':40}
    te=timerh.TimerEntry.parse(map)
    assert te.weekday==0
    assert te.channel==1
    assert te.start=='09:40'
    assert te.duration==40

