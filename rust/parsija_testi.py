
import ctypes
class Pysakki(ctypes.Structure):
    _fields_ = [("id", ctypes.c_char_p), ("nimi", ctypes.c_char_p), ("lat", ctypes.c_char_p), ("lon", ctypes.c_char_p)]

lib = ctypes.cdll.LoadLibrary("parsija/target/release/libparsija.so")

lib.anna_esimerkki_pysakki.restype = Pysakki

esim1 = lib.anna_esimerkki_pysakki()
print(esim1.id)
print(esim1.nimi)
print(esim1.lat)
print(esim1.lon)
