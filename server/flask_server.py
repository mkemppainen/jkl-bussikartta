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

#TODO virheiden kasittely, vaarista pyynnoista virhekoodit ja tieto mika meni pieleen

@app.route('/')
def index():
    return render_template('index.html')

#TODO ei viela valmis, tarkista miten oikeasti kannattaa tehda
def create_response(data):
    if data is not None:
        resp = Response(response=json.dumps(data),
        status = 200,
        mimetype = "application/json")
        return resp
    else:
        resp = Response(response=render_template('virhe.html'),
        status = 400 )
        return resp

@app.route("/get_all_routes")
def get_all_routes():
    date = check_argument('date', request.args.get('date'))
    if date is not None:
        today = translate_weekday_name(datetime.datetime.now().strftime("%A").lower())
        valinta = 'select distinct lnimi from matkojen_nimet where route_id in (select route_id from matkat where service_id in (select service_id from kalenteri where ' + today + ' = 1))'
        rows = [item[0] for item in exec_sql_query(valinta)]
        
        if len(rows) <= 0:
            return render_template('virhe.html'),400
        
        route_names = {
            "reitit": rows
            }

        resp = Response(response=json.dumps(route_names),
        status=200,
        mimetype="application/json")
        
        return(resp)
    else:
        return render_template('virhe.html'),400

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
        return cur.fetchall()
    except IOError:
        return None

@app.route("/get_stops")
def get_stops():
    #tsekkaillaan että löytyy tarvittavat argumentit ja ovat oikeata muotoa
    route = check_argument('route', request.args.get('route'))
    stoptime = check_argument('time', request.args.get('time'))
    if stoptime is not None and route is not None:
        service_id_ehto = get_service_id_condition(datetime.datetime.today())
        
        #Hakee ajan perusteella tiedon missa kohdissa busseja on liikkeella
        if stoptime[1] < stoptime[3]:
            valinta = 'select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where saapumis_aika_tunnit between ' + str(stoptime[0]) + ' and ' + str(stoptime[4]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[3]) + ' and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + route + '\" and ' + service_id_ehto + '))'
        else:
            #Melko kömpelö tapa tarkistaa ajat, olisikohan jotain parempaa?
            valinta = 'select trip_id, stop_id, saapumis_aika_tunnit, saapumis_aika_minuutit, saapumis_aika_sekunnit, lahto_aika_tunnit, lahto_aika_minuutit, lahto_aika_sekunnit, jnum from pysahtymis_ajat where ((saapumis_aika_tunnit = ' + str(stoptime[0]) + ' and saapumis_aika_minuutit between ' + str(stoptime[1]) + ' and ' + str(stoptime[1] + (59 - stoptime[1])) + ') or (saapumis_aika_tunnit =  ' + str(stoptime[4]) + ' and saapumis_aika_minuutit between 0 and ' + str(stoptime[3]) + ')) and trip_id in (select trip_id from matkat where route_id in (select route_id from matkojen_nimet where lnimi like \"' + route + '\" and ' + service_id_ehto + '))order by trip_id'
        rows = exec_sql_query(valinta)
        if len(rows) <= 0: return(render_template('virhe.html', selitys='Tyhja taulukko'),400)
        elif len(rows[0]) <= 0: return(render_template('virhe.html', selitys='Tyhja taulukko2'),400)
        tripId = rows[0][0]
        stopit = {
            "reitinNimi": request.args.get('route'),
            "matkat": []
                }
        j = 0
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
                         "jnum": rows[i][8],
                             })
                     i+=1
            else:
                #vaihdetaan seuraava trip_id
                tripId = rows[i][0]
                j+=1
                
        resp = Response(response=json.dumps(stopit),
        status=200,
        mimetype="application/json")   
        return(resp)

    else: return(render_template('virhe.html', selitys='Virheellinen aika tai reitti'),400)
    
def get_service_id_condition(pvm):
    lista = get_service_ids(pvm)

    if len(lista) <= 0: return('(1==2)')
    a = ('(service_id like \"' + '\" OR service_id like \"'.join(lista) + '\")')
    print(a)
    return(a)
    

#Antaa sopivat service id:t listana
def get_service_ids(pvm):
    id_list = list()
    for row in exec_sql_query("select distinct service_id, maanantai, tiistai, keskiviikko, torstai, perjantai, lauantai, sunnuntai, alku_paiva, loppu_paiva from Kalenteri"):#TODO Tarkista toimivuus.
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
#TODO date tarkistus
def check_argument(argument, value):
     if request.method == 'GET' and argument is not None:
            print(argument, file=sys.stderr)
            #TODO ei hyvaksy aikoja yli 24h, kannasta sellaisia loytyy. Varmaan tehtava oma parsiminen ajalle
            try:
                if argument == 'time':
                    time.strptime(str(value), '%H:%M:%S')       
                    stoptime = list(map(int, value.split(':',2)))
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
                    
                    print(stoptime, file=sys.stderr)#test
                    return stoptime
                elif argument == 'route':
                    routes = [item[0] for item in exec_sql_query('select distinct lnimi from matkojen_nimet')]
                    if value not in routes:
                        return None
                    return value
                elif argument == 'date':
                    return value
                else:
                    return None
            except ValueError:
                return None

