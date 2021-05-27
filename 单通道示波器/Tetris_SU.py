#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial
This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

# from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
# from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
# from PyQt5.QtGui import QPainter, QColor
import random
import machine
from lpc55 import Pin, SPI
from lpc55 import CTimer
from display import LCD154

import time

FIELD_X = 70
FIELD_Y = 0

FIELD_WIDTH =100
FIELD_HEIGHT=240

Key_P       = b'p'
Key_Left    = b'j'
Key_Right   = b'l'
Key_Down    = b'k'
Key_Up      = b'i'
Key_Space   = b' '
Key_D       = b'd'

KeyStruct = {
    'PIO1_18': [Key_Down, 0, None],     # rotateRight, [key-value,  ticks, Pin obj]
    'PIO1_28': [Key_Space, 0, None],    # drop down
    'PIO1_31': [Key_Left, 0, None],     # move left
    'PIO1_29': [Key_Right, 0, None],    # move right
    'PIO1_30': [Key_Up, 0, None],       # rotateLeft
}
DEBOUNCE_MS = 120

WHITE = const(0xFFFF)
BLACK = const(0x0000)
BLUE  = const(0x001F)
BRED  = const(0XF81F)
GRED  = const(0XFFE0)
RED   = const(0xF800)
MAGENTA=const(0xF81F)
GREEN = const(0x07E0)
CYAN  = const(0x07FF)
YELLOW= const(0xFFE0)
BROWN = const(0XBC40)
BRRED = const(0XFC07)
GRAY  = const(0X8430)

