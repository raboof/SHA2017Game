import sys
import time
import badge
sys.path.append('/lib/SHA2017Game')
import game_common

try:
    import sparkle as callsign
except:
    import callsign

def setup():
    return False

def loop():
    league = game_common.determineLeague()
    callsign.blink(league)

    return 25 * 60 * 1000
