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


class Consumer():
  def __init__(self,q):
    self.queue = q
  def work(self):
    while True:
      print self.queue.get()
      self.queue.task_done()
      # netflow_data = self.queue.get()
      # panda.new_flying_thing(netflow_data.from,netflow_data.to)

def main():
  q = Queue.Queue()
  producer = addNetflowToQueue(q)
  consumer = Consumer(q)
  t_p = thread.start_new_thread(producer.work,())
  t_c = thread.start_new_thread(consumer.work,())
  while True:
    time.sleep(100)



if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass