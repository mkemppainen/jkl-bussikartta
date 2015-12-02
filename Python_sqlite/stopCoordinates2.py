# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 10:55:27 2015

@author: Joakim

The only thing that needs to be called from this library is
updateCoordinatePairs, 
it does the rest
"""
import requests
import sqlite3 as lite
import json
import time

dbname = 'tietokanta_testi.data'
tablename = 'Pysakkiparit'


def initializePairTable():
    """Initializes the paired stops table by 
    trying to remove it and trying to recreate it"""
    success=[1,1]
    #Remove the table
    try:
        con = lite.connect(dbname)
        with con:
            cur=con.cursor()
            cur.execute('DROP TABLE '+tablename)
    except:
        #Table does not exist, it cannot be removed
        success[0]=0
    #Create the table
    try:
        con = lite.connect(dbname)
        with con:
            cur=con.cursor()
        cur.execute("CREATE TABLE "+tablename+"("+\
            "stop_id_1 VARCHAR(10) NOT NULL, "+\
            "stop_id_2 VARCHAR(10) NOT NULL, "+\
            "tripcrd TEXT NOT NULL, "+\
            "duration TEXT NOT NULL)")
    except:
        #Table creation failed
        success[1] = 0
    return success
    
def getMidCoordinates(crd1, crd2):
    """Asks mapbox the coordinates for a route 
    between two coordinates. 
    Coordinates should be of the form (longitude, latitude)"""
    crdstr = ""
    duration = ""
    #Mapbox asking webaddress
    addp1 = "https://api.mapbox.com/v4/directions/mapbox.driving/"
    addp2 = "{lon1},{lat1};{lon2},{lat2}".format(
            lon1=crd1[0],lat1=crd1[1],
            lon2=crd2[0],lat2=crd2[1])
    addp3 = ".json?access_token="
    addp4 = "pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251"
    addp5 = "dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false"
    address = addp1+addp2+addp3+addp4+addp5
    #Do the actual data retrieval
    r = requests.get(address)
    #r is a group of dictionaries in a json, parse it
    dicts = json.loads(r.text)
    #Get the duration of the trip, seconds
    duration = str(((dicts['routes'])[0])['duration'])
    #Get the coordinates of the route
    crdstrRaw = ((dicts['routes'])[0])['geometry']['coordinates']
    for crd in crdstrRaw:
        crdstr+="({lon},{lat}),".format(lon=crd[0],lat=crd[1])
    #return the results
    return "("+str(crdstr[:-1])+")", duration

def updateCoordinatePairs():
    """Reads unique stop-stop pairs from the database and lists them. 
    Then adds the coordinates for the map display for each stop to stop 
    route."""
    #print("Start")
    #Create a table into the database, first, try to remove the old one
    #print("Initialization")
    #print(initializePairTable())
    #initializePairTable()
    #Open a connection to the database
    con = lite.connect(dbname)
    #Initialize paired stop list
    stopPairList = []
    with con:
        #Start by creating a list of unique stop pairs in routes
        cur = con.cursor()
        
        cur.execute("SELECT distinct trip_id, stop_id, jnum FROM Pysahtymis_ajat order by trip_id,jnum")

        
        pari_lista = []

        tulos = cur.fetchall()
        nykyinen_trip_id = tulos[0][0]
        edellinen_stop_id = tulos[0][1]
        for i in range(1,len(tulos)):
            rivi = tulos[i]
            nykyinen_stop_id = tulos[i][1]
            if rivi[0] != nykyinen_trip_id:
                nykyinen_trip_id = rivi[0]
            else: pari_lista.append((edellinen_stop_id, nykyinen_stop_id))
            edellinen_stop_id = nykyinen_stop_id 

        lista = set(pari_lista)

        print(len(lista))

        lisattava_lista = []

        for item in lista:
            cur.execute("SELECT * FROM Pysakkiparit WHERE stop_id_1 like \"" + item[0] + "\" AND stop_id_2 like \"" + item[1] + "\"")
            if len(cur.fetchall()) <= 0: lisattava_lista.append(item) 

        if len(lisattava_lista=0): return 1
        print(len(lisattava_lista))

        count = 0;

        #Put values into the stop-stop route table        
        for pair in lisattava_lista:
            vasen = pair[0]
            oikea = pair[1]
            cur.execute("Select lat, lon From Pysakit where stop_id like \"" + vasen + "\"")

            parsittava = cur.fetchone()
            vasen_lat = parsittava[0]
            vasen_lon = parsittava[1]

            cur.execute("Select lat, lon From Pysakit where stop_id like \"" + oikea + "\"")

            parsittava = cur.fetchone()
            oikea_lat = parsittava[0]
            oikea_lon = parsittava[1]

            #Progress monitoring            
            if(count%100==0):
                print(count)
            
            #Get the stop to stop coordinates 
            #and route duration
            crdString, duration = getMidCoordinates((vasen_lon,vasen_lat),(oikea_lon,oikea_lat))
            #Insert data into table
            cur.execute("INSERT INTO {tn} VALUES(\"{id1:s}\",\"{id2:s}\",\"{crd:s}\",\"{dur:s}\")".format(tn=tablename,
            id1=vasen,
            id2=oikea,
            crd=str(crdString),
            dur=str(duration)))
            #Slow down the progress a bit
            time.sleep(0.1)
            #Progress monitoring
            count+=1
    return 1

#Tests: ===============================================================    
#def trial():
#    #print("Creation: "+str(tableCreation(dbname)))
#    print(initializePairTable())

#crdplist = list(getCoordinatePairs())
#print(len(crdplist))
#trial()

#Main test
#print("Success: "+str(updateCoordinatePairs())
