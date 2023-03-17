import board
import time
import terminalio
import busio
import adafruit_adt7410
from analogio import AnalogIn
font = terminalio.FONT
from math import floor
import ui
import feeds
from feeds import io

i2c_bus = busio.I2C(board.SCL, board.SDA)
adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
adt.high_resolution = True
lightSensor = AnalogIn(board.LIGHT)

def message(client, feed_id, payload):
    print(feed_id, "is set to", payload)
    if (feed_id == feeds.temperatureSettingFeed):
        ui.updateTemperature(int(payload))
    if (feed_id == feeds.fanSettingFeed):
        ui.updateFanSpeed(payload)
    if (feed_id == feeds.modeSettingFeed):
        ui.updateMode(payload)

io.on_message = message
print("Connecting to IO...")
io.connect()

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
                    feeds.publish(feeds.modeSettingFeed, "manual")
                    feeds.publish(feeds.fanSettingFeed, ui.fanSetting)
                    ui.fanControl = 1
                    ui.updateMode("manual")
                elif i == 1:
                    feeds.publish(feeds.modeSettingFeed, "warm")
                    ui.updateMode("warm")
                elif i == 2:
                    feeds.publish(feeds.modeSettingFeed, "cool")
                    ui.updateMode("cool")

        # check temperature buttons
        for i, button in enumerate(ui.temperatureButtons):
            if button.contains(point):
                lastButtonPush = time.monotonic()
                if i == 0:
                    feeds.publish(feeds.temperatureSettingFeed, ui.temperatureSetting + 1)
                    ui.updateTemperature(ui.temperatureSetting + 1)
                elif i == 1:
                    feeds.publish(feeds.temperatureSettingFeed, ui.temperatureSetting - 1)
                    ui.updateTemperature(ui.temperatureSetting - 1)
        
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
    currTemp = adt.temperature * 1.8 + 32 - 18
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
ui.updateMode("manual")
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