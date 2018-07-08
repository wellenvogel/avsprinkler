#! /usr/bin/env python
import Constants
import controller
import time
import os
import timerh
import pprint
import logging
import logging.handlers
import Constants
import httpserver


class Main:
  def getHttpRequestParam(cls,requestparam,name):
    rt = requestparam.get(name)
    if rt is None:
      return None
    if isinstance(rt, list):
      return rt[0].decode('utf-8', errors='ignore')
    return rt
  def getTimerFileName(self):
    return os.path.join(os.path.dirname(os.path.relpath(__file__)),"timer.json")
  def saveTimers(self):
    fn=self.getTimerFileName()
    tmp=fn+".tmp"
    timercfg=self.timers.toJson()
    h=open(tmp,"w")
    if h is not None:
      h.write(timercfg)
      h.close()
      os.unlink(fn)
      os.rename(tmp,fn)
    else:
      raise Exception("unable to open "+tmp)
  def handleRequest(self,param):
    request=self.getHttpRequestParam(param,'request')
    if  request is None or request == 'status':
      return {
        'status':'OK',
        'data':{
          'controller':self.controller.getStatus(),
          'timer':self.timers.info(),
          'channels':self.controller.getBaseInfo()
        }
      }
    if request == "start":
      channel=self.getHttpRequestParam(param,'channel')
      time=self.getHttpRequestParam(param,'duration')
      if channel is None:
        raise Exception("missing parameter channel")
      self.controller.start(int(channel),int(time) if time is not None else None)
      return{
        'status':'OK',
        'data': self.controller.getStatus()
      }
    if request == "stop":
      self.controller.stop()
      return {
        'status': 'OK'
      }
    if request == 'clearTimer':
      channel = self.getHttpRequestParam(param, 'channel')
      if channel is None:
        raise Exception("missing parameter channel")
      weekday=self.getHttpRequestParam(param, 'weekday')
      if weekday is not None:
        weekday=int(weekday)
      start=self.getHttpRequestParam(param, 'start')
      self.timers.removeByChannel(int(channel),weekday=weekday,start=start)
      self.saveTimers()
      return {
        'status': 'OK',
        'data': self.timers.info()
      }
    if request == 'addTimer':
      rq=['channel','start','weekday','duration']
      map={}
      for r in rq:
        p = self.getHttpRequestParam(param, r)
        if p is None:
          raise Exception("missing parameter "+r)
        map[r]=p
      map['duration']=int(map['duration'])
      map['channel']=int(map['channel'])
      map['weekday']=int(map['weekday'])
      te=timerh.TimerEntry.parse(map)
      self.timers.addTimer(te)
      self.saveTimers()
      return {
        'status': 'OK',
        'data':self.timers.info()
      }
    if request == 'stopTimers':
      self.timers.pause()
      return {
        'status': 'OK',
        'data': self.timers.info()
      }
    if request == 'startTimers':
      self.timers.unpause()
      return {
        'status': 'OK',
        'data': self.timers.info()
      }
    return {
      'status':'ERROR',
      'info':'not found'
    }
  def _timercb(self,timer):
    self.logger.info("timer fired, channel=%d, on=%d minutes"%(timer.channel,timer.duration))
    self.controller.start(timer.channel,timer.duration*60)
  def start(self):
    self.logger=logging.getLogger(Constants.LOGNAME)
    self.logger.setLevel(logging.INFO)
    handler=logging.handlers.TimedRotatingFileHandler(filename="sprinkler.log",when="D")
    handler.setFormatter(logging.Formatter("%(asctime)s-%(message)s"))
    self.logger.addHandler(handler)
    self.logger.info("####Sprinkler started####")
    self.controller=controller.Controller()
    timerfilename=self.getTimerFileName()
    self.timers = timerh.TimerHandler(self._timercb)
    if os.path.exists(timerfilename):
      self.logger.info("reading timers from %s"%(timerfilename))
      self.timers.readFromJson(open(timerfilename).read())
      self.logger.info(pprint.pformat(self.timers.info()))
    self.httpServer=httpserver.HTTPServer(httpserver.HTTPHandler,self)

main=Main()
main.start()
while True:
  time.sleep(10)
