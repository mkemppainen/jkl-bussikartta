extern crate libc;

use libc::c_char;
use std::slice;
use std::mem;
use std::ffi::CString;

/// Sisältää pysäkin tiedot
#[repr(C)]
pub struct Pysakki {
    id: *mut c_char,
    nimi: *mut c_char, 
    lat: *mut c_char,
    lon: *mut c_char,
}

#[test]
fn it_works() {
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

    Pysakki{id: a_p as *mut _, nimi: b_p as *mut _ , lat: c_p as *mut _ , lon: d_p as *mut _}
}
