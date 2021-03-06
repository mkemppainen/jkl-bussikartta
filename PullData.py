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

"""Package source website"""
SourcePageAddress = 'http://data.jyvaskyla.fi/data.php'

"""Package dating information address on the webpage in XPath-coding:
NOTE: this is an absolute address, it has to be changed into a dynamic one later"""
PackageDateAddress_XPath = '/html/body/div/div[3]/div[2]/div[1]/div[1]/div[14]/div[5]/br'
#PackageDateAddress_XPath = '/html/body/div/div[3]/div[2]/div[1]/div[1]/div[14]/div[5]/br/text()'

"""Package http-donwload address"""
PackageAddress = 'http://data.jyvaskyla.fi/tiedostot/linkkidata.zip'

"""Example current package dating, this has to be read from a file later on"""
lastUpdatedDate = "3.9.2015"

#--------------------------------------------------------------------------- 
def reader(fileaddress):
    """Reads the contents of a given file into an array"""
    tied = []
    with open(fileaddress, 'r') as ft:
        for line in ft:
            if(line[0]!="#"):
                tied.append(line)
    ft.close()
    return tied

def getCurrentPackageDate(fileaddress):
    """Reads a given file and extracts the current dating of the linkkidata-package"""
    #setFile = reader(fileaddress) #Commented out for now
    #TODO: handle the setting file reading
    currentPackageDate = "3.9.2015"
    return currentPackageDate

def checkIfUpdateAvailable(setFileAddress):
    """Checks the Jyväskylä open data website for wheter 
    there is an update for the linkkidata-package 
    Returns true if there is, false if there is not"""
    try:
        lastUpdatedDate = getCurrentPackageDate(setFileAddress)
        page = requests.get(SourcePageAddress)
        tree = html.fromstring(page.text)
        
        #Read the date from the webpage and clean it up
        dating = tree.xpath(PackageDateAddress_XPath)
        brcstr = etree.tostring(dating[0])
        rcstr = brcstr.decode("utf-8")
        cstr=rcstr.replace("\n","").replace("\t","").replace("<br/>","")
        print(cstr)    
        
        #Form datetime objects for package update status comparison
        dLastUpdatedDate = datetime.datetime.strptime(lastUpdatedDate,'%d.%m.%Y').date()
        dPackageDate = datetime.datetime.strptime(cstr,'%d.%m.%Y').date()
        
        #Check if the package requires updating
        if(time.mktime(dPackageDate.timetuple()) > time.mktime(dLastUpdatedDate.timetuple())):
           return True
        else:
            return False
    except:
        return -1
    
def downloadUpdatedPackage(PackageAddress = 'http://data.jyvaskyla.fi/tiedostot/linkkidata.zip'):
    """Downloads a zip package from the given address. 
    Default is the linkkidata-package address. """
    f = urllib.request.urlopen(PackageAddress)
    data = f.read()
    with open("linkkidata.zip", "wb") as code:
        code.write(data)

checkIfUpdateAvailable("")

#TODO: remove this when the package update file is done
print('Done')