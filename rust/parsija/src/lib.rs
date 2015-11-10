extern crate libc;
extern crate regex;
extern crate rusqlite;

use libc::c_char;
use regex::Regex; 
use std::path::Path;
use std::mem;
use std::ffi::CString;
use std::io::BufReader;
use std::fs::File;
use std::io::prelude::*;
use rusqlite::SqliteConnection;



/// Sisältää pysäkin tiedot
#[repr(C)]
pub struct Pysakki {
    id: *mut c_char,
    nimi: *mut c_char, 
    lat: *mut c_char,
    lon: *mut c_char,
}


struct PysakkiData {
    stop_id: String,
    nimi: String,
    lat: String,
    lon: String,
}

struct MatkatData {
    route_id: String,
    service_id: String,
    trip_id: String,
}

struct PysahtymisAjatData {
    trip_id: String,
    saapumis_aika: String,
    lahto_aika: String,
    stop_id: String,
    jnum: i32,
}

struct MatkaNimetData {
    route_id: String,
    lnimi: String,
    pnimi: String,
}


/// Lukee pysäkit 
fn lue_pysakit(polku: &Path) -> Option<Vec<PysakkiData>> {
    let f = match File::open(polku) {
        Ok(f) => f,
        Err(_) => return None,
    };

    let lukija: BufReader<_> = BufReader::new(f);
    let lista = lukija.lines().filter_map(|x| anna_pysakit(&x.unwrap())).collect();
    Some(lista) 
}


/// Lukee matkat 
fn lue_matkat(polku: &Path) -> Option<Vec<MatkatData>> {
    let f = match File::open(polku) {
        Ok(f) => f,
        Err(_) => return None,
    };

    let lukija: BufReader<_> = BufReader::new(f);
    let lista = lukija.lines().filter_map(|x| anna_matkat(&x.unwrap())).collect();
    Some(lista) 
}


/// Lukee pysähtymisajat
fn lue_pysahtymisajat(polku: &Path) -> Option<Vec<PysahtymisAjatData>> {
    let f = match File::open(polku) {
        Ok(f) => f,
        Err(_) => return None,
    };

    let lukija: BufReader<_> = BufReader::new(f);
    let lista = lukija.lines().filter_map(|x| anna_pysahtymisaika(&x.unwrap())).collect();
    Some(lista) 
}


/// Lukee matkojen nimet 
fn lue_nimet(polku: &Path) -> Option<Vec<MatkaNimetData>> {
    let f = match File::open(polku) {
        Ok(f) => f,
        Err(_) => return None,
    };

    let lukija: BufReader<_> = BufReader::new(f);
    let lista = lukija.lines().filter_map(|x| anna_matkanimet(&x.unwrap())).collect();
    Some(lista) 
}


