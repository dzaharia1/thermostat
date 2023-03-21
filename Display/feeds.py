import board
import busio
import neopixel
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_minimqtt.adafruit_minimqtt import MQTT
from adafruit_io.adafruit_io import IO_MQTT
from adafruit_io.adafruit_io import IO_HTTP
import adafruit_requests as requests
from secrets import secrets

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)
requests.set_socket(socket, esp)

temperatureSettingFeed = "thermostat.temperature-setting"
temperatureReadingFeed = "thermostat.temperature-reading"
fanSettingFeed = "thermostat.fan-setting"
modeSettingFeed = "thermostat.mode"

def disconnected(client):
    print("Disconnected from IO")
    wifi.reset()
    wifi.connect()
    io.reconnect()

def publish(feed, data):
    try:
        io.publish(feed, data)
    except:
        wifi.reset()
        wifi.connect()
        io.reconnect()

wifi.connect()

mqtt_client = MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=socket,
)

io = IO_MQTT(mqtt_client)
io_http = IO_HTTP(secrets["aio_username"], secrets["aio_key"], requests)

io.on_disconnect = disconnected
