from adafruit_esp32spi.adafruit_esp32spi_socket import socket
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from secrets import secrets

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

temperatureSettingFeed = "state/temp-setting"
fanSettingFeed = "state/fan-setting"
modeSettingFeed = "state/thermostat-mode"
temperatureReadingFeed = "state/temp-sensor"
humidityFeed = "state/humidity-sensor"

def connected(client):
    print("Connected to HA!")

def disconnected(client):
    print("Disconnected from HA")

print("Connecting to wifi")
wifi.connect()
print("Connected to wifi!")

MQTT.set_socket(socket, esp)
mqtt_client = MQTT.MQTT(
    broker=secrets["mqtt_broker"],
    port=secrets["mqtt_port"],
    username=secrets["mqtt_username"],
    password=secrets["mqtt_password"]
)

def publish(feed, data):
    try:
        mqtt_client.publish(feed, data)
    except:
        wifi.reset()
        wifi.connect()
        mqtt_client.reconnect()

mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected

print("Connecting to Home Assistant")
mqtt_client.connect()

mqtt_client.subscribe(temperatureSettingFeed)
mqtt_client.subscribe(fanSettingFeed)
mqtt_client.subscribe(modeSettingFeed)
mqtt_client.subscribe(temperatureReadingFeed)
mqtt_client.subscribe(humidityFeed)
