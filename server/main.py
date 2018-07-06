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

class Main:
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
    timerfilename=os.path.join(os.path.dirname(os.path.relpath(__file__)),"timer.json")
    if os.path.exists(timerfilename):
      self.logger.info("reading timers from %s"%(timerfilename))
      self.timers=timerh.TimerHandler(self._timercb)
      self.timers.readFromJson(open(timerfilename).read())
      self.logger.info(pprint.pformat(self.timers.info()))

main=Main()
main.start()
while True:
  time.sleep(10)
