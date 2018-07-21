import logging
import threading

import RPi.GPIO as GPIO
import json
import os
import time

import Constants

basedir=os.path.dirname(os.path.relpath(__file__))
DEFAULT_OUT=GPIO.HIGH
ON_OUT=GPIO.LOW
DEAD_TIME=0.9


class ChannelDevice:
  def __init__(self,cfg,deadHandler=None):
    self.logger = logging.getLogger(Constants.LOGNAME)
    self.gpio = cfg['gpio']
    self.channel = int(cfg['channel'])
    self.name = "Channel %d" % (self.channel,)
    if (cfg.get('name')):
      self.name=cfg.get('name')
    self.deadHandler=deadHandler
  def getChannel(self):
    return self.channel
  def getGpio(self):
    return self.gpio
  def isOn(self):
    return (GPIO.input(self.getGpio()) != DEFAULT_OUT)
  def getName(self):
    return self.name
  def info(self):
    return{
      'channel': self.getChannel(),
      'name':self.getName(),
      'gpio':self.getGpio()
    }

class Output(ChannelDevice):
  def __init__(self,cfg,deadHandler):
    ChannelDevice.__init__(self,cfg,deadHandler)
    self.switchTime=None
    self.accumulated=0
    self.startcount=0
    self.accumulatedCount=0;
    GPIO.setup(self.getGpio(),GPIO.OUT)
    GPIO.output(self.getGpio(),DEFAULT_OUT)
    self.logger.info("setup output at gpio %d, value %d"%(self.getGpio(),DEFAULT_OUT))
  def switchOn(self,count=0):
    self.switchTime=time.time()
    self.startcount=count
    if self.deadHandler is not None:
      self.deadHandler.switchOn()
    GPIO.output(self.getGpio(),ON_OUT)
  def switchOff(self,count=0):
    if not self.isOn():
      return False
    now=time.time()
    if self.switchTime is not None:
      self.accumulated+=now-self.switchTime
      self.accumulatedCount+=count-self.startcount
    if self.deadHandler is not None:
      self.deadHandler.switchOff()
    GPIO.output(self.getGpio(),DEFAULT_OUT)
    self.switchTime=None
    self.startcount=0
    self.logger.info("switched off %d, count=%d"%(self.getChannel(),self.getAccumulatedCount()))
  def getSwitchTime(self):
    return self.switchTime
  def getAccumulatedCount(self):
    return self.accumulatedCount
  def getAccumulatedTime(self):
    return self.accumulated
  def getStartCount(self):
    return self.startcount
  def info(self):
    rt=ChannelDevice.info(self)
    rt['accumulatedTime']=self.accumulated
    rt['accumulatedCount']=self.accumulatedCount
    return rt
  def getStatus(self):
    return {
      'channel':self.channel,
      'accumulatedTime':self.accumulated,
      'accumulatedCount':self.accumulatedCount
    }
  def setStatus(self,map):
    v=map.get('accumulatedTime')
    if v is not None:
      self.accumulated=v
    v=map.get('accumulatedCount')
    if v is not None:
      self.accumulatedCount=v

class Input(ChannelDevice):
  def __init__(self,cfg,deadHandler,pup=GPIO.PUD_UP):
    ChannelDevice.__init__(self,cfg,deadHandler)
    self.callback=None
    GPIO.setup(self.getGpio(),GPIO.IN,pull_up_down = pup)
    self.logger.info("setup input at gpio %d" % (self.getGpio()))
    GPIO.add_event_detect(self.getGpio(),GPIO.FALLING,callback=self.__callback,bouncetime=200)
  def registerCallback(self,callback):
    self.callback=callback
  def __callback(self,what):
    if self.deadHandler is not None:
      if self.deadHandler.isDeadTime():
        return
    #time.sleep(0.001)
    #if not self.isOn():
    #  return
    self.logger.info("**callback*** %d"%(self.getChannel()))
    if self.callback is not None:
      self.callback(self.getChannel())

