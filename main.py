from machine import Pin, I2C
import machine
import ssd1306
import random
from time import sleep
from time import time
import os
import framebuf
import network

# using default address 0x3C
i2c = I2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

p12 = Pin(12, Pin.IN, Pin.PULL_UP)
p13 = Pin(13, Pin.IN, Pin.PULL_UP)

die_size = [4,4,4,4,4,4]
die_index = 0

sleeptimer = 0

def reshuf():
    bits = 3
    for i in [0,1,2,3,4,5]:
        random.seed()
        bits = (die_size[i]+2)//2
        num = random.getrandbits(bits)
        while num < 1 or num > die_size[i]:
            num = random.getrandbits(bits)
        drawDie(i,num)

def gotobed(p):
    display.fill(0)
    display.text('BYE',56,28,1)
    display.show()
    sleep(2)
    display.fill(0)
    display.show()
    machine.deepsleep()

def drawDieConfig(position):
    #display.fill(0)
    drawDie(position,die_size[position])
    if position == die_index:
        if position == 0:
            offsetx = 0
            offsety = 0
        if position == 1:
            offsetx = 44
            offsety = 0
        if position == 2:
            offsetx = 88
            offsety = 0
        if position == 3:
            offsetx = 0
            offsety = 32
        if position == 4:
            offsetx = 44
            offsety = 32
        if position == 5:
            offsetx = 88
            offsety = 32

        #display.fill_rect(offsetx, offsety, 12, 12, 0)
        #display.text("*",2+offsetx,2+offsety,1)
        display.rect(offsetx, offsety, 41, 31, 1)
        display.show()

def drawDie(position,value):
    if position == 0:
        offsetx = 0
        offsety = 0
    if position == 1:
        offsetx = 44
        offsety = 0
    if position == 2:
        offsetx = 88
        offsety = 0
    if position == 3:
        offsetx = 0
        offsety = 32
    if position == 4:
        offsetx = 44
        offsety = 32
    if position == 5:
        offsetx = 88
        offsety = 32

    if die_size[position] in [4,6,8,10,12,20]:
        printDado(die_size[position],value,offsetx,offsety)
    else:
        display.fill_rect(2+offsetx, 4+offsety, 42, 32, 0)
        display.rect(2+offsetx, 4+offsety, 32, 28, 1)
        display.text(str(value),15+offsetx,15+offsety,1)
        display.show()

def cycleDieSides(p):
    global die_size
    global sleeptimer
    sleeptimer = time()
    die_size[die_index] += 1
    if die_size[die_index] == 5: die_size[die_index] = 6
    if die_size[die_index] == 7: die_size[die_index] = 8
    if die_size[die_index] == 9: die_size[die_index] = 10
    if die_size[die_index] == 11: die_size[die_index] = 12
    if die_size[die_index] in [13,14,15,16,17,18,19]: die_size[die_index] = 20
    if die_size[die_index] >= 21: die_size[die_index] = 4
    drawDieConfig(die_index)

def cycleDie(p):
    global die_index
    global sleeptimer
    sleeptimer = time()
    file = open("cfg.txt", "w")
    cfg = ','.join(str(x) for x in die_size)
    file.write(cfg)
    file.close()
    die_index += 1
    if die_index >= 6: die_index = 0
    for i in [0,1,2,3,4,5]:
        drawDieConfig(i)


def printDado(die_size,side,x,y):
    print("display image")
    img = "d"
    img += str(die_size)
    img += "l"
    img += str(side)
    img += ".pbm"
    with open(img,'rb') as f:
        f.readline()       # Image format
        f.readline()       # explanatory note
        f.readline()       # Image size
        data = bytearray(f.read())
    fbuf = framebuf.FrameBuffer(data, 41, 31, framebuf.MONO_HLSB)
    #display.invert(1)
    display.blit(fbuf, x, y)
    display.show()


#p13.irq(trigger=Pin.IRQ_FALLING, handler=cycleDie)
#p12.irq(trigger=Pin.IRQ_FALLING, handler=cycleDieSides)

###################################################
###################################################
#file.write(str(die_size[0]))
print("loading config")
file = open("cfg.txt", "r")
cfg = file.read()
file.close()
die_size_str = cfg.split(',', 6)
die_size[0] = int(die_size_str[0])
die_size[1] = int(die_size_str[1])
die_size[2] = int(die_size_str[2])
die_size[3] = int(die_size_str[3])
die_size[4] = int(die_size_str[4])
die_size[5] = int(die_size_str[5])
die_index = 0

reshuf()

sleeptimer = time()

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

while True:
    #print("running")
    if p12.value() == 0:
        cycleDie(0)
        print("cycleDie")
        sleep(0.1)
    if p13.value() == 0:
        cycleDieSides(0)
        print("cycleDieSides")
        sleep(0.1)
    
    if (time() - sleeptimer) > 30:
        gotobed(0)
