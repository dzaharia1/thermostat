import time
import board
import pwmio
from adafruit_motor import servo
import ssl
import socketpool
import wifi
from digitalio import DigitalInOut
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT
from secrets import secrets

# set up servo
pwm = pwmio.PWMOut(board.A12, duty_cycle=2 ** 15, frequency=50)
servo = servo.Servo(pwm)
rotationRange = 120
zeroAngle = 48
servo.angle = zeroAngle

# set up adafruit io
groupName = "thermostat"
fanFeed = "thermostat.fan-setting"
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s" % secrets["ssid"])

def connected(client):
    print("Connected to Adafruit IO! Listening for changes...")
    io.subscribe(fanFeed)

def subscribe(client, userdata, topic, granted_qos):
    print ("Subscribed to {0} with QUOS level {1}".format(topic, granted_qos))

def unsubscribe(client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID level {1}".format(topic, pid))

def disconnected(client):
    print("Disconnected from IO")

def message(client, feed_id, payload):
    print("Set fan speed to", payload)
    setFan(int(payload))

def setFan(fanSpeed):
    if fanSpeed == 0:
        servo.angle = zeroAngle
    else:
        servo.angle = zeroAngle + (rotationRange - (fanSpeed - 1) * (rotationRange / 3))

pool = socketpool.SocketPool(wifi.radio)

mqttClient = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context()
)

io = IO_MQTT(mqttClient)

io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = message

print("Connecting to Adafruit IO...")
io.connect()
io.get(fanFeed)
io.loop()

while True:
    try:
        io.loop()
    except:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        io.reconnect()
    time.sleep(.25)