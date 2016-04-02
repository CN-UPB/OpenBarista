from threading import current_thread

from zmq import Socket,Context

from decaf_utils_ioloop.decaf_ioloop import DecafIOThread, DecafActor


class ZMQSocketWrapper(object):

    def __init__(self, actor, socket):
        self.socket = socket
        self.actor = actor

    def send_json(self, obj, flags=0, **kwargs):
        if isinstance(current_thread(), DecafIOThread):
            self.socket.send_json(obj,flags,**kwargs)
        else:
            self.actor.call_on_loop(self.send_json,obj,flags,**kwargs)

    def send_pyobj(self, obj, flags=0, **kwargs):
        if isinstance(current_thread(), DecafIOThread):
            print "Sending:", obj
            self.socket.send_pyobj(obj,flags,**kwargs)
        else:
            self.actor.call_on_loop(self.send_pyobj,obj,flags,**kwargs)

    def send_multipart(self, msg_parts, flags=0, **kwargs):
        if isinstance(current_thread(), DecafIOThread):
            self.socket.send_multipart(msg_parts,flags,**kwargs)
        else:
            self.actor.call_on_loop(self.send_multipart,msg_parts,flags,**kwargs)

    def send_string(self, string, flags=0, encoding='utf-8'):
        if isinstance(current_thread(), DecafIOThread):
            self.socket.send_string(string,flags,encoding)
        else:
            self.actor.call_on_loop(self.send_string,string,flags,encoding)

    def __getattr__(self, item):
        return getattr(self.socket, item)


class ZmqActor(DecafActor):

    def __init__(self):
        super(ZmqActor, self).__init__()
        self.ctx = Context.instance()

    def new_socket(self, type):
        s = self.ctx.socket(type)
        return ZMQSocketWrapper(self,s)


    def addCallback(self, socket, callback):
        pass
