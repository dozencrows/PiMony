#=======================================================================
# Copyright Nicholas Tuckett 2015.
# Distributed under the MIT License.
# (See accompanying file license.txt or copy at
#  http://opensource.org/licenses/MIT)
#=======================================================================

import socket

LIRCD_ADDRESS = "/var/run/lirc/lircd"

def init():
    pass
    
def deinit():
    pass

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
  
def send_once(message):
    send_ir('SEND_ONCE ' + message)
