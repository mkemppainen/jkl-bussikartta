import ctypes;
lib = ctypes.cdll.LoadLibrary("./parsija/target/release/libparsija.so")

koodi = lib.luo_tietokanta()
print koodi
