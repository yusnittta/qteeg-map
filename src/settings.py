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
        self._save_setting('electrodes', 'fp1', self.fp1_colour)  
        self._save_setting('electrodes', 'fp2', self.fp2_colour)  
        self._save_setting('electrodes', 'f3', self.f3_colour)  
        self._save_setting('electrodes', 'f4', self.f4_colour)  
        self._save_setting('electrodes', 'c3', self.c3_colour)  
        self._save_setting('electrodes', 'c4', self.c4_colour)   
        self._save_setting('electrodes', 'p3', self.p3_colour)  
        self._save_setting('electrodes', 'p4', self.p4_colour)  
        self._save_setting('electrodes', 'o1', self.o1_colour)  
        self._save_setting('electrodes', 'o2', self.o2_colour)  
        self._save_setting('electrodes', 'f7', self.f7_colour)  
        self._save_setting('electrodes', 'f8', self.f8_colour)  
        self._save_setting('electrodes', 't3', self.t3_colour)  
        self._save_setting('electrodes', 't8', self.t4_colour)  
        self._save_setting('electrodes', 't5', self.t5_colour)  
        self._save_setting('electrodes', 't6', self.t6_colour)  

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
        self.fp1_colour.setText(settings['electrodes']['fp1'])  
        self.fp2_colour.setText(settings['electrodes']['fp2'])  
        self.f3_colour.setText(settings['electrodes']['f3'])  
        self.f4_colour.setText(settings['electrodes']['f4'])  
        self.c3_colour.setText(settings['electrodes']['c3'])  
        self.c4_colour.setText(settings['electrodes']['c4'])  
        self.p3_colour.setText(settings['electrodes']['p3'])  
        self.p4_colour.setText(settings['electrodes']['p4'])  
        self.o1_colour.setText(settings['electrodes']['o1'])  
        self.o2_colour.setText(settings['electrodes']['o2'])  
        self.f7_colour.setText(settings['electrodes']['f7'])  
        self.f8_colour.setText(settings['electrodes']['f8'])  
        self.t3_colour.setText(settings['electrodes']['t3'])  
        self.t4_colour.setText(settings['electrodes']['t4'])  
        self.t5_colour.setText(settings['electrodes']['t5'])  
        self.t6_colour.setText(settings['electrodes']['t6'])  
        
        #Mengatur nilai warna untuk setiap pita frekuensi di UI
        self.gamma_colour.setText(settings['bands']['gamma']) 
        self.beta_colour.setText(settings['bands']['beta']) 
        self.alpha_colour.setText(settings['bands']['alpha']) 
        self.theta_colour.setText(settings['bands']['theta']) 
        self.delta_colour.setText(settings['bands']['delta']) 