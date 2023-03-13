import board
import time
import terminalio
import busio
import adafruit_adt7410
font = terminalio.FONT
from math import floor

import ui
import feeds
from feeds import io
import styles
from adafruit_pyportal import PyPortal

i2c_bus = busio.I2C(board.SCL, board.SDA)
adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
adt.high_resolution = True

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
# io.loop(.1)

lastTempButtonPush = 0.0
def checkButtons():
    point = ui.ts.touch_point
    if point:
        # check mode buttons
        for i, button in enumerate(ui.modeButtons):
            if button.contains(point):
                if i == 0:
                    io.publish(feeds.modeSettingFeed, "manual")
                    io.publish(feeds.fanSettingFeed, ui.fanSetting)
                    ui.fanControl = 1
                    ui.updateMode("manual")
                elif i == 1:
                    io.publish(feeds.modeSettingFeed, "warm")
                    ui.updateMode("warm")
                elif i == 2:
                    io.publish(feeds.modeSettingFeed, "cool")
                    ui.updateMode("cool")

        # check temperature buttons
        for i, button in enumerate(ui.temperatureButtons):
            if button.contains(point):
                global lastTempButtonPush
                lastTempButtonPush = time.monotonic()
                if i == 0:
                    io.publish(feeds.temperatureSettingFeed, ui.temperatureSetting + 1)
                    ui.updateTemperature(ui.temperatureSetting + 1)
                elif i == 1:
                    io.publish(feeds.temperatureSettingFeed, ui.temperatureSetting - 1)
                    ui.updateTemperature(ui.temperatureSetting - 1)
        
        # check fan buttons
        for i, button in enumerate(ui.fanButtons):
            if button.contains(point):
                if i == 0:
                    if ui.fanControl == 1:
                        io.publish(feeds.fanSettingFeed, "0")
                    ui.updateFanSpeed("0")
                else:
                    newFanSpeed = 4 - i
                    if ui.fanControl == 1:
                        io.publish(feeds.fanSettingFeed, str(newFanSpeed))
                    ui.updateFanSpeed(str(newFanSpeed))
        time.sleep(.075)

def checkTemperature():
    # check current temperature (the board seems to add 21 degrees to actual? How to account for heat of board?)
    currTemp = adt.temperature * 1.8 + 32 - 21
    ui.currTempLabel.text = str(floor(currTemp)) + "F"
    # if (time.monotonic() - lastTempButtonPush) > 7:
    #     ui.temperatureSettingLabel.text = str(floor(currTemp))
    # else:
    #     ui.temperatureSettingLabel.text = str(ui.temperatureSetting)
    # compare against set temperature
    if ui.modeSetting == "warm":
        if (currTemp <= ui.temperatureSetting):
            if ui.fanControl != 1:
                print("Turning on the fan")
                io.publish(feeds.fanSettingFeed, ui.fanSetting)
                ui.fanControl = 1
        else:
            if ui.fanControl != 0:
                print("Turning off the fan")
                io.publish(feeds.fanSettingFeed, "0")
                ui.fanControl = 0
    elif ui.modeSetting == "cool":
        if (currTemp >= ui.temperatureSetting):
            if ui.fanControl != 1:
                print("Turning on the fan")
                io.publish(feeds.fanSettingFeed, ui.fanSetting)
                ui.fanControl = 1
        else:
            if ui.fanControl != 0:
                io.publish(feeds.fanSettingFeed, "0")
                ui.fanControl = 0

                

print("Starting loop")
prev_refresh_time = 0.0
while True:
    checkButtons()
    checkTemperature()
    if (time.monotonic() - prev_refresh_time) > 30:
        print("repinging")
        try:
            io.get(feeds.temperatureSettingFeed)
        except (ValueError, RuntimeError) as e:
            print("Error trying to connect. Retrying\n", e)
            feeds.wifi.reset()
            io.reconnect()
            continue
        prev_refresh_time = time.monotonic()
    time.sleep(.01)
    # io.loop(timeout=.1)