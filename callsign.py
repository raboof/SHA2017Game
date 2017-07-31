import badge
import time
import binascii
import urandom

leaguename = [ "red", "fuchsia", "blue", "green", "yellow", "orange" ]
leaguecolor = [
    "000a0000",
    "000e0000",
    "00000a00",
    "0a000000",
    "0a0e0000",
    "041e0000"
]
off = "00000000"

def blink3(color, delay = 50):
    for i in range(3):
        badge.leds_send_data(binascii.unhexlify(color * 6), 24)
        time.sleep_ms(delay)
        badge.leds_send_data(binascii.unhexlify(off * 6), 24)
        time.sleep_ms(delay)

def blinksos(color):
    blink3(color)
    time.sleep_ms(100)
    blink3(color, 150)
    blink3(color)

def callsign(league):
    blinksos(leaguecolor[league])
