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

CW1 = pyb.Pin('Y1', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 高有效
CL1 = pyb.Pin('Y2', pyb.Pin.IN) # 低有效
CW2 = pyb.Pin('Y3', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL2 = pyb.Pin('Y4', pyb.Pin.IN)
CW3 = pyb.Pin('Y5', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL3 = pyb.Pin('Y6', pyb.Pin.IN)
CW4 = pyb.Pin('Y7', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL4 = pyb.Pin('Y8', pyb.Pin.IN)
DV = pyb.Pin('Y12', pyb.Pin.IN) # 高有效
DDO_EN = pyb.Pin('Y11', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 高有效
DG_EN = pyb.Pin('X1', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP) # 低有效
BP = pyb.Pin('X2', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 高有效
SP_EN = pyb.Pin('X11', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 低有效
ANSWER = pyb.Pin('X11', pyb.Pin.IN) # 低有效
RSTB = pyb.Pin('X18', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP) # 低有效
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
        self.set_bypass(0)
        self.mem_write(0x22f8, 0x8000) # 1mic 8k (VDA setup)
        self.mem_write(0x22f8, 0) # choose profile
        self.mem_write(0x2301, 0x12) # 16KHz MIC/SPK sample rate, PCM/I2S data rate set to 8KHz
        self.mem_write(0x2302, 0x1) # Bits[1:0]: number of microphones. Bit[4]: uni_omni Bit[8]: PSEUDO-2mic
        self.mem_write(0x22fb, 0) # let IC run after configuration is done

    def lreg_write(self, addr, data):
        self.ser.write(struct.pack('>HBBH', 0xfcf3, 0x6a, addr, data))

    def sreg_write(self, addr, data):
        self.ser.write(struct.pack('>HBBB', 0xfcf3, 0x68, addr, data))

    def mem_write(self, addr, data):
        self.ser.write(struct.pack('>HBHH', 0xfcf3, 0x3b, addr, data))

    def reg_read(self, addr):
        self.ser.write(struct.pack('>HBB', 0xfcf3, 0x60, addr))
        return self.ser.readall()

    def mem_read(self, addr):
        self.ser.write(struct.pack('>HBH', 0xfcf3, 0x37, addr))
        self.reg_read('26')
        self.reg_read('25')
        return self.ser.readall()

    def reset(self):
        self.lreg_write(0x2a, 0x30) # long_reg_write

    def set_ADPGA(self, value):
        """
        Gain Selection /PGA Gain Setting /Differential full scale Input /Bypass Communication Gain
            Value              (dB)               Signal  (Vpp)                       (dB)

          [ 0 0 0 0 ]            0                       2.83                           -2

          [ 0 0 0 1 ]            1                       2.52                           -1

          [ 0 0 1 0 ]            2                       2.25                           0

          [ 0 0 1 1 ]            4                       1.78                           2

          [ 0 1 0 0 ]            6                       1.42                           4

          [ 0 1 0 1 ]            8                       1.13                           6

          [ 0 1 1 0 ]            10                      0.89                           8

          [ 0 1 1 1 ]            12                      0.71                           10

          [ 1 0 0 0 ]            14                      0.56                           12

          [ 1 0 0 1 ]            16                      0.45                           14

          [ 1 0 1 0 ]            18                      0.36                           16

          [ 1 0 1 1 ]            20                      0.28                           18

          [ 1 1 0 0 ]            22                      0.22                           20

          [ 1 1 0 1 ]            24                      0.18                           22

          [ 1 1 1 0 ]            26                      0.14                           24

          [ 1 1 1 1 ]            28                      0.11                           26
        :param value:
        :return:
        """
        self.mem_write(0x22e5, value)

    def set_DAPGA(self, value):
        """
        Gain Selection   /PGA Gain Setting  /Differential full scale Output /Bypass Communication Gain
                 Value                 (dB)               Signal (Vpp)                         (dB)

        [ 0 0 0 0 ]               +2                    3.00                            0

        [ 0 0 0 1 ]                0                    2.40                            -2

        [ 0 0 1 0 ]               -2                    1.91                            -4

        [ 0 0 1 1 ]               -4                    1.51                            -6

        [ 0 1 0 0 ]               -6                    1.20                            -8

        [ 0 1 0 1 ]               -8                    0.95                           -10

        [ 0 1 1 0 ]               -10                   0.76                           -12

        [ 0 1 1 1 ]               -12                   0.60                           -14

        [ 1 0 0 0 ]               -14                   0.48                           -16

        [ 1 0 0 1 ]               -16                   0.38                           -18

        [ 1 0 1 0 ]               -18                   0.30                           -20

        [ 1 0 1 1 ]               -20                   0.24                           -22

        [ 1 1 0 0 ]               -22                   0.19                           -24

        [ 1 1 0 1 ]               -24                   0.15                           -26

        [ 1 1 1 0 ]               -26                   0.12                           -28

        [ 1 1 1 1 ]               -28                   0.09                           -30
        :param value:
        :return:
        """
        self.mem_write(0x22e9, value)

    def set_bypass(self, stat):
         BP.value(stat)


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
        # TODO: LCD
        pass

def get_key():
    #i2cKey.scan()
    i2cKEY.send(0xb0, 0x58)
    if i2cKEY.is_ready(0x58):
        i2cKEY.send(0x10, 0x58)
        if i2cKEY.is_ready(0x58):
            return i2cKEY.recv(0x10, 0x58)
    return i2cKEY.mem_read(1, 0x58, 0x10)
    i2cKEY.mem_write(0x10, 0x58, 0x08)

intbKEY.callback(get_key)

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
    