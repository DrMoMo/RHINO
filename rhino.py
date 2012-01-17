#!/usr/bin/python

import Queue
import time
import thread
from ReceiveNetflow import *


class addNetflowToQueue():
  def __init__(self,q):
    self.queue = q
  def work(self):
    receive = ReceiveNetflow('rhino.conf')
    while True:
      data = receive.run()
      self.queue.put(data)


class getNetflowFromQueue():
  def __init__(self,q):
    self.queue = q
  def work(self):
    while True:
      print self.queue.get()
      self.queue.task_done()





def main():
  q = Queue.Queue()
  add = addNetflowToQueue(q)
  get = getNetflowFromQueue(q)
  t_p = thread.start_new_thread(add.work,())
  t_c = thread.start_new_thread(get.work,())
  while True:
    time.sleep(100)



if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass