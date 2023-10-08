import logging

import Constants
import hardware
import time
import json
import os
import time
import threading
import history

DEFAULT_RUNTIME=15*60

basedir=os.path.dirname(os.path.relpath(__file__))


class Controller:
  def __init__(self):
    self.logger = logging.getLogger(Constants.LOGNAME)
    configString = open(os.path.join(basedir, "config.json")).read()
    self.config = json.loads(configString)
    self.hardware=hardware.Hardware()
    self.activeChannel=None
    self.stopTime=None
    self.timerThread=threading.Thread(target=self.timerRun)
    self.timerThread.daemon=True
    self.timerThread.start()
    self.history=history.History(os.path.join(basedir,"history.txt"))
    self.history.readEntries()
    for ch in self.hardware.getInputChannelNumbers():
      self.hardware.getInput(ch).registerCallback(self.__cb)
  def getStatusFileName(self):
    return os.path.join(basedir,"status.json")
  def stop(self):
    if self.activeChannel is None:
      return
    self.logger.info("switching off %d"%(self.activeChannel))
    ch = self.hardware.getOutput(self.activeChannel)
    startTime=None
    startCount=None
    if ch is not None:
      startTime=ch.getAccumulatedTime()
      startCount=ch.getAccumulatedCount()
    self.hardware.stopOutput(self.activeChannel)
    channel=self.activeChannel
    self.activeChannel=None
    self.writeStatus()
    if ch is None:
      return
    hentry="STOP,%d,%s,%d,%d" %(ch.getChannel(),
                           ch.getName(),
                           ch.getAccumulatedTime(),
                           round(ch.getAccumulatedCount() / self.hardware.getMeter().getPPl()))
    if startCount is not None and startTime is not None:
      hentry+=",%d,%d"%(ch.getAccumulatedTime()-startTime,
                        round((ch.getAccumulatedCount()-startCount)/self.hardware.getMeter().getPPl()))
    self.history.addEntry(hentry)
  def __cb(self,channel):
    if channel == 0:
      self.stop()
    else:
      self.start(channel,manual=True)
  def start(self,channel,runtime=None,manual=None):
    if self.activeChannel is not None and self.activeChannel != channel:
      self.stop()
    self.stopTime=None
    ch=self.hardware.getOutput(channel)
    if ch is None:
      raise Exception("no channel %s found"%channel)
    if not manual and not ch.isTimerEnabled():
      raise Exception("timer disabled for channel %s"%channel)
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
    self.logger.info("switching on %d till %s"%(channel, time.ctime(self.stopTime)))
    self.activeChannel=channel
    self.hardware.startOutput(channel)
    self.writeStatus()
    self.history.addEntry("START,%d,%s,%d,%d"%
                          (channel,
                           ch.getName(),
                           ch.getAccumulatedTime(),
                           int(ch.getAccumulatedCount()/self.hardware.getMeter().getPPl())))

  def isTimerEnabled(self,channel):
    ch=self.hardware.getOutput(channel)
    if ch is None:
      return False
    return ch.isTimerEnabled()
  def enableDisableTimer(self,channel,enable):
    ch=self.hardware.getOutput(channel)
    if ch is None:
      raise Exception("channel %s not found"%channel)
    ch.timerEnabled=enable
    self.writeStatus()
  def getStatus(self):
    if self.activeChannel is None or not self.hardware.isOn(self.activeChannel):
      return {
        'status':'off',
        'meter': self.hardware.getMeter().getValue(),
        'ppl': self.hardware.getMeter().getPPl()
      }
    ch=self.hardware.getOutput(self.activeChannel)
    return {
      'status': 'on',
      'channel': {
        'id':ch.getChannel(),
        'name':ch.getName(),
        'started':ch.getSwitchTime(),
        'running':time.time()-(ch.getSwitchTime() or time.time()),
        'remain': (self.stopTime - time.time()) if self.stopTime is not None else 0,
        'startCount':ch.getStartCount(),
        'runtime': self.stopTime-ch.getSwitchTime() if (ch.getSwitchTime() is not None  and self.stopTime is not None )else 0
      },
      'meter': self.hardware.getMeter().getValue(),
      'ppl': self.hardware.getMeter().getPPl()
    }

  def getBaseInfo(self):
    return {
      'outputs': map(lambda o: o.info(),self.hardware.outputs),
      'inputs': map(lambda o: o.info(), self.hardware.inputs)
    }

  def getPersistanceInfo(self):
    rt={}
    rt['outputs']=map(lambda o:o.getStatus(),self.hardware.outputs)
    rt['meter']={'value':self.hardware.getMeter().getValue()}
    return rt

  def setPersistanceInfo(self,map):
    op=map.get('outputs')
    if op is not None:
      for opi in op:
        ch=opi.get('channel')
        ce=self.hardware.getOutput(ch)
        if ce is not None:
          ce.setStatus(opi)
    me=map.get('meter')
    if me is not None:
      v=me.get('value')
      if v is not None:
        self.hardware.getMeter().setValue(v)

  def writeStatus(self):
    fn=self.getStatusFileName()
    h=open(fn,"w")
    if h is not None:
      h.write(json.dumps(self.getPersistanceInfo()))
      h.close()

  def readStatus(self):
    try:
      fn=self.getStatusFileName()
      if os.path.exists(fn):
        status=open(fn).read()
        self.setPersistanceInfo(json.loads(status))
    except:
      self.logger.warn("execption in read status")

  def getHistory(self):
    return self.history.getEntries()

  def timerRun(self):
    while True:
      try:
        #do some audit as the "on" events could occur asynchronously
        #and in parallel - so we check for only one active output
        for cn in self.hardware.getOutputChannelNumbers():
          if self.activeChannel is None or cn != self.activeChannel:
            #we can safely call stop here as this will check first if the channel is running
            self.hardware.stopOutput(cn)
      except:
        pass
      try:
        if self.activeChannel is not None and self.stopTime is not None:
          now=time.time()
          if now >= self.stopTime:
            self.stop()
      except:
        self.logger.warn("Exception in timerloop")
      time.sleep(1)
