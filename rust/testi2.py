import ctypes;
lib = ctypes.cdll.LoadLibrary(".\\parsija\\target\\release\\parsija.dll")

lib.testi_anna_pysahtymisaika()
