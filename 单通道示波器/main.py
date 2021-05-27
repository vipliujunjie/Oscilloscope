import lpc55
import os
# execfile('Show_logo.py')

WHITE = const(0xFFFF)
BLACK = const(0x0000)
BLUE  = const(0x001F)
BRED  = const(0XF81F)
GRED  = const(0XFFE0)
RED   = const(0xF800)
MAGENTA=const(0xF81F)
GREEN = const(0x07E0)
CYAN  = const(0x7FFF)
YELLOW= const(0xFFE0)
BROWN = const(0XBC40)
BRRED = const(0XFC07)
GRAY  = const(0X8430)

SCREEN_WIDTH = const(240)   # 屏幕宽度
SCREEN_HEIGHT = const(240)  # 屏幕高度
SCOPE_HEIGHT = const(200)   # 波形区域高度
SCOPE_WIDTH = SCREEN_WIDTH-10
SCOPE_GRID = 30
WAVE_NUM = const(5)         # 波形数目
WAVE_HEIGHT = SCOPE_HEIGHT//WAVE_NUM

import math
import lpc55
from lpc55 import SPI
from lpc55 import Pin
from display import LCD154

class Panel():
    def __init__(self, id, rst, cs):
        lcd_spi = lpc55.SPI(id, SPI.MASTER, baudrate=50000000, polarity=1, phase=1)
        lcd_rst=Pin(rst, Pin.OUT, pull=Pin.PULL_UP, value=1)
        if cs:
            lcd_cs =Pin(cs, Pin.OUT, pull=Pin.PULL_UP, value=0)
        self.lcd = LCD154(lcd_spi, lcd_rst)
        if not cs:
            self.lcd.orientation(2)         # This LCD is placed up side down 
        self.fb0 = self.lcd.getframe()      # Get the basic framebuf
        self.fb0.clear(BROWN)
        self.fb0.string(18,0,"Oscilloscope DEMO", color=BLACK, font=24,mode=1)  # Top banner

    def setup(self, color_table):
        BANNER_HEIGHT = 24
        Scope_x = (SCREEN_WIDTH-SCOPE_WIDTH)//2
        self.ss = self.lcd.scope(Scope_x,BANNER_HEIGHT,SCOPE_WIDTH,SCOPE_HEIGHT,
                                    bits=3,lut=color_table)
        self.ss.clear(0)
        self.ss.color(5,2)

        y_low_banner = BANNER_HEIGHT + SCOPE_HEIGHT
        self.fb0.line(0, y_low_banner, SCREEN_WIDTH, y_low_banner,
                        size=16, color=0xE79C)    # 绘制下面的刻度条
        for x in range(SCOPE_GRID, SCOPE_WIDTH, SCOPE_GRID):
            self.ss.line(x, 0, x, SCOPE_HEIGHT, color=6)
            marker_x = Scope_x + x - len(str(x)) * 4
            # 显示刻度字体
            self.fb0.string(marker_x, y_low_banner, str(x), font=16, color=0x1C, mode=1)
        for y in range(SCOPE_GRID, SCOPE_HEIGHT, SCOPE_GRID):
            self.ss.line(0, y, SCOPE_WIDTH, y, color=6)

        self.ss.string(48,10,"Hello World!", font=24) # 字体居上
        self.ss.show()

        # Create channels
        WAVE_COLOR = (RED, GREEN, BLUE, YELLOW, MAGENTA)
        self.ch1 = self.ss.channel(1)
        self.ch1.init(SCOPE_HEIGHT, GREEN, offset=0, ratio=1/328)
        # self.ch2 = self.ss.channel(2)
        # self.ch2.init(SCOPE_HEIGHT//2, YELLOW, offset=0, ratio=0.5)

lcd1 = Panel(8,'PIO1_3','PIO0_20')
lcd1.setup((BLACK, WHITE, RED, GREEN, BLUE, YELLOW, 0x300, MAGENTA))

####################################################################
### Define 2 ADC pins
from lpc55 import ADC
ADC_IN_CH1 = ADC('PIO1_0')
adc2 = ADC('PIO1_9')

ADC_IN_CH1.mode(sample=0, average=0)
adc2.mode(sample=0, average=0)
 
NUM_SAMPLE = 1024
### Read ADC_IN_CH1 at 500kHz rate to a buffer (length is defined by NUM_SAMPLE)
from lpc55 import CTimer
import uarray

# Configure a CTimer to have 500kHz wave
<<<<<<< HEAD
t4 = CTimer(4, 14)	   # Config CTimer4, Prescaler = 15. Get 10MHz
t4_3 = t4.channel(3)    # Channel 3
t4_3.action(CTimer.COUNTER_RESET | CTimer.MATCH_TOGGLE)   # On match to reset counter and toggle output
t4_3.match(10)   			# 10MHz / 20 = 500,000Hz
=======
t4 = CTimer(4, 14)     # Config CTimer4, Prescaler = 15. Get 10MHz
t4_3 = t4.channel(3)    # Channel 3
t4_3.action(CTimer.COUNTER_RESET | CTimer.MATCH_TOGGLE)   # On match to reset counter and toggle output
t4_3.match(10)              # 10MHz / 20 = 500,000Hz
>>>>>>> 5923824... 初始化

buffer = uarray.array('H', (0,)*NUM_SAMPLE)      # setup a 2K elements (unsigned short) array
finish = False

# Callback function to set finish flag
def adc_callback(x):
    global finish
    finish = True

<<<<<<< HEAD
ADC_IN_CH1.callback(adc_callback)		# setup the callback funtion
=======
ADC_IN_CH1.callback(adc_callback)       # setup the callback funtion
>>>>>>> 5923824... 初始化

# Getting ADC data to buffer
def grab_data():
    global finish
    finish = False
<<<<<<< HEAD
    t4.enable()			# Start the CTimer4 running
    ADC_IN_CH1.read_timed(buffer, t4)
    print("buffer:"buffer)
    while not finish:		# Wait for end of conversion
        pass
    t4.enable(False)		# Stop CTimer4
=======
    t4.enable()         # Start the CTimer4 running
    ADC_IN_CH1.read_timed(buffer, t4)
    print("buffer:", buffer)
    while not finish:       # Wait for end of conversion
        pass
    t4.enable(False)        # Stop CTimer4
>>>>>>> 5923824... 初始化

# Plot the wave
def draw():
    STEP = 1        # Show 1 sample in every 5 samples
    for x in range(0, NUM_SAMPLE, STEP):
        lcd1.ch1.value(buffer[x])
        if x % (5*STEP) == 0:   # Speed is 5
            lcd1.ss.refresh()

# lcd1.ch1.scale(-1300,0.05)
while True:
    grab_data()
    draw()



<<<<<<< HEAD
=======

>>>>>>> 5923824... 初始化
