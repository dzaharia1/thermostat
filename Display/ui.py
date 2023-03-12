import displayio
from displayio import Group
import styles
import board
import terminalio
from adafruit_display_text.label import Label

font = terminalio.FONT
display = board.DISPLAY

temperatureSetting = 60
temperatureReading = 70
fanSetting = 0
modeSetting = "cool"

ui = Group(x=0, y=0)
topBarDiv = Group(x=10, y=10)
temperatureDiv = Group(x=45, y=65)
fanSelectorDiv = Group(x=10, y=262)
ui.append(temperatureDiv)
ui.append(fanSelectorDiv)
ui.append(topBarDiv)

# build out top bar
powerIcon = Group(x=0, y=2)
powerIcon.append(styles.icons["power"])
warmIcon =  Group(x=84, y=0)
warmIcon.append(styles.icons['warm'])
coolIcon =  Group(x=84, y=0)
coolIcon.append(styles.icons["cool"])
manualIcon =  Group(x=84, y=0)
manualIcon.append(styles.icons["manual"])
topBarDiv.append(warmIcon)
topBarDiv.append(coolIcon)
topBarDiv.append(manualIcon)
topBarDiv.append(powerIcon)

# build out temperatureDiv
increaseIcon = Group(x=45, y=0)
increaseIcon.append(styles.icons["chevron_up"])
decreaseIcon = Group(x=45, y=135)
decreaseIcon.append(styles.icons["chevron_down"])
temperatureLabel = Label(font, color=styles.colors["white"], x=28, y=95, text="...")
temperatureLabel.scale = 7
temperatureDiv.append(increaseIcon)
temperatureDiv.append(decreaseIcon)
temperatureDiv.append(temperatureLabel)

# build out bottom bar
fanSelectorDiv.append(styles.icons["fan_0"])

display.show(ui)

def updateMode(newMode):
    global modeSetting
    modeSetting = newMode
    temperatureLabel.color = styles.colors[newMode]

    if modeSetting == "warm":
        warmIcon.hidden = False
        coolIcon.hidden = True
        manualIcon.hidden = True
    elif modeSetting == "cool":
        warmIcon.hidden = True
        coolIcon.hidden = False
        manualIcon.hidden = True
    elif modeSetting == "manual":
        warmIcon.hidden = True
        coolIcon.hidden = True
        manualIcon.hidden = False

def updateTemperature(newTemperature):
    global temperatureSetting
    global temperatureLabel
    temperatureSetting = newTemperature
    temperatureLabel.text = str(temperatureSetting)

def updateFanSpeed(newSpeed):
    global fanSetting
    global fanSelectorDiv
    fanSetting = newSpeed
    while True:
        try:
            fanSelectorDiv.pop()
        except:
            break
    fanSelectorDiv.append(styles.icons["fan_" + fanSetting])

def showCurrentTemperature(temp):
    # todo
    return