import os
import datetime
class History:
  TIMEFORMAT="%Y/%m/%d %H:%M:%S"
  def __init__(self,filename):
    self.filename=filename
    self.entries=[]

  def addEntry(self,entry):
    dt=datetime.datetime.now().strftime(self.TIMEFORMAT)
    st=dt+"-"+entry
    self.entries.append(st)
    if (self.filename):
      with open(self.filename,"a") as h:
        h.write(st+"\n")
        h.close()

  def getEntries(self):
    return self.entries

  def readEntries(self):
    if self.filename is None:
      return False
    if not os.path.exists(self.filename):
      return False
    with open(self.filename) as h:
      self.entries=[line.rstrip('\n') for line in h]
      h.close()
    return True


