#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
from flask import Flask, Response
from flask import render_template
from flask import request
from flask import url_for, redirect, jsonify, make_response
import requests
import json
import sys
import sqlite3
import time
import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    print("Lähetetään index.html")
    lista = get_route_list("kala")
#    print("Lista:" + str(lista),file=sys.stderr)
    return render_template('index.html',lista=lista)

def create_response(data, error, error_code):
    if data is not None:
        resp = Response(response=json.dumps(data, ensure_ascii=False).encode('utf-8'),
        status = 200,
        content_type="application/json; charset=utf-8")
        return resp
    else:
        resp = Response(response=error,
        status = error_code )
        return resp

@app.route("/get_all_routes")
def get_all_routes():
    date = check_argument('date', request.args.get('date'))
    if date is not None:
        today = translate_weekday_name(datetime.datetime(2015, 11, 18).strftime("%A").lower())
        valinta = 'select distinct lnimi from matkojen_nimet where route_id in (select route_id from matkat where service_id in (select service_id from kalenteri where ' + today + ' = 1))'
        rows = [item[0] for item in exec_sql_query(valinta)]
#        print(valinta)
        if len(rows) <= 0:
            return render_template('virhe.html'),400
        
        route_names = {
            "reitit": rows
            }

        return(create_response(route_names, None, None))
    else:
        return create_response(None, "Virheellinen haku", 400)

#Gives list of all routes on given date
def get_route_list(date):
    if date is not None:
        # muutettu datetime.now() -> datetime.
        today = translate_weekday_name(datetime.datetime(2016, 11, 18).strftime("%A").lower())
        #valinta = 'select distinct lnimi from matkojen_nimet where route_id in (select route_id from matkat where service_id in (select service_id from kalenteri where ' + today + ' = 1))'
        valinta = 'select distinct lnimi from matkojen_nimet where route_id in (select route_id from matkat where service_id in (select service_id from kalenteri where ' + today + ' = 1))'

        sulut = lambda s: '(' + s + ')'
        inner1 = 'select service_id from kalenteri where ' + today + ' = 1'
        inner2 = 'select route_id from matkat where service_id in ' + sulut(inner1)
        valinta = 'select distinct lnimi from matkojen_nimet where route_id in ' + sulut(inner2)
                  
        return [item[0] for item in exec_sql_query(valinta)]
    else: return([])
     

def translate_weekday_name(weekday):
    return {
        'monday': 'maanantai',
        'tuesday': 'tiistai',
        'wednesday': 'keskiviikko',
        'thursday': 'torstai',
        'friday': 'perjantai',
        'saturday': 'lauantai',
        'sunday': 'sunnuntai',
    }[weekday]

def exec_sql_query(query):
    try:
        con = sqlite3.connect("tietokanta_testi.data")
        con.text_factory = str
        cur = con.cursor()
        cur.execute(query)
        resp = cur.fetchall()
        return resp
    except IOError:
        return None


@app.route("/get_single_route")
def get_single_route():
    id_1 = str(request.args.get('stop1'))
    id_2 = str(request.args.get('stop2'))

    valinta = "select pysakkiparit.tripcrd, pysakkiparit.duration from Pysakkiparit where stop_id_1 like \"" + id_1 + "\" and stop_id_2 like \"" + id_2 + "\""

    tulos = exec_sql_query(valinta)
#    print(tulos,file=sys.stderr)
    valinta2 = "select nimi, lat, lon from pysakit where stop_id like \"" + id_1 + "\""
    valinta3 = "select nimi, lat, lon from pysakit where stop_id like \"" + id_2 + "\""
    tulos2 = exec_sql_query(valinta2)
#    print(tulos2, file=sys.stderr)
    tulos3 = exec_sql_query(valinta3)
    if (len(tulos) <=0): return(create_response(None, "Tyhjä taulukko", 400))

    a = tulos[0][0].replace("(", "[")
    b = a.replace(")", "]")
    
    pysakinValit = {
            "lahtoNimi":tulos2[0][0],
            "lahtoPiste":[tulos2[0][1],tulos2[0][2]],
            "lahtoID":id_1,
            "paateNimi":tulos3[0][0],
            "paatePiste":[tulos3[0][1],tulos3[0][2]],
            "paateID":id_2,
            "duration": tulos[0][1],
            "coordinates":b
    }
    return(create_response(pysakinValit, None, None))

