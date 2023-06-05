import board
import time
import terminalio
import busio
import adafruit_htu31d
from analogio import AnalogIn
font = terminalio.FONT
from math import floor
import ui
import feeds
from feeds import mqtt_client

i2c_bus = busio.I2C(board.SCL, board.SDA)
temp_probe = adafruit_htu31d.HTU31D(i2c_bus)
temp_probe.heater = False
lightSensor = AnalogIn(board.LIGHT)

lastButtonPush = 0.0
def checkButtons():
    global lastButtonPush
    point = ui.ts.touch_point

    # touch detected
    if point and point[-1] > 30000:
        if ui.screenActivateButton.contains(point):
            ui.enableScreen()
            lastButtonPush = time.monotonic()

    if point and ui.screenEnabled:
        # check mode buttons
        for i, button in enumerate(ui.modeButtons):
            if button.contains(point):
                lastButtonPush = time.monotonic()
                if i == 0:
                    ui.updateMode("manual")
                    ui.fanToggle = 1
                    feeds.publish(feeds.modeSettingFeed, "manual")
                    feeds.publish(feeds.fanSpeedFeed, ui.fanSpeed)
                    feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
                elif i == 1:
                    ui.updateMode("warm")
                    feeds.publish(feeds.modeSettingFeed, "warm")
                elif i == 2:
                    ui.updateMode("cool")
                    feeds.publish(feeds.modeSettingFeed, "cool")

        # check temperature buttons
        for i, button in enumerate(ui.temperatureButtons):
            if button.contains(point):
                lastButtonPush = time.monotonic()
                if i == 0:
                    ui.updateTemperature(ui.temperatureSetting + 1)
                    feeds.publish(feeds.temperatureSettingFeed, ui.temperatureSetting)
                elif i == 1:
                    ui.updateTemperature(ui.temperatureSetting - 1)
                    feeds.publish(feeds.temperatureSettingFeed, ui.temperatureSetting)
        
        # check fan buttons
        for i, button in enumerate(ui.fanButtons):
            if button.contains(point):
                lastButtonPush = time.monotonic()
                if i == 0:
                    if ui.fanToggle == 1:
                        feeds.publish(feeds.fanSpeedFeed, "0")
                    ui.updateFanSpeed("0")
                    ui.set_backlight(1)
                else:
                    newFanSpeed = 4 - i
                    if ui.fanToggle == 1:
                        feeds.publish(feeds.fanSpeedFeed, str(newFanSpeed))
                    ui.updateFanSpeed(str(newFanSpeed))
                    ui.set_backlight(1)
        time.sleep(.075)


def checkTemperature():
    currTemp = round(temp_probe.temperature * (9 / 5) + 32 - 4, 1)
    currHumidity = round(temp_probe.relative_humidity, 1)
    ui.currTempLabel.text = str(floor(currTemp)) + "F\n" + str(floor(currHumidity)) + "%"
    feeds.publish(feeds.temperatureSensorFeed, currTemp)
    feeds.publish(feeds.humidityFeed, currHumidity)

    if ui.modeSetting == "warm":
        if (currTemp <= ui.temperatureSetting):
            ui.fanToggle = 1
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
        else:
            ui.fanToggle = 0
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
    elif ui.modeSetting == "cool":
        if (currTemp >= ui.temperatureSetting):
            ui.fanToggle = 1
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
        else:
            ui.fanToggle = 0
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
    ui.refresh_status_light()

def mqtt_message(client, feed_id, payload):
    print('Got {0} from {1}'.format(payload, feed_id))
    if feed_id == feeds.temperatureSettingFeed:
        ui.updateTemperature(int(payload))

mqtt_client.on_message = mqtt_message

checkTemperature()
ui.updateMode("manual")
feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
prev_refresh_time = 0.0
while True:
    checkButtons()
    if (time.monotonic() - lastButtonPush) > 15 :
        ui.disableScreen()
    if (time.monotonic() - prev_refresh_time) > 40:
        print("Refreshing data")
        checkTemperature()
        prev_refresh_time = time.monotonic()
    # feeds.loop()
    time.sleep(.01)