/// Parsii pysähtymisaika tiedoston tyylisen rivin ja palauttaa sen, jos pystyttiin parsimaan.
fn anna_pysahtymisaika(teksti: &str) -> Option<PysahtymisAjatData> {
    let re = Regex::new(r##""((\w+-){4}\w+)","(\d\d:\d\d:\d\d)","(\d\d:\d\d:\d\d)","(\d+)","(\d+)""##).unwrap();
    let napatut = match re.captures(teksti) {
        Some(a) => a,
        None => return None,
    };

    let jnum:i32 = match napatut.at(6).unwrap().parse::<i32>() {
        Ok(a) => a,
        Err(_) => return None,
    };
    
    Some(PysahtymisAjatData{trip_id: napatut.at(1).unwrap().to_string(), saapumis_aika: napatut.at(3).unwrap().to_string(), lahto_aika: napatut.at(4).unwrap().to_string(), stop_id: napatut.at(5).unwrap().to_string(), jnum: jnum})
}


/// Parsii pysakki tiedoston tyylisen rivin ja palauttaa sen, jos pystyttiin parsimaan.
fn anna_pysakit(teksti: &str) -> Option<PysakkiData> {
    let re = Regex::new(r##""(\d+)","?([^,"]*)"?,"([^,"]*)","(\d*.\d+)","(\d*.\d+)","(\d*)","([^,"]*)","(\d*)""##).unwrap();
    let napatut = match re.captures(teksti) {
        Some(a) => a,
        None => return None,
    };
    
    Some(PysakkiData{stop_id: napatut.at(1).unwrap().to_string() ,nimi: napatut.at(3).unwrap().to_string(), lat: napatut.at(4).unwrap().to_string(), lon: napatut.at(5).unwrap().to_string()}) 
}


/// Parsii matkat tiedoston tyylisen rivin ja palauttaa sen, jos pystyttiin parsimaan.
fn anna_matkat(teksti: &str) -> Option<MatkatData> {
    let re = Regex::new(r##""(\d*)","([^,"])+","(((\w+-){4}\w+))","(\d+)",("([^,"]*)")?"##).unwrap();
    let napatut = match re.captures(teksti) {
        Some(a) => a,
        None => return None,
    };
    
    Some(MatkatData{route_id: napatut.at(1).unwrap().to_string(),service_id: napatut.at(2).unwrap().to_string(),trip_id: napatut.at(3).unwrap().to_string()}) 
}


/// Parsii nimi tiedoston tyylisen rivin ja palauttaa sen, jos pystyttiin parsimaan.
fn anna_matkanimet(teksti: &str) -> Option<MatkaNimetData> {
    let re = Regex::new(r##""(\d+)","(\d+)","([^,"]+)","([^,"]+)","([^,"]+)""##).unwrap();
    let napatut = match re.captures(teksti) {
        Some(a) => a,
        None => return None,
    };
    
    Some(MatkaNimetData{route_id: napatut.at(1).unwrap().to_string(), lnimi: napatut.at(3).unwrap().to_string(), pnimi: napatut.at(1).unwrap().to_string()}) 
}


/// Lukee tarvittavat tiedostot ja luo tietokannan
#[no_mangle]
pub extern fn luo_tietokanta() -> i32 {
    let pysahtymis_ajat = match lue_pysahtymisajat(Path::new(r"./linkkidata/stop_times.txt")) {
        Some(a) => { println!("{}",a.len()); a},
        None => return 11,
    };
    let matkat = match lue_matkat(Path::new(r"./linkkidata/trips.txt")) {
        Some(a) => { println!("{}",a.len()); a},
        None => return 12,
    };
    let pysakit = match lue_pysakit(Path::new(r"./linkkidata/stops.txt")) {
        Some(a) => { println!("{}",a.len()); a},
        None => return 13,
    };
    let nimet = match lue_nimet(Path::new(r"./linkkidata/routes.txt")) {
        Some(a) => { println!("{}",a.len()); a},
        None => return 14,
    };

    kirjoita_tietokantaan(Path::new(r"./tietokanta_testi.data"),matkat,nimet,pysakit,pysahtymis_ajat)
}


///Kirjoittaa tiedot sqlite tietokantaan ja palauttaa virhekoodin. 0 jos ei virhettä.
fn kirjoita_tietokantaan(polku: &Path, matkat: Vec<MatkatData>, nimet: Vec<MatkaNimetData>, pysakit: Vec<PysakkiData>, pysahtymis_ajat: Vec<PysahtymisAjatData>) -> i32{
    let yhteys = match SqliteConnection::open(polku) {
        Ok(a) => a,
        Err(_) => {println!("Tietokantaa ei voida avata, eikä sinne kirjoittaminen ole siksi mahdollista (vika voi olla toki jossain muussakin kuin avaamisessa. Tarkalleen ottaen ei voida muodostaa yhteyttä.)"); return 21;},
    };

    let tx = match yhteys.transaction() {
        Ok(t) => t,
        Err(_) => {println!("Transaktiota ei voitu muodostaa."); return 22;},
    };

    match yhteys.execute("CREATE TABLE Pysakit (
                    stop_id     varchar(10) PRIMARY KEY,
                    nimi        varchar(50) NOT NULL,
                    lat         varchar(20) NOT NULL,
                    lon         varchar(20) NOT NULL
                    )", &[]) {
                    Ok(_) => (),
                    Err(_) => {println!("Virhe Pysakit-taulun luonnissa."); return 23;},
    }

    match yhteys.execute("CREATE TABLE Matkat (
                    trip_id     varchar(50) NOT NULL,
                    route_id    varchar(10) NOT NULL,
                    service_id  varchar(30) NOT NULL
                    )", &[]) {
                    Ok(_) => (),
                    Err(_) => {println!("Virhe Matkat-taulun luonnissa."); return 24;},
    }

    match yhteys.execute("CREATE TABLE Pysahtymis_ajat (
                    trip_id     varchar(50) NOT NULL,
                    stop_id     varchar(10) NOT NULL,
                    saapumis_aika varchar(10) NOT NULL,
                    lahto_aika  varchar(10) NOT NULL,
                    jnum        integer NOT NULL
                    )", &[]) {
                    Ok(_) => (),
                    Err(_) => {println!("Virhe Pysahtymis_ajat-taulun luonnissa."); return 25;},
    }

    match yhteys.execute("CREATE TABLE Matkojen_nimet (
                    route_id    varchar(10) NOT NULL,
                    lnimi       varchar(10) NOT NULL,
                    pnimi       varchar(50) NOT NULL
                    )", &[]) {
                    Ok(_) => (),
                    Err(_) => {println!("Virhe Matkojen_nimet-taulun luonnissa."); return 26;},
    }

    for rivi in pysakit {
        match yhteys.execute("INSERT INTO Pysakit (stop_id, nimi, lat, lon)
                        VALUES ($1, $2, $3, $4)",
                        &[&rivi.stop_id, &rivi.nimi, &rivi.lat, &rivi.lon]) {
                            Ok(_) => (),
                            Err(_) => println!("Pysakit-tauluun kirjoittaminen epäonnistui."),
                        }
    }

    println!("Pysakit-taulu suoritettu.");

    for rivi in nimet {
        match yhteys.execute("INSERT INTO Matkojen_nimet (route_id, lnimi, pnimi)
                        VALUES ($1, $2, $3)",
                        &[&rivi.route_id, &rivi.lnimi, &rivi.pnimi]) {
                            Ok(_) => (),
                            Err(_) => println!("Matkojen_nimet-tauluun kirjoittaminen epäonnistui."),
                        }
    }
    println!("Matkojen_nimet-taulu suoritettu.");
    for rivi in pysahtymis_ajat {
        match yhteys.execute("INSERT INTO Pysahtymis_ajat(trip_id, stop_id, saapumis_aika, lahto_aika, jnum)
                        VALUES ($1, $2, $3, $4, $5)",
                        &[&rivi.trip_id, &rivi.stop_id, &rivi.saapumis_aika, &rivi.lahto_aika, &rivi.jnum]) {
                            Ok(_) => (),
                            Err(_) => println!("Matkojen_nimet-tauluun kirjoittaminen epäonnistui."),
                        }
    }
    println!("Pysahtymis_ajat-taulu suoritettu");
    for rivi in matkat{
        match yhteys.execute("INSERT INTO Matkat(trip_id, route_id, service_id)
                        VALUES ($1, $2, $3)",
                        &[&rivi.trip_id, &rivi.route_id, &rivi.service_id]) {
                            Ok(_) => (),
                            Err(_) => println!("Matkojen_nimet-tauluun kirjoittaminen epäonnistui."),
                        }
    }
    println!("Matkat-taulu suoritettu");

    match tx.commit() {
        Ok(_) => 0,
        Err(_) => 30,
    }
}


