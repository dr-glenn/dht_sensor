import time
import paho.mqtt.client as paho
import dht
broker="broker.hivemq.com"
broker="iot.eclipse.org"
MQTT_PORT = 1883

#define callbacks
def on_publish(client, userdata, mID):
    print("publish msg ID=%d"%(int(mID)))

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message = %s" %str(message.payload.decode("utf-8")))

client= paho.Client("gdn-client-001") #create client object

###### Bind functions to callback
client.on_publish = on_publish #assign function to callback
client.on_message=on_message

#####
print("connecting to broker %s" %broker)
client.connect(broker, MQTT_PORT)
client.loop_start() #start loop to process received messages
print("subscribing ")
client.subscribe("house/bulb1")#subscribe
client.subscribe("house/temp1")#subscribe
time.sleep(2)
print("publishing ")
client.publish("house/bulb1","on")#publish
temp,humid = dht.read_dht(dht.DHT_TYPE,dht.DHT_PIN)
client.publish("house/temp1","%.1f, %.1f%%" %(float(temp),float(humid)))  #publish
time.sleep(4)
client.disconnect() #disconnect
client.loop_stop() #stop loop

