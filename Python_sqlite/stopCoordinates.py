# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 10:55:27 2015

@author: Joakim
"""
import requests
import sqlite3 as lite
import json
import time

dbname = 'tietokanta_testi.data'
tablename = 'Pysakkiparit'


def initializePairTable():
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
    crdstr = ""
    duration = ""
    
    address = "https://api.mapbox.com/v4/directions/mapbox.driving/{lon1},{lat1};{lon2},{lat2}.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false".format(
            lon1=crd1[0],lat1=crd1[1],
            lon2=crd2[0],lat2=crd2[1])
    r = requests.get(address)
    dicts = json.loads(r.text)
    crdstrRaw = ((dicts['routes'])[0])['geometry']['coordinates']
    duration = str(((dicts['routes'])[0])['duration'])
    for crd in crdstrRaw:
        crdstr+="({lon},{lat}),".format(lon=crd[0],lat=crd[1])
    #print(duration)
    return "("+str(crdstr[:-1])+")", duration

def updateCoordinatePairs():
    print("Start")
    #Create a table into the database, first, try to remove the old one
    print("Initialization")
    print(initializePairTable())
    
    con = lite.connect(dbname)
    #coordPairs = []
    #lista=[]
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
        #sorted(stopPairList,key=(lambda x: x[0][0]))
        
        
        #con = lite.connect(dbname)
        count = 0
        print(count)

        for pair in stopPairList:
            if(count%100==0):
                print(count)
            #print("Handling pair: "+str(list(pair)))
            #print(pair[0][1]," ",pair[0][2])
            #print(pair[1][1]," ",pair[1][2])
            crdString, duration = getMidCoordinates((pair[0][2],pair[0][1]),
                                       (pair[1][2],pair[1][1]))
            #print(crdString)
            cur.execute("INSERT INTO {tn} VALUES(\"{id1:s}\",\"{id2:s}\",\"{crd:s}\",\"{dur:s}\")".format(tn=tablename,
            id1=str(pair[0][0]),
            id2=str(pair[1][0]),
            crd=str(crdString),
            dur=str(duration)))
            time.sleep(0.1)
            count+=1
    return 1
        
        
    #return list(stopPairList)
    
def trial():
    #print("Creation: "+str(tableCreation(dbname)))
    print(initializePairTable())

#crdplist = list(getCoordinatePairs())
#print(len(crdplist))
#trial()
print("Success: "+str(updateCoordinatePairs())
