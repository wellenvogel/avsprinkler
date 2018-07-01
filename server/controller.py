import hardware
import time
import json
import os
import time
import threading

DEFAULT_RUNTIME=15*60

basedir=os.path.dirname(os.path.relpath(__file__))


class Controller:
  def __init__(self):
    configString = open(os.path.join(basedir, "config.json")).read()
    self.config = json.loads(configString)
    self.hardware=hardware.Hardware()
    self.active=None
    self.stopTime=None
    self.timerThread=threading.Thread(target=self.timerRun)
    self.timerThread.daemon=True
    self.timerThread.start()
    for ch in range(0, 7):
      self.hardware.getInput(ch).registerCallback(self.__cb)
  def stop(self):
    if self.active is None:
      return
    print "switching off %d"%(self.active.getChannel())
    self.active.switchOff()
    self.active=None
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
