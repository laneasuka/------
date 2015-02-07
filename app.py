#-*- coding:utf-8 -*-
__author__ = 'Lane'

import uos

uos.remove('main.py')
del uos
switch = pyb.Switch()
accel = pyb.Accel()

def bulin(tm):
    for i in range(1,5):
        pyb.LED(i).toggle()
        pyb.delay(tm)
    for i in range(1,5):
        pyb.LED(i).toggle()
        pyb.delay(tm)

def breathe(n):
    for t in range(n):
        for i in range(256):
            pyb.LED(4).intensity(i)
            pyb.delay(3)
        for i in range(256):
            pyb.LED(4).intensity(255-i)
            pyb.delay(3)

pyb.delay(20)
start = pyb.micros()
n = sum(range(100000))
ed = pyb.elapsed_micros(start)
print(start, ed, n)

while pyb.elapsed_micros(start) < 1000000:
    print(accel.filtered_xyz(), accel.tilt())
    pyb.delay(100)

breathe(2)

while pyb.elapsed_micros(start) < 5000000:
    bulin(60)
