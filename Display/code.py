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
from feeds import io

i2c_bus = busio.I2C(board.SCL, board.SDA)
temp_probe = adafruit_htu31d.HTU31D(i2c_bus)
lightSensor = AnalogIn(board.LIGHT)

def message(client, feed_id, payload):
    print(feed_id, "is set to", payload)
    if (feed_id == feeds.temperatureSettingFeed):
        ui.updateTemperature(int(payload))
    if (feed_id == feeds.fanSettingFeed):
        ui.updateFanSpeed(payload)
    if (feed_id == feeds.modeSettingFeed):
        ui.updateMode(payload)

def connected(client):
    io.subscribe(feeds.temperatureSettingFeed)
    io.subscribe(feeds.fanSettingFeed)
    io.subscribe(feeds.modeSettingFeed)
    io.get(feeds.temperatureSettingFeed)
    io.get(feeds.fanSettingFeed)
    io.get(feeds.modeSettingFeed)


io.on_message = message
io.on_connect = connected
io.connect()
ui.updateTemperature(int(feeds.io_http.get_feed(feeds.temperatureSettingFeed)["last_value"]))
ui.updateFanSpeed(feeds.io_http.get_feed(feeds.fanSettingFeed)["last_value"])
ui.updateMode(feeds.io_http.get_feed(feeds.modeSettingFeed)["last_value"])
print("Just finished getting last data")

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
        for i, button in enumerate(ui.modeButtons):
            if button.contains(point):
                lastButtonPush = time.monotonic()
                if i == 0:
                    ui.updateMode("manual")
                    ui.fanControl = 1
                    feeds.publish(feeds.modeSettingFeed, "manual")
                    feeds.publish(feeds.fanSettingFeed, ui.fanSetting)
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
                    feeds.publish(feeds.temperatureSettingFeed, ui.temperatureSetting + 1)
                elif i == 1:
                    ui.updateTemperature(ui.temperatureSetting - 1)
                    feeds.publish(feeds.temperatureSettingFeed, ui.temperatureSetting - 1)
        
        # check fan buttons
        for i, button in enumerate(ui.fanButtons):
            if button.contains(point):
                lastButtonPush = time.monotonic()
                if i == 0:
                    if ui.fanControl == 1:
                        feeds.publish(feeds.fanSettingFeed, "0")
                    ui.updateFanSpeed("0")
                    ui.set_backlight(1)
                else:
                    newFanSpeed = 4 - i
                    if ui.fanControl == 1:
                        feeds.publish(feeds.fanSettingFeed, str(newFanSpeed))
                    ui.updateFanSpeed(str(newFanSpeed))
                    ui.set_backlight(1)
        time.sleep(.075)


def checkTemperature():
    currTemp = temp_probe.temperature * (9 / 5) + 32 - 4
    ui.currTempLabel.text = str(floor(currTemp)) + "F"
    feeds.publish(feeds.temperatureReadingFeed, currTemp)
    
    if ui.modeSetting == "warm":
        if (currTemp <= ui.temperatureSetting):
            if ui.fanControl != 1:
                feeds.publish(feeds.fanSettingFeed, ui.fanSetting)
                ui.fanControl = 1
                ui.refresh_status_light()
        else:
            if ui.fanControl != 0:
                feeds.publish(feeds.fanSettingFeed, "0")
                ui.fanControl = 0
                ui.refresh_status_light()
    elif ui.modeSetting == "cool":
        if (currTemp >= ui.temperatureSetting):
            if ui.fanControl != 1:
                feeds.publish(feeds.fanSettingFeed, ui.fanSetting)
                ui.fanControl = 1
                ui.refresh_status_light()
        else:
            if ui.fanControl != 0:
                feeds.publish(feeds.fanSettingFeed, "0")
                ui.fanControl = 0
                ui.refresh_status_light()

checkTemperature()

prev_refresh_time = 0.0
while True:
    checkButtons()
    if (time.monotonic() - lastButtonPush) > 15 :
        ui.disableScreen()
    if (time.monotonic() - prev_refresh_time) > 40:
        print("Refreshing data")
        checkTemperature()
        prev_refresh_time = time.monotonic()
    time.sleep(.01)