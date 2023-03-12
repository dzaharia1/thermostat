import displayio
import styles
import board
import terminalio
from adafruit_display_text.label import Label

font = terminalio.FONT
display = board.DISPLAY

def displayUI(mode, temperature, fanSpeed):
    ui = displayio.Group()
    color = styles.colors[mode]

    # create top bar
    topBar = displayio.Group(x=10, y=10)
    powerIcon = displayio.Group(x=0, y=2)
    powerIcon.append(styles.icons["power"])
    modeIcon = displayio.Group(x=140, y=0)
    modeIcon.append(styles.icons[mode])
    topBar.append(powerIcon)
    topBar.append(modeIcon)
    ui.append(topBar)

    # create temperature div
    temperatureDiv = displayio.Group(x=47, y=47)
    increaseIcon = displayio.Group(x=45, y=0)
    increaseIcon.append(styles.icons["chevron_up"])
    decreaseIcon = displayio.Group(x=45, y=154)
    decreaseIcon.append(styles.icons["chevron_down"])
    temperature_label = Label(font, color=color, text=str(temperature), x=0, y=38)
    temperatureDiv.append(temperature_label)
    temperatureDiv.append(increaseIcon)
    temperatureDiv.append(decreaseIcon)
    ui.append(temperatureDiv)

    # create bottom bar
    fanDiv = displayio.Group(x=10, y=262)
    fanDiv.append(styles.icons["fan_" + str(fanSpeed)])
    ui.append(fanDiv)

    display.show(ui)