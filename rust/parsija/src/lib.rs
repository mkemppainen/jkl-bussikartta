#![feature(cstr_memory2)]
extern crate libc;
extern crate regex;

use libc::c_char;
use regex::Regex; 
use std::path::Path;
use std::mem;
use std::ffi::CString;
use std::io::BufReader;
use std::fs::File;
use std::io::prelude::*;

/// Sisältää pysäkin tiedot
#[repr(C)]
pub struct Pysakki {
    id: *const c_char,
    nimi: *const c_char, 
    lat: *const c_char,
    lon: *const c_char,
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
    nimi: String,
}

struct PysahtymisAjatData {
    trip_id: String,
    saapumis_aika: String,
    lahto_aika: String,
    stop_id: String,
    jnum: String,
}

fn lue_pysahtymisajat() -> Option<Vec<PysahtymisAjatData>> {
    let mut f = match File::open("./linkkidata/stop_times.txt") {
        Ok(f) => f,
        Err(e) => return None,
    };

    let lukija: BufReader<_> = BufReader::new(f);

    let mut lista = lukija.lines().filter_map(|x| anna_pysahtymisaika(&x.unwrap())).collect();
    Some(lista) 
}

fn anna_pysahtymisaika(teksti: &str) -> Option<PysahtymisAjatData> {
    println!("{}",teksti);
    let re = Regex::new(r##""((\w+-){4}\w+)","(\d\d:\d\d:\d\d)","(\d\d:\d\d:\d\d)","(\d+)","(\d+)""##).unwrap();
    let napatut = match re.captures(teksti) {
        Some(a) => a,
        None => return None,
    };
    
    println!("id{}, saika{}, laika{}, stopid{}, jnum{}", napatut.at(1).unwrap(), napatut.at(3).unwrap(), napatut.at(4).unwrap(), napatut.at(5).unwrap(), napatut.at(6).unwrap());
    Some(PysahtymisAjatData{trip_id: napatut.at(1).unwrap().to_string(), saapumis_aika: napatut.at(3).unwrap().to_string(), lahto_aika: napatut.at(4).unwrap().to_string(), stop_id: napatut.at(5).unwrap().to_string(), jnum: napatut.at(6).unwrap().to_string()})
}

#[no_mangle]
pub extern fn testi_anna_pysahtymisaika() {
    println!("Moi");
    anna_pysahtymisaika(r#""fe8ad47e-e0db-4d5b-be89-8ec759ecd6d3","05:01:00","05:01:00","303713","2""#);
    println!("{}",lue_pysahtymisajat().unwrap().len());
}


#[no_mangle]
pub extern fn pysakki_free(pysakki: Pysakki) {
   println!("Tultiin pysakin poistamiseen");
   cstring_free(pysakki.id);
   cstring_free(pysakki.nimi);
   cstring_free(pysakki.lon);
   cstring_free(pysakki.lat);
   println!("Lähdetään pysäkin poistamisesta.");
}

#[no_mangle]
pub extern fn cstring_free(p: *const c_char) {
    unsafe { CString::from_ptr(p) };
    println!("Tuhotaan jotain.");
}

#[no_mangle]
pub extern fn anna_esimerkki_teksti() -> *const c_char {
    CString::new("112514").unwrap().into_ptr()
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
