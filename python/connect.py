# Example for ethernet communication with Raspberry Pi

#!/usr/bin/python

# This file is a quick and dirty way to control digital ios of rpi
# Copyright(C)  2015 Kurt Zerzawy www.blksize.ch
# 
# connect.py is free software:
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
# along with connect.py. 
# If not, see <http://www.gnu.org/licenses/>.
#
# blkSize GmbH, Villnachern, Switzerland
# www.blksize.ch
#
 
# Example for communication with Raspberry Pi
# this file has to be on the PC side

# it will connect by to the programm server.py by the port 60606.
# On the small graphic interface the output can be switched on and off
# A text is telling the state of the the output, even if changed locally
#  on the raspberry.

# NOTE: This is a quick and dirty way that was used as an example
#        on 'Zukunftstag'

#
# \file
# client for control on raspberry pi side
# \author
# Kurt Zerzawy
#

#
# $Author: kurt $
# $Date: 2015-12-13 14:02:39 +0200 (Don, 31. Dez 2015) $
# $Revision: 2706 $

# ethernet connection example
import socket, select, string, sys
#import fcntl, os
import errno
from time import sleep
import tkinter
from _thread import *
import re

#global variables (ugly)

global set_on
global set_off
global timer
global is_on


def ende():
    main.destroy()

def func_set_on():
    global set_on
    global set_off
    global timer
    print('switch on')
    set_on = True
    set_off = False
    timer = 5           # try five times
    
def func_set_off():
    global set_on
    global set_off
    global timer
    print('switch off')
    set_on = False
    set_off = True
    timer = 5
    
def thread_led_label():
    global lb
    print('starting led label thread')
    global is_on
    print('setting label' + str(is_on))
    while True:
        if is_on:
            lb['text'] = 'LED ist EIN'
        else:
            lb['text'] = 'LED ist AUS'
            
def server():
    global set_on
    global set_off
    global timer
    global is_on
    print('Usage : python telnet.py hostname port')
     
    host = '192.168.0.172'
    port = 60606
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print('Unable to connect')
        sys.exit()
     
    print('Connected to remote host')
     
    while True:
        #incoming message from remote server
        try:
            print('Timer is ' + str(timer))
            if timer > 0:
                timer -= 1    
                tosend = 'Set on:' + str(set_on) + ', Set off:' + str(set_off)

            else:
                tosend = 'Set on: False, Set off: False'    # keepalive
                
            s.sendall(tosend.encode())
            data = s.recv(4096)
            sleep(1)
        except socket.timeout as e:
            err = e.args[0]
            if err == 'timed out':
                sleep(1)
                print('receiver timed out, retry later')
                continue
            else:
                print(e)
                sys.exit(1)

        except socket.error as e:
            print(e)
            sys.exit(1)
            
        else:
            if len(data) == 0:
                print('orderly shutdown on server end')
                sys.exit(0)
            else:
                print(data.decode())
                led = re.sub('OK...Led is on :', '', data.decode())
                print(led)
                x = led.find('True')
                if 0 == x:
                    is_on = True
                    print('Led is on')
                else:
                    is_on = False
                    print('Led is off')
    return

#main function
#if __name__ == "__main__":
print('hallo')
set_on = False
set_off = True
is_on = False
timer = 5

start_new_thread(server, ())

print('starting mmi')
main = tkinter.Tk()

b = tkinter.Button(main, text = 'Ende', command = ende)
c = tkinter.Button(main, text = 'Ein', command = func_set_on)
d = tkinter.Button(main, text = 'Aus', command = func_set_off)
lb = tkinter.Label(main, text = 'LED ist ---')
b.pack()
c.pack()
d.pack()
lb.pack()

start_new_thread(thread_led_label, ())

main.mainloop()

    
