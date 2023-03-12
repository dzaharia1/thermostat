import board
import time
import terminalio

import displayio
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
display = board.DISPLAY
display.rotation = 270
screen_width = 240
screen_height = 320
import adafruit_touchscreen
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_YD, board.TOUCH_YU,
                                      board.TOUCH_XR, board.TOUCH_XL,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))
font = terminalio.FONT

import ui
import feeds
from feeds import io
import styles


print("Connecting to IO...")

def message(client, feed_id, payload):
    print(feed_id, "is set to", payload)
    if (feed_id == feeds.temperatureSettingFeed):
        ui.updateTemperature(payload)
    if (feed_id == feeds.fanSettingFeed):
        ui.updateFanSpeed(payload)
    if (feed_id == feeds.modeSettingFeed):
        ui.updateMode(payload)

io.on_message = message
io.connect()
io.get(feeds.temperatureSettingFeed)
io.get(feeds.modeSettingFeed)
io.get(feeds.fanSettingFeed)
io.loop()

while True:
    io.loop()
    time.sleep(.2)