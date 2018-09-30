# dht_reader.py
import cayenne.client as cayenne
import time
import Adafruit_DHT


time.sleep(60) #Sleep to allow wireless to connect before starting MQTT

MQTT_USERNAME  = "3c9f82b0-ae30-11e8-9bc2-335872d4b092"
MQTT_PASSWORD  = "d7e764d9f3df983ac9c302070df769ee8b1e096f"
MQTT_CLIENT_ID = "5df2add0-af06-11e8-85ea-f10189fd2756"

client = cayenne.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

timestamp = 0

temp11 = None
humidity11 = None

while True:
    client.loop()
    if (time.time() > timestamp + 120):
        #humidity11, temp11 = Adafruit_DHT.read_retry(11, 18) #11 is the sensor type, 18 is the GPIO pin number that DATA wire is connected to
        humidity22, temp22 = Adafruit_DHT.read_retry(22, 5) #22 is the sensor type, 19 is the GPIO pin number that DATA wire is connected to

        if temp11 is not None:
            client.virtualWrite(1, temp11, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        if humidity11 is not None:
            client.virtualWrite(2, humidity11, cayenne.TYPE_RELATIVE_HUMIDITY, cayenne.UNIT_PERCENT)
        if temp22 is not None:
            #print 'temp22='+str(temp22)
            client.virtualWrite(3, temp22, cayenne.TYPE_TEMPERATURE, cayenne.UNIT_CELSIUS)
        if humidity22 is not None:
            client.virtualWrite(4, humidity22, cayenne.TYPE_RELATIVE_HUMIDITY, cayenne.UNIT_PERCENT)
        timestamp = time.time()
