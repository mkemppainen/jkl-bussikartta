# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:16:32 2015

@author: Joakim
"""

import sqlite3 as lite
import sys

con = lite.connect('tietokanta_testi.data')
#http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html#querying
#tutorial

with con:
    cur = con.cursor()    
    #testi = cur.execute("SELECT * FROM Pysakit")
    testi = cur.execute("SELECT COUNT(stop_id) FROM Pysakit")
    #testi = cur.execute("SELECT * FROM Pysahtymis_ajat")
    #testi = cur.execute("SELECT stop_id FROM Pysakit")
    #testi = cur.execute("SELECT mn.lnimi,  FROM Pysakit p, Matkat m,"+\
    #" Pysahtymis_ajat pa, Matkojen_nimet mn, Kalenteri k"+\
    #" WHERE mn.route_id=m.route_id AND m.stop_id LIKE 112514")
    #testi = cur.execute("SELECT mn.lnimi FROM "+\
    #"Pysakit p, Matkat m, Pysahtymis_ajat pa, Matkojen_nimet mn, kalenteri k "+\
    #"WHERE "+\
    #"mn.route_id==m.route_id AND "+\
    #"m.trip_id==pa.trip_id AND "+\
    #"pa.stop_id==p.stop_id AND "+\
    #"p.nimi LIKE \"Laukaa linja-autoasema\"") #EI TOIMI
    #testi=cur.execute("SELECT lnimi FROM Matkojen_nimet WHERE "+\
    #"route_id==(SELECT route_id FROM Matkat WHERE "+\
    #"route_id LIKE 9011)")
    #cur.close()
    
print(list(testi)) 
    
print("\nEnd of Line")