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

sys.path.append('/lib/game')
import game_common
import callsign

def listenForOracle(leaguename):
    ugfx.clear(ugfx.WHITE)
    ugfx.string(0, 0, "Find the oracle!", "PermanentMarker22", ugfx.BLACK)
    ugfx.string(0, 30, "Welcome, brave traveller of league %s. Your quest" % leaguename, "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 50, "starts once you have found the oracle. When you are", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 70, "near she will call out for you and provide further", "Roboto_Regular12", ugfx.BLACK)
    ugfx.string(0, 90, "instructions. You have 30 seconds per attempt.", "Roboto_Regular12", ugfx.BLACK)
    ugfx.flush()

    w = network.WLAN(network.AP_IF)
    w.active(True)
    w.config(essid='OracleSeeker', channel=11)

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
        badge.nvs_set_str("game", "myfragment", req)

        client_stream.close()
        print("Done.")
    except OSError:
        print("Error")
    s.close()
    w.active(False)
    main()

def main():
    gc.collect()
    league = game_common.determineLeague()
    callsign.callsign(league)
    leaguename = callsign.leaguename[league]

    myfragment = badge.nvs_get_str("game", "myfragment")
    if myfragment:
        print("Have a fragment, no need to fetch")
    else:
        def oracle_selection_made(value):
            callsign.callsign(league)
            if value:
                listenForOracle(leaguename)
            else:
                appglue.start_app("")

        dialogs.prompt_boolean('Are you ready to start your quest?',
            title = "SHA2017Game - you are in league %s" % leaguename,
            true_text = 'Search for the oracle',
            false_text = 'Back to home screen',
            height = 100,
            cb=oracle_selection_made)

main()
