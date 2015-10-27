import ctypes
class Pysakki(ctypes.Structure):
    _fields_ = [("id", ctypes.c_void_p), ("nimi", ctypes.c_void_p), ("lat", ctypes.c_void_p), ("lon", ctypes.c_void_p)]

lib = ctypes.cdll.LoadLibrary("parsija/target/release/libparsija.so")
lib.pysakki_free.argtypes = [ctypes.POINTER(Pysakki)]
lib.pysakki_free.restype = None
lib.cstring_free.restype = None
lib.cstring_free.argtypes = [ctypes.c_void_p]
lib.anna_esimerkki_teksti.restype = ctypes.c_void_p
lib.anna_esimerkki_pysakki.restype = Pysakki

#esim1 = lib.anna_esimerkki_pysakki()
#print(esim1.id)
#print(esim1.nimi)
#print(esim1.lat)
#print(esim1.lon)
#lib.pysakki_free(esim1)

esim2 = lib.anna_esimerkki_teksti()
print ctypes.cast(esim2, ctypes.c_char_p).value
lib.cstring_free(esim2)
print("Kala")
