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
    print("Lähetetään index.html")
    lista = get_route_list("kala")
    print("Lista:" + str(lista),file=sys.stderr)
    return render_template('index.html',lista=lista)

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

        resp = Response(response=json.dumps(route_names, ensure_ascii=False).encode('utf-8'),
        content_type="application/json; charset=utf-8",
        status=200
        )
        
        return(resp)
    else:
        return render_template('virhe.html'),400

#Gives list of all routes on given date
def get_route_list(date):
    if date is not None:
        today = translate_weekday_name(datetime.datetime.now().strftime("%A").lower())
        valinta = 'select distinct lnimi from matkojen_nimet where route_id in (select route_id from matkat where service_id in (select service_id from kalenteri where ' + today + ' = 1))'
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
        return cur.fetchall()
    except IOError:
        return None


@app.route("/get_single_route")
def get_single_route():
    id_1 = str(request.args.get('stop1'))
    id_2 = str(request.args.get('stop2'))

    valinta = "select pysakkiparit.tripcrd, pysakkiparit.duration from Pysakkiparit where stop_id_1 like \"" + id_1 + "\" and stop_id_2 like \"" + id_2 + "\""

    tulos = exec_sql_query(valinta)
    print(tulos,file=sys.stderr)
    valinta2 = "select nimi, lat, lon from pysakit where stop_id like \"" + id_1 + "\""
    valinta3 = "select nimi, lat, lon from pysakit where stop_id like \"" + id_2 + "\""
    tulos2 = exec_sql_query(valinta2)
    print(tulos2, file=sys.stderr)
    tulos3 = exec_sql_query(valinta3)
    #if (len(tulos) <=1): return(render_template('virhe.html', selitys='Sopivaa väliä ei löytynyt.'),4005)

    pysakinValit = {
            "lahtoNimi":tulos2[0][0],
            "lahtoPiste":[tulos2[0][1],tulos2[0][2]],
            "lahtoID":id_1,
            "paateNimi":tulos3[0][0],
            "paatePiste":[tulos3[0][1],tulos3[0][2]],
            "paateID":id_2,
            "duration": tulos[0][1],
            "coordinates":tulos[0][0]
    }
    
    resp = Response(response=json.dumps(pysakinValit, ensure_ascii=False).encode('utf-8'),
        content_type='application/json; charset=utf-8',
        status=200
        )   
    return(resp)

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
            #Melko kömpelö tapa tarkistaa ajat kun tunti vaihtuu, olisikohan jotain parempaa?
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
                 print(i, file=sys.stderr)
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

                
        resp = Response(response=json.dumps(stopit, ensure_ascii=False).encode('utf-8'),
        content_type='application/json; charset=utf-8',
        status=200
        )   
        return(resp)

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
        if is_day_between(pvm, row[8], row[9]) and row[1+pvm.weekday()] == '1': id_list.append(row[0])
    #print(id_list)
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
    else: date = datetime.date(year, month, day)

    if stoptime is not None and route is not None:
        #Haetaan kannasta halutulle linjalle kuuluvat pysakit
        service_id_ehto = service_id_ehto = get_service_id_condition(date)
       
        trip_id_ehto = "select distinct trip_id from Matkat where route_id in (select route_id from Matkojen_nimet where lnimi like \"" + route + "\" and " + service_id_ehto + " and trip_id in (select trip_id from Pysahtymis_ajat where lahto_aika_tunnit like \"" + str(stoptime[0]) + "\" and lahto_aika_minuutit BETWEEN " + (str(int(stoptime[1]) - 10)) + " and " + str(int(stoptime[1]) + 10) + "))"

        #print(trip_id_ehto)
        trip_id_lista = [[item for item in r] for r in exec_sql_query(trip_id_ehto)]
        if len(trip_id_lista) <= 0: return render_template('virhe.html',selitys='Tyhjä taulukko'),400

        try:
            hakuehto = "select Pysakit.lat, Pysakit.lon, Pysakit.nimi, Pysahtymis_ajat.stop_id, Pysahtymis_ajat.jnum from Pysahtymis_ajat, Pysakit where trip_id in (" + trip_id_ehto + ") and Pysakit.stop_id like Pysahtymis_ajat.stop_id order by trip_id, jnum asc" 
        except TypeError: 
            return render_template('virhe.html',selitys='Tyyppivirhe'),400

        print(hakuehto,file=sys.stderr)

        #kannasta haetut pysakkien koordinaatit
        stop_crdnts = [[item for item in r] for r in exec_sql_query(hakuehto)]
        
        print('Löydettyjen pysäkkien määrä: ' + str(len(stop_crdnts)), file=sys.stderr)

        #TODO Try catch castaukselle
        #reitin kaikki koordinaatit
        route_crdnts = []
        #pysakkivalien kestot
        durations = []
        
        if len(stop_crdnts) <= 0:
            return render_template('virhe.html',selitys='Tyhjä taulukko'),4001
        
        #haetaan jokaiselle koordinaattiparille reitti, tallennetaan
        i = 0
        ii = 1
        while i < len(stop_crdnts)-1:
            #stop1 = stop_crdnts[i][1] + ',' + stop_crdnts[i][0]
            #stop2 = stop_crdnts[i+1][1] + ',' + stop_crdnts[i+1][0]          
            #haetaan pysakkien valin koordinaatit
            connection = sqlite3.connect("tietokanta_testi.data")
            connection.text_factory = str
            cursor = connection.cursor()
            if stop_crdnts[i+1][4] is not stop_crdnts[i][4] + 1:
                if stop_crdnts[i+1][3] == stop_crdnts[i][3]:
                    del stop_crdnts[i+1]
                else:
                    i += 1
                ii += 1
                
            valinta_kasky = "select tripcrd, duration from pysakkiparit where stop_id_1 = " + stop_crdnts[i][3] + " and stop_id_2 = " + stop_crdnts[i+1][3]
            #print(valinta_kasky)
            cursor.execute(valinta_kasky)
            
            #print(i,file=sys.stderr)
            #print(len(stop_crdnts),file=sys.stderr)
            #print(stop_crdnts[i][3])
            #print(stop_crdnts[i+1][3])
            i+=1

            #heitetaan koordinaatit reitin listalle
            f = cursor.fetchone()
            if f is not None:
                durations.append(f[1])
                a = f[0].replace("(", "")
                b = a.replace(")", "")
                c = b.split(',')            
            else: return(render_template('virhe.html',selitys='Ei löydetä pysäkkien välistä reittiä.'),4002) 
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
        #for i in range(0,len(stop_crdnts) - ii):
        i = 0
        while i < len(stop_crdnts) - ii:
            r2["pysakinValit"].append({
            "lahtoNimi":stop_crdnts[i][2],
            "lahtoPiste":[stop_crdnts[i][1],stop_crdnts[i][0]],
            "lahtoID":stop_crdnts[i][3],
            "paateNimi":stop_crdnts[i+1][2],
            "paatePiste":[stop_crdnts[i+1][1],stop_crdnts[i+1][0]],
            "paateID":stop_crdnts[i+1][3],
            "duration": durations[i],
            "coordinates":route_crdnts[i]})
            i+=1
    
        resp = Response(response=json.dumps(r2, ensure_ascii=False).encode('utf-8'),
        status=200,
        content_type="application/json; charset=utf-8")   
        
        return(resp)
    
    else:
        return(render_template('virhe.html'),4004) 


if __name__ == '__main__':
    app.run(debug=True)
