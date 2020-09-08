# main.py - Written by Hugo Woesthuis 
# Licensed under MIT License. See LICENSE for more info

from collections import namedtuple
from datetime import datetime
Link = namedtuple('Link', 'url data')

#--------CONFIG--------#
username = 'leerlingnummer'
password = 'wachtwoord je weet toch'
#start_tool = True # Uncomment als je direct wilt testen
start_tool = datetime(2020, 9, 9, 0, 0, 0, 0) # Uncomment als je wacht op een bepaald tijdstip
link_queue = [Link("https://nuovo.magister.net/api/personen/100757/activiteiten/888/onderdelen/7401/inschrijvingen", {"persoonId":"100757","activiteitId":"888","onderdeelId":"7401"})]
#----------------------#

# Script begint hier :)
import server
import cli
from colorama import init
import threading
import os
import signal
import time
init()

ready = False
go = False

def time_handler():
    global start_tool, ready, go
    difference = start_tool - datetime.now() 
    cli.print_info(f'Waiting for {str(difference)}\n')
    secs = difference.total_seconds()

    while(secs > 0):
        secs -= 1;
        # T-90: Start the browser and get ready
        if(secs <= 90):
            ready = True
            return
        time.sleep(1)

def time_handle_p2():
    global start_tool, ready, go
    difference = start_tool - datetime.now() 
    cli.print_info(f'Waiting for {str(difference)}\n')
    secs = difference.total_seconds()

    while(secs > 0):
        secs -= 1;
        #T-1: GO!
        if(secs <= 1):
            go = ready = True
            return
        time.sleep(1)

def link_handler(linkt:Link):
    print(linkt)
    while(not s.POST(linkt.url, linkt.data)):
        time.sleep(0.5)
    return

def sigint_handler(self, *args):
    print('SIGINT found')
    s.dispose()
    os._exit(0)
    exit(0)

# main func.
if __name__ == "__main__":
    # Register SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)

    if(start_tool == True):
        ready = True
        go = True
    else:
        t = threading.Thread(target=time_handler)
        t.start()
        t.join()

    

    s = server.Magister("https://nuovo.magister.net", username, password)
    del username, password
    
    
    
    if(not s.login() or not s.get_bearer() or not s.inject_test()):
        cli.print_error("FATAL ERROR, exiting")
        s.dispose()
        exit(1)

    if(not go):
        t = threading.Thread(target=time_handle_p2)
        t.start()
        t.join()

    for linkt in link_queue:
        print(linkt)
        x = threading.Thread(target=link_handler, args=(linkt,))
        x.start()

