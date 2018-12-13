# dht_reader.py
# In order to have this run at boot time, edit "sudo crontab -e"
# Add this line in crontab "@reboot python /home/pi/src/DHT/dht_mqtt.py &"

import os
import glob
import time
import cayenne.client as cayenne
import Adafruit_DHT
import I2C_LCD_driver
import logging
from logging.handlers import RotatingFileHandler,TimedRotatingFileHandler
#handler = TimedRotatingFileHandler('mqtt.log', when='midnight', interval=1, backupCount=3)
handler = RotatingFileHandler('/home/pi/mqtt.log', maxBytes=50000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)
defLogger = logging.getLogger('')
defLogger.addHandler(handler)
defLogger.setLevel(logging.DEBUG)

logger = logging.getLogger('mqtt')

logger.info('start dht_mqtt')
if True:
    mylcd = I2C_LCD_driver.lcd()
    mylcd.backlight(0)
else:
    mylcd = None

# Assume this program is run in crontab at startup
time.sleep(40) # Sleep to allow wireless to connect before starting MQTT

DHT_TEMP_CHAN = 3
DHT_HUMID_CHAN = 4
READ_DS18B20 = True
DS18_CHAN = 5
UPDATE_SECONDS = 30

# Assigned by Cayenne
MQTT_USERNAME  = "3c9f82b0-ae30-11e8-9bc2-335872d4b092"
MQTT_PASSWORD  = "d7e764d9f3df983ac9c302070df769ee8b1e096f"
MQTT_CLIENT_ID = "5df2add0-af06-11e8-85ea-f10189fd2756"

client = cayenne.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

timestamp = 0

temp11 = None
humidity11 = None
 
def ds18b20_start():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
 
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    return device_file
 
def read_temp_raw(dev_file):
    f = open(dev_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(dev_file):
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
	
def lcd_show(timestr, temp22, hum22):
    global mylcd
    if mylcd:
        # turn off backlight at night
        hour = int(timestr.split(':')[0])
        if hour < 6 or hour >= 22:
            mylcd.backlight(0)
        else:
            if True:
                # Show time on line 1, T,H on line 2
                obsstr = ""
                mylcd.lcd_display_string(timestr, 1)
                obsstr += "T=%.1f%sF, " % (1.8*float(temp22)+32.0, chr(223))
                obsstr += "H=%d%%" % int(hum22)
                mylcd.lcd_display_string(obsstr, 2)
            else:
                # if not timestr, then temp and hum each get a line of the display
                mylcd.lcd_display_string("Temp: %.1f%s F" % (1.8*float(temp22)+32.0, chr(223)), 1)
                mylcd.lcd_display_string("Humidity: %d%%" % int(hum22), 2)

if READ_DS18B20:
    dev_ds18b20 = ds18b20_start()

while True:
    client.loop()   # default timeout is 1 second. I think this actually blocks for 1 second.
    if (time.time() > timestamp + UPDATE_SECONDS):
        #humidity11, temp11 = Adafruit_DHT.read_retry(11, 18) #11 is the sensor type, 18 is the GPIO pin number that DATA wire is connected to
        humidity22, temp22 = Adafruit_DHT.read_retry(22, 5) #22 is the sensor type, 19 is the GPIO pin number that DATA wire is connected to
        logger.info('temp=%.1f, hum=%.1f' %(float(temp22), float(humidity22)))
        timestr = time.strftime("%H:%M:%S")
        obsstr = ""
        if temp11 is not None:
            client.virtualWrite(1, temp11, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        if humidity11 is not None:
            client.virtualWrite(2, humidity11, cayenne.TYPE_RELATIVE_HUMIDITY, cayenne.UNIT_PERCENT)
        if temp22 is not None:
            client.virtualWrite(DHT_TEMP_CHAN, temp22, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        if humidity22 is not None:
            client.virtualWrite(DHT_HUMID_CHAN, humidity22, cayenne.TYPE_RELATIVE_HUMIDITY, cayenne.UNIT_PERCENT)
        if READ_DS18B20:
            t_c,t_f = read_temp(dev_ds18b20)
            client.virtualWrite(DS18_CHAN, t_c, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        lcd_show(timestr, temp22, humidity22)
        timestamp = time.time()
