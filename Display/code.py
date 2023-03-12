# basics
import board
import time
import busio
import terminalio

# display
import displayio
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_pyportal import PyPortal
display = board.DISPLAY
display.rotation = 270
screen_width = 240
screen_height = 320
import adafruit_touchscreen
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_YD, board.TOUCH_YU,
                                      board.TOUCH_XR, board.TOUCH_XL,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))
# pyportal = PyPortal()
import neopixel
import styles

# network setup
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_minimqtt.adafruit_minimqtt import MQTT
from adafruit_io.adafruit_io import IO_MQTT
from secrets import secrets

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

temperatureSettingFeed = "thermostat.temperature-setting"
fanSettingFeed = "thermostat.fan-setting"
modeFeed = "thermostat.mode"
feedGroup = "thermostat"
font = terminalio.FONT

boot_message = displayio.Group()
boot_text = Label(font, color=styles.colors["white"], text="Connecting...", x=60, y=60)
boot_message.append(boot_text)
display.show(boot_message)

def connected(client):
    print("Connected to AdafruitIO!")
    io.subscribe(temperatureSettingFeed)
    io.subscribe(fanSettingFeed)
    io.subscribe(modeFeed)

def subscribe(client, userdata, topic, granted_qos):
    print("Subscribed to {0} with PID level {1}".format(topic, granted_qos))

def unsubscribe(client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID level {1}".format(topic, pid))

def disconnected(client):
    print("Disconnected from IO")

def message(client, feed_id, payload):
    print(feed_id, "set to", payload)

wifi.connect()

mqtt_client = MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=socket
)

io = IO_MQTT(mqtt_client)

io.on_connect = connected
io.on_disconnect = disconnected
io.on_message = message

print("Connecting to IO...")
io.connect()

def displayUI(mode, fanSpeed, temperature):
    color = styles.colors[mode]

    # set up the top bar
    topBar = displayio.Group(x=10, y=10)
    powerIcon = displayio.Group(x=0, y=0)
    powerIcon.append(styles.icons["power"])
    heatIcon = displayio.Group(x=144, y=0)
    heatIcon.append(styles.icons["heat"])
    coolIcon = displayio.Group(x=188, y=0)
    coolIcon.append(styles.icons["cool"])
    topBar.append(powerIcon)
    topBar.append(heatIcon)
    topBar.append(coolIcon)
    display.show(topBar)

    # set up the temperature display
    temperatureDiv = displayio.Group(x=47, y=47)
    increaseIcon = displayio.Group(x=45, y=0)
    increaseIcon.append(styles.icons["chevron_up"])
    decreaseIcon = displayio.Group(x=45, y=154)
    decreaseIcon.append(styles.icons["chevron_down"])
    temperature_label = Label(font, color=color, text=str(temperature), x=0, y=38)
    temperatureDiv.append(temperature_label)
    temperatureDiv.append(increaseIcon)
    temperatureDiv.append(decreaseIcon)


displayUI("heat", "3", 73)

while True:
    io.loop()
    time.sleep(.2)