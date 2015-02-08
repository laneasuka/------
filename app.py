#-*- coding:utf-8 -*-
import pyb
import struct
#import uos

#uos.remove('main.py')
#del uos
ID = '100000'
DFT = '00'
CAL = '01'
ANS = '02'
BC = '03'
POL = '04'
PAIR = '05'

CW1 = pyb.Pin('Y1', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL1 = pyb.Pin('Y2', pyb.Pin.IN)
CW2 = pyb.Pin('Y3', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL2 = pyb.Pin('Y4', pyb.Pin.IN)
CW3 = pyb.Pin('Y5', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL3 = pyb.Pin('Y6', pyb.Pin.IN)
CW4 = pyb.Pin('Y7', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL4 = pyb.Pin('Y8', pyb.Pin.IN)
DV = pyb.Pin('Y12', pyb.Pin.IN)
DDO_EN = pyb.Pin('Y11', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
DG_EN = pyb.Pin('X1', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP)
BP = pyb.Pin('X2', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
SP = pyb.Pin('X11', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
ANSWER = pyb.Pin('X11', pyb.Pin.IN)
RSTB = pyb.Pin('X18', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP)
D0 = pyb.Pin('X19')
D1 = pyb.Pin('X20')
D2 = pyb.Pin('X21')
D3 = pyb.Pin('X22')

LBK_LED = pyb.LED(1)
PLARUN_LED = pyb.LED(2)
SAFE_LED = pyb.LED(3)
REC_LED = pyb.LED(4)
intbKEY = pyb.Switch()
serFM = pyb.UART(1, 9600, timeout=100)
serRF = pyb.UART(2, 9600, timeout=100)
spiLCD = pyb.SPI(1, pyb.SPI.MASTER, baudrate=200000, polarity=1, phase=0)
i2cKEY = pyb.I2C(2, pyb.I2C.MASTER, baudrate=100000)
accel = pyb.Accel()
## adc = pyb.ADC(pyb.Pin('X19'))
## dac = pyb.DAC(pyb.Pin('X5'))
#tmr1 = pyb.Timer(1, freq=0.5)
#tmr2 = pyb.Timer(2, freq=1)

class FM1288():
    def __init__(self, ):
        self.ser = pyb.UART(1, 9600, timeout=100)

class RF():
    def __init__(self, id=ID, cmd=DFT, ch=5, vl=0, st=0):
        self.id = id
        self.cmd = cmd
        self.ch = ch
        self.vl = vl
        self.st = st

        self.ser = pyb.UART(2, 9600, timeout=100)

        self.set_st(self.st)
        self.set_ch(self.ch)
        self.set_vl(self.vl)
        self.set_id(self.id, cmd)

    def set_ch(self, x):
        rst = ''
        while rst != 'SETCH:%s\r\n' %x:
            self.ser.write('ATCH:%s\r\n' %x)
            rst = self.ser.readall()
        self.ch = x
        return rst.strip()

    def set_vl(self, x):
        rst = ''
        while rst != 'SETVL:%02d\r\n' %x:
            self.ser.write('ATVL:%02d\r\n' %x)
            rst = self.ser.readall()
        self.vl = x
        return rst.strip()

    def set_id(self, x, xx):
        rst = ''
        while not rst:# != 'SETID\r\n':
            self.ser.write('ATID:%s\r\n' %(x + xx))
            rst = self.ser.readall()
        self.id = x
        self.cmd = xx
        return rst.strip()

    def set_st(self, x):
        """
        x=0 RX off    TX off (MIC OFF, SPK OFF)
        x=1 发完ID + Command 后 TX on and RX on.(MIC ON , SPK ON)
        x=2 TX ON and RX on (MIC ON ,SPK ON)
        x=3 TX OFF and RX ON (  MIC OFF, SPK ON)
        """
        rst = ''
        while rst != 'SETST:%s\r\n' %x:
            self.ser.write('ATST:%s\r\n' %x)
            rst = self.ser.readall()
        self.st = x
        return rst.strip()

    def get_stat(self):
        return self.id, self.cmd, self.ch, self.vl, self.st


class LCD():
    def __init__(self, ):
        pass


def bulin(tm):
    for i in range(1,5):
        pyb.LED(i).toggle()
        pyb.delay(tm)
    for i in range(1,5):
        pyb.LED(i).toggle()
        pyb.delay(tm)

def breathe(n):
    for t in range(n):
        for i in range(10, 256):
            pyb.LED(4).intensity(i)
            pyb.delay(4)
        for i in range(10, 256):
            pyb.LED(4).intensity(265-i)
            pyb.delay(4)

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

"""    
#tmr2.callback(lambda a:print('D:', d))
#tmr1.callback(lambda b:print('Ram:', gc.mem_free(), gc.mem_alloc()))
#try:"""
    
while 1:
    #ser.write(struct.pack('h',0x55))
    #rst = ser.readall() #(rst[0] * 256 + rst[1])
    #ad = adc.read()
##     i2c.scan()
##     i2c.is_ready(0x03)
    print(accel.filtered_xyz(), accel.tilt()) # returns list of slave addresses
    
##     i2c.send('hello', 0x42) # send 5 bytes to slave with address 0x42
##     i2c.recv(5, 0x42) # receive 5 bytes from slave
##     i2c.mem_read(2, 0x42, 0x10) # read 2 bytes from slave 0x42, slave memory 0x10
##     i2c.mem_write('xy', 0x42, 0x10) # write 2 bytes to slave 0x42, slave memory 0x10
    #dac.write(120) # output between 0 and 255
    pyb.delay(500)
    #print(accel.filtered_xyz())
#except:
    #print('Some error occurred, prepared to restart...')
    #pyb.hard_reset()
    