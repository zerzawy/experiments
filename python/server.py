#!/usr/bin/python

# This file is a quick and dirty way to control digital ios of rpi
# Copyright(C)  2015 Kurt Zerzawy www.blksize.ch
# 
# server.py is free software:
# you can redistribute it and/or modify it under the terms of the
# GNU General Public Licence as published by the Free Software Foundation,
# either version 3 of the Licence, or (at your option) any later version.
#
# Raspberry Pi steuert Modelleisenbahn is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with server.py. 
# If not, see <http://www.gnu.org/licenses/>.
#
# blkSize GmbH, Villnachern, Switzerland
# www.blksize.ch
#
 
# Example for communication with Raspberry Pi
# this file has to be on the raspberry side and must be
# started with sudo. Reason: GPIO control.

# it will connect by the given port (or by default with 60606)
#  to the controlling pc. After receiving commands it will change
#  the state of the IO.
# the led is on output 11
# pushing the button on input 16 is changing state of output as well!

# NOTE: This is a quick and dirty way that was used as an example
#        on 'Zukunftstag'

#
# \file
# server for control on raspberry pi side
# \author
# Kurt Zerzawy
#

#
# $Author: kurt $
# $Date: 2015-12-13 14:02:39 +0200 (Don, 31. Dez 2015) $
# $Revision: 2706 $

# server for connecting to the PC
import socket, select, string, sys
import errno
import time 
from thread import *
import re
import RPi.GPIO as GPIO
 
global set_on
global set_off
global led_is_on
global conn_closed    

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(16, GPIO.IN)
GPIO.setup(18, GPIO.IN)
GPIO.setup(22, GPIO.IN)
GPIO.setup(7, GPIO.IN)

if(len(sys.argv) < 2) :
    port = 60606
    print('Usage : server.py port, using port 60606')
else:
    port = int(sys.argv[1])
 
host = ''
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')
#s.settimeout(5)
 
# connect to remote host
try :
    s.bind((host, port))
except socket.error as e:
    print('bind failed. Error code : ' + str(e[0]))
    sys.exit()
 
print('Socket bind complete')
s.listen(10) 
print('Socket is now listening')

def  clientthread(conn):
    global set_on
    global set_off
    global led_is_on
    global conn_closed

    try:
        #wait to accept a connection - blocking call
        tosend = 'Welcome to server, type something'
        conn.sendall(tosend.encode())

        while True:
            #receiving from client
            data = conn.recv(1024)
            print('received ' + data)
            noled1 = re.sub('Set on:', '', data)
            print('now ' + str(noled1))
            x = noled1.find('True')
            if 0 == x:
                # now switch on Led
                print('set led true, please')
                set_on = True;
                noled1 = re.sub('True, Set off:', '', noled1)            
            else:
                noled1 = re.sub('False, Set off:', '', noled1)
                set_on = False

            # now handle switching off the led
            x = noled1.find('True')
            if 0 == x:
                # now switch off Led
                print('set led false, please')
                set_off = True
            else:
                set_off = False

            data = 'Led is on :' + str(led_is_on)
            reply = 'OK...' + data
            if not data:
                break;

            conn.sendall(reply.encode())
    except:
	print('client thread closed')
        conn.close()
        conn_closed = True

#now keep talking with the client
was_open = False
led_is_on = False
set_on = False
set_off = False
key1_was = False

conn_closed = True

while True:
    if(set_on):
        led_is_on = True
	GPIO.output(11, True)
    
    if(set_off):
        led_is_on = False 
	GPIO.output(11, False)

    if conn_closed:
        conn, addr = s.accept()
        print('connected with ' + addr[0] + ':' + str(addr[1]))
        start_new_thread(clientthread, (conn,))
        conn_closed = False 

    time.sleep(0.1)
    if not GPIO.input(16):
        print('button 1 pushed')
        if not key1_was:
            if led_is_on:
                set_off = True
            else:
                set_on = True

        key1_was = True
    else:
        print('button 1 released')
        key1_was = False



s.close()
