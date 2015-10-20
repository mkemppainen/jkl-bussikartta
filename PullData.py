# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 22:47:23 2015

@author: Joakim

Python version: 3.4.1

Reads a website, determines wheter a package is old or new.
If package is old, downloads a newer one. 
Else, does nothing. 

NOTE:
This is a raw version, it does not work in conjunction with other codes.
Yet.
"""

import urllib.request 
import urllib.parse 
import urllib.error
from lxml import html, etree
import requests
import datetime, time

#Package source website
SourcePageAddress = 'http://data.jyvaskyla.fi/data.php'

#Package dating information address on the webpage in XPath-coding:
#NOTE: this is an absolute address, it has to be changed into a dynamic one later
PackageDateAddress_XPath = '/html/body/div/div[3]/div[2]/div[1]/div[1]/div[14]/div[5]/br'

#Package http-donwload address
PackageAddress = 'http://data.jyvaskyla.fi/tiedostot/linkkidata.zip'

#Example current package dating, this has to be read from a file later on
lastUpdatedDate = "3.9.2015"

#---------------------------------------------------------------------------

#set webpage-object of the source webpage of the package
page = requests.get(SourcePageAddress)
tree = html.fromstring(page.text)

#Read the date from the webpage and clean it up
dating = tree.xpath(PackageDateAddress_XPath)
brcstr = etree.tostring(dating[0])
rcstr = brcstr.decode("utf-8")
cstr=rcstr.replace("\n","").replace("\t","").replace("<br/>","")

#Form datetime objects for package update status comparison
dLastUpdatedDate = datetime.datetime.strptime(lastUpdatedDate,'%d.%m.%Y').date()
dPackageDate = datetime.datetime.strptime(cstr,'%d.%m.%Y').date()

#Check if the package requires updating
if(time.mktime(dPackageDate.timetuple()) > time.mktime(dLastUpdatedDate.timetuple())):
    print('A newer package is in the website, downloading')
    #print("downloading with urllib2")
    f = urllib.request.urlopen(PackageAddress)
    data = f.read()
    with open("linkkidata.zip", "wb") as code:
        code.write(data)
else:
    print('The package is up to date.')
 

#TODO: later on, add at least these: 

def checkIfUpdateAvailable(currentPackageDate):
    #TODO: create this method
    print("The method does nothing!")
    
def downloadUpdatedPackage():
    #TODO: create this method
    print("The method does nothing!")

#TODO: remove this when the package update file is done
print('Done')