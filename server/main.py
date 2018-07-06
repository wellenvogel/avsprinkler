import controller
import time
import os
import timerh
import pprint

class Main:
  def _timercb(self,timer):
    print "timer fired, channel=%d, on=%d minutes"%(timer.channel,timer.duration)
    self.controller.start(timer.channel,timer.duration*60)
  def start(self):
    self.controller=controller.Controller()
    timerfilename=os.path.join(os.path.dirname(os.path.relpath(__file__)),"timer.json")
    if os.path.exists(timerfilename):
      print "reading timers from %s"%(timerfilename)
      self.timers=timerh.TimerHandler(self._timercb)
      self.timers.readFromJson(open(timerfilename).read())
      pprint.pprint(self.timers.info())

main=Main()
main.start()
while True:
  time.sleep(10)
