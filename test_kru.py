#!/usr/bin/python
from serial import Serial as Sr
from time import sleep
from Tkinter import *
from threading import Thread
from json import load


need_to_exit = 0

class Biu:
    M,S,Fl,Fr = [0]*4
    
t = Tk()
lock = False



def write(x):
    global lock
    lock = True
    print x.encode('hex')
    s.write(x)
    lock = False

def init():
    biudata = load(open('/home/mismp/.biu.json.conf'))
    s = Sr(port=biudata['port'])#, timeout=0)
    binsdata = load(open('/home/mismp/.bins.json.conf'))
    d = Sr(
        port=binsdata['port'],
        baudrate=460800,
        parity='N',
        stopbits=1,
        bytesize=8,
    )
    s.write('aeae0100020800ff'.decode('hex'))
    return s, d
    



    
def gooooo(e):

    write('aeae01000108001e'.decode('hex'))
    sleep(0.2)
    write('aeae010001080001'.decode('hex'))
    sleep(0.2)
    write('aeae010001080001'.decode('hex'))
    
def more(e):
    global Biu
    write('aeae010001080001'.decode('hex'))
    Biu.M += 1

def less(e):
    global Biu
    write('aeae010002080001'.decode('hex'))
    Biu.M -= 1


def brake(e):
    global Biu
    write('aeae0100040700'.decode('hex'))
    write('aeae0100020800ff'.decode('hex'))
    Biu.M = 0
    sleep(2)
    write('aeae0100040700'.decode('hex'))



def stop(e):
#    global binsreader,need_to_exit
    #brake(e)
    need_to_exit = 1
#    del binsreader
    exit()
    
    #aeae0100040700 - left break
    #aeae0100040700 - WTF
    #aeae0100040700 - WTF
        
s, d = init()
t.bind('w', gooooo)
t.bind('p', stop)
t.bind('s', brake)
t.bind('<Up>',more)
t.bind('<Down>',less)

# w = Canvas(t, width=200, height=200)
# w.pack()
# binsreader = Thread(target = readpacket)
# binsreader.start()

t.mainloop()

exit(0)