@app.route("/get_stops")
def get_stops():
    #tsekkaillaan että löytyy tarvittavat argumentit ja ovat oikeata muotoa 26
    route = check_argument('route', request.args.get('route'))
    if route == '27' or route=='25':
        print('saatanan 27')
        return(render_template('virhe.html', selitys='Virheellinen aika tai reitti'),400)
    
    stoptime = check_argument('time', request.args.get('time'))
    if stoptime is not None and route is not None:
        service_id_ehto = get_service_id_condition(datetime.datetime.now())
        #print('id ehto:)')
        #print(service_id_ehto)
        #Hakee ajan perusteella tiedon missa kohdissa busseja on liikkeella
        if stoptime[1] < stoptime[3]:
            #valinta = 'select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where saapumis_aika_tunnit between ' + str(stoptime[0]) + ' and ' + str(stoptime[4]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[3]) + ' and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + route + '\" and ' + service_id_ehto + '))'

            valinta = 'select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where saapumis_aika_tunnit between ' + str(stoptime[0]) + ' and ' + str(stoptime[4]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[3]) + ' and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + route + '\" ' + '))order by trip_id'
        else:
            #Melko kömpelö tapa tarkistaa ajat kun tunti vaihtuu, olisikohan jotain parempaa?
            valinta = 'select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where ((saapumis_aika_tunnit = ' + str(stoptime[0]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[1] + (59 - stoptime[1])) + ') or (saapumis_aika_tunnit =  ' + str(stoptime[4]) + ' and saapumis_aika_minuutit between 0 and ' + str(stoptime[3]) + ')) and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + route + '\"  '  + '))order by trip_id'
        rows = exec_sql_query(valinta)
        if len(rows) <= 0: return create_response(None, "Tyhjä taulukko", 400)
        elif len(rows[0]) <= 0: return(render_template('virhe.html', selitys='Tyhja taulukko2'),400)
        tripId = rows[0][0]
        stopit = {
            "reitinNimi": request.args.get('route'),
            "matkat": []
                }
        j = 0
        i = 0
        a = 0
        #luodaan selaimelle palautettava json-data
        """
        "lahtoAika": str(rows[i][2]) + ':' + str(rows[i][3]) + ':' + str(rows[i][4]),
        "paateAika": str(rows[i][5]) + ':' + str(rows[i][6]) + ':' + str(rows[i][7]),
        """
        while i is not len(rows) - 1:
            #pysahdykset ensimmaiselle trip_id:lle
            if rows[i][0] == tripId:
                 stopit["matkat"].append({
                     "tripID": tripId,
                     "pysahdykset" : []})
#                 print(i, file=sys.stderr)
                 while rows[i][0] == tripId and i < len(rows) - 1:
                     stopit["matkat"][j]["pysahdykset"].append({
                         "lahtoID": rows[i][1],
                         "paateID": rows[i+1][1],
                         "lahtoAika": str(rows[i][5]) + ':' + str(rows[i][6]) + ':' + str(rows[i][7]),
                         "paateAika": str(rows[i+1][2]) + ':' + str(rows[i+1][3]) + ':' + str(rows[i+1][4]),
                         "jnum": rows[i][8],
                         "onkoPaate": False
                     })
                     a+=1
                     if i == len(rows) - 2:
                         stopit["matkat"][j]["pysahdykset"][a-1]["onkoPaate"] = True
                     i+=1
            else:
                #vaihdetaan seuraava trip_id
                stopit["matkat"][j]["pysahdykset"][a-1]["onkoPaate"] = True
                tripId = rows[i][0]
                j+=1
                a=0

                
        return(create_response(stopit, None, None))

    else: return(render_template('virhe.html', selitys='Virheellinen aika tai reitti'),400)
    
