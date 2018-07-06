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
    self.activeChannel=None
    self.stopTime=None
    self.timerThread=threading.Thread(target=self.timerRun)
    self.timerThread.daemon=True
    self.timerThread.start()
    for ch in range(0, 7):
      self.hardware.getInput(ch).registerCallback(self.__cb)
  def stop(self):
    if self.activeChannel is None:
      return
    print "switching off %d"%(self.active.getChannel())
    self.hardware.startOutput(self.activeChannel)
    self.activeChannel=None
  def __cb(self,channel):
    if channel == 0:
      self.stop()
    else:
      self.start(channel)
  def start(self,channel,runtime=None):
    if self.activeChannel is not None and self.activeChannel != channel:
      self.stop()
    self.stopTime=None
    now = time.time()
    if runtime is None:
      cfg=self.config.get(str(channel))
      if cfg is not None:
        runtime=cfg.get("runtime")
        if runtime is not None:
          self.stopTime=now+int(runtime)
    else:
      self.stopTime=now + runtime
    if self.stopTime is None:
      self.stopTime=now + DEFAULT_RUNTIME
    print "switching on %d till %s"%(channel, time.ctime(self.stopTime))
    self.activeChannel=channel
    self.hardware.startOutput(channel)

  def getStatus(self):
    if self.activeChannel is None or not self.hardware.isOn(self.activeChannel):
      return { 'status':'off'}
    ch=self.hardware.getOutput(self.activeChannel)
    return {
      'status': 'on',
      'channel': {
        'id':ch.getChannel(),
        'name':ch.getName(),
        'started':ch.getSwitchTime(),
        'running':time.time()-ch.getSwitchTime()
      }
    }

  def timerRun(self):
    while True:
      try:
        if self.activeChannel is not None and self.stopTime is not None:
          now=time.time()
          if now >= self.stopTime:
            self.stop()
        time.sleep(1)
      except:
        print "Exception in timerloop"
