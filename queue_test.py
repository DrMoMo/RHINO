import Queue
import time
import thread

def main_stupid_simple():
  q = Queue.Queue()
  print q
  q.put("fuck")
  q.put("you")
  q.put("asshole")
  q.put("likeomg")
  while True:
    print q.get()
    q.task_done()

class NetFlowData():
  def __init__(self,dict):
    self.dict = dict
  def process_data_in_a_cool_way(self)
    return self.dict.awesome

class Producer():
  def __init__(self,q):
    self.queue = q
    self.count = 0
  def work(self):
    while True:
      self.queue.put("hi %d" %(self.count))
      # self.queue.put(NetFlowData(asdf,asdf,asdf))
      self.count = self.count + 1
      time.sleep(5)

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
  producer = Producer(q)
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