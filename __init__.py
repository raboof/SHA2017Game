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

sys.path.append('/lib/game')
import game_common
import callsign

leaguenames = [ "red", "fuchsia", "blue", "green", "yellow", "orange" ]

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
    print("Listening")
    s.settimeout(30)
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

        done = cb(req)

        client_stream.close()
        print("Done.")
    except OSError:
        print("Error")
        done = errcb()

    s.close()
    w.active(False)
    if done:
        main()

def gotOracleData(data):
    badge.nvs_set_str("game", "myfragment", data)
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

    try:
        w = network.WLAN(network.STA_IF)
        w.active(True)
        ap ="Gamer %s %s" % (leaguename(), recv)
        print('Connecting to', ap)
        w.connect(ap)
        while not w.isconnected():
            time.sleep(1)
    except msg:
        print("error!", msg)
        ugfx.string(0, 50, "Error connecting to other player...", "Roboto_Regular12", ugfx.BLACK)
        ugfx.flush()
        return

    ugfx.string(0, 50, "Sending fragments...", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    s = socket.socket()
    ai = socket.getaddrinfo("192.168.4.1", 2017)
    addr = ai[0][-1]
    s.connect(addr)
    myfragment = badge.nvs_get_str("game", "myfragment")
    s.send(myfragment)
    s.send('\r\n')
    s.close()
    w.active(False)
    print('Done sending')
    ugfx.string(0, 70, "Sent fragments. Press A.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: initiate_sharing() if pressed else 0)

def gotFragmentData(data):
    # TODO show how many fragment you have and need, check key if done.
    print('Got fragment data: ', data)
    return False;

def receive_fragments_failed():
    ugfx.string(0, 70, "Failed to receive fragments. Press A.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: initiate_sharing() if pressed else 0)
    
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
    ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else 0)
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: initiate_sharing() if pressed else 0)

def main():
    gc.collect()
    league = game_common.determineLeague()
    callsign.callsign(league)

    myfragment = badge.nvs_get_str("game", "myfragment")
    if myfragment:
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
    else:
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

main()
