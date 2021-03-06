import sys
import gc
import network
import machine
import usocket as socket
import badge
import ugfx
import appglue
import time
import dialogs
import machine

sys.path.append('/lib/SHA2017Game')
import game_common
import callsign

leaguenames = [ "red", "fuchsia", "blue", "green", "yellow", "orange" ]

def shift_fragments(i):
    for n in range(i, 26):
        next_fragment = badge.nvs_get_str('SHA2017Game', "fragment_%d" % (n+1))
        if next_fragment:
            badge.nvs_set_str('SHA2017Game', "fragment_%d" % n, next_fragment)
        else:
            badge.nvs_erase_key('SHA2017Game', "fragment_%d" % n)
            return

def remove_duplicate_initial_fragment():
    initial_fragment = badge.nvs_get_str('SHA2017Game', "fragment_0")
    if initial_fragment:
        for i in range(1, 25):
            fragment = badge.nvs_get_str('SHA2017Game', "fragment_%d" % i)
            if fragment and fragment.strip() == initial_fragment.strip():
                shift_fragments(i)
                return

def get_fragments():
    result = []
    for i in range(0, 25):
        fragment = badge.nvs_get_str('SHA2017Game', "fragment_%d" % i)
        if fragment:
            result.append(fragment.replace('\n', '').replace('\r', ''))
    return result

def add_fragment(newfragment):
    for i in range(0, 25):
        fragment = badge.nvs_get_str('SHA2017Game', "fragment_%d" % i)
        if fragment:
            if fragment.strip() == newfragment.strip():
                return
        else:
            badge.nvs_set_str('SHA2017Game', "fragment_%d" % i, newfragment)
            return

def leaguename():
    league = game_common.determineLeague()
    return leaguenames[league]

def receiveData(essid, cb, errcb):
    w = network.WLAN(network.AP_IF)
    w.active(True)
    w.config(essid=essid, channel=11)

    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 2017)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print('Listening at', essid)
    s.settimeout(120)
    try:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)

        client_stream = client_sock

        print("Request:")
        req = client_stream.readline()
        print(req)
        client_stream.send('OK\r\n')

        done = cb(req)

        client_stream.close()
        print("Done.")
    except OSError:
        print("Error")
        done = errcb()

    s.close()
    w.active(False)
    if done:
        appglue.start_app('SHA2017Game')

def gotOracleData(data):
    badge.nvs_set_str('SHA2017Game', 'fragment_0', data)
    return True

