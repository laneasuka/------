#-*- coding:utf-8 -*-
import struct
## import micropython
## micropython.alloc_emergency_exception_buf(100)
GP = '10'
ID = '0000'
DFT = '00'
CAL = '01'
ANS = '02'
BC = '03'
POL = '04'
PAIR = '05'
PD = '06'

CW1 = pyb.Pin('Y1', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 高有效
CL1 = pyb.Pin('Y2', pyb.Pin.IN) # 低有效
CW2 = pyb.Pin('Y3', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL2 = pyb.Pin('Y4', pyb.Pin.IN)
CW3 = pyb.Pin('Y5', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL3 = pyb.Pin('Y6', pyb.Pin.IN)
CW4 = pyb.Pin('Y7', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
CL4 = pyb.Pin('Y8', pyb.Pin.IN)
DV = pyb.Pin('Y12', pyb.Pin.IN, pyb.Pin.PULL_DOWN) # 高有效
DDO_EN = pyb.Pin('Y11', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 高有效
DG_EN = pyb.Pin('X1', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP) # 低有效
BP = pyb.Pin('X2', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN) # 高有效
SP_EN = pyb.Pin('X11', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP) # 低有效
ANSWER = pyb.Pin('X12', pyb.Pin.IN) # 低有效
RSTB = pyb.Pin('X18', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP) # 低有效

LBK_LED = pyb.LED(4)
PLARUN_LED = pyb.LED(3)
SAFE_LED = pyb.LED(2)
REC_LED = pyb.LED(1)
intbKEY = pyb.Switch()

nkmap = {64:'1', 72:'2', 80:'3', 65:'4', 73:'5', 120:'6', 81:'7', 89:'8', 97:'9', 66:'0'}
skmap = {121:'*', 74:'#', 88:'set', 104:'msg', 105:'rcd', 82:'cal', 96:'sch', 112:'vlu', 113:'vld', 90:'lck'}

def init():
    CW1.value(0)
    CW2.value(0)
    CW3.value(0)
    CW4.value(0)
    DDO_EN.value(0)
    DG_EN.value(1)
    BP.value(0)
    SP_EN.value(1)
    RSTB.value(1)

class FM1288:
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
        self.mem_write(0x22e5, value)

    def set_DAPGA(self, value):
        self.mem_write(0x22e9, value)

    def set_bypass(self, stat):
         BP.value(stat)


class RF:
    def __init__(self, id='10000000', ch=0, vl=0, st=0):
        self.id = id
        self.ch = ch
        self.vl = vl
        self.st = st
        self.rbuf = bytearray(16)
        self.wbuf = bytearray(16)

        self.ser = pyb.UART(2, 9600, timeout=100)

        self.set_id(self.id)
        self.set_ch(self.ch)
        self.set_vl(self.vl)
        self.set_st(self.st)
        print(self.get_stat())

    def rcv_clear(self):
        while self.rcv():
            pyb.delay(1)
            
    def set_ch(self, x):
        rst = ''
        self.rcv_clear()
        while not rst:# != b'SETCH:%s\r\n' %x:
            self.ser.write('ATCH:%s\r\n' %x)
            rst = self.ser.readall()
        self.ch = x
        return rst.strip()

    def set_vl(self, x):
        rst = ''
        self.rcv_clear()
        while not rst:# != b'SETVL:%02d\r\n' %x:
            self.ser.write('ATVL:%02d\r\n' %x)
            rst = self.ser.readall()
        self.vl = x
        return rst.strip()

    def set_id(self, x):
        rst = ''
        self.rcv_clear()
        while not rst:# != 'SETID\r\n':
            self.ser.write('ATID:%s\r\n' %x)
            rst = self.ser.readall()
        self.id = x
        return rst.strip()

    def set_st(self, x):
        rst = ''
        self.rcv_clear()
        while not rst:# != b'SETST:%s\r\n' %x:
            self.ser.write('ATST:%s\r\n' %x)
            rst = self.ser.readall()
        self.st = x
        return rst.strip()
        
    def rssi(self):
        rst = ''
        self.rcv_clear()
        while not rst:# != b'SETST:%s\r\n' %x:
            self.ser.write('SETPH:\r\n')
            rst = self.ser.readall()
        return rst[8]&0xf
        
    def rcv(self):
        return self.ser.readall()

    def get_stat(self):
        self.rcv_clear()
        return self.id, self.ch, self.vl, self.st, self.rssi()


class LCD:
    def __init__(self):
        """
        cs  高有效
        写指令: 0b11111000(0xf8) + 高四位xxxx0000 + 低四位xxxx0000
        写数据: 0b11111010(0xfa) + 高四位xxxx0000 + 低四位xxxx0000
        """
        self.spi = pyb.SPI(1, pyb.SPI.MASTER, baudrate=200000, polarity=0, phase=0)
        self.cs = pyb.Pin('X5', pyb.Pin.OUT_PP, pyb.Pin.PULL_UP)
        self.send_cmd(0x30)  # set mode base
        #self.lcd.send_cmd(0x34)  # set mode ext
        self.send_cmd(0x0c)  # display on, cursor off, select off
        self.send_cmd(0x01)  # clear
        self.send_cmd(0x06)  # cursor right move

    def send_cmd(self, cmd):
        self.cs.high()
        self.spi.send(0xf8)
        pyb.delay(1)
        self.spi.send(cmd&0xf0)
        pyb.delay(1)
        self.spi.send(cmd<<4&0xf0)
        pyb.delay(1)
        self.cs.low()
        
    def send_dat(self, dat, y=None, x=None):
        if (x and y) is not None:
            if y == 0:
                addr = 0x80 + x
            elif y == 1:
                addr = 0x90 + x
            elif y == 2:
                addr = 0x88 + x
            elif y == 3:
                addr = 0x98 + x
            self.send_cmd(0x30)
            self.send_cmd(addr)
        
        self.send_cmd(0x30)
        self.cs.high()
        self.spi.send(0xfa)
        if isinstance(dat, type(1)):
            self.spi.send(dat&0xf0)
            pyb.delay(1)
            self.spi.send(dat<<4&0xf0)
            pyb.delay(1)
        elif isinstance(dat, type(b'')):
            for d in dat:
                self.spi.send(d&0xf0)
                pyb.delay(1)
                self.spi.send(d<<4&0xf0)
                pyb.delay(1)
        elif isinstance(dat, type('')):
            for d in dat:
                d = ord(d)
                self.spi.send(d&0xf0)
                pyb.delay(1)
                self.spi.send(d<<4&0xf0)
                pyb.delay(1)
        self.cs.low()

    def clear(self, y=4):
        self.send_cmd(0x30)
        if y >= 0 and y <= 3:
            self.send_dat(' '*16, y, 0)
        else:
            self.send_cmd(1)
            pyb.delay(1)


class KEY:
    def __init__(self):
        self.i2c = pyb.I2C(2, pyb.I2C.MASTER, baudrate=100000)
        self.rst()
        
    def read(self, dat):
        return self.i2c.mem_read(dat, 0x58, 0x10, timeout=500)
               
    def write(self, dat):
        self.i2c.mem_write(dat, 0x58, 0x08)
    
    def rst(self):
        RSTB.low()
        pyb.delay(1)
        RSTB.high()


class DTMF:
    def __init__(self):
        self.rcv = 0
        self.prercv_time = 0
        self.D0 = pyb.Pin('X19', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.D1 = pyb.Pin('X20', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.D2 = pyb.Pin('X21', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.D3 = pyb.Pin('X22', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        DG_EN.value(1)  # 输出无效
        DDO_EN.value(0) # 输出无效
        
    def set(self, nl):
        self.D0 = pyb.Pin('X19', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
        self.D1 = pyb.Pin('X20', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
        self.D2 = pyb.Pin('X21', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
        self.D3 = pyb.Pin('X22', pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
        
        for n in nl:
            self.D0.value(n&1)
            self.D1.value(n&2)
            self.D2.value(n&4)
            self.D3.value(n&8)
            DG_EN.value(0)
            pyb.delay(200)
            DG_EN.value(1)
            pyb.delay(100)
            
        self.D0 = pyb.Pin('X19', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.D1 = pyb.Pin('X20', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.D2 = pyb.Pin('X21', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.D3 = pyb.Pin('X22', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        
    def get(self):
        if self.rcv > 9999 or pyb.elapsed_millis(self.prercv_time) > 1000: # 大于4位数或间隔大于1s
            self.rcv = 0
        
        DDO_EN.value(1)
        tmp = (self.D3.value()<<3) + (self.D2.value()<<2) + (self.D1.value()<<1) + self.D0.value()
        self.prercv_time = pyb.millis()
        DDO_EN.value(0)
        
        if tmp == 10:
            tmp = 0
        elif tmp > 10: # 或收到ABCD清零
            self.rcv = 0
            tmp = 0
        
        self.rcv = self.rcv * 10 + tmp # 等价于原数进一位加上本次数字
        print(self.rcv)
        

msg = b'\xce\xde\xcf\xdf\xb6\xd4\xbd\xb2\xcf\xb5\xcd\xb3'

if __name__ == '__main__':
    keybuf = bytearray(1)
    kl = b''
    off_flag = 0
    slaveID = ''
    currID = ''
    slave_list = ['0011', '0012', '0013', '0014', '0021', '0022', '0023', '0024']
    init()
    lcd = LCD()
    lcd.clear()
    fm = FM1288()
    dtmf = DTMF()
    rf = RF(id='10000000', ch=5, vl=12, st=0)
    rf.rcv_clear()
    key = KEY()
    key.write(0b1010000) #auto clear init
    
    rf_stat = rf.ch, rf.vl, rf.st
    lcd.send_dat(msg, 0, 1)
    lcd.send_dat(b'CH:%d VL:%02d ST:%d' %(rf.ch, rf.vl, rf.st), 1, 0)
    lcd.send_dat('----TIBOSHI----', 2, 0)
    lcd.send_dat(b'\xd7\xb4\xcc\xac\xa3\xba\xbe\xcd\xd0\xf7', 3, 0) # '状态：就绪'
    
    start = pyb.millis()
    
    rf.wbuf = 'SETPH:\r\n'
    def et2cb():
        global off_flag
        off_flag = 1
        
    def recive():
        pyb.disable_irq()
        if rf.ser.any():
            rf.ser.readinto(rf.rbuf)
            print(rf.rbuf)
        pyb.enable_irq()
        
    intbKEY.callback(lambda:key.read(keybuf))
    extint = pyb.ExtInt(DV, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE, lambda x:dtmf.get())
    extint2 = pyb.ExtInt(ANSWER, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE, lambda x:et2cb())
    extint2.disable()
##     t14 = pyb.Timer(14, freq=20)
##     t14.callback(lambda t:recive())
        
    def pick_off():
        global currID
        SP_EN.high()
        if currID:
            currID = '00%s%s' %(currID[2:6], PD)
            rf.set_id(currID)
##             rf.set_st(1)
        rf.set_st(1)
        rf.set_st(0)
        extint2.disable()
        PLARUN_LED.off()
        lcd.clear(3)
        lcd.send_dat(b'\xd7\xb4\xcc\xac\xa3\xba\xcd\xa8\xbb\xb0\xbd\xe1\xca\xf8', 3, 0) # 状态：通话结束
    
    def call(num):
        global currID, start
        for i in range(3):
            rf.set_id(num)
            rf.set_st(1)
            lcd.clear(3)
            lcd.send_dat(b'\xd7\xb4\xcc\xac\xa3\xba\xd5\xfd\xd4\xda\xba\xf4\xbd\xd0..', 3, 0) # 状态：正在呼叫..
            pyb.delay(1000)
            if rf.rssi():
                lcd.clear(3)
                lcd.send_dat(b'\xd7\xb4\xcc\xac\xa3\xba\xcd\xa8\xbb\xb0\xd6\xd0...', 3, 0) # 状态：通话中...
                SP_EN.low()
                extint2.enable()
                PLARUN_LED.on()
                currID = num
                start = pyb.millis()
                return
        rf.set_id(num[:6] + PD)
##         rf.set_st(1)
        rf.set_st(0)
        lcd.clear(3)
        lcd.send_dat(b'\xd7\xb4\xcc\xac\xa3\xba\xba\xf4\xbd\xd0\xca\xa7\xb0\xdc', 3, 0) # 状态：呼叫失败
        
    def response_key():
        global kl
        kp = keybuf[0]
        keybuf[0] = 0
        if kp in nkmap:
            if len(kl) < 4:
                kl += nkmap[kp]
            else:
                kl = nkmap[kp].encode()
            lcd.clear(2)        
            lcd.send_dat(b'\xba\xc5\xc2\xeb\xa3\xba' + kl, 2, 0) # 号码：kl
        elif kp in skmap:
            if skmap[kp] == 'cal':
                if kl:
                    call('00%04d%s' %(int(kl), CAL))
                else:
                    lcd.clear(3)
                    lcd.send_dat(b'\xc7\xeb\xcf\xc8\xb2\xa6\xba\xc5\xd4\xd9\xba\xf4\xbd\xd0', 3, 0) # 请先拨号再呼叫
            elif skmap[kp] == 'set':
                kl = b''
                lcd.clear(2)
                lcd.send_dat(b'\xba\xc5\xc2\xeb\xa3\xba', 2, 0) # 号码：
            elif skmap[kp] == 'vld':
                if rf.vl > 0:
                    rf.set_vl(rf.vl-1)
                lcd.clear(1) 
                lcd.send_dat(b'CH:%d VL:%02d ST:%d' %(rf.ch, rf.vl, rf.st), 1, 0)
            elif skmap[kp] == 'vlu':
                if rf.vl < 15:
                    rf.set_vl(rf.vl+1)
                lcd.clear(1) 
                lcd.send_dat(b'CH:%d VL:%02d ST:%d' %(rf.ch, rf.vl, rf.st), 1, 0)
            elif skmap[kp] == 'lck':
##                 rf.set_id(rf.id,PD)
##                 rf.set_st(1)
                pick_off()
            elif skmap[kp] == 'sch':
                lcd.clear(3)
                lcd.send_dat(b'RcvID:' + slaveID, 3, 0)
##                 lcd.send_dat(b'DRCV:' + str(dtmf.rcv), 3, 0)
            elif skmap[kp] == 'msg':
                extint.disable()
                dtmf.set([int(chr(i)) for i in kl])
                extint.enable()
                lcd.clear(3) 
                lcd.send_dat(b'Send DTMF:' + kl, 3, 0)
            elif skmap[kp] == 'rcd':
                rf.set_st(1)
                SP_EN.low()
                extint2.enable()
                lcd.clear(3)
                lcd.send_dat(b'SR ON', 3, 0)
        
    def rcv_id():
        rcv = rf.rcv()
        if len(rcv) >= 16:
            return ''.join([str(i&0xf) for i in rcv[6:14]])
        else:
            return ''
            
    def als_id(id):
        global currID, start, kl
        if id[2:6] in slave_list:
            if id[6:8] == CAL and rf.st == 0 and ANSWER.value() == 1:
                for i in range(3):
                    rf.set_st(2)
                    rf.set_st(2)
                    if rf.rssi():
                        rf.set_st(2)
                        extint2.enable()
                        PLARUN_LED.on()
                        SP_EN.low()
                        currID = id
                        kl = id[2:6].encode()
                        lcd.clear(2)
                        lcd.send_dat(b'\xba\xc5\xc2\xeb\xa3\xba' + kl, 2, 0) # 号码：
                        lcd.clear(3)
                        lcd.send_dat(b'\xb7\xd6\xbb\xfa' + kl + b'\xba\xf4\xbd\xd0', 3, 0) # 分机xx呼叫
                        start = pyb.millis()
                        while ANSWER.value():
                            dtmf.set([1])
                            pyb.delay(1000)
                            if pyb.elapsed_millis(start) > 20000:
                                pick_off()
                                break
                        start = pyb.millis()
                        break
            elif id[6:8] == PD and rf.st != 0:
                pass
##                 pick_off()
    
    def update_stat():
        global rf_stat
        if rf_stat != (rf.ch, rf.vl, rf.st):
            lcd.clear(1) 
            lcd.send_dat(b'CH:%d VL:%02d ST:%d' %(rf.ch, rf.vl, rf.st), 1, 0)
            rf_stat = rf.ch, rf.vl, rf.st
    
    def check_pd():
        global off_flag, start
        if off_flag:
            pick_off()
            off_flag = 0
            print('off')
        elif pyb.elapsed_millis(start) > 300:
            if not rf.rssi():
                pick_off()
                off_flag = 0
                print('off line')
            start = pyb.millis()

    while 1:
        slaveID = rcv_id()
        if slaveID and (slaveID != currID):
            print(currID, slaveID)
            currID = slaveID
            als_id(slaveID)
        
        response_key()
        
        if rf.st != 0:
            check_pd()
        update_stat()
