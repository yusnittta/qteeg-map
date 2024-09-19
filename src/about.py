from PyQt5 import uic                               #Mengimpor modul 'uic' dari PyQt5
from PyQt5.QtWidgets import QDialog                 #Mengimpor `QDialog` dari PyQt5.QtWidgets
    
#Jendela Dialog 'Tentang'
class AboutWindow(QDialog):                         #Mendefinisikan kelas `AboutWindow` yang merupakan subclass dari `QDialog`. 
#Kelas ini digunakan untuk membuat jendela dialog "About"
    def __init__(self, parent=None):                #Inisialisasi konstruktor kelas
        super().__init__(parent)                    #Memanggil konstruktor dari kelas induk (`QDialog`) untuk mewarisi fungsionalitas dari QDialog
        uic.loadUi("ui/about.ui", self)             #Memuat file UI "about.ui"
        self.buttonBox.clicked.connect(self.close)  #Menghubungkan sinyal `clicked` dari elemen `buttonBox` di UI dengan metode `close()`, yang akan menutup jendela saat tombol diklik     