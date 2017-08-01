import badge
import time
import binascii
import urandom

import sys
sys.path.append('/lib/SHA2017Game')
import callsign

off = "00000000"

def sparkle(color):
    result = ""
    for i in range(6):
        result += color[:-2] + ("00" if urandom.getrandbits(5) else "d0")
    return result

def spark(color, delay):
    remain = delay
    while remain > 0:
        badge.leds_send_data(binascii.unhexlify(sparkle(color)), 24)
        time.sleep_ms(25)
        remain -= 25

def blinkspark(color, delay = 50):
    for i in range(3):
        spark(color, delay)
        badge.leds_send_data(binascii.unhexlify(off * 6), 24)
        time.sleep_ms(delay)

def sosspark(color):
        blinkspark(color)
        time.sleep_ms(100)
        blinkspark(color, 150)
        blinkspark(color)

def blink(league):
	sosspark(callsign.league_color(league))

