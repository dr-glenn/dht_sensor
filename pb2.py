# coding=utf-8
# Pushbutton demo.
# You can run it standalone or import to use the gpioInput class.
 
import RPi.GPIO as GPIO
import datetime
from functools import partial
 
class gpioInput:
    def __init__(self,pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        self.x = 1
        self.y = 2
        self.cb = partial(self.callback2, self.x)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.cb)
    def callback(self, channel):
        self.x += 1
        if GPIO.input(channel) == GPIO.HIGH:
            print('x = %d' %(self.x))
            print('▼  at ' + str(datetime.datetime.now()))
        else:
            print(' ▲ at ' + str(datetime.datetime.now())) 
    def callback2(self, x, channel):
        # callback2 is used with functools.partial.
        # Additional args appear first and then add_event_detect inserts channel as the last arg.
        self.x += 1
        print('cb2: channel=%d, x=%d self.x=%d' %(channel,x,self.x))

def my_callback(channel):
    if GPIO.input(6) == GPIO.HIGH:
        print('\n▼  at ' + str(datetime.datetime.now()))
    else:
        print('\n ▲ at ' + str(datetime.datetime.now())) 
 
def cb_func(p1, x, y):
    print('cb_func: %d %d %d' %(p1,x,y))

def main():
    gpIn = gpioInput(6)
    return gpIn

def main1():
    x1 = 5
    y1 = 7
    cb = lambda pin1,x=x1,y=y1: cb_func(pin1, x, y)

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(6, GPIO.IN)
        #GPIO.add_event_detect(6, GPIO.BOTH, callback=my_callback)
        GPIO.add_event_detect(6, GPIO.BOTH, callback=cb)
     
    finally:
        GPIO.cleanup()
 

if __name__ == '__main__':
    gpin = main()
    message = raw_input('\nPress any key to exit.\n')
    print('Exit: x=%d' %(gpin.x))
    GPIO.cleanup()
    print("Goodbye!")
