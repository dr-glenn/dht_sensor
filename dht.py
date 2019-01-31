# coding=utf-8
# dht_reader.py

'''
Reads DHT22 or DHT11 for temperature and humidity.
Also may read DS18B20 temp sensor.
'''

import os
import glob
import time
import Adafruit_DHT # DHT device interface

READ_DS18B20 = False
DHT_TYPE=22
DHT_PIN=5

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

if READ_DS18B20:
    dev_ds18b20 = ds18b20_start()

def read_dht(dht_type, dht_gpio):
    #22 is the sensor type, 5 is the GPIO pin number that DATA wire is connected to
    humid, temp = Adafruit_DHT.read_retry(dht_type, dht_gpio)
    return temp,humid