def listenForOracle(leaguename):
    ugfx.clear(ugfx.WHITE)
    ugfx.string(0, 0, "Find the oracle!", "PermanentMarker22", ugfx.BLACK)
    ugfx.string(0, 30, "Welcome, brave traveller of league %s. Your quest" % leaguename, "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 50, "starts once you have found the oracle. When you are", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 70, "near she will call out for you and provide further", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 90, "instructions. You have 30 seconds per attempt.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()

    receiveData('OracleSeeker', gotOracleData, appglue.home)

def send_to(recv):
    ugfx.clear(ugfx.WHITE)
    ugfx.string(0, 0, "Share your fragments!", "PermanentMarker22", ugfx.BLACK)
    ugfx.string(0, 30, "Connecting to other player...", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()

    n = 0

    try:
        w = network.WLAN(network.STA_IF)
        w.active(True)
        ap ="Gamer %s %s" % (leaguename(), recv)
        print('Connecting to', ap)
        w.connect(ap)
        while not w.isconnected() and n < 30:
            time.sleep(1)
            n = n + 1
    except msg:
        print("error!", msg)
        ugfx.string(0, 50, "Error connecting to other player...", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        ugfx.input_init()
        ugfx.input_attach(ugfx.BTN_A, lambda pressed: appglue.start_app('SHA2017Game') if pressed else 0)
        return

    if n == 30:
        print('No connection after sleeping 30 seconds')
        ugfx.string(0, 50, "Error connecting to other player...", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        ugfx.input_init()
        ugfx.input_attach(ugfx.BTN_A, lambda pressed: appglue.start_app('SHA2017Game') if pressed else 0)
        return

    ugfx.string(0, 50, "Sending fragments...", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    s = socket.socket()
    ai = socket.getaddrinfo("192.168.4.1", 2017)
    addr = ai[0][-1]
    s.connect(addr)
    s.send('#'.join(get_fragments()))
    s.send("\r\n")
    s.readline()
    s.close()
    w.active(False)
    print('Done sending')
    ugfx.string(0, 70, "Sent fragments. Press A.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_init()
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: appglue.start_app('SHA2017Game') if pressed else 0)

def gotFragmentData(data):
    print('Got fragment data: ', data)
    for fragment in data.decode().split('#'):
        add_fragment(fragment.replace('\n', '').replace('\r', ''))

    fragments = get_fragments()
    if len(fragments)>=25:
        appglue.start_app('SHA2017Game')

    ugfx.string(0, 70, "You now own %d unique fragments, %d to go!" % (len(fragments), 25 - len(fragments)), "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(5, 113, "B: Back to home                                A: Share fragments", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_init()
    ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else 0)
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: appglue.start_app('SHA2017Game') if pressed else 0)
    return False;

def receive_fragments_failed():
    ugfx.string(0, 70, "Failed to receive fragments. Press A.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_init()
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: appglue.start_app('SHA2017Game') if pressed else 0)

def receive_fragments():
    receiveData("Gamer %s %03d%03d" % (leaguename(), machine.unique_id()[4], machine.unique_id()[5]), gotFragmentData, receive_fragments_failed)

def send_or_recv(send):
    if send:
        ugfx.clear(ugfx.WHITE)
        dialogs.prompt_text("Receiver address:", cb=send_to)
    else:
        ugfx.clear(ugfx.WHITE)
        ugfx.string(0, 0, "Share your fragments!", "PermanentMarker22", ugfx.BLACK)
        ugfx.string(0, 30, "Tell the other player of your league your address,", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 50, "which is %03d%03d. Waiting..." % (machine.unique_id()[4], machine.unique_id()[5]), "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        receive_fragments()

def initiate_sharing():
    ugfx.clear(ugfx.WHITE)
    ugfx.string(0, 0, "Share your fragments!", "PermanentMarker22", ugfx.BLACK)
    dialogs.prompt_boolean("Do you want to send or receive?", true_text="Send", false_text="Receive", height=100, cb=send_or_recv)

def won():
    ugfx.clear(ugfx.WHITE)
    ugfx.string(0, 0, "Congratulations!", "PermanentMarker22", ugfx.BLACK)
    ugfx.string(0, 30, "Cool! You've unlocked your league's secret. As a reward", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 50, "the signal shown by your badge LEDs will now sparkle.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 70, "Is this the end? That is up to you! Contact raboof for", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 90, "the game code and design new challenges!", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(5, 113, "B: Back to home                                A: Share fragments", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_init()
    ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else 0)
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: initiate_sharing() if pressed else 0)

def main():
    gc.collect()
    league = game_common.determineLeague()
    callsign.callsign(league)

    remove_duplicate_initial_fragment()

    if False:
        ugfx.clear(ugfx.WHITE)
        ugfx.string(0, 0, "Welcome, early bird!", "PermanentMarker22", ugfx.BLACK)
        ugfx.string(0, 30, "Welcome to the SHA2017Game! You are in league", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 50, "%s, as your 'callsign' shows if you soldered on your" % leaguename(), "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 70, "LEDs. The game starts when the oracle is on the field,", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 90, "keep an eye on https://twitter.com/SHA2017Game.", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(5, 113, "B: Back to home", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        ugfx.input_init()
        ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else 0)
        return

    fragments = get_fragments()
    print('number of fragments so far', len(fragments))

    oracle_exists = False

    if len(fragments) >= 25:
        badge.nvs_set_str('SHA2017Game', 'fragment_0', fragments[0].strip())
        ugfx.clear(ugfx.WHITE)
        try:
            import os
            os.stat('/lib/SHA2017game/sparkle.py')
            won()
        except:
            import wifi
            import urequests
            import shards
            wifi.init()
            while not wifi.sta_if.isconnected():
                time.sleep(1)
            cleaned_fragments = []
            for fragment in fragments:
                cleaned_fragments.append(fragment.replace('\n', '').replace('\r', ''))
            key = shards.key_from_shards(cleaned_fragments)
            print('Collecting shards.py with key', key)
            r = urequests.get("http://pi.bzzt.net/%s/sparkle.py" % key)
            f = open('/lib/SHA2017game/sparkle.py', 'w')
            f.write(r.content)
            f.close()
            won()
    elif len(fragments) > 1:
        badge.nvs_set_str('SHA2017Game', 'fragment_0', fragments[0].strip())
        ugfx.clear(ugfx.WHITE)
        ugfx.string(0, 0, "Share your fragments!", "PermanentMarker22", ugfx.BLACK)
        ugfx.string(0, 30, "By sharing you have now brought together %d" % len(fragments), "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 50, "fragments of league %s. Sharing will send them all." % leaguename(), "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 70, "Unlock your league %s key with 25 fragments!" % leaguename(), "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(5, 113, "B: Back to home                                A: Share fragments", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        ugfx.input_init()
        ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else 0)
        ugfx.input_attach(ugfx.BTN_A, lambda pressed: initiate_sharing() if pressed else 0)
    elif len(fragments) == 1:
        ugfx.clear(ugfx.WHITE)
        ugfx.string(0, 0, "Share your fragments!", "PermanentMarker22", ugfx.BLACK)
        ugfx.string(0, 30, "The oracle gave you a fragment of a relic of the " + leaguename(), "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 50, "league. 25 such fragments must be brought together", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 70, "to unlock its potential. Find other league members to", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 90, "share fragments along with a story or Mate.", "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(5, 113, "B: Back to home                                A: Share fragments", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        ugfx.input_init()
        ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else 0)
        ugfx.input_attach(ugfx.BTN_A, lambda pressed: initiate_sharing() if pressed else 0)
    elif oracle_exists:
        def oracle_selection_made(value):
            callsign.callsign(league)
            if value:
                listenForOracle(leaguename())
            else:
                appglue.home()

        def dialog_title():
            return "SHA2017Game - you are in league " + leaguename()
        dialogs.prompt_boolean('Are you ready to start your quest?',
            title = dialog_title(),
            true_text = 'Search for the oracle',
            false_text = 'Back to home screen',
            height = 100,
            cb=oracle_selection_made)
    else:
        ugfx.clear(ugfx.WHITE)
        ugfx.string(0, 0, "Retrieving fragment!", "PermanentMarker22", ugfx.BLACK)
        ugfx.string(0, 30, "Welcome player of league " + leaguename(), "Roboto_Regular12", ugfx.BLACK)
        ugfx.string(0, 50, "Fetching your initial fragment!", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        import wifi
        import urequests
        wifi.init()
        n = 0
        while not wifi.sta_if.isconnected() and n < 30:
            time.sleep(1)
            n = n + 1
        if n == 30:
            ugfx.string(0, 70, "Failed! Press A.", "Roboto_Regular12", ugfx.BLACK)
            ugfx.input_init()
            ugfx.input_attach(ugfx.BTN_A, lambda pressed: appglue.start_app('SHA2017Game') if pressed else 0)
            return
            
        fragmentid = (machine.unique_id()[3] + machine.unique_id()[4] + machine.unique_id()[5]) % 700
        r = urequests.get("http://pi.bzzt.net/oracle/%d/%d" % (league, fragmentid))
        gotOracleData(r.content)
        appglue.start_app('SHA2017Game')

main()