def get_service_id_condition(pvm):
    lista = get_service_ids(pvm)

    if len(lista) <= 0: return('(1==2)')
    a = ('(service_id like \"' + '\" OR service_id like \"'.join(lista) + '\")')
    #print(a)
    return(a)
    

#Antaa sopivat service id:t listana
def get_service_ids(pvm):
    id_list = list()
    for row in exec_sql_query("select distinct service_id, maanantai, tiistai, keskiviikko, torstai, perjantai, lauantai, sunnuntai, alku_paiva, loppu_paiva from Kalenteri"):#TODO Tarkista toimivuus.
        # muutettu: or True, koska ei toiminu
        if is_day_between(pvm, row[8], row[9]) and row[1+pvm.weekday()] == '1' or True: id_list.append(row[0])
    #print(id_list)
    return(id_list)

#Tarkistaa onko annettu paiva, muiden kahden annetun paivan valissa.
def is_day_between(middle,left, right):
    #TODO Tarkista, etta toimii sellaisina paivina, jolloin kuukausi ja paiva on yhdella luvulla esitettavissa
    middle_number = int('{0:0=4d}{1:0=2d}{2:0=2d}'.format(middle.year,middle.month,middle.day))#Todella ruma tapa. En tunnusta kirjoittaneeni tata.
    #print('{0} <= {1} <= {2}'.format(left, middle_number, right))
    return(int(left) <= middle_number and middle_number <= int(right)) #Ei saisi tehdä tarkistamattonta parsimista intiksi. Tietokannassa kuitenkin pitaisi olla vain lukuja.

#Tarkistaa annetun argumentin oikeellisuuden        
#TODO date tarkistus
def check_argument(argument, value):
    if request.method == 'GET' and argument is not None:
#        print(argument, file=sys.stderr)
        try:
            if argument == 'time':
                try:
                    time.strptime(str(value), '%H:%M:%S')
                    stoptime = list(map(int, value.split(':',2)))
                except ValueError:
                    tmp = list(map(int, value.split(':',2)))
                    if (tmp[0] >= 24 and tmp[0] < 28) is not True:
                        return None
                    stoptime = tmp
                
                #Lisätään stoptime-taulukkoon myös ajat 5min ennen ja 10min jälkeen haetun ajan
                if stoptime[1] + 10 >= 60:
                    stoptime.append(stoptime[1] + 10 - 60)
                    stoptime.append(stoptime[0] + 1)
                else:
                    stoptime.append(stoptime[1] + 10)
                    stoptime.append(stoptime[0] + 0)
                if stoptime[1] - 5 < 0:
                    stoptime[1] = stoptime[1] - 5 + 60
                    stoptime[0] -= 1
                else:
                    stoptime[1] -= 5
                
#                print(stoptime, file=sys.stderr)#test
                return stoptime
            elif argument == 'route':
                routes = [item[0] for item in exec_sql_query('select distinct lnimi from matkojen_nimet')]
                if value not in routes:
                    return None
                return value
            elif argument == 'date':
                return value
            elif argument == 'luku':
                if value is None: return None
                return int(value)
            else:
                return None
        except ValueError:
            return None
    return None


