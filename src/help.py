from PyQt5 import uic                   #Mengimpor modul uic dari PyQt5
from PyQt5.QtWidgets import QDialog     #Mengimpor QDialog dari PyQt5.QtWidgets
                                                
#Jendela Dialog 'Bantuan'
class HelpWindow(QDialog):                            #Mendefinisikan kelas HelpWindow yang mewarisi dari QDialog
    def __init__(self, parent=None):                  #Konstruktor untuk HelpWindow, menerima parameter 'parent' opsional yang merupakan widget induk
        super().__init__(parent)                      #Memanggil konstruktor kelas induk (QDialog) dengan parameter 'parent'
        uic.loadUi("ui/help.ui", self)                #Memuat file UI 'help.ui' dan menghubungkannya ke instance saat ini (self) dari HelpWindow
        self.buttonBox.clicked.connect(self.close)    #Menghubungkan sinyal 'clicked' dari buttonBox ke metode 'close', sehingga jendela ditutup saat buttonBox diklik