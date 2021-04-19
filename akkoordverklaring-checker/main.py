# main.py - Written by Hugo Woesthuis 
# Licensed under MIT License. See LICENSE for more info

from collections import namedtuple
from datetime import datetime
Link = namedtuple('Link', 'url data')

#--------CONFIG--------#



# Script begint hier :)
import server
import cli
from colorama import init
import threading
from datetime import datetime
import math
import os
import signal
import time
import sys
import coloredlogs, logging
import json

from urllib.parse import urlparse



init()

ready = False
go = False


class Serialized(object):
    def __init__(self, s):
        self.__dict__ = json.loads(s)

def printIntro():
    print('#----------------------------------------------------#')
    print('#          Akkoordverklaring Checker ding v0.1       #')
    print('# PanicTriggers (c) 2021. Licensed under MIT License #')
    print('#        Checkout the source and the license at:     #')
    print('#  https://github.com/panictriggers/magister-tools   #')
    print('#----------------------------------------------------#\n')

def sigint_handler(self, *args):
    print('SIGINT found')
    try:
        m.dispose()
    except Exception:
        pass

    os._exit(0)
    exit(0)

def switch_args():
    logtype = 'WARNING'
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-v' or sys.argv[i] == '--verbose':
            logtype = 'INFO'
        elif sys.argv[i] == '--debug':
            logtype = 'DEBUG'
    return logtype

def link_inp():
    print('Typ de link in van de magister website: ', end='')
    l = input()

    if not 'https' in l:
        l = f"https://{l}"

    url = urlparse(l)

    # Deze checks zijn bedoeld om grotendeels te checken of de link een magister link is
    if not '.magister.net' in url.netloc:
        print('Is dit wel een link die naar Magister verwijst? (5) Een link ziet er ongeveer zo uit: https://jeschool.magister.net. Probeer het opnieuw')
        return False

    

    return url


def question(msg):
    print(msg, end='')
    okinp = False
    while not okinp:
        a = input()
    
        if 'nee' in a or a is 'no' or a is 'n':
            return False

        if a is 'ja' or a is 'yes' or a is 'j' or a is 'y':
            return True

        else:
            print("Verkeerde input. typ 'ja' of 'nee' in")

