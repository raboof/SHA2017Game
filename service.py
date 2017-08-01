import sys
import time
import badge
sys.path.append('/lib/game')
import game_common

try:
    print('importing sparkle')
    import sparkle as callsign
    print('imported sparkle')
except:
    import callsign
    print('imported callsign instead')

def setup():
    return False

def draw(x,y):
    # Nothing
    return False

def loop(sleepCnt):
    # TODO put speed in nvs
    if time.ticks_cpu() % 260 == 0:
    # if time.ticks_cpu() % 20 == 0:
        league = game_common.determineLeague()
        callsign.blink(league)

    return False