/// Vapauttaa pysäkin muistin.
#[no_mangle]
pub extern fn pysakki_free(pysakki: Pysakki) {
   println!("Tultiin pysakin poistamiseen");
   cstring_free(pysakki.id);
   cstring_free(pysakki.nimi);
   cstring_free(pysakki.lon);
   cstring_free(pysakki.lat);
   println!("Lähdetään pysäkin poistamisesta.");
}


/// Vapauttaa cstringin käyttämän muistin.
#[no_mangle]
pub extern fn cstring_free(p: *mut c_char) {
    unsafe { CString::from_raw(p) };
    println!("Tuhotaan jotain.");
}


/// Antaa esimerkki tekstin cstring muodossa osoittimena.
#[no_mangle]
pub extern fn anna_esimerkki_teksti() -> *const c_char {
    CString::new("112514").unwrap().into_raw()
}

/// Antaa esimerkki pysäkin.
#[no_mangle]
pub extern fn anna_esimerkki_pysakki() -> Pysakki {
    let a = CString::new("112514").unwrap();
    let b = CString::new("Laukaa linja-autoasema").unwrap();
    let c = CString::new("62.4146943734173").unwrap();
    let d = CString::new("25.9521651226176").unwrap();
    let a_p = a.as_ptr();
    let b_p = b.as_ptr();
    let c_p = c.as_ptr();
    let d_p = d.as_ptr();

    mem::forget(a);
    mem::forget(b);
    mem::forget(c);
    mem::forget(d);

    let pysakki = Pysakki{id: a_p as *mut _, nimi: b_p as *mut _ , lat: c_p as *mut _ , lon: d_p as *mut _};
    pysakki
}
