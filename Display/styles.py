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
    "fan": cwd + "icons/fan.bmp",
    "fan_off": cwd + "icons/fan_off.bmp",
    "chevron_up": cwd + "icons/chevron_up.bmp",
    "chevron_down": cwd + "icons/chevron_down.bmp"
}

icons = {
    "power": createIcon(iconsPaths["power"]),
    "cool": createIcon(iconsPaths["cool"]),
    "heat": createIcon(iconsPaths["heat"]),
    "fan": createIcon(iconsPaths["fan"]),
    "fan_off": createIcon(iconsPaths["fan_off"]),
    "chevron_up": createIcon(iconsPaths["chevron_up"]),
    "chevron_down": createIcon(iconsPaths["chevron_down"])
}

colors = {
    "heat": 0xFF6928,
    "cool": 0x2898FF,
    "white": 0xFFFFFF,
    "black": 0x000000
}