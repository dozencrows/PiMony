import socket
import threading
import Queue

LIRCD_ADDRESS = "/var/run/lirc/lircd"
message_queue = Queue.Queue()
ir_thread = None

def init():
    global message_queue, ir_thread
    ir_thread = threading.Thread(target=ir_thread_queue_handler, args=(message_queue,))
    ir_thread.start()
    print "IR initialised"
    
def deinit():
    global message_queue, ir_thread
    message_queue.put("QUIT")
    ir_thread.join()
    print "IR deinitialised"

def send_ir(message):
    lircd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    lircd_socket.connect(LIRCD_ADDRESS) 
    lircd_socket.sendall(message + "\n")
    
    lircd_socket_file = lircd_socket.makefile('r')

    for response in lircd_socket_file:
        if response == 'END\n':
            break

    lircd_socket_file.close()
    lircd_socket.shutdown(socket.SHUT_RDWR)
    lircd_socket.close()
    
def ir_thread_queue_handler(queue):
    while True:
        msg = queue.get()
        if msg != 'QUIT':
            send_ir(msg)
        else:
            break    
    
def send_once(message):
    global message_queue
    message_queue.put('SEND_ONCE ' + message)
