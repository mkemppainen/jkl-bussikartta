# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:54:19 2015

@author: Joakim
"""

import requests
import json

lat1 = '62.2645441882972'
lon1 = '26.2081937104288'
lat2 = '62.2613280440931'
lon2 = '26.1977470945014'
"""
address = "https://api.mapbox.com/v4/directions/mapbox.driving/{lon1},{lat1};{lon2},{lat2}.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false".format(
            lon1=lon1,lat1=lat1,
            lon2=lon2,lat2=lat2)
print(address+"\n\n")
r = requests.get(address)
#print(r.status_code)
#print(list(r.json()))
#print(r.text)
teksti = r.text
ls = json.loads(teksti)
#print(str(len(ls))+"\n")
#print(ls['destination'])
#print("\n")
#print(ls['routes'])
#print("\n")
#print(ls['origin'])
#print("\n")
#print(ls['waypoints'])
eka = (ls['routes'])[0]
toka = eka['geometry']
kolmas = toka['coordinates']
#print(kolmas)
print(list(((ls['routes'])[0])['geometry']['coordinates']))
"""

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
        crdstr+="{lon},{lat}:".format(lon=crd[0],lat=crd[1])
    print(duration)
    return crdstr[:-1], duration
    
a, b = getMidCoordinates((lon1,lat1),(lon2,lat2))
print(b)
print("\n")
print(a)
