import displayio

cwd = ("/"+__file__).rsplit('/', 1)[0]

def createIcon(iconPath):
    image_file = open(iconPath, "rb")
    icon = displayio.OnDiskBitmap(image_file)
    return displayio.TileGrid(icon, pixel_shader=getattr(icon, 'pixel_shader', displayio.ColorConverter()))

iconsPaths = {
    "power": cwd + "icons/power.bmp",
    "cool": cwd + "icons/cool.bmp",
    "heat": cwd + "icons/heat.bmp",
    "chevron_up": cwd + "icons/chevron_up.bmp",
    "chevron_down": cwd + "icons/chevron_down.bmp",
    "fan_0": cwd + "icons/fan_0.bmp",
    "fan_1": cwd + "icons/fan_1.bmp",
    "fan_2": cwd + "icons/fan_2.bmp",
    "fan_3": cwd + "icons/fan_3.bmp",
}

icons = {
    "power": createIcon(iconsPaths["power"]),
    "cool": createIcon(iconsPaths["cool"]),
    "heat": createIcon(iconsPaths["heat"]),
    "chevron_up": createIcon(iconsPaths["chevron_up"]),
    "chevron_down": createIcon(iconsPaths["chevron_down"]),
    "fan_0": createIcon(iconsPaths["fan_0"]),
    "fan_1": createIcon(iconsPaths["fan_1"]),
    "fan_2": createIcon(iconsPaths["fan_2"]),
    "fan_3": createIcon(iconsPaths["fan_3"]),
}

colors = {
    "heat": 0xFF6928,
    "cool": 0x2898FF,
    "white": 0xFFFFFF,
    "black": 0x000000
}