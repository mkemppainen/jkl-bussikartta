# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:16:32 2015

@author: Joakim
"""

import sqlite3 as lite
import sys

con = lite.connect('tietokanta_testi.data')

with con:
    cur = con.cursor()    
    testi = cur.execute("SELECT * FROM Pysakit")
    
print(list(testi)) 
    
print("\nEnd of Line")