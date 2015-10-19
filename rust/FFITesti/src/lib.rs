extern crate libc;

use std::slice;
use std::mem;

#[test]
fn it_works() {
}

#[no_mangle]
pub extern fn moi() {
  println!("Moi!");
}

#[no_mangle]
pub extern fn anna_luku() -> i8 {
  13
}

#[repr(C)]
pub struct Tuple {
   a: libc::uint32_t,
   b: libc::uint32_t,
}

#[repr(C)]
pub struct Array {
  data: *const libc::c_void,
  len: libc::size_t,
}

impl Array {
   unsafe fn as_u32_slice(&self) -> &[u32] {
      assert!(!self.data.is_null());
      slice::from_raw_parts(self.data as *const u32, self.len as usize)
   }

   fn from_vec<T>(mut vec: Vec<T>) -> Array {
      vec.shrink_to_fit();
      let array = Array { data: vec.as_ptr() as *const libc::c_void, len: vec.len() as libc::size_t };

      mem::forget(vec);

      array
   }
}

#[no_mangle]
pub extern fn convert_vec(lon: Array, lat: Array) -> Array {
   let lon = unsafe { lon.as_u32_slice() };
   let lat = unsafe { lat.as_u32_slice() };
   
   let vec = lat.iter().zip(lon.iter()).map(|(&lat, &lon)| Tuple { a: lat, b: lon}).collect();
 
   Array::from_vec(vec)
}
