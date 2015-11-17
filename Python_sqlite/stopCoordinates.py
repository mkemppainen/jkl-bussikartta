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
    initializePairTable()
    #Open a connection to the database
    con = lite.connect(dbname)
    #Initialize paired stop list
    stopPairList = []
    with con:
        #Start by creating a list of unique stop pairs in routes
        cur = con.cursor()
        
        routeIDr = cur.execute("SELECT route_id FROM Matkojen_nimet")        
        routeID = []
        for route in routeIDr:
            routeID.append(route[0])
        routeStopList=[]    
        for route in routeID:
            tmp = list(cur.execute("SELECT pa.stop_id, p.lat, p.lon "+\
            "FROM Pysakit p, Pysahtymis_ajat pa "+\
            "WHERE "+\
            "(trip_id==(SELECT trip_id FROM Matkat WHERE "+\
            "route_id=="+route+")) AND p.stop_id==pa.stop_id"))
            routeStopList.append(tmp)
        #Create stop-stop pairs
        inroutePairs=[]
        for route in routeStopList:
            #routePairs = []
            routeStopNum = len(route)
            for i in range(routeStopNum-1):
                inroutePairs.append((int(route[i][0]),int(route[i+1][0]),
                                       (route[i],route[i+1])))
        #Remove duplicates from stop-pairs
        setOfPairs = list(set(inroutePairs))
        #Remove extra from stop-pairs
        stopPairList = list(map((lambda x: x[2]),setOfPairs))
        #Sort the list, unnecessary
        #sorted(stopPairList,key=(lambda x: x[0][0]))
        
        #Progress monitoring
        #count = 0
        #print(count)

        #Put values into the stop-stop route table        
        for pair in stopPairList:
            #Progress monitoring            
            #if(count%100==0):
            #    print(count)
            
            #Get the stop to stop coordinates 
            #and route duration
            crdString, duration = getMidCoordinates((pair[0][2],pair[0][1]),
                                       (pair[1][2],pair[1][1]))
            #Insert data into table
            cur.execute("INSERT INTO {tn} VALUES(\"{id1:s}\",\"{id2:s}\",\"{crd:s}\",\"{dur:s}\")".format(tn=tablename,
            id1=str(pair[0][0]),
            id2=str(pair[1][0]),
            crd=str(crdString),
            dur=str(duration)))
            #Slow down the progress a bit
            time.sleep(0.1)
            #Progress monitoring
            #count+=1
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