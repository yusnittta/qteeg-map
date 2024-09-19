import pyqtgraph as pg                 #Mengimpor modul pyqtgraph dengan alias pg untuk membuat grafik dan antarmuka pengguna berbasis Qt
import pandas as pd                    #Mengimpor modul pandas dengan alias pd untuk manipulasi data dan konversi waktu
      
class TimeAxisItem(pg.AxisItem):                                    #Mendefinisikan kelas TimeAxisItem yang mewarisi dari pg.AxisItem
    def tickStrings(self, values, scale, spacing):                  #Mengonversi nilai tick (dalam bentuk timestamp) menjadi objek datetime pandas dan mengembalikannya sebagai list string datetime
        return [pd.Timestamp(value).to_pydatetime(warn=False)       #Mengonversi setiap nilai timestamp ke objek datetime Python
                for value in values]                                #Mengiterasi semua nilai untuk konversi dan membentuk list