@app.route("/get_route")
def get_route():
    #Tarkistetaan että löytyy oikeat argumentit ja ovat oikeita
    route = check_argument('route', request.args.get('route'))
    stoptime = check_argument('time', request.args.get('time'))

    day = check_argument('luku', request.args.get('day'))
    month = check_argument('luku', request.args.get('month'))
    year = check_argument('luku', request.args.get('year'))

    

    if (day is None or month is None or year is None): date = datetime.datetime.today()
    # todo: tonow: 
    else: date = datetime.date(year, month, day)

    if stoptime is not None and route is not None:
        #Haetaan kannasta halutulle linjalle kuuluvat pysakit
        service_id_ehto = service_id_ehto = get_service_id_condition(date) #todo: tassa saattaa olla vikaa, onko date vs datetime oikein get_service_id_ssa
       
        trip_id_ehto = "select distinct trip_id from Matkat where route_id in (select route_id from Matkojen_nimet where lnimi like \"" + route + "\" and " + service_id_ehto + " and trip_id in (select trip_id from Pysahtymis_ajat where lahto_aika_tunnit like \"" + str(stoptime[0]) + "\" and lahto_aika_minuutit BETWEEN " + (str(int(stoptime[1]) - 10)) + " and " + str(int(stoptime[1]) + 10) + "))"

        #print(trip_id_ehto)
        trip_id_lista = [[item for item in r] for r in exec_sql_query(trip_id_ehto)]
        if len(trip_id_lista) <= 0: return render_template('virhe.html',selitys='Ei löydy sopivia matkoja'),400

        reitti_lista = []

        #Haetaan kullekin trip_id:lle reitin tiedot.
        for trip_id_i in trip_id_lista:
            trip_id = trip_id_i[0]
            try:
                hakuehto = "select Pysakit.lat, Pysakit.lon, Pysakit.nimi, Pysahtymis_ajat.stop_id, Pysahtymis_ajat.jnum, Pysahtymis_ajat.lahto_aika_tunnit, Pysahtymis_ajat.lahto_aika_minuutit from Pysahtymis_ajat, Pysakit where trip_id like \"" + trip_id + "\" and Pysakit.stop_id like Pysahtymis_ajat.stop_id order by jnum asc" 
            except TypeError: 
                return render_template('virhe.html',selitys='Tyyppivirhe3'),400
            tiedot = [[item for item in r] for r in exec_sql_query(hakuehto)]

            pari_lista = []

            #Käydään kaikki muut paitsi viimeinen kierros läpi.
            for i in range(0, len(tiedot) - 1):
                a_lat = tiedot[i][0]
                a_lon = tiedot[i][1]
                a_nimi = tiedot[i][2]
                a_stop_id = tiedot[i][3]
                a_jnum = tiedot[i][4]

                lahto_aika_tunnit = tiedot[i][5]
                lahto_aika_minuutit = tiedot[i][6]

                l_lat = tiedot[i+1][0]
                l_lon = tiedot[i+1][1]
                l_nimi = tiedot[i+1][2]
                l_stop_id = tiedot[i+1][3]
                l_jnum = tiedot[i+1][4]

                reitti_kysely= "select tripcrd, duration from pysakkiparit where stop_id_1 like \"" + a_stop_id + "\" and stop_id_2 = \"" + l_stop_id + "\""
                reitti = [[item for item in r] for r in exec_sql_query(reitti_kysely)]

                if reitti == None: return(render_template('virhe.html',selitys='Ei löydetä pysäkkien välistä reittiä.'),4002) 
                duration = reitti[0][1]

                a = reitti[0][0].replace("(", "")
                b = a.replace(")", "")
                c = b.split(',')  

                koordinaatit =[]
            
                j = 0
                while j < len(c)-1:
                    try:
                        koordinaatit.append([float(c[j]),float(c[j+1])])
                        j+=2
                    except TypeError:
                        return render_template('virhe.html', selitys='Tyyppivirhe'),4003
                
                taso = {
                    "lahtoNimi": a_nimi,
                    "lahtoPiste": [a_lon,a_lat],
                    "lahtoID": a_stop_id,
                    "paateNimi": l_nimi,
                    "paatePiste": [l_lon,l_lat],
                    "paateID": l_stop_id,
                    "duration": duration,
                    "lahtoAikaTunnit": lahto_aika_tunnit,
                    "lahtoAikaMinuutit": lahto_aika_minuutit,
                    "coordinates": koordinaatit}
                pari_lista.append(taso)
            #Parien läpikäynti loppuu
            r2 = {
                "reitinNimi":str(request.args.get('route')),
                "pysakinValit": pari_lista}
            reitti_lista.append(r2)
        #Trip_id läpikäynti loppuu
        r1 = {"reitit": reitti_lista}
        
        #Palautetaan tulos
        return create_response(r1, None, None)
    else:
        return(create_response(None, "Virheellinen aika tai reitti", 4004)) 


if __name__ == '__main__':
    port = os.environ.get('PORT')
    if port is not None:
        app.run(host='0.0.0.0', port=int(port), debug=True)
    else:
        app.run(debug=True)
