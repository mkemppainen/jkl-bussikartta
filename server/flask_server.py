#!/usr/bin/env python
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

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#Testasin koodia. Täysin turha
@app.route('/testi/')
def testi():
    print(get_service_id_condition(datetime.datetime.today()))
    return render_template('virhe.html'),400

@app.route("/get_all_stops")
def get_all_stops():
    
    return None

@app.route("/get_stops")
def get_stops():
    #tsekkaillaan että löytyy tarvittavat argumentit ja ovat oikeata muotoa
    check_argument('route', request.args.get('route'))
    stoptime = check_argument('time', request.args.get('time'))
    if stoptime is not None:
        service_id_ehto = get_service_id_condition(datetime.datetime.today())

        #Hakee ajan perusteella tiedon missa kohdissa busseja on liikkeella
        #HUOM LOPUSSA PUUTTUU SKANDIT SERVICE_ID:STA
        con = sqlite3.connect("tietokanta_testi.data")
        con.text_factory = str
        cur = con.cursor()
        #TODO tarkistus myos sekuntien mukaan. Poikkeuksia on todella vahan, ei kiireinen
        valinta = 'select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where saapumis_aika_tunnit = ' + str(stoptime[0]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[1] + 10) + ' and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + request.args.get('route') + '\" and ' + service_id_ehto + '))'
        print(valinta)
        cur.execute(valinta)
        rows = cur.fetchall()

        if len(rows) <= 0: return(render_template('virhe.html'),400)
        elif len(rows[0]) <= 0: return(render_template('virhe.html'),400)
        tripId = rows[0][0]
        stopit = {
            "reitinNimi": request.args.get('route'),
            "matkat": []
                }

        i = 0
        #luodaan selaimelle palautettava json-data
        while i is not len(rows) - 1:
            #pysahdykset ensimmaiselle trip_id:lle
            if rows[i][0] == tripId:
                 stopit["matkat"].append({
                     "tripID": tripId,
                     "pysahdykset" : []})
                 print(i, file=sys.stderr)
                 while rows[i][0] == tripId and i < len(rows) - 1:
                     stopit["matkat"][j]["pysahdykset"].append({
                         "lahtoID": rows[i][1],
                         "paateID": rows[i+1][1],
                         "lahtoAika": str(rows[i][2]) + ':' + str(rows[i][3]) + ':' + str(rows[i][4]),
                         "paateAika": str(rows[i][5]) + ':' + str(rows[i][6]) + ':' + str(rows[i][7]),
                         "duration": "300",
                             })
                     i+=1
            else:
                #vaihdetaan seuraava trip_id
                tripId = rows[i][0]
                j+=1
        #kirjoitus tiedostoon testin vuoksi
        f = open("stoppidata.txt","w")
        f.write(json.dumps(stopit))

        resp = Response(response=json.dumps(stopit),
        status=200,
        mimetype="application/json")   
        
    return(resp)
    
def get_service_id_condition(pvm):
    lista = get_service_ids(pvm)

    if len(lista) <= 0: return('(1==2)')
    a = ('(service_id like \"' + '\" OR service_id like \"'.join(lista) + '\")')
    print(a)
    return(a)
    

#Antaa sopivat service id:t listana
def get_service_ids(pvm):
    connection = sqlite3.connect("tietokanta_testi.data")
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute("select distinct service_id, maanantai, tiistai, keskiviikko, torstai, perjantai, lauantai, sunnuntai, alku_paiva, loppu_paiva from Kalenteri")

    id_list = list()
    for row in cursor.fetchall():#TODO Tarkista toimivuus.
        if is_day_between(pvm, row[8], row[9]) and row[1+pvm.weekday()] == '1': id_list.append(row[0])
    print(id_list)
    return(id_list)

#Tarkistaa onko annettu paiva, muiden kahden annetun paivan valissa.
def is_day_between(middle,left, right):
    #TODO Tarkista, etta toimii sellaisina paivina, jolloin kuukausi ja paiva on yhdella luvulla esitettavissa
    middle_number = int('{0:0=4d}{1:0=2d}{2:0=2d}'.format(middle.year,middle.month,middle.day))#Todella ruma tapa. En tunnusta kirjoittaneeni tata.
    print('{0} <= {1} <= {2}'.format(left, middle_number, right))
    return(int(left) <= middle_number and middle_number <= int(right)) #Ei saisi tehdä tarkistamattonta parsimista intiksi. Tietokannassa kuitenkin pitaisi olla vain lukuja.

