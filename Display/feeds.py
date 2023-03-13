import board
import busio
import neopixel
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
modeSettingFeed = "thermostat.mode"

def connected(client):
    print("Connected to AdafruitIO!")
    io.subscribe(temperatureSettingFeed)
    io.subscribe(fanSettingFeed)
    io.subscribe(modeSettingFeed)

def subscribe(client, userdata, topic, granted_qos):
    print("Subscribed to {0} with PID level {1}".format(topic, granted_qos))

def unsubscribe(client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID level {1}".format(topic, pid))

def disconnected(client):
    print("Disconnected from IO")

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
