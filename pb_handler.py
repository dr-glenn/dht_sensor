# coding=utf-8
# Example of button push. Hook up button with both pullup (330)
# and pulldown (2K?) resistors.
# Enable the GPIO to detect both rising and falling edges.
# Write a message.
# When user presses and key, exit the program.

import RPi.GPIO as GPIO
import datetime
 
BUTTON_PIN = 6

def my_callback(channel):
    if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        print('\n▼  at ' + str(datetime.datetime.now()))
    else:
        print('\n ▲ at ' + str(datetime.datetime.now())) 
 
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=my_callback)
 
    message = raw_input('\nPress any key to exit.\n')
 
finally:
    GPIO.cleanup()
 
print("Goodbye!")

if __name__ == '__main__':
    pass
