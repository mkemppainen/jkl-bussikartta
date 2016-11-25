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
import os
import shutil
import zipfile

"""Package source website"""
SourcePageAddress = 'http://data.jyvaskyla.fi/data.php'

"""Package dating information address on the webpage in XPath-coding:
NOTE: this is an absolute address, it has to be changed into a dynamic one later"""
PackageDateAddress_XPath = '/html/body/div/div[3]/div[2]/div[1]/div[1]/div[15]/div[5]/br'
#PackageDateAddress_XPath = '/html/body/div/div[3]/div[2]/div[1]/div[1]/div[14]/div[5]/br/text()'

"""Package http-donwload address"""
PackageAddress = 'http://data.jyvaskyla.fi/tiedostot/linkkidata.zip'

linkkidataNames = ['agency.txt','calendar.txt','calendar_dates.txt',
                   'contracts.txt','routes.txt','stop_times.txt',
                   'stops.txt','translations.txt', 'trips.txt']
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
    
def writer(fileaddress, contents, oneline=False):
    #fileaddress = filename
    if(os.path.exists(fileaddress)):
        os.remove(fileaddress)        
    tied = open(fileaddress, 'w')
    if(not oneline):
        for line in contents:
            tied.write(line+"\n")
    else:
        tied.write(contents+"\n")
    tied.close()

def getCurrentPackageDate(fileaddress):
    """Reads a given file and extracts the current dating 
    of the linkkidata-package"""
    rawUpdateDateData = reader(fileaddress)
    currentPackageDate = ((rawUpdateDateData[0]).splitlines())[0]
    return currentPackageDate

def checkIfUpdateAvailable(updateDateFileAddress):
    """Checks the Jyväskylä open data website for wheter 
    there is an update for the linkkidata-package 
    Returns true if there is, false if there is not"""
    try:
        lastUpdatedDate = getCurrentPackageDate(updateDateFileAddress)
        page = requests.get(SourcePageAddress)
        tree = html.fromstring(page.text)
        
        #Read the date from the webpage and clean it up
        dating = tree.xpath(PackageDateAddress_XPath)
        brcstr = etree.tostring(dating[0])
        rcstr = brcstr.decode("utf-8")
        cstr=rcstr.replace("\n","").replace("\t","").replace("<br/>","")
        print(cstr)
        
        #Form datetime objects for package update status comparison
        dLastUpdatedDate = datetime.datetime.\
            strptime(lastUpdatedDate,'%d.%m.%Y').date()
        dPackageDate = datetime.datetime.strptime(cstr,'%d.%m.%Y').date()
        
        #Check if the package requires updating
        if(time.mktime(dPackageDate.timetuple()) > \
            time.mktime(dLastUpdatedDate.timetuple())):
           return True,cstr
        else:
            return False,cstr
    except:
        return -1,"1.1.2000"
    
def downloadUpdatedPackage(PackageAddress = 
    'http://data.jyvaskyla.fi/tiedostot/linkkidata.zip'):
    """Downloads a zip package from the given address. 
    Default is the linkkidata-package address. """
    try:
        f = urllib.request.urlopen(PackageAddress)
        data = f.read()
        with open("linkkidata.zip", "wb") as code:
            code.write(data)
        return 1
    except:
        return -1
        
def unzip(source_filename, dest_dir):
    """Unzips a source file into destination file"""
    #Source: 
    # https://stackoverflow.com/questions/12886768/how-to-unzip-file-in-python-on-all-oses
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)
        
def formFileTreeFromZipPackage():#(ZipPackageAddress = 'oletusosoite'):
    """Locates the current working directory, creates the 
    unzipped data tree or updates the old data tree"""
    cwd = os.getcwd().replace('\\','/')
    dataAddress = cwd+"/linkkidata.zip"
    writeDataAddress = cwd+"/linkkidata"
    #print(writeDataAddress)
    if(os.path.exists(dataAddress)):
        #Extract the zip-package
        try:
            unzip(dataAddress,writeDataAddress)
            return 1
        except:
            return -1
    else:
        #There is no zip-package, return error signal
        return -1

def updateLinkkiData():
    """Handles the update of the linkkidata-package, if necessary. 
    Returns 1 if update successful, 0 if no update was needed and -1 if update failed. """
    cwd = os.getcwd().replace('\\','/')
    updateDateFileAddress = cwd+"/lastUpdateDate.txt"
    if not os.path.exists(updateDateFileAddress):
        #Last update date file not found, create it
        writer(updateDateFileAddress,['1.1.1950'])
    #The last update date is found, 
    requiresUpdate, webPackageDate = checkIfUpdateAvailable(updateDateFileAddress)
    if requiresUpdate:
        #Update the linkkidata-package
        print("Download successful: "+str(downloadUpdatedPackage()))
        print("File tree creation: "+str(formFileTreeFromZipPackage()))
        print("Write current package date "+webPackageDate+" into file")
        if downloadUpdatedPackage() == 1:
            if formFileTreeFromZipPackage() == 1:
                writer(updateDateFileAddress,[webPackageDate])
                return 1 
        return -1
    else:
        #Do not update the linkkidata package
        return 0
    #There has been an error
    return -1

        
res = updateLinkkiData()
print(res)

#TODO: remove this when the package update file is done
print('Done')