#Tarkistaa annetun argumentin oikeellisuuden        
def check_argument(argument, value):
     if request.method == 'GET' and argument is not None:
            print(argument, file=sys.stderr)
            try:
                if argument == 'time':
                    time.strptime(str(value), '%H:%M:%S')       
                    stoptime = list(map(int, value.split(':',2)))
                    print(stoptime, file=sys.stderr)#test
                    return stoptime
                elif argument == 'route':
                    return value
                else:
                    return None
            except ValueError:
                return None

#Pitaa muokata hakemaan dataa dynaamisesti, nyt palautuu osittain staattinen
#JSON-data
@app.route("/get_route")
def get_route():
    
    route = check_argument('route', request.args.get('route'))
    stoptime = check_argument('time', request.args.get('time'))
    if stoptime is not None:
        #Haetaan kannasta halutulle linjalle kuuluvat pysakit
        connection = sqlite3.connect("tietokanta_testi.data")
        connection.text_factory = str
        cursor = connection.cursor()
        #haetaan reitin tiedot

        service_id_ehto = service_id_ehto = get_service_id_condition(datetime.datetime.today())
        cursor.execute("select distinct pysakit.lat, pysakit.lon from pysakit, pysahtymis_ajat where pysakit.stop_id = pysahtymis_ajat.stop_id and pysahtymis_ajat.trip_id in (select trip_id from matkat where " + service_id_ehto +" and route_id in (select route_id from matkojen_nimet where lnimi like \"" + str(request.args.get('route')) + "\")) and pysahtymis_ajat.trip_id in (select trip_id from pysahtymis_ajat where saapumis_aika_tunnit = " + str(stoptime[0]) + "  and saapumis_aika_minuutit = " + str(stoptime[1]) + ") order by pysahtymis_ajat.trip_id")
       
        
        #kannasta haetut pysakkien koordinaatit
        stop_crdnts = [[item for item in r] for r in cursor.fetchall()]
        route_crdnts = [] #reitin kaikki koordinaatit
        #haetaan jokaiselle koordinaattiparille reitti, tallennetaan
        for i in range(0, len(stop_crdnts)-1):
            stop1 = stop_crdnts[i][1] + ',' + stop_crdnts[i][0]
            #if i+1 < len(stop_crdnts):
            stop2 = stop_crdnts[i+1][1] + ',' + stop_crdnts[i+1][0]
            
            #haetaan pysakkien valin koordinaatit
            cursor.execute("select tripcrd from pysakkiparit where stop_id_1 = (select stop_id from pysakit where lat = " + stop_crdnts[i][0] + " and lon = " + stop_crdnts[i][1] + " ) and stop_id_2 = ( select stop_id from pysakit where lat = " + stop_crdnts[i+1][0] + " and lon = " + stop_crdnts[i+1][1] + ")")
            i+=1
            
            #heitetaan koordinaatit reitin listalle
            f = cursor.fetchone()
            if f is not None:
                a = f[0].replace("(", "")
                b = a.replace(")", "")
                c = b.split(',')            
            d =[]
            i = 0
            while i < len(c)-1:
                d.append([c[i], c[i+1]])
                i+=2
            route_crdnts.append(d)
            
            
        #Tassa muodossa palautus selaimelle
        #TODO kannasta saadut tiedot staattisien tilalle
        # Tallainen jokaiselle pysakinvalille {lahtonimi, lahtoaika, lahtopiste, paatenimi, paatepiste, paateaika, duration, coords[[data,data]]}
        j = 0   
        r2 = {
            "reitinNimi":str(request.args.get('route')),
            "pysakinValit":[]}
        for i in range(0,len(stop_crdnts) - 1):
            r2["pysakinValit"].append({
            "lahtoNimi":"pysakki3",
            "lahtoAika":"12:15",
            "lahtoPiste":[stop_crdnts[i][1],stop_crdnts[i][0]],
            "paateNimi":"pysakki17",
            "paatePiste":[stop_crdnts[i+1][1],stop_crdnts[i+1][0]],
            "paateAika": "12:20",
            "duration": 300,
            "coordinates":route_crdnts[i]})#[j]["coordinates"] = route_crdnts[j]
            i+=1
        #testin vuoksi datan kirjoitus tiedostoon
        f = open("reittidata.txt","w")
        f.write(json.dumps(r2))

    resp = Response(response=json.dumps(r2),
        status=200,
        mimetype="application/json")   
        
    return(resp)
    

if __name__ == '__main__':
   app.run(debug=True)
