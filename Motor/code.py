import time
import board
import pwmio
from adafruit_motor import servo
import ssl
import socketpool
import wifi
from digitalio import DigitalInOut
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from secrets import secrets

# set up servo
pwm = pwmio.PWMOut(board.A12, duty_cycle=2 ** 15, frequency=50)
servo = servo.Servo(pwm)
rotationRange = 130
zeroAngle = 0

groupName = "thermostat"
fanSpeedFeed = "state/fan-speed"
fanToggleFeed = "state/fan-on"
fanSpeed = 2
fanOn = 1

wifi.radio.connect(secrets["ssid"], secrets["password"])
wifi.radio.ipv4_address
print("Connected to %s" % secrets["ssid"])

def connected(client):
    print("Connected to home assistant! Listening for changes...")
    mqttClient.subscribe(fanSpeedFeed)
    mqttClient.subscribe(fanToggleFeed)

def subscribe(client, userdata, topic, granted_qos):
    print ("Subscribed to {0} with QUOS level {1}".format(topic, granted_qos))

def unsubscribe(client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID level {1}".format(topic, pid))

def disconnected(client):
    print("Disconnected from IO")

def message(client, feed_id, payload):
    print(feed_id, payload)
    global fanSpeed
    global fanOn
    if feed_id == fanSpeedFeed:
        fanSpeed = int(payload)
    elif feed_id == fanToggleFeed:
        fanOn = int(payload)
    fanSpeed = fanSpeed * fanOn
    setFanSpeed()

def setFanSpeed():
    print("setting fan speed to", fanSpeed)
    if fanSpeed == 0:
        servo.angle = zeroAngle
    else:
        servo.angle = zeroAngle + (rotationRange - (fanSpeed - 1) * (rotationRange / 3))

pool = socketpool.SocketPool(wifi.radio)

mqttClient = MQTT.MQTT(
    broker=secrets["mqtt_broker"],
    port=secrets["mqtt_port"],
    username=secrets["mqtt_username"],
    password=secrets["mqtt_password"],
    socket_pool=pool
)

# mqttClient.on_connect = connected
# mqttClient.on_disconnect = disconnected
# mqttClient.on_subscribe = subscribe
# mqttClient.on_unsubscribe = unsubscribe
mqttClient.on_message = message

print("Connecting to home assistant...")
mqttClient.connect()
mqttClient.subscribe(fanSpeedFeed)
mqttClient.subscribe(fanToggleFeed)
mqttClient.loop(timeout=40)

prev_refresh_time = 0.0
while True:
    try:
        if prev_refresh_time > 30:
            mqttClient.get(fanSpeedFeed)
            mqttClient.get(fanToggleFeed)
        mqttClient.loop(timeout=40)
    except:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        mqttClient.reconnect()
    prev_refresh_time = time.monotonic()
    time.sleep(.25)