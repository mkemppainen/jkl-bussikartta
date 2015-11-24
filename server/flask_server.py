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
    return render_template('virhe.html',selitys='aalio')

@app.route("/get_stops")
def get_stops():
    #tsekkaillaan että löytyy tarvittavat argumentit ja ovat oikeata muotoa
    #if request.method == 'GET' and request.args.get('time') is not None:
    if request.args.get('time') is not None:
        try:
            time.strptime(str(request.args.get('time')), '%H:%M:%S')            
            stoptime = map(int, request.args.get('time').split(':',2))
            print(stoptime, file=sys.stderr)#test
        except ValueError:
            return render_template('virhe.html',selitys=u'Annetut tiedot ovat väärää tyyppiä')
        
        service_id_ehto = get_service_id_condition(datetime.datetime.today())

        #Hakee ajan perusteella tiedon missa kohdissa busseja on liikkeella
        #TODO kaivannee lisatietoa: lat, lon?
        #HUOM LOPUSSA PUUTTUU SKANDIT SERVICE_ID:STA
        con = sqlite3.connect("tietokanta_testi.data")
        con.text_factory = str
        cur = con.cursor()
        #TODO tarkistus myos sekuntien mukaan. Poikkeuksia on todella vahan, ei kiireinen
        cur.execute('select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where saapumis_aika_tunnit = ' + str(stoptime[0]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[1] + 10) + ' and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + request.args.get('route') + '\" and ' + service_id_ehto)
        rows = cur.fetchall()
        print("rivien testi", file=sys.stderr)
        print(rows, file=sys.stderr)

        if len(rows) <= 0: return(render_template('virhe.html',selitys='Annettua linjaa ei ole'))
        elif len(rows[0]) <= 0: return(render_template('virhe.html',selitys='Kaalimaassa sataa usein'))
        tripId = rows[0][0]
        stopit = {
            "reitinNimi": request.args.get('route'),
            "matkat": []
                }

        a = 0
        j = 0
        i = 0
        while i is not len(rows) - 1:
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
                tripId = rows[i][0]
                j+=1
        f = open("stoppidata.txt","w")
        f.write(json.dumps(stopit))
        resp = Response(response=json.dumps(stopit),
        status=200,
        mimetype="application/json")   
        
    return(resp)

def get_weekday(weekday_number):
    return {
        0: "M-P",
        1: "M-P",
        2: "M-P",
        3: "M-P",
        4: "M-P",
        5: "L -",
        6: "S -"
    }[weekday_number]

    
def get_service_id_condition(pvm):
    lista = get_service_ids(pvm)

    if len(lista) <= 0: return('(1==2)')
    return(('(service_id like \"' + '\" OR service_id like \"'.join(lista) + '\")'))
    

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
def check_argument(argument):
     if request.method == 'GET' and argument is not None:
            print(argument, file=sys.stderr)
            try:
                time.strptime(str(request.args.get('time')), '%H:%M:%S')            
                stoptime = map(int, request.args.get('time').split(':',2))
                print(stoptime, file=sys.stderr)#test
                service_id = get_weekday(datetime.datetime.today().weekday())
                print(service_id, file=sys.stderr)#test
                return stoptime
            except ValueError:
                return render_template('virhe.html')

#Pitaa muokata hakemaan dataa dynaamisesti, nyt palautuu osittain staattinen
#JSON-data
@app.route("/get_route")
def get_route():
    if request.method == 'GET' and request.args.get('time') is not None:
        print(request.args.get('route'), file=sys.stderr)
        try:
            time.strptime(str(request.args.get('time')), '%H:%M:%S')            
            stoptime = map(int, request.args.get('time').split(':',2))
            print(stoptime, file=sys.stderr)#test
            service_id = get_weekday(datetime.datetime.today().weekday())
            print(service_id, file=sys.stderr)#test
        except ValueError:
            return render_template('index.html')
        #Haetaan kannasta halutulle linjalle kuuluvat pysakit
        connection = sqlite3.connect("tietokanta_testi.data")
        connection.text_factory = str
        cursor = connection.cursor()
        #haetaan reitin tiedot
        cursor.execute("select distinct pysakit.lat, pysakit.lon from pysakit, pysahtymis_ajat where pysakit.stop_id = pysahtymis_ajat.stop_id and pysahtymis_ajat.trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"" + str(request.args.get('route')) + "\")) and pysahtymis_ajat.trip_id in (select trip_id from pysahtymis_ajat where saapumis_aika_tunnit = " + str(stoptime[0]) + "  and saapumis_aika_minuutit = " + str(stoptime[1]) + ") order by pysahtymis_ajat.trip_id")
       
        
        #kannasta haetut pysakkien koordinaatit
        stop_crdnts = [[item for item in r] for r in cursor.fetchall()]
        route_crdnts = [] #reitin kaikki koordinaatit
        #haetaan jokaiselle koordinaattiparille reitti, tallennetaan

        for i in range(0, len(stop_crdnts)):
            stop1 = stop_crdnts[i][1] + ',' + stop_crdnts[i][0]
            if i+1 < len(stop_crdnts):
                stop2 = stop_crdnts[i+1][1] + ',' + stop_crdnts[i+1][0]
            i+=1
            #haetaan pysakkien valin koordinaatit
            r  = requests.get('https://api.mapbox.com/v4/directions/mapbox.driving/'+ stop1 + ';' + stop2 + '.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')    
            
            #heitetaan koordinaatit reitin listalle
            print(r.text, file=sys.stderr)
            jisondata = json.loads(r.text)
            route_crdnts.append(jisondata["routes"][0]["geometry"]["coordinates"])
            
            
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
