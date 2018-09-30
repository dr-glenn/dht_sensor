# dht_reader.py
# Getting lots of ideas and code from Steve: http://www.steves-internet-guide.com/client-connections-python-mqtt/
import paho.mqtt.client as mqtt
import time
#import Adafruit_DHT

# Here are params to connect to Cayenne MQTT
MQTT_USERNAME  = "3c9f82b0-ae30-11e8-9bc2-335872d4b092"
MQTT_PASSWORD  = "d7e764d9f3df983ac9c302070df769ee8b1e096f"
MQTT_CLIENT_ID = "5df2add0-af06-11e8-85ea-f10189fd2756"
# v1/username/things/clientID/data/channel
TOPIC="v1/%s/things/%s/data/%d" %(MQTT_USERNAME,MQTT_CLIENT_ID,3)

def on_connect(mclient, userdata, flags, rc):
    if rc == 0:
        mclient.connected_flag = True
        print "connected OK"
    else:
        print "Bad connection, returned code=%d"%(rc)
        mclient.bad_connection_flag = True

def on_message(mclient, userdata, message):
    time.sleep(1)
    mclient.has_message = True
    print "received mesage =%s" %(str(message.payload.decode("utf-8")))

def on_subscribe(mclient, userdata, mid, granted_qos):
    print "Subscribed: %s" %(str(mid)+" "+str(granted_qos))

client = mqtt.Client(client_id="", clean_session=True, userdata=None, transport="tcp", protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
#client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
# Steve recommends adding a connect flag:
client.connected_flag = False
client.bad_connection_flag = False

client.loop_start()
client.connect("mqtt.mydevices.com", port=1883, keepalive=60, bind_address="")
while not client.connected_flag:
    print "Wait for connect"
    time.sleep(1)
print "Start Main loop"
client.has_message = False
client.on_subscribe = on_subscribe
client.on_message = on_message
result,msg_id = client.subscribe(TOPIC)
time_cnt = 0
while not client.has_message:
    time.sleep(5)
    time_cnt += 5
    print "waiting for message, t=%d" %(time_cnt)
client.unsubscribe(TOPIC)
client.disconnect()
client.loop_stop()