# main func.
if __name__ == "__main__":
    
    # Register SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)
    
    printIntro()

    print("INSTRUCTIE: Volg de instructies op dit scherm")
    
    f = open('output.log', 'w+', encoding = 'utf-8')
    f.truncate()
    f.write(f"AKKOORDVERKLARING CHECKER\nVersion: 0.1\nTimestamp: {datetime.now()}")

    coloredlogs.install()

    # check args
    ar = switch_args()
    coloredlogs.install(level=ar)
    url = False

    while not url:
        url = link_inp() 

    # maakt niet uit wat de path was, deze strippen we maar. We willen alleen het domein weten
    strippedurl = f"https://{url.netloc}"

    # Start the server!
    m = server.Magister(strippedurl, verbose=ar)

    print("INSTRUCTIE: Log in met de browser. Het laden kan even duren!")
    logging.info("Waiting for Chrome...")
    m.login()    
    if not m.get_bearer():
        
        logging.critical("Fout! Gebruik --verbose of --debug voor meer info")
        logging.info("Authorization bearer could not be obtained!")
        m.dispose()

    if not m.inject_test():
        logging.critical("Fout! Gebruik --verbose of --debug voor meer info")
        logging.info("Failed to inject JS!")
        m.dispose()

    print("Laden van metadata...")

    logging.info("Obtaining identity")

    # Verkrijg id
    resp = m.GET(f"{strippedurl}/api/account?noCache=0")

    if resp == None or not resp:
        logging.critical("Fout! Kon niet identeit verkrijgen")
        m.dispose()
    logging.debug(resp)
    d = Serialized(resp)
    uid = d.Persoon['Id']
    
    logging.debug(f"User ID: {uid}")

    # Verkrijg huidige 'aanmelding' (wat een kut naam)

    print("INSTRUCTIE: Beantwoord de volgende reeks vragen met een 'ja' of 'nee'. Combinatiecijfers, A-Som en LOB dienen normaliter ook met een 'ja' worden beantwoord.\n")

    aresp = m.GET(f'{strippedurl}/api/leerlingen/{uid}/aanmeldingen?begin=2011-01-01&einde=2022-01-01')
    
    logging.debug(aresp)
    
    ad = json.loads(aresp)
    
    # Index 0 zou meest recente moeten zijn
    aid = ad['items'][0]['id']
    vid = ad['items'][1]['id']

    # Verkrijg vakken Id's
    cresp = m.GET(f'{strippedurl}/api/personen/{uid}/aanmeldingen/{aid}/vakken')
    logging.debug(cresp)
    
    vakken = json.loads(cresp)
    f.write("\n\n============ VRIJSTELLINGEN ==============\n")
    # Check voor vrijstellingen
    for vak in vakken:
        ui = question(f'Heb je vrijstelling of ontheffing voor het vak {vak["omschrijving"]}? (ja/nee) ')
        if vak['vrijstelling'] or vak['heeftOntheffing']:
            if not ui:
                logging.warning("Dataconfict: Vrijstelling is gegeven terwijl dit niet zo is.")
                cb = question('Wil je alsnog doorgaan met het verifieren van je akkoordverklaring? (ja/nee) ')
                if not cb:
                    f.write(f"Vrijstelling voor {vak['omschrijving']} gegeven terwijl dit niet zo moet zijn!")
                    logging.critical("AKKOORDVERKLARING ONGELDIG!")
                    m.dispose()
                    exit(1)
        else:
            if ui:
                logging.warning("Dataconfict: Vrijstelling is niet gegeven terwijl dit wel zo is.")
                cb = question('Wil je alsnog doorgaan met het verifieren van je akkoordverklaring? (ja/nee) ')
                if not cb:
                    f.write(f"Vrijstelling voor {vak['omschrijving']} niet gegeven terwijl dit wel zo moet zijn!")
                    logging.critical("AKKOORDVERKLARING ONGELDIG!")
                    m.dispose()
                    exit(1)
    f.write("OK\n")

    # Verkrijg alle cijfers
    tries = 0
    print("")
    f.write("\n\n============ VRAGEN ==============\n")
    if question("Missen er nog cijfers in Magister? (ja/nee) ") or not question("Kloppen de profielen vermeld op de akkoordverklaring? (ja/nee) ") or not question("Kloppen alle persoonsgegevens in de akkoordverklaring? (ja/nee) "):
        f.write("Invalid answers")
        logging.critical("AKKOORDVERKLARING ONGELDIG!")
        m.dispose()
        exit(1)
    f.write("OK!\n")


    while tries <= 5:
        print("Cijfer map proberen op te halen....", end="")
        cijfer_raw = m.GET(f'{strippedurl}/api/personen/{uid}/aanmeldingen/{aid}/cijfers/cijferoverzichtvooraanmelding?actievePerioden=false&alleenBerekendeKolommen=false&alleenPTAKolommen=false')
        logging.debug(cijfer_raw)

        if cijfer_raw == None or cijfer_raw == False:
            tries = tries + 1
        else:
            break
        
    
    if cijfer_raw == None or cijfer_raw == False:
            logging.critical("Cijfers konden niet worden opgehaald")
            m.dispose()
            exit(1)
    else: 
        tries = 0
    
    print("OK")
    
    cijfers = json.loads(cijfer_raw)

    stripped_data = []

    print("v5 cijfermap ophalen...", end="")
    # vwo5
    v5cijfers_raw = m.GET(f'{strippedurl}/api/personen/{uid}/aanmeldingen/{vid}/cijfers/cijferoverzichtvooraanmelding?actievePerioden=false&alleenBerekendeKolommen=true&alleenPTAKolommen=false&peildatum=2020-07-31')
    
    if v5cijfers_raw == None or v5cijfers_raw == False:
            logging.critical("v5 cijfers konden niet worden opgehaald")
            m.dispose()
            exit(1)
    else: 
        tries = 0

    v5cijfers = json.loads(v5cijfers_raw)
    print("OK")
        
    print("INSTRUCTIE: Voer bij de volgende vragen je cijfers in die vermeld staan op je akkoordverklaring. Het gebruik van een , of . als decimaal maakt niet uit!\n")

    # Initalization run
    for cijfer in cijfers['Items']:
        #time.sleep(1)
        typ = cijfer['CijferKolom']['KolomSoort']

        if typ == 2:
            print(f"Welk gemiddelde is vermeld op je akkoordverklaring voor het vak {cijfer['Vak']['Omschrijving']}? ")
            av = input()
            if av == 'skip':
                continue
            elif av == 'G' or av == 'V' or av == 'O':
                pass
            else:
                try:
                    av = float(av.replace(',','.'))
                except ValueError:
                    logging.critical("Parsing failed!")
                    continue

                
            
                dicet = {"afkorting" : cijfer['Vak']['Afkorting'], "naam" : cijfer['Vak']['Omschrijving'], 'gem_av' : av, 'cijfers' : []}
            
            stripped_data.append(dicet)
        else:
            continue
    logging.debug(stripped_data)
    print('Cijfers van v5 downloaden...', end="")
    #v5 gemiddeldes ophalen
    for gemiddelde in v5cijfers['Items']:
        # Dit is een SE gemiddelde!
        logging.debug(f"{gemiddelde['CijferKolom']['KolomKop']}")
        if gemiddelde['CijferKolom']['KolomKop'] == "VSED":
            logging.debug("HIT!")
            gid = gemiddelde['CijferKolom']['Id']

            tries = 0 
            while tries <= 5:
                w_raw = m.GET(f"{strippedurl}/api/personen/{uid}/cijfers/gerelateerdekolommen/{gid}")
                if(w_raw == None or w_raw == False):
                    tries += 1
                else:
                    break
                    
            if w_raw == None or w_raw == False:
                logging.critical("Kon cijfers niet ophalen!")
                m.dispose()
                exit()
            logging.debug(w_raw)

            w = json.loads(w_raw)

            weegf = 0
            for cijfer in w['Items']:
                weegf += cijfer['Weegfactor']

                
            af = gemiddelde['Vak']['Afkorting']
            for j in stripped_data:
                if af == j['afkorting']:
                    logging.debug(f"Cijfer: {gemiddelde['CijferStr'].replace(',', '.')}. Weegfactor: {weegf}")
                    j['cijfers'].append({'value': float(gemiddelde['CijferStr'].replace(',', '.')), 'weegfactor' : weegf})
        else:
            continue
    print("OK")
    logging.debug(stripped_data)

    print('Cijfers van v6 downloaden...', end="")
    # Data filling run
    for cijfer in cijfers['Items']:
        typ = cijfer['CijferKolom']['KolomSoort']

        if typ == 1: 
            af = cijfer['Vak']['Afkorting']
            
            # Vul met cijfers
            for j in stripped_data:
                if j['afkorting'] == af:

                    cs = cijfer['CijferStr'].replace(',', '.')
                    if cs != 'O' and cs != 'V' and cs != 'G' and cs != 'Vr':
                        # Gekke conversion omdat er kommas worden gebruikt
                        c = float(cs)
                    else:
                        c = cs

                    tries = 0 
                    while tries <= 5:
                        w_raw = m.GET(f"{strippedurl}/api/personen/{uid}/aanmeldingen/{aid}/cijfers/extracijferkolominfo/{cijfer['CijferKolom']['Id']}")
                        logging.debug(w_raw)
                        if(w_raw == None or w_raw == False):
                            tries += 1
                        else:
                            break
                    
                    if w_raw == None or w_raw == False:
                        logging.critical("Kon cijfers niet ophalen!")
                        m.dispose()
                        exit()

                    logging.debug(w_raw)
                    
                    w = json.loads(w_raw)
                    

                    dicts = {'value' : c, 'weegfactor' : w['Weging']}
                    logging.debug(dicts)
                    j['cijfers'].append({'value' : c, 'weegfactor' : w['Weging']})
            
        else:
            # Opmerkingen veld, heb je niks aan
            continue

    logging.debug(stripped_data)
    print("OK")
    m.dispose()

    
    f.write("\n\n============ CIJFER CHECK ==============\n")
    valid = True
    # Checken maar!
    for vak in stripped_data:
        delim = 0
        values = 0
        
        for cijfer in vak['cijfers']:
            if isinstance(cijfer['value'], str):
                continue
            values += cijfer['value']*cijfer['weegfactor']
            delim += cijfer['weegfactor']
        try:
            ex_g = values/delim
            val = math.ceil(ex_g*10)/10
            if vak['gem_av'] == val:
                print(f"OK! Vak {vak['naam']} geverifieerd!")
                f.write(f"{vak['naam']} - OK\n")
            else:
                logging.error(f"Vak {vak['naam']} heeft een ander gemiddelde dan berekend! (Berekend: {val})")
                f.write(f"{vak['naam']} - FOUT (Akkoordverklaring gemiddelde: {vak['gem_av']}. Berekend gemiddelde: {val})\n")
                logging.debug(f'gem_av = {vak["gem_av"]}, calc = {val}')
                valid = False
        except Exception as e:
            logging.critical(f"Vak {vak['naam']} kon niet worden berekend")
            f.write(f"{vak['naam']} - FOUT (kan niet worden berekend)\n")
            logging.debug(e)
    
    f.write("===============================================\n")
    if not valid:
        logging.critical("ONGELDIGE AKKOORDVERKLARING!")
        f.write(f"Result: Invalid")
    else:
        print("Akkoordverklaring is OK!")
        f.write(f"Result: Valid")
    
    f.close()
    exit(0)