@app.route("/get_route")
def get_route():
    
    route = check_argument('route', request.args.get('route'))
    stoptime = check_argument('time', request.args.get('time'))
    if stoptime is not None and route is not None:
        #Haetaan kannasta halutulle linjalle kuuluvat pysakit
        service_id_ehto = service_id_ehto = get_service_id_condition(datetime.datetime.today())
        #try:
            #valinta = "select distinct pysakit.lat, pysakit.lon, pysakit.nimi, pysakit.stop_id, pysahtymis_ajat.trip_id, pysahtymis_ajat.jnum from pysakit, pysahtymis_ajat where pysakit.stop_id = pysahtymis_ajat.stop_id and pysahtymis_ajat.trip_id in (select trip_id from matkat where " + service_id_ehto +" and route_id in (select route_id from matkojen_nimet where lnimi like \"" + route + "\")) and pysahtymis_ajat.trip_id in (select trip_id from pysahtymis_ajat where saapumis_aika_tunnit = " + str(stoptime[0]) + "  and saapumis_aika_minuutit = " + str(stoptime[1]) + ") order by pysahtymis_ajat.trip_id, pysahtymis_ajat.jnum asc"
        #except TypeError:
        #    return render_template('virhe.html',selitys='Tyyppivirhe'),4001
       
        trip_id_ehto = "select distinct trip_id from Matkat where route_id in (select route_id from Matkojen_nimet where lnimi like \"" + route + "\" and " + service_id_ehto + " and trip_id in (select trip_id from Pysahtymis_ajat where lahto_aika_tunnit like \"" + str(stoptime[0]) + "\" and lahto_aika_minuutit BETWEEN " + (str(int(stoptime[1]) - 10)) + " and " + str(int(stoptime[1]) + 10) + "))"

        print(trip_id_ehto)
        trip_id_lista = [[item for item in r] for r in exec_sql_query(trip_id_ehto)]
        if len(trip_id_lista) <= 0: return render_template('virhe.html',selitys='Tyhjä taulukko'),400

        try:
            hakuehto = "select distinct Pysakit.lat, Pysakit.lon, Pysakit.nimi, Pysahtymis_ajat.stop_id, Pysahtymis_ajat.jnum from Pysahtymis_ajat, Pysakit where trip_id like \"" + trip_id_lista[0][0] + "\" and Pysakit.stop_id like Pysahtymis_ajat.stop_id order by jnum asc" 
        except TypeError: 
            return render_template('virhe.html',selitys='Tyyppivirhe'),400

        print(hakuehto,file=sys.stderr)

        #kannasta haetut pysakkien koordinaatit
        #stop_crdnts = [[item for item in r] for r in exec_sql_query(valinta)]
        stop_crdnts = [[item for item in r] for r in exec_sql_query(hakuehto)]
        #TODO Try catch castaukselle
        #reitin kaikki koordinaatit
        route_crdnts = []
        #pysakkivalien kestot
        durations = []
        
        if len(stop_crdnts) <= 0:
            return render_template('virhe.html',selitys='Tyhjä taulukko'),4001
        
        #haetaan jokaiselle koordinaattiparille reitti, tallennetaan
        i = 0
        while i < len(stop_crdnts)-1:
            #stop1 = stop_crdnts[i][1] + ',' + stop_crdnts[i][0]
            #stop2 = stop_crdnts[i+1][1] + ',' + stop_crdnts[i+1][0]          
            #haetaan pysakkien valin koordinaatit
            connection = sqlite3.connect("tietokanta_testi.data")
            connection.text_factory = str
            cursor = connection.cursor()
            valinta_kasky = "select tripcrd, duration from pysakkiparit where stop_id_1 = " + stop_crdnts[i][3] + " and stop_id_2 = " + stop_crdnts[i+1][3]
            #print(valinta_kasky)
            cursor.execute(valinta_kasky)
            
            #print(i,file=sys.stderr)
            #print(len(stop_crdnts),file=sys.stderr)
            print(stop_crdnts[i][3])
            print(stop_crdnts[i+1][3])
            i+=1

            #heitetaan koordinaatit reitin listalle
            f = cursor.fetchone()
            if f is not None:
                durations.append(f[1])
                a = f[0].replace("(", "")
                b = a.replace(")", "")
                c = b.split(',')            
            else: return(render_template('virhe.html',selitys='Hakuun ei löydy mitään kai.'),4002) 
            d =[]
            
            j = 0
            while j < len(c)-1:
                try:
                    d.append([float(c[j]),float(c[j+1])])
                    j+=2
                except TypeError:
                    return render_template('virhe.html', selitys='Tyyppivirhe'),4003
            route_crdnts.append(d)
            
            
        #Tassa muodossa palautus selaimelle
        j = 0   
        r2 = {
            "reitinNimi":str(request.args.get('route')),
            "pysakinValit":[]}
        for i in range(0,len(stop_crdnts) - 1):
            r2["pysakinValit"].append({
            "lahtoNimi":stop_crdnts[i][2],
            "lahtoPiste":[stop_crdnts[i][1],stop_crdnts[i][0]],
            "paateNimi":stop_crdnts[i+1][2],
            "paatePiste":[stop_crdnts[i+1][1],stop_crdnts[i+1][0]],
            "duration": durations[i],
            "coordinates":route_crdnts[i]})
            i+=1
    
        resp = Response(response=json.dumps(r2),
        status=200,
        mimetype="application/json")   
        
        return(resp)
    
    else:
        return(render_template('virhe.html'),4004) 
    

if __name__ == '__main__':
   app.run(debug=True)