class Meter(ChannelDevice):
  def __init__(self,cfg,deadHandler):
    self.counter=0
    if cfg is None:
      return
    ChannelDevice.__init__(self, cfg,deadHandler)
    self.ppl=cfg.get('ppl')
    if self.ppl is not None:
      self.ppl=float(self.ppl)
    GPIO.setup(self.getGpio(), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    self.logger.info("setup input at gpio %d" % (self.getGpio()))
    GPIO.add_event_detect(self.getGpio(), GPIO.FALLING, callback=self.meterCallback, bouncetime=50)
  def meterCallback(self,channel):
    if self.deadHandler is not None:
      if self.deadHandler.isDeadTime():
        return
    self.counter+=1
    if (self.counter % 1000) == 0:
      self.logger.log("meter callback, value=%d"%(self.counter))
  def getValue(self):
    return self.counter
  def setValue(self,v):
    self.counter=v
  def getPPl(self):
    return self.ppl

class Booster(Output):
  def __init__(self,cfg,deadHandler):
    Output.__init__(self,cfg,deadHandler)
    self.timerThread = threading.Thread(target=self.timerRun)
    self.timerThread.daemon = True
    self.timerThread.start()
    self.stopTime=None
    self.boosterTime=cfg.get("time") if cfg is not None else None
    if self.boosterTime is None:
      self.boosterTime=30
    else:
      self.boosterTime=int(self.boosterTime)
  def timerRun(self):
    while True:
      try:
        if self.stopTime is not None:
          now=time.time()
          if now >= self.stopTime:
            self.logger.info("booster off")
            self.switchOff(0)
            self.stopTime=None
      except :
        self.logger.warn("Exception in booster timer")
      time.sleep(1)

  def switchOn(self,count=0):
    Output.switchOn(self,count)
    self.stopTime=time.time()+self.boosterTime
    self.logger.info("booster on")


class DeadHandler:
  def __init__(self,booster=None):
    self.last=None
    self.booster=booster

  def isDeadTime(self):
    if self.last is None:
      return False
    now=time.time()
    if (now-self.last) < DEAD_TIME:
      return True
    return False
  def switchOn(self):
    self.last=time.time()
    if self.booster is not None:
      self.booster.switchOn(0)
  def switchOff(self):
    self.last = time.time()

class Hardware:
  def __init__(self):
    configString = open(os.path.join(basedir, "base.json")).read()
    self.config = json.loads(configString)
    GPIO.setmode(GPIO.BCM)
    self.booster = Booster(self.config['gpio'].get('booster'),None)
    self.deadHandler=DeadHandler(self.booster)
    self.outputs = self.createOutputs()
    self.inputs = self.createInputs()
    self.meter = Meter(self.config['gpio'].get('meter'),self.deadHandler)
  def createOutputs(self):
    list=self.config['gpio'].get('outputs')
    if list is None:
      return None
    rt=[]
    for cfg in list:
      op=Output(cfg,self.deadHandler)
      rt.append(op)
    return rt
  def createInputs(self):
    list=self.config['gpio'].get('inputs')
    if list is None:
      return None
    rt=[]
    for cfg in list:
      op=Input(cfg,self.deadHandler)
      rt.append(op)
    return rt
  def getOutput(self,channel):
    '''
    get output by channel id
    :param channel:
    :return: Output
    '''
    for o in self.outputs:
      if o.getChannel()==channel:
        return o

  def getInput(self,channel):
    '''
    get input by channel id
    :param channel:
    :return: Input
    '''
    for i in self.inputs:
      if i.getChannel() == channel:
        return i

  def getMeter(self):
    return self.meter

  def startOutput(self,channel):
    ch=self.getOutput(channel)
    if ch is None:
      return
    if ch.isOn():
      return True
    v=self.meter.getValue()
    ch.switchOn(v)

  def stopOutput(self,channel):
    ch=self.getOutput(channel)
    if ch is None:
      return
    if not ch.isOn():
      return
    v = self.meter.getValue()
    ch.switchOff(v)
    return True

  def isOn(self,channel):
    ch=self.getOutput(channel)
    if not ch:
      return False
    return ch.isOn()

  def getInputChannelNumbers(self):
    rt=[]
    for c in self.inputs:
      rt.append(c.getChannel())
    return rt

  def getOutputChannelNumbers(self):
    rt=[]
    for c in self.outputs:
      rt.append(c.getChannel())
    return rt

