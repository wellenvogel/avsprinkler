import hardware
import time
import json
import os
import time
import threading

DEFAULT_RUNTIME=15*60

basedir=os.path.dirname(os.path.relpath(__file__))

class TimerEntry:
  def __init__(self,channel,weekday,start,duration):
    self.channel=channel
    self.weekday=weekday
    self.start=start
    self.duration=duration

class TimerHandler:
  def __init__(self):
    configString = open(os.path.join(basedir, "timer.json")).read()
    self.config = json.loads(configString)
    self.timerThread=threading.Thread(target=self.timerRun)
    self.timerThread.daemon=True
    self.timerThread.start()
    self.timerlist=[]
  def removeByChannel(self,channel):
    for timer in self.timerlist:
      pass
  def __cb(self,channel):
    if channel == 0:
      self.stop()
    else:
      self.start(channel)
  def start(self,channel):
    self.stop()
    op=self.hardware.getOutput(channel)
    if op is None:
      return
    self.stopTime=None
    now = time.time()
    cfg=self.config.get(str(channel))
    if cfg is not None:
      runtime=cfg.get("runtime")
      if runtime is not None:
        self.stopTime=now+int(runtime)
    if self.stopTime is None:
      self.stopTime=now + DEFAULT_RUNTIME
    print "switching on %d till %s"%(channel, time.ctime(self.stopTime))
    self.active=op
    op.switchOn()

  def timerRun(self):
    while True:
      try:
        if self.active is not None and self.stopTime is not None:
          now=time.time()
          if now >= self.stopTime:
            self.stop()
        time.sleep(1)
      except:
        print "Exception in timerloop"
