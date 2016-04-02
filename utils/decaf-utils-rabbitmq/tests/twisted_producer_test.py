__author__ = 'thgoette'

from decaf_utils_rabbitmq.twisted_connection.twisted_producer import TwistedProducer
import threading
import time

def printer(x):
    print x

def setter(x):
    print x
    d = x.queue_declare(queue="hello..hello")
    d.addCallback(printer)

channels = []
p = TwistedProducer()
p.start()

time.sleep(2)

d = p.openChannel()
d.addCallback(setter)
