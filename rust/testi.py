import ctypes

class FFITuple(ctypes.Structure):
   _fields_ = [("a", ctypes.c_uint32),("b", ctypes.c_uint32)]

class FFIArray(ctypes.Structure): 
   _fields_ = [("data", ctypes.c_void_p), ("len", ctypes.c_size_t)]

   @classmethod
   def from_param(cls, seq):
      return cls(seq)

   def __init__(self, seq, data_type = ctypes.c_uint32):
      array_type = data_type * len(seq)
      raw_seq = array_type(*seq)
      self.data = ctypes.cast(raw_seq, ctypes.c_void_p)
      self.len = len(seq)

def void_array_to_tuple_list(array, _func, _args):
   tuple_array = ctypes.cast(array.data, ctypes.POINTER(FFITuple))
   return [tuple_array[i] for i in range(0, array.len)]

#Ilmeisesti varsinainen koodi alkaa tasta
lib = ctypes.cdll.LoadLibrary("./FFITesti/target/release/libFFITesti.so")#Ladataan rust-kirjasto

lib.moi()#Kutsuu rust-kirjaston moi() aliohjelmaa (tulostaa "Moi")
luku = lib.anna_luku()#asettaa luku muuttujaksi rust-kirjaston aliohjelmasta saatavan luvun.
print(luku)

print("Jotain toivottavasti tapahtui.")

#Alla hyodynnetaan rakenteiden valittamista kielten valilla.
lib.convert_vec.argtypes = (FFIArray, FFIArray)#Tassa luultavasti maaritetaan manuaalisesti rust-kirjaston convert_vec() aliohjelman parametrien tyypit
lib.convert_vec.restype = FFIArray#Sama mutta palautustyyppi luultavasti
lib.convert_vec.errcheck = void_array_to_tuple_list#Tama taas on mysteeri minullekin

#Tassa ilmeisesti kaytetaan rust-kirjaston aliohjelmia.
for tupl in lib.convert_vec([1,2,3], [9,8,7]):
   print tupl.a, tupl.b
