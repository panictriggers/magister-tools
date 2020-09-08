# Quick Guide

## Eerste stappen
Voordat je met dit programma aan de slag kan moet je weten wat een terminal is.

1. Download [Python](https://python.org)
2. Unzip de bestanden naar een map naar keuze
3. Open een terminal in `early-subscriber/src`
4. Run `pip install -r requirements.txt` (dit installeert alle dependencies)
5. Open `main.py`. Daarin zie je `username` en `password`. Hier moeten je inloggegevens van Magister in komen.
6. Stel `start_tool` in als `True` als je direct de inschrijving wilt opvragen. Gebruik `start_tool = datetime(jaar, maand, dag, uur, minuut, seconde, microseconde)` als je wilt dat het script op een specifiek tijdstip start (aanbeloven)


## De juiste links vinden
Het script wilt van te voren de links weten die hij moet opvragen. Dit kan die niet uit zichzelf...

**Stap 1.** Log in Magister. Ga naar de 'Activiteiten' pagina

**Stap 2.** Open Inspector/Element Inspecteren. Ga naar het tabblad 'Netwerk' (zie plaatje)

![foto?](https://i.imgur.com/RS5i9Jy.png)

**Stap 3.** Druk op een activiteit/ronde. Je zult nu zien dat er requests binnenkomen.

**Stap 4.** Druk op de request 'onderdelen'. Druk in de popup op 'response'. (zie plaatje)

![foto?](https://i.imgur.com/D6JAdJJ.png)

**Stap 5.** In de response popup zie je allemaal 'Objects'. Als je die opent zie je een veld genaamd `Titel`. Daaruit is te halen om welke sport het gaat. (zie plaatje)

![foto?](https://i.imgur.com/rucZW39.png)

**Stap 6.** Zoek het veld `href` in `links` -> `subscribe` (zie plaatje). Deze link heb je nodig. Voorbeeldlink: `https://nuovo.magister.net/api/personen/123456/activiteiten/666/onderdelen/1234/inschrijvingen`

![Waar is ie dan?](https://i.imgur.com/6JqV18J.png)

**Stap 7.** In het script (`main.py`) zie je een variablele genaamd `link_queue`. Per link zijn er twee variabelen nodig: de link (die je net hebt gekregen) en een JSON Payload.
Wat dat precies is, is een zorg voor later. De JSON payload is als volgt te maken. 

Stel onze link is `https://nuovo.magister.net/api/personen/123456/activiteiten/666/onderdelen/1234/inschrijvingen`, dan is onze payload `{"persoonId":"123456","activiteitId":"666","onderdeelId":"1234"}`.

Zet de link op de volgende manier in het script:
```py
link_queue = [Link("link", {"persoonId":"123456","activiteitId":"666","onderdeelId":"1234"})
```

Mocht je meer links willen gebruiken, voeg dan een comma toe.

Voorbeeld:
```py
link_queue = [Link("https://nuovo.magister.net/api/personen/100757/activiteiten/888/onderdelen/7403/inschrijvingen", {"persoonId":"100755","activiteitId":"888","onderdeelId":"7403"}), 
              Link("https://nuovo.magister.net/api/personen/100757/activiteiten/906/onderdelen/7537/inschrijvingen", {"persoonId":"100755","activiteitId":"906","onderdeelId":"7537"}),
              Link("https://nuovo.magister.net/api/personen/100757/activiteiten/899/onderdelen/7465/inschrijvingen", {"persoonId":"100755","activiteitId":"899","onderdeelId":"7465"}),
              Link("https://nuovo.magister.net/api/personen/100757/activiteiten/908/onderdelen/7550/inschrijvingen", {"persoonId":"100755","activiteitId":"908","onderdeelId":"7550"}),
              Link("https://nuovo.magister.net/api/personen/100757/activiteiten/909/onderdelen/7553/inschrijvingen", {"persoonId":"100755","activiteitId":"909","onderdeelId":"7553"})]
              
```

## Script runnen
Het script run je door `py main.py` in je terminal in te voeren. Als dat niet werkt: probeer `python3 main.py`. 
              
             
              
