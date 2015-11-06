from __future__ import print_function
from flask import Flask, Response
from flask import render_template
from flask import request
from flask import url_for, redirect, jsonify, make_response
import requests
import json
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#Pitaa muokata hakemaan dataa dynaamisesti, nyt palautuu staattinen
#JSON-data
@app.route("/get_route")
def get_route():
    if request.method == 'GET':
        print(request.args.get('time'), file=sys.stderr) # testi

        #Tassa haetaan selaimelta pyydetyn reitin tiedot, toistaiseksi staattinen
        
        #kannasta haetut pysakkien koordinaatit taulukossa
        stop_crdnts = [['62.25287', '25.70022'],['62.24816', '25.270514']]
        stop_crdnts2 = []
        #haetaan jokaiselle koordinaattiparille reitti, tallennetaan
        for i in stop_crdnts:
            strng = i[1] + ',' + i[0]
            #haetaan pysakkien valin koordinaatit
            r  = requests.get('https://api.mapbox.com/v4/directions/mapbox.driving/'+ strng + ';25.70514,62.24816;25.736,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')     
            #heitetaan koordinaatit reitin listalle
            jisondata = json.loads(r.text)
            stop_crdnts2.append(jisondata["routes"][0]["geometry"]["coordinates"])
            #mapbox-pyynto mallina 
            """
            rr = requests.get('https://api.mapbox.com/v4/directions/mapbox.driving/25.70022,62.25287;25.70514,62.24816;25.736,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')
            """

        #MIKSI TAMA EI TALLENNU OIKEASSA MUODOSSA? Vai onko silla valia?
        r2 = [{
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
                        ]}]

    resp = Response(response=json.dumps(r2),
        status=200,
        mimetype="application/json")   
        
    return(resp)
    

if __name__ == '__main__':
   app.run(debug=True)
