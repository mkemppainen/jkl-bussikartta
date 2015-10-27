import ctypes;
lib = ctypes.cdll.LoadLibrary("parsija/target/release/libparsija.so")

lib.testi_anna_pysahtymisaika()
