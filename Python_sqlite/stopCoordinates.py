# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 10:55:27 2015

@author: Joakim
"""

import sqlite3 as lite

dbname = 'tietokanta_testi.data'
tablename = 'Pysakkiparit'

def tableRemoval(databasename):
    #try:
    con = lite.connect(databasename)
    with con:
        cur=con.cursor()
        cur.execute('DROP TABLE '+tablename)
    return 1
        #cur.commit()
    #    return 1
    #except:
    #    return 0
        
def tableCreation(databasename):
    #try:
    con = lite.connect(databasename)
    with con:
        cur=con.cursor()
        cur.execute("CREATE TABLE "+tablename+"("+\
            "stop_id_1 VARCHAR(10) PRIMARY KEY, "+\
            "stop_id_2 VARCHAR(10) PRIMARY KEY, "+\
            "tripcrd TEXT NOT NULL)")
    return 1
        #cur.commit()
    #    return 1
    #except:
    #    return 0

def initializePairTable():
    success=(1,1)
    #Remove the table
    try:
        con = lite.connect(dbname)
        with con:
            cur=con.cursor()
            cur.execute('DROP TABLE '+tablename)
    except:
        #Table does not exist, it cannot be removed
        success[0] = 0
    #Create the table
    try:
        con = lite.connect(dbname)
        with con:
            cur=con.cursor()
            cur.execute("CREATE TABLE "+tablename+"("+\
                "stop_id_1 INT, stop_id_2 INT, "+\
                "crd_1 TEXT, crd_2 TEXT, tripcrd TEXT)")
    except:
        #Table creation failed
        success[1]=1
    return success
    

def getCoordinatePairs():
    con = lite.connect(dbname)
    #coordPairs = []
    #lista=[]
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
        
        #Create a table into the database, first, try to remove the old one
        initializePairTable()
        
        
        
    return list(stopPairList)
    
def trial():
    #print("Creation: "+str(tableCreation(dbname)))
    print(initializePairTable())

#crdplist = list(getCoordinatePairs())
#print(len(crdplist))

trial()