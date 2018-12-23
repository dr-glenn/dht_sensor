# dht_reader.py
# In order to have this run at boot time, edit "sudo crontab -e"
# Add this line in crontab "@reboot python /home/pi/src/DHT/dht_mqtt.py &"

'''
Reads DHT22 or DHT11 for temperature and humidity.
Also may read DS18B20 temp sensor.
This program is a MQTT client.
Posts data to MQTT broker. In this program the broker is the Cayenne cloud service.
Writes data to LOGFILE.
Optionally displays temp and humidity on LCD device.
'''

import os
import glob
import time
import cayenne.client as cayenne
import Adafruit_DHT # DHT device interface
import I2C_LCD_driver   # for LCD1602 device with backpack

LOGFILE = '/home/pi/mqtt.log'
HAS_LCD = True

DHT_TEMP_CHAN = 3   # channel for my Cayenne dashboard
DHT_HUMID_CHAN = 4
READ_DS18B20 = True
DS18_CHAN = 5
UPDATE_SECONDS = 30

# Assigned by Cayenne
MQTT_USERNAME  = "3c9f82b0-ae30-11e8-9bc2-335872d4b092"
MQTT_PASSWORD  = "d7e764d9f3df983ac9c302070df769ee8b1e096f"
MQTT_CLIENT_ID = "5df2add0-af06-11e8-85ea-f10189fd2756"

lcdHourOn = 6   # backlight turns on at this hour
lcdHourOff = 22 # don't want that bright backlight during the night

timestr = ""
temp22 = None
humid22 = None

########### Logging Setup ###########
import logging
from logging.handlers import RotatingFileHandler,TimedRotatingFileHandler
#handler = TimedRotatingFileHandler(LOGFILE, when='midnight', interval=1, backupCount=3)
handler = RotatingFileHandler(LOGFILE, maxBytes=50000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)
defLogger = logging.getLogger('')
defLogger.addHandler(handler)
defLogger.setLevel(logging.DEBUG)

logger = logging.getLogger('mqtt')

logger.info('start dht_mqtt')
if HAS_LCD:
    mylcd = I2C_LCD_driver.lcd()
    mylcd.backlight(0)  # start with backlight off
else:
    # no LCD hooked up
    mylcd = None

# Assume this program is run in crontab at startup
time.sleep(40) # Sleep to allow wireless to connect before starting MQTT

client = cayenne.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

timestamp = 0

# I don't have DHT11 device:
temp11 = None
humid11 = None
DHT_GPIO = 5    # R-pi GPIO data pin
 
def ds18b20_start():
    '''
    Setup for reading DS18B20.
    It is a system device on r-pi and leaves data in /sys/bus...

    :return: filename for device data
    '''
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
 
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    return device_file
 
def read_temp_raw(dev_file):
    '''
    Fetch recent data for DS18B20
    '''
    f = open(dev_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(dev_file):
    '''
    Read and parse data for DS18B20.

    :return: tuple of (temp C, temp F)
    '''
    lines = read_temp_raw(dev_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(dev_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    else:
        return (-100.0,-100.0)
	
def on_button():
    '''
    If button is pressed, display LCD even if during off hours
    '''
    global timestr, temp22, humid22
    lcd_show(timestr, temp22, humd22, True)

def lcd_show(timestr, temp22, hum22, override=False):
    '''
    Display temp and humid on local LCD display.
    '''
    global mylcd, lcdHourOn, lcdHourOff
    if mylcd:
        # turn off backlight at night
        hour = int(timestr.split(':')[0])
        if override or (hour >= lcdHourOn and hour < lcdHourOff):
            # Show time on line 1, T,H on line 2
            obsstr = ""
            mylcd.lcd_display_string(timestr, 1)
            obsstr += "T=%.1f%sF, " % (1.8*float(temp22)+32.0, chr(223))
            obsstr += "H=%d%%" % int(hum22)
            mylcd.lcd_display_string(obsstr, 2)
        else:
            # night time, make it dark
            mylcd.backlight(0)

if READ_DS18B20:
    dev_ds18b20 = ds18b20_start()

while True:
    client.loop()   # default timeout is 1 second. I think this actually blocks for 1 second.
    if (time.time() > timestamp + UPDATE_SECONDS):
        #humidity11, temp11 = Adafruit_DHT.read_retry(11, 18) #11 is the sensor type, 18 is the GPIO pin number that DATA wire is connected to
        humid22, temp22 = Adafruit_DHT.read_retry(22, DHT_GPIO) #22 is the sensor type, 5 is the GPIO pin number that DATA wire is connected to
        logger.info('temp=%.1f, hum=%.1f' %(float(temp22), float(humid22)))
        timestr = time.strftime("%H:%M:%S")
        obsstr = ""
        if temp11 is not None:
            client.virtualWrite(1, temp11, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        if humidity11 is not None:
            client.virtualWrite(2, humidity11, cayenne.TYPE_RELATIVE_HUMIDITY, cayenne.UNIT_PERCENT)
        if temp22 is not None:
            client.virtualWrite(DHT_TEMP_CHAN, temp22, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        if humid22 is not None:
            client.virtualWrite(DHT_HUMID_CHAN, humid22, cayenne.TYPE_RELATIVE_HUMIDITY, cayenne.UNIT_PERCENT)
        if READ_DS18B20:
            t_c,t_f = read_temp(dev_ds18b20)
            client.virtualWrite(DS18_CHAN, t_c, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        lcd_show(timestr, temp22, humid22)
        timestamp = time.time()
