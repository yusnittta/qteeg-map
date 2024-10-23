from PyQt5.QtCore import QEvent                 #Mengimpor kelas QEvent dari PyQt5.QtCore, digunakan untuk menangani peristiwa
from pyqtgraph import ViewBox, Point, fn        #Mengimpor ViewBox, Point, dan fn dari pyqtgraph untuk visualisasi grafis
import numpy as np                              #Mengimpor numpy dengan alias np, digunakan untuk operasi matematika dan array
from PyQt5 import QtCore                        #Mengimpor modul QtCore dari PyQt5 untuk fungsionalitas tambahan
   
class ViewBoxCustom(ViewBox):                   #Mendefinisikan subclass ViewBoxCustom yang merupakan turunan dari ViewBox
    
    def __init__(self,                          #Mendefinisikan metode konstruktor untuk ViewBoxCustom
                 parent=None,                   #Argumen opsional parent, menentukan widget induk jika ada
                 border=None,                   #Argumen opsional border, menentukan batas untuk ViewBox
                 lockAspect=False,              #Argumen opsional lockAspect, jika True akan mengunci rasio aspek tampilan
                 enableMouse=True,              #Argumen opsional enableMouse, jika True akan mengaktifkan kontrol mouse
                 invertY=False,                 #Argumen opsional invertY, jika True akan membalik sumbu Y
                 enableMenu=True,               #Argumen opsional enableMenu, jika True akan menampilkan menu konteks
                 name=None,                     #Argumen opsional name, memberikan nama untuk ViewBox
                 invertX=False):                #Argumen opsional invertX, jika True akan membalik sumbu X
        super().__init__(parent=parent,                     #Memanggil konstruktor superclass (ViewBox) dengan argumen parent
                         border=border,                     #Meneruskan argumen border ke konstruktor superclass
                         lockAspect=lockAspect,             #Meneruskan argumen lockAspect ke konstruktor superclass
                         enableMouse=enableMouse,           #Meneruskan argumen enableMouse ke konstruktor superclass
                         invertY=invertY,                   #Meneruskan argumen invertY ke konstruktor superclass
                         enableMenu=enableMenu,             #Meneruskan argumen enableMenu ke konstruktor superclass
                         name=name,                         #Meneruskan argumen name ke konstruktor superclass
                         invertX=invertX)                   #Meneruskan argumen invertX ke konstruktor superclass
          
    def wheelEvent(self, ev: QEvent, axis: int = None) -> None:                        #Mendefinisikan metode wheelEvent untuk menangani peristiwa roda mouse
        """                                                                            #Docstring
        Adjust wheel event.  
        Y wheel event (vertical zoom) should only work over Y-axis.  
        X wheel event (horizontal zoom) should work on both axis and chart area.   
        Parameters   
        ---------------
        ev: QEvent                                                                     #Peristiwa roda mouse
        axis: int                                                                      #Sumbu yang terpengaruh (0 untuk sumbu X, 1 untuk sumbu Y)
        Returns  
        ---------------
        None                                                                           #Tidak mengembalikan nilai
        """   
        mask = [False, False]                                                          #Inisialisasi daftar mask dengan dua nilai False
        if axis in (0, 1):                                                             #Jika axis adalah 0 (X) atau 1 (Y)
            mask[axis] = self.state['mouseEnabled'][axis]                              #Atur mask sesuai dengan status mouseEnabled pada sumbu yang sesuai
        else:                                                                          #Jika axis bukan 0 atau 1
            mask[0] = self.state['mouseEnabled'][0]                                    #Atur mask untuk sumbu X sesuai dengan status mouseEnabled
        s = 1.02 ** (ev.delta() * self.state['wheelScaleFactor'])                      #Hitung faktor skala zoom berdasarkan delta roda mouse dan wheelScaleFactor
        s = [(None if m is False else s) for m in mask]                                #Terapkan skala pada mask, setel None jika mask adalah False
        center = Point(fn.invertQTransform(                                            #Hitung titik pusat untuk skala berdasarkan posisi mouse
            self.childGroup.transform()).map(ev.pos())) 
        self._resetTarget()                                                            #Reset target skala sebelum menerapkan skala baru
        self.scaleBy(s, center)                                                        #Terapkan skala pada ViewBox berdasarkan mask dan titik pusat
        ev.accept()                                                                    #Tandai peristiwa sebagai diterima
        self.sigRangeChangedManually.emit(mask)                                        #Emit sinyal bahwa rentang telah diubah secara manual
  
    def mouseDragEvent(self, ev: QEvent, axis=None) -> None:                           #Mendefinisikan metode mouseDragEvent untuk menangani peristiwa seret mouse
        """                                                                            #Docstring
        Adjust drag event.  
        Y drag event (vertical movement) should work only on Y-axis.  
        X drag event (horizontal movement)  
        should work on both axis and chart area.  
        Parameters  
        ---------------
        ev: QEvent                                                                     #Peristiwa seret mouse
        axis: int                                                                      #Sumbu yang terpengaruh (0 untuk sumbu X, 1 untuk sumbu Y), jika None maka akan berfungsi pada kedua sumbu
        Returns   
        ---------------
        None                                                                           #Tidak mengembalikan nilai
        """    
        #Jika axis ditentukan, peristiwa hanya akan mempengaruhi sumbu tersebut.
        ev.accept()                 #Menandai peristiwa sebagai diterima
        pos = ev.pos()              #Posisi saat ini dari peristiwa
        lastPos = ev.lastPos()      #Posisi sebelumnya dari peristiwa
        dif = pos - lastPos         #Hitung perbedaan posisi
        dif = dif * -1              #Balikkan perbedaan posisi
    
        #Abaikan sumbu jika mouse dinonaktifkan
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)             #Ambil status mouseEnabled
        mask = mouseEnabled.copy()                                                      #Salin status mouseEnabled
        if axis is None:                                                                #Jika axis tidak ditentukan
            mask = [1.0, 0.0]                                                           #Hanya aktifkan sumbu X
        if axis is not None:                                                            #Jika axis ditentukan
            mask[1 - axis] = 0.0                                                        #Nonaktifkan sumbu yang berlawanan
    
        #Skala atau terjemahkan berdasarkan tombol mouse
        if ev.button() & (QtCore.Qt.LeftButton | QtCore.Qt.MidButton):                           #Jika tombol kiri atau tengah mouse ditekan
            if self.state['mouseMode'] == ViewBox.RectMode and axis is None:                     #Jika mode mouse adalah RectMode dan axis tidak ditentukan
                if ev.isFinish():                                                                #Jika ini adalah akhir dari seret
                    #Ini adalah gerakan terakhir dalam seret, ubah skala tampilan sekarang
                    self.rbScaleBox.hide()                                                       #Sembunyikan kotak skala
                    ax = QtCore.QRectF(Point(ev.buttonDownPos(ev.button())),                     #Buat kotak batas dari posisi awal dan posisi akhir
                                       Point(pos))   
                    ax = self.childGroup.mapRectFromParent(ax)                                   #Peta kotak batas dari sistem koordinat parent
                    self.showAxRect(ax)                                                          #Tampilkan kotak batas
                    self.axHistoryPointer += 1                                                   #Tambah pointer sejarah kotak batas
                    #Menetapkan nilai baru untuk atribut axHistory
                    self.axHistory =\
                         self.axHistory[:self.axHistoryPointer] + [ax]                           #Menggabungkan dua bagian daftar menjadi satu
                    #Perbarui bentuk kotak skala
                    self.updateScaleBox(ev.buttonDownPos(), ev.pos())   
            else:   
                tr = self.childGroup.transform()                                         #Ambil transformasi dari childGroup
                tr = fn.invertQTransform(tr)                                             #Balikkan transformasi
                tr = tr.map(dif * mask) - tr.map(Point(0, 0))                            #Terapkan transformasi ke perbedaan posisi yang disaring
                x = tr.x() if mask[0] == 1 else None                                     #Tentukan nilai x jika sumbu X aktif
                y = tr.y() if mask[1] == 1 else None                                     #Tentukan nilai y jika sumbu Y aktif
                self._resetTarget()                                                      #Reset target sebelum menerapkan transformasi
                if x is not None or y is not None:                                       #Jika x atau y tidak None
                    self.translateBy(x=x, y=y)                                           #Terjemahkan tampilan
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])            #Emit sinyal bahwa rentang telah diubah secara manual
        elif ev.button() & QtCore.Qt.RightButton:                                        #Jika tombol kanan mouse ditekan
            #print "vb.rightDrag"
            if self.state['aspectLocked'] is not False:                                  #Jika rasio aspek terkunci
                mask[0] = 0                                                              #Nonaktifkan sumbu X
            dif = ev.screenPos() - ev.lastScreenPos()                                    #Hitung perbedaan posisi di layar
            dif = np.array([dif.x(), dif.y()])                                           #Konversi perbedaan posisi menjadi array numpy
            dif[0] *= -1                                                                 #Balikkan nilai x
            s = ((mask * 0.02) + 1) ** dif                                               #Hitung faktor skala berdasarkan perbedaan posisi dan mask
            tr = self.childGroup.transform()                                             #Ambil transformasi dari childGroup
            tr = fn.invertQTransform(tr)                                                 #Balikkan transformasi
            x = s[0] if mouseEnabled[0] == 1 else None                                   #Tentukan skala x jika sumbu X aktif
            y = s[1] if mouseEnabled[1] == 1 else None                                   #Tentukan skala y jika sumbu Y aktif
            center = Point(tr.map(ev.buttonDownPos(QtCore.Qt.RightButton)))              #Hitung titik pusat untuk skala berdasarkan posisi awal tombol kanan
            self._resetTarget()                                                          #Reset target sebelum menerapkan skala
            self.scaleBy(x=x, y=y, center=center)                                        #Terapkan skala pada tampilan
            self.sigRangeChangedManually.emit(self.state['mouseEnabled'])                #Emit sinyal bahwa rentang telah diubah secara manual