from __future__ import print_function
from flask import Flask, Response
from flask import render_template
from flask import request
from flask import url_for, redirect, jsonify, make_response
import requests
import json
import sys
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#Pitaa muokata hakemaan dataa dynaamisesti, nyt palautuu staattinen
#JSON-data
@app.route("/get_route")
def get_route():
    if request.method == 'GET':
        print(request.args.get('route'), file=sys.stderr)
        #Haetaan kannasta halutulle linjalle kuuluvat pysakit
        connection = sqlite3.connect("tietokanta_testi.data")
        connection.text_factory = str
        cursor = connection.cursor()
        #TODO jarjestaminen reitin pysakkien jnumin mukaan?
        cursor.execute("select distinct  pysakit.lat, pysakit.lon from pysakit, pysahtymis_ajat where pysakit.stop_id = pysahtymis_ajat.stop_id and pysahtymis_ajat.trip_id in (select trip_id from matkat where route_id in (select min(route_id) from matkojen_nimet where lnimi like \"" + str(request.args.get('route')) + "\"))group by pysahtymis_ajat.jnum")

        #kannasta haetut pysakkien koordinaatit taulukossa
        stop_crdnts = [[item for item in r] for r in cursor.fetchall()]
        route_crdnts = [] #reitin kaikki koordinaatit

        #haetaan jokaiselle koordinaattiparille reitti, tallennetaan
        
        for i in range(0,len(stop_crdnts)):
            strng = stop_crdnts[i][1] + ',' + stop_crdnts[i][0]
            if i+1 < len(stop_crdnts):
                strng2 = stop_crdnts[i+1][1] + ',' + stop_crdnts[i+1][0]
            i+=1
            #haetaan pysakkien valin koordinaatit
            r  = requests.get('https://api.mapbox.com/v4/directions/mapbox.driving/'+ strng + ';' + strng2 + '.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')     
            #heitetaan koordinaatit reitin listalle
            jisondata = json.loads(r.text)
            route_crdnts.append(jisondata["routes"][0]["geometry"]["coordinates"])
            """
            #mapbox-pyynto mallina 
            """
            rr = requests.get('https://api.mapbox.com/v4/directions/mapbox.driving/25.70022,62.25287;25.70514,62.24816;25.736,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')
        
        #Tassa muodossa palautus selaimelle
        #TODO kannasta saadut tiedot staattisien tilalle
        #[{reitinnimi, pysakinvalit[{lahtonimi, lahtoaika, lahtopiste, paatenimi, paatepiste, paateaika, duration, coords[[data,data]]}]}]
        # Tallainen jokaiselle pysakinvalille {lahtonimi, lahtoaika, lahtopiste, paatenimi, paatepiste, paateaika, duration, coords[[data,data]]}
        j = 0   
        r2 = {
            "reitinNimi":"kuokkala",
            "pysakinValit":[{
            "lahtoNimi":"pysakki3",
            "lahtoAika":"12:15",
            "lahtoPiste":[62.25287, 25.70022],
            "paateNimi":"pysakki17",
            "paatePiste":[62.24816, 25.270514],
            "paateAika": "12:20",
            "duration": 300,
            "coordinates":[[25.700226,62.252873],[25.700302,62.25277], 
			  [25.700522,62.252304],[25.700153,62.251181],
                           [25.700726,62.252204],[25.70153,62.252123]]}
                        ]}
        for i in range(0,len(stop_crdnts) - 1):
            r2["pysakinValit"].append({
            "lahtoNimi":"pysakki3",
            "lahtoAika":"12:15",
            "lahtoPiste":[stop_crdnts[i][0],stop_crdnts[i][1]],
            "paateNimi":"pysakki17",
            "paatePiste":[stop_crdnts[i+1][0],stop_crdnts[i+1][1]],
            "paateAika": "12:20",
            "duration": 300,
            "coordinates":route_crdnts[j]})#[j]["coordinates"] = route_crdnts[j]
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
