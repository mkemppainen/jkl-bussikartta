# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:43:02 2015

@author: Joakim
"""

import sqlite3 as lite
import sys

con = lite.connect('test2.db')

with con:
    cur = con.cursor()    
    cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
    cur.execute("INSERT INTO Cars VALUES(1,'Audi',52642)")
    cur.execute("INSERT INTO Cars VALUES(2,'Mercedes',57127)")
    cur.execute("INSERT INTO Cars VALUES(3,'Skoda',9000)")
    cur.execute("INSERT INTO Cars VALUES(4,'Volvo',29000)")
    cur.execute("INSERT INTO Cars VALUES(5,'Bentley',350000)")
    cur.execute("INSERT INTO Cars VALUES(6,'Citroen',21000)")
    cur.execute("INSERT INTO Cars VALUES(7,'Hummer',41400)")
    cur.execute("INSERT INTO Cars VALUES(8,'Volkswagen',21600)")
    cur.execute("INSERT INTO Cars VALUES(8,'((1.1,2.1),(1.1,3.3),(4.4,5.5))',21600)")
 
con.close   
print('\nEnd of Line')