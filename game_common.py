import machine

def determineLeague():
    return (machine.unique_id()[5] >> 1) % 6
