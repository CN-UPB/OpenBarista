__author__ = 'thorsten'


# --------------------------------------------------
# ----- Step 1: Add RPCLayer to Interpreter -------
#
# In PyCharm:
#
# Right-Click on folder "decaf-utils-rabbitmq"
# and then choose       "Mark Directory As.."
# and click on          "Source Folder"
#
# (the folder then becomes blue)
# --------------------------------------------------

# --------------------------------------------------
# ------------ Step 2: Start RabbitMQ -------------
#
# 1: Download and install RabbitMQ for Linux
#
# 2: Open a terminal and type "sudo rabbitmqctl start_app"
# --------------------------------------------------

# -------------------------------------------------
# ----- Step 3: Import the RPCLayer ---------------
# -------------------------------------------------

import decaf.utils.rabbitmq.rpc_layer.rpc_layer as rpc

# -------------------------------------------------
# ----- Step 4: Create an Instance ----------------
# -------------------------------------------------

rpc_layer = rpc.RpcLayer()

# -------------------------------------------------
# -------------- Step 5A: Register ----------------
#
# If you want to provide method,
#
# you have to register them with a unique name
#
# -------------------------------------------------


def example_method():
    '''
    This is the method we want to provide
    '''
    return "Example Result"


rpc_layer.register("example_method",example_method)

# ---------------------------------------------
# -------------- Step 5B: Call ----------------
#
# If you want to call a remote method,
#
# you simply provide the name as a string
#
# and the parameters as usual.
#
# The call returns a Deferred to which either
#
# add a callback
#
# or use inline Callback.
#
# --------------------------------------------

#This makes sure, everything is set up
import time
time.sleep(1)

# *********Ansynchronous Call******************

def print_method(result):
    'We want to print the return value'
    print "Async:" + str(result)

d = rpc_layer.call("example_method")
d.addBoth(print_method)

print "This is executed immedeatly"

# *********Synchronous Call******************

import twisted.internet.defer as defer

@defer.inlineCallbacks
def call_sync():
    'This waits until the result is present and then prints it'
    result = yield rpc_layer.call("example_method")
    print "Sync:" +str(result)


call_sync()
