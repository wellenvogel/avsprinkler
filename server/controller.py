import logging

import Constants
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
    self.logger = logging.getLogger(Constants.LOGNAME)
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
  def getStatusFileName(self):
    return os.path.join(basedir,"status.json")
  def stop(self):
    if self.activeChannel is None:
      return
    self.logger.info("switching off %d"%(self.activeChannel))
    self.hardware.stopOutput(self.activeChannel)
    self.activeChannel=None
    self.writeStatus()
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
    self.logger.info("switching on %d till %s"%(channel, time.ctime(self.stopTime)))
    self.activeChannel=channel
    self.hardware.startOutput(channel)
    self.writeStatus()

  def getStatus(self):
    if self.activeChannel is None or not self.hardware.isOn(self.activeChannel):
      return {
        'status':'off',
        'meter': self.hardware.getMeter().getValue()
      }
    ch=self.hardware.getOutput(self.activeChannel)
    return {
      'status': 'on',
      'channel': {
        'id':ch.getChannel(),
        'name':ch.getName(),
        'started':ch.getSwitchTime(),
        'running':time.time()-ch.getSwitchTime(),
        'remain': (self.stopTime - time.time()) if self.stopTime is not None else 0,
        'startCount':ch.getStartCount()
      },
      'meter': self.hardware.getMeter().getValue()
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

  def timerRun(self):
    while True:
      try:
        if self.activeChannel is not None and self.stopTime is not None:
          now=time.time()
          if now >= self.stopTime:
            self.stop()
        time.sleep(1)
      except:
        self.logger.warn("Exception in timerloop")