class Tetris(object):
    Speed = 300

    def __init__(self, ks, lcd):

        # self.initUI()
        self.key_hand = ks
        self.tboard = Board(self)
        self.tboard.set_painter(lcd.lcd)
        self.tboard.start()

    def timerCB(self, hundred_ms):
        # print('hundred_ms = ', hundred_ms)
        keys = self.key_hand.Key_Values
        for k in keys:
            self.tboard.keyPressEvent(k)
        self.key_hand.Key_Values.clear()

        if hundred_ms % (self.Speed//100) == 0:
            self.tboard.timerEvent()

class Board():
#    msg2Statusbar = pyqtSignal(str)
   BoardWidth = 10
   BoardHeight = 24

   def __init__(self, parent):
    #    super().__init__(parent)
       self.initBoard()

   def initBoard(self):
       '''initiates board'''
    #    self.timer = QBasicTimer()
       self.isWaitingAfterLine = False

       self.curX = 0
       self.curY = 0
       self.numLinesRemoved = 0
       self.board = []

    #    self.setFocusPolicy(Qt.StrongFocus)
       self.isStarted = False
       self.isPaused = False
       self.clearBoard()

   def set_painter(self, lcd):
       # color = lambda x: ((x & 0xF80000) >> 8) | ((x & 0xFC00) >> 5) | (( x & 0xF8) >> 3)
    #    Colors = (0x0, 0xCB2C, 0x666C, 0x6339, 0xCE6C, 0xCB39, 0x6679, 0xDD00)
       Colors = (BLACK, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE)
       self.painter = lcd.framebuf(FIELD_X-2, FIELD_Y, FIELD_WIDTH+2*2, FIELD_HEIGHT, bits=4, lut=Colors)
       self.painter.clear(0)

   def shapeAt(self, x, y):
       '''determines shape at the board position'''
       try:
          return self.board[(y * Board.BoardWidth) + x]
       except IndexError:
          return Tetrominoe.NoShape

   def setShapeAt(self, x, y, shape):
       '''sets a shape at the board'''

       self.board[(y * Board.BoardWidth) + x] = shape


   def squareWidth(self):
       '''returns the width of one square'''

       return FIELD_WIDTH // Board.BoardWidth
    #    return self.contentsRect().width() // Board.BoardWidth

   def squareHeight(self):
       '''returns the height of one square'''
       return FIELD_HEIGHT // Board.BoardHeight
    #    return self.contentsRect().height() // Board.BoardHeight

   def start(self):
       '''starts game'''

       if self.isPaused:
           return

       self.isStarted = True
       self.isWaitingAfterLine = False
       self.numLinesRemoved = 0
       self.clearBoard()

    #    self.msg2Statusbar.emit(str(self.numLinesRemoved))
       print(str(self.numLinesRemoved))

       self.newPiece()

    #    self.timer.start(Board.Speed, self)

   def pause(self):
       '''pauses game'''

       if not self.isStarted:
           return

       self.isPaused = not self.isPaused

       if self.isPaused:
        #    self.timer.stop()
        #    self.msg2Statusbar.emit("paused")
           print('Paused')

       else:
        #    self.timer.start(Board.Speed, self)
        #    self.msg2Statusbar.emit(str(self.numLinesRemoved))
           print(str(self.numLinesRemoved))

       self.update()


#    def paintEvent(self, event):
   def update(self):
       '''paints all shapes of the game'''

    #    print(".",end='')
    #    painter = QPainter(self)
    #    rect = self.contentsRect()
       self.painter.clear(0)

    #    boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()
       boardTop = FIELD_HEIGHT - Board.BoardHeight * self.squareHeight()

       for i in range(Board.BoardHeight):
           for j in range(Board.BoardWidth):
               shape = self.shapeAt(j, Board.BoardHeight - i - 1)

               if shape != Tetrominoe.NoShape:
                   self.drawSquare(self.painter,
                       2 + j * self.squareWidth(),
                    #    rect.left() + j * self.squareWidth(),
                       boardTop + i * self.squareHeight(), shape)

       if self.curPiece.shape() != Tetrominoe.NoShape:
        #    print("%d" % self.curPiece.shape(), end='')
           for i in range(4):
               x = self.curX + self.curPiece.x(i)
               y = self.curY - self.curPiece.y(i)
            #    self.drawSquare(painter, rect.left() + x * self.squareWidth(),
               self.drawSquare(self.painter, 2 + x * self.squareWidth(),
                   boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                   self.curPiece.shape())

       if not self.isStarted:
          self.painter.color(4, 1)
          self.painter.string(20, 80, 'Game', font=32)
          self.painter.string(20, 80+32, 'Over', font=32)
       self.painter.show()
    #    for pt in self.painter:
    #        pt.dma_refresh()

   def keyPressEvent(self, key):
       '''processes key press events'''
       if not self.isStarted and key == Key_Space:
           key = Key_P
       if not self.isStarted and key == Key_P:  # Ping add this for re-start
           self.isPaused = False
           self.start()
           return

       if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
        #    super(Board, self).keyPressEvent(event)
           return

    #    key = event.key()

       if key == Key_P:
           self.pause()
           return

       if self.isPaused:
           return

       elif key == Key_Left:
           self.tryMove(self.curPiece, self.curX - 1, self.curY)

       elif key == Key_Right:
           self.tryMove(self.curPiece, self.curX + 1, self.curY)

       elif key == Key_Down:
           self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

       elif key == Key_Up:
           self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

       elif key == Key_Space:
           self.dropDown()

       elif key == Key_D:
           self.oneLineDown()


   def timerEvent(self):
       '''handles timer event'''

       if self.isPaused:
           return       # Do nothing when paused

       if self.isWaitingAfterLine:
          self.isWaitingAfterLine = False
          self.newPiece()
       else:
          self.oneLineDown()

   def clearBoard(self):
       '''clears shapes from the board'''

       self.board.clear()       # Ping add this. Important for re-start
       for i in range(Board.BoardHeight * Board.BoardWidth):
           self.board.append(Tetrominoe.NoShape)


   def dropDown(self):
       '''drops down a shape'''
       newY = self.curY

       while newY > 0:
           if not self.tryMove(self.curPiece, self.curX, newY - 1):
               break
           newY -= 1
       self.pieceDropped()

   def oneLineDown(self):
       '''goes one line down with a shape'''

       if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
           self.pieceDropped()


   def pieceDropped(self):
       '''after dropping shape, remove full lines and create new shape'''

       for i in range(4):

           x = self.curX + self.curPiece.x(i)
           y = self.curY - self.curPiece.y(i)
           self.setShapeAt(x, y, self.curPiece.shape())

       self.removeFullLines()

       if not self.isWaitingAfterLine:
           self.newPiece()


   def removeFullLines(self):
       '''removes all full lines from the board'''

       numFullLines = 0
       rowsToRemove = []

       for i in range(Board.BoardHeight):

           n = 0
           for j in range(Board.BoardWidth):
               if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                   n = n + 1

           if n == 10:
               rowsToRemove.append(i)

       rowsToRemove.reverse()

       for m in rowsToRemove:

           for k in range(m, Board.BoardHeight):
               for l in range(Board.BoardWidth):
                       self.setShapeAt(l, k, self.shapeAt(l, k + 1))

       numFullLines = numFullLines + len(rowsToRemove)

       if numFullLines > 0:

           self.numLinesRemoved = self.numLinesRemoved + numFullLines
        #    self.msg2Statusbar.emit(str(self.numLinesRemoved))
           print(str(self.numLinesRemoved))

           self.isWaitingAfterLine = True
           self.curPiece.setShape(Tetrominoe.NoShape)
           self.update()


   def newPiece(self):
       '''creates a new shape'''

       self.curPiece = Shape()
       self.curPiece.setRandomShape()
       self.curX = Board.BoardWidth // 2 + 1
       self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

       if not self.tryMove(self.curPiece, self.curX, self.curY):

           self.curPiece.setShape(Tetrominoe.NoShape)
        #    self.timer.stop()
        #    self.isStarted = False
        #    self.msg2Statusbar.emit("Game over")
           if self.isStarted:
               self.isStarted = False
               print("Game over")


   def tryMove(self, newPiece, newX, newY):
       '''tries to move a shape'''

       for i in range(4):

           x = newX + newPiece.x(i)
           y = newY - newPiece.y(i)

           if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
               return False

           if self.shapeAt(x, y) != Tetrominoe.NoShape:
               return False

       self.curPiece = newPiece
       self.curX = newX
       self.curY = newY
       self.update()

       return True

   def drawSquare(self, painter, x, y, shape):
       '''draws a square of a shape'''
       
       BLOCK = b'\xFF\xFF\xFF\xFF\xFF\xFF\x87\x03\x87\x03\x87\x03\x87\x03\xFF\xFF\xFF\xFF\xFF\xFF'
    #    BLOCK = b'\x00\x00' * 10
       painter.color(0, shape)
       painter.monoicon(x, y, 10, 10, BLOCK)

class Tetrominoe(object):

   NoShape = 0
   ZShape = 1
   SShape = 2
   LineShape = 3
   TShape = 4
   SquareShape = 5
   LShape = 6
   MirroredLShape = 7


class Shape(object):

   coordsTable = (
       ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
       ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
       ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
       ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
       ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
       ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
       ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
       ((1, -1),    (0, -1),    (0, 0),     (0, 1))
   )

   def __init__(self):

       self.coords = [[0,0] for i in range(4)]
       self.pieceShape = Tetrominoe.NoShape

       self.setShape(Tetrominoe.NoShape)


   def shape(self):
       '''returns shape'''

       return self.pieceShape


   def setShape(self, shape):
       '''sets a shape'''

       table = Shape.coordsTable[shape]

       for i in range(4):
           for j in range(2):
               self.coords[i][j] = table[i][j]

       self.pieceShape = shape


   def setRandomShape(self):
       '''chooses a random shape'''

       self.setShape(random.randint(1, 7))


   def x(self, index):
       '''returns x coordinate'''

       return self.coords[index][0]


   def y(self, index):
       '''returns y coordinate'''

       return self.coords[index][1]


   def setX(self, index, x):
       '''sets x coordinate'''

       self.coords[index][0] = x


   def setY(self, index, y):
       '''sets y coordinate'''

       self.coords[index][1] = y


   def minX(self):
       '''returns min x value'''

       m = self.coords[0][0]
       for i in range(4):
           m = min(m, self.coords[i][0])

       return m


   def maxX(self):
       '''returns max x value'''

       m = self.coords[0][0]
       for i in range(4):
           m = max(m, self.coords[i][0])

       return m


   def minY(self):
       '''returns min y value'''

       m = self.coords[0][1]
       for i in range(4):
           m = min(m, self.coords[i][1])

       return m


   def maxY(self):
       '''returns max y value'''

       m = self.coords[0][1]
       for i in range(4):
           m = max(m, self.coords[i][1])

       return m


   def rotateLeft(self):
       '''rotates shape to the left'''

       if self.pieceShape == Tetrominoe.SquareShape:
           return self

       result = Shape()
       result.pieceShape = self.pieceShape

       for i in range(4):

           result.setX(i, self.y(i))
           result.setY(i, -self.x(i))

       return result


   def rotateRight(self):
       '''rotates shape to the right'''

       if self.pieceShape == Tetrominoe.SquareShape:
           return self

       result = Shape()
       result.pieceShape = self.pieceShape

       for i in range(4):

           result.setX(i, -self.y(i))
           result.setY(i, self.x(i))

       return result

### Add this class to handle all keys ###########################

class Keys(object):
    Key_Values = []
    def __init__(self):
        for name in KeyStruct:
            pin = Pin(name, Pin.IN, pull=Pin.PULL_UP)
            pin.irq(Keys.key_cb, Pin.IRQ_FALLING)
            KeyStruct[name][1] = time.ticks_ms()
            KeyStruct[name][2] = pin

    def read_keys(self):
        keys = list(Keys.Key_Values)
        Keys.Key_Values.clear()
        return keys

    @staticmethod
    def key_cb(pin):
        now = time.ticks_ms()
        name = pin.name()
        key = KeyStruct[name]
        # debounce = DEBOUNCE_MS*2 if key[0] == Key_Space else DEBOUNCE_MS
        if now - key[1] > DEBOUNCE_MS:  # Check ticks
            if key[0] not in Keys.Key_Values and pin.value() == 0:
                Keys.Key_Values.append(key[0])
            # print(name)
        key[1] = now

class Panel():
    def __init__(self, id, rst, cs=None):
        lcd_spi = SPI(id, SPI.MASTER, bits=8, baudrate=50000000, polarity=1, phase=1)
        lcd_rst= Pin(rst, Pin.OUT, pull=Pin.PULL_UP, value=1)
        if cs:
            lcd_cs =Pin(cs, Pin.OUT, pull=Pin.PULL_UP, value=0)
        self.lcd = LCD154(lcd_spi, lcd_rst)
        if not cs:
            self.lcd.orientation(2)
        self.fb0 = self.lcd.getframe()    # Get the basic framebuf

    def setup(self, color_table):
        self.desk = self.lcd.framebuf(0, 0, 240, 240, bits=2, lut=color_table)
        self.desk.clear(0)
        self.desk.color(0,1)
        self.desk.show()
        # for x in range(20,240,20):
        #     self.desk.line(x, 0, x, SCREEN_HEIGHT)
        # for y in range(20,240,20):
        #     self.desk.line(0, y, SCREEN_WIDTH, y)
        # self.desk.string(24, 100, "Hello World!", color=3, font=32, mode=1)

        # self.ball  = self.lcd.framebuf(0, 100, 32, 32, bits=1, lut=(BLACK, RED))
        # self.ball.clear()
        # self.ball.circle(15,15,14,color=1,style=1)

    # def update(self):
    #     pos = self.track.next()
    #     if pos:
    #         self.ball.move(pos[0], pos[1])
    #         self.ball.showwith(self.desk, mode=1)


if __name__ == '__main__':

    try:
        timer.deinit()  # used to stop timer in 2nd launch
    except:
        pass
    
    lcd = Panel(8, 'PIO1_3', 'PIO0_20')
    lcd.setup( (0x8410, BLACK, GREEN, BLUE) )
        
    gif = open('Count_Down.gif', 'rb')
    lcd.fb0.loadgif(gif, loop=1)
    # lpc55.delay(1000)

    keys = Keys()
    tetris = Tetris(keys, lcd)

    def timerCB(sft):
        tetris.timerCB(sft.time_ms//100)

    timer = machine.Timer(-1)
    timer.init(freq=10, callback=timerCB)

