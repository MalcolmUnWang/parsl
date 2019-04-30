import logging
import zmq
import os
import pickle
from ipyparallel.serialize import unpack_apply_message, serialize_object

logger = logging.getLogger('StandAloneServer')


def StandAloneServer(data_dir='.',
                     server_id=0):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect('tcp://localhost:5555')
    while True:
        message = socket.recv().decode('utf-8')
        #print('Received message : %s' % message)
        try:
            filepath = os.path.join(data_dir, message)
            input_function = open(filepath, "rb")
            #print('File opened')
            function_tuple = pickle.load(input_function)
            input_function.close()
        except Exception:
            exit(2)

        user_ns = locals()
        user_ns.update({'__builtins__': __builtins__})
        f, args, kwargs = unpack_apply_message(function_tuple, user_ns, copy=False)

        result = f(*args, **kwargs)

        # TODO: Support for large object
        socket.send(serialize_object(result)[0])
        print('Server %d Finish Sending Result : %s' %(server_id, message))



def StandAloneBroker():
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    backend = context.socket(zmq.DEALER)
    frontend.bind('tcp://*:5556')
    backend.bind('tcp://*:5555')

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())

        if socks.get(frontend) == zmq.POLLIN:

            message = frontend.recv_multipart()
            print('Receive from WQWorker: %s' % message[-1].decode('utf-8'))
            backend.send_multipart(message)

        if socks.get(backend) == zmq.POLLIN:
            print('Receive from Server')
            message = backend.recv_multipart()
            frontend.send_multipart(message)
