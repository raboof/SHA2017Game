import sys
import time
import badge
sys.path.append('/lib/game')
import game_common
import callsign

def setup():
    return False

def draw(x,y):
    # Nothing
    return False

def loop(sleepCnt):
    # TODO put speed in nvs
    if time.ticks_cpu() % 260 == 0:
    	print("game service called")
        league = game_common.determineLeague()
        callsign.callsign(league)

    return False
