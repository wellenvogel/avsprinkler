import RPi.GPIO as GPIO
import json
import os
import time

basedir=os.path.dirname(os.path.relpath(__file__))
DEFAULT_OUT=GPIO.HIGH
ON_OUT=GPIO.LOW
DEAD_TIME=0.5


class ChannelDevice:
  def __init__(self,cfg,deadHandler=None):
    self.gpio = cfg['gpio']
    self.channel = int(cfg['channel'])
    self.name = "Channel %d" % (self.channel,)
    self.deadHandler=deadHandler
  def getChannel(self):
    return self.channel
  def getGpio(self):
    return self.gpio

class Output(ChannelDevice):
  def __init__(self,cfg,deadHandler):
    ChannelDevice.__init__(self,cfg,deadHandler)
    self.switchTime=None
    self.accumulated=0
    GPIO.setup(self.getGpio(),GPIO.OUT)
    GPIO.output(self.getGpio(),DEFAULT_OUT)
  def isOn(self):
    return (GPIO.input(self.getGpio()) != DEFAULT_OUT)
  def switchOn(self):
    self.switchTime=time.time()
    if self.deadHandler is not None:
      self.deadHandler.switch()
    GPIO.output(self.getGpio(),ON_OUT)
  def switchOff(self):
    if not self.isOn():
      return False
    now=time.time()
    self.accumulated+=now-self.switchTime
    if self.deadHandler is not None:
      self.deadHandler.switch()
    GPIO.output(self.getGpio(),DEFAULT_OUT)
    self.switchTime=None

class Input(ChannelDevice):
  def __init__(self,cfg,deadHandler,pup=GPIO.PUD_UP):
    ChannelDevice.__init__(self,cfg,deadHandler)
    self.callback=None
    GPIO.setup(self.getGpio(),GPIO.IN,pull_up_down = pup)
    GPIO.add_event_detect(self.getGpio(),GPIO.FALLING,callback=self.__callback,bouncetime=200)
  def registerCallback(self,callback):
    self.callback=callback
  def __callback(self,what):
    if self.deadHandler is not None:
      if self.deadHandler.isDeadTime():
        return
    print "**callback %d"%(self.getChannel())
    if self.callback is not None:
      self.callback(self.getChannel())

class Meter(Input):
  def __init__(self,cfg,deadHandler):
    self.counter=0
    if cfg is None:
      return
    Input.__init__(self, cfg,deadHandler)
    self.registerCallback(self.meterCallback)
  def meterCallback(self,channel):
    self.counter+=1
  def getValue(self):
    return self.counter

class DeadHandler:
  def __init__(self):
    self.last=None

  def isDeadTime(self):
    if self.last is None:
      return False
    now=time.time()
    if (now-self.last) < DEAD_TIME:
      return True
    return False
  def switch(self):
    self.last=time.time()

class Hardware:
  def __init__(self):
    configString = open(os.path.join(basedir, "base.json")).read()
    self.config = json.loads(configString)
    GPIO.setmode(GPIO.BCM)
    self.deadHandler=DeadHandler()
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