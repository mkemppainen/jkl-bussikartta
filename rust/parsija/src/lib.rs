#![feature(cstr_memory2)]
extern crate libc;

use libc::c_char;
use std::mem;
use std::ffi::CString;

/// Sisältää pysäkin tiedot
#[repr(C)]
pub struct Pysakki {
    id: *const c_char,
    nimi: *const c_char, 
    lat: *const c_char,
    lon: *const c_char,
}

#[test]
fn it_works() {
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
