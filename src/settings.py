import configparser                                                                  #Mengimpor modul configparser untuk membaca dan menulis file konfigurasi
from PyQt5 import uic                                                                #Mengimpor uic dari PyQt5 untuk memuat file UI
from PyQt5.QtWidgets import QDialog, QLineEdit                                       #Mengimpor kelas QDialog dan QLineEdit dari PyQt5 untuk membuat dialog dan input teks
from PyQt5.QtWidgets import QDialogButtonBox                                         #Mengimpor QDialogButtonBox untuk menangani tombol dalam dialog
     
#Jendela Pengaturan                             
class SettingsWindow(QDialog):                                                       #Mendefinisikan kelas SettingsWindow yang merupakan turunan dari QDialog
    def __init__(self, parent=None):                                                 #Konstruktor untuk inisialisasi jendela pengaturan
        super().__init__(parent)                                                     #Memanggil konstruktor QDialog
        uic.loadUi("ui/settings.ui", self)                                           #Memuat file antarmuka pengguna (UI) dengan uic.loadUi
        self.config = None                                                           #Inisialisasi variabel config yang akan digunakan untuk menyimpan konfigurasi
        self.buttonBox.button(                                                       #Menghubungkan tombol Cancel di buttonBox dengan metode close untuk menutup dialog
            QDialogButtonBox.Cancel).clicked.connect(self.close)   
        self.buttonBox.button(                                                       #Menghubungkan tombol Save di buttonBox dengan metode _save_settings untuk menyimpan pengaturan
            QDialogButtonBox.Save).clicked.connect(self._save_settings)                 
        
    def _save_setting(self, section: str, key: str, value: QLineEdit):               #Metode untuk menyimpan nilai pengaturan tertentu
        if value.text() != '' and len(value.text()) == 7:                            #Mengecek apakah input tidak kosong dan panjang teks adalah 7
            self.config[section][key] = value.text()                                 #Menyimpan nilai input ke dalam konfigurasi sesuai dengan section dan key
       
    def _save_settings(self):                                                        #Metode untuk menyimpan semua pengaturan
        #Menyimpan pengaturan untuk elektroda
        self._save_setting('electrodes', 'tp9', self.tp9_colour)                     
        self._save_setting('electrodes', 'af7', self.af7_colour)   
        self._save_setting('electrodes', 'af8', self.af8_colour)   
        self._save_setting('electrodes', 'tp10', self.tp10_colour)   
        #Menyimpan pengaturan untuk pita frekuensi
        self._save_setting('bands', 'gamma', self.gamma_colour)                      
        self._save_setting('bands', 'beta', self.beta_colour)  
        self._save_setting('bands', 'alpha', self.alpha_colour)  
        self._save_setting('bands', 'theta', self.theta_colour)  
        self._save_setting('bands', 'delta', self.delta_colour)  
        with open('settings.ini', 'w') as configfile:                                #Menyimpan file konfigurasi ke 'settings.ini'
            self.config.write(configfile)    
      
    def settings(self, settings):                                                    #Metode untuk mengisi nilai input dengan data dari file pengaturan
        self.config = settings                                                       #Mengatur config dengan data pengaturan yang diterima
        #Mengatur nilai warna untuk setiap elektroda di UI
        self.tp9_colour.setText(settings['electrodes']['tp9'])                       
        self.af7_colour.setText(settings['electrodes']['af7'])  
        self.af8_colour.setText(settings['electrodes']['af8'])  
        self.tp10_colour.setText(settings['electrodes']['tp10'])  
        #Mengatur nilai warna untuk setiap pita frekuensi di UI
        self.gamma_colour.setText(settings['bands']['gamma']) 
        self.beta_colour.setText(settings['bands']['beta']) 
        self.alpha_colour.setText(settings['bands']['alpha']) 
        self.theta_colour.setText(settings['bands']['theta']) 
        self.delta_colour.setText(settings['bands']['delta']) 