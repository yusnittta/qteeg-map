from typing import Optional, List, Tuple, Any           #Mengimpor tipe data dari modul typing untuk anotasi tipe di Python
import matplotlib                                       #Mengimpor modul matplotlib untuk plotting grafik
import pyqtgraph as pg                                  #Mengimpor pyqtgraph untuk plotting dan visualisasi interaktif di PyQt
import numpy as np                                      #Mengimpor numpy untuk operasi numerik dan manipulasi array
import pandas as pd                                     #Mengimpor pandas dengan alias 'pd', digunakan untuk analisis dan manipulasi data berbentuk tabel
from PyQt5.QtWidgets import QCheckBox                   #Mengimpor QCheckBox dari modul QtWidgets PyQt5 untuk membuat checkbox di GUI
import ui.resources  # noqa: F401                       #Mengimpor modul ui.resources tanpa menggunakan apa pun dari modul tersebut, 'noqa: F401' digunakan untuk mengabaikan peringatan tentang impor yang tidak digunakan
from src.UIMainWindow import UIMainWindow               #Mengimpor kelas UIMainWindow dari modul src.UIMainWindow
from src.TimeAxisItem import TimeAxisItem               #Mengimpor kelas TimeAxisItem dari modul src.TimeAxisItem
from src.ViewBoxCustom import ViewBoxCustom             #Mengimpor kelas ViewBoxCustom dari modul src.ViewBoxCustom
from src.frequency import Frequency                     #Mengimpor kelas Frequency dari modul src.frequency, yang berisi enumerasi frekuensi
from src.helpers import extend_unique, difference       #Mengimpor fungsi extend_unique dan difference dari modul src.helpers
from src.spike import Spike                             #Mengimpor kelas Spike dari modul src.spike
from src.transformer import Transformer                 #Mengimpor kelas Transformer dari modul src.transformer
import logging                                          #Mengimpor modul logging untuk pencatatan dan logging dalam aplikasi
import sys                                              #Mengimpor modul sys untuk berinteraksi dengan interpreter Python dan sistem
import pyedflib # type: ignore                          #Mengimpor modul pyedflib untuk membaca dan menulis file EDF (European Data Format)
from scipy.io import loadmat                            #Mengimpor fungsi loadmat dari modul scipy.io untuk membaca file MATLAB .mat
 
matplotlib.use('Qt5Agg')                                    #Mengatur backend matplotlib menjadi 'Qt5Agg', yang memungkinkan matplotlib untuk menggunakan Qt5 sebagai backend rendering
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG) #Mengkonfigurasi pengaturan dasar untuk logging, mengarahkan output log ke stdout dan mengatur level log ke DEBUG
 
#Jendela Utama
class MainWindow(UIMainWindow):                    #Kelas MainWindow mewarisi dari UIMainWindow, kelas utama untuk antarmuka pengguna aplikasi
    def __init__(self, *args, **kwargs):           #Konstruktor untuk inisialisasi objek MainWindow dan menerima argumen opsional
        super().__init__(*args, **kwargs)          #Memanggil konstruktor induk (UIMainWindow) untuk inisialisasi dasar     
        self.active_bands: List[Frequency] = []                         #Daftar untuk menyimpan frekuensi aktif yang sedang digunakan
        self.active_series: List[str] = []                              #Daftar untuk menyimpan seri data aktif yang sedang digunakan
        self.axis_items: List[Tuple[str, Frequency, pg.AxisItem]] = []  #Daftar item sumbu, setiap item adalah tuple berisi nama sumbu, frekuensi, dan objek AxisItem dari pyqtgraph
        self.data: pd.DataFrame = None                                  #DataFrame untuk menyimpan data dalam format tabel menggunakan pandas
        self.plotItem: pg.PlotItem = None                               #Objek PlotItem dari pyqtgraph untuk menampilkan grafik
        self.viewBox1: pg.ViewBox = None                                #Objek ViewBox dari pyqtgraph untuk tampilan grafik, kemungkinan view utama
        self.view_boxes: List[pg.ViewBox] = []                          #Daftar untuk menyimpan beberapa objek ViewBox dari pyqtgraph
        self.spikes = {                           #Kamus untuk menyimpan objek Spike yang terkait dengan masing-masing lokasi elektroda
            'TP9': Spike('TP9'),                  #Membuat objek Spike untuk lokasi 'TP9'
            'AF7': Spike('AF7'),                  #Membuat objek Spike untuk lokasi 'AF7'
            'AF8': Spike('AF8'),                  #Membuat objek Spike untuk lokasi 'AF8'
            'TP10': Spike('TP10')                 #Membuat objek Spike untuk lokasi 'TP10'
        } 
        self._prepare_frequency_bands()           #Menyiapkan pita frekuensi
        self._prepare_modes()                     #Menyiapkan mode operasi
        self._prepare_electrodes()                #Menyiapkan elektroda
                
    @staticmethod  
    def zip_longer(labels: List[Any],                       #Menggabungkan dua daftar dengan panjang yang tidak sama
                   bands: Optional[List[Any]]) -> zip:      #Parameter 'bands' adalah daftar yang mungkin kosong dan fungsi ini akan mengembalikan objek zip
        """                                                 #Docstring
        Zip unequal lists. 
        Parameters                                          #Parameter
        -----------
        labels: List[Any]                                   #Daftar label
        bands: List[Any]                                    #Daftar pita        
        Returns 
        -----------
        zip                                                 #Hasil zip dari dua daftar dengan panjang yang disesuaikan
        """ 
        if bands is None or len(bands) == 0:                #Jika 'bands' None atau kosong
            bands = [None]                                  #Set 'bands' menjadi [None]            
        if len(labels) == 1:                                #Jika hanya ada satu label
            labels = labels * len(bands)                    #Gandakan 'labels' untuk mencocokkan panjang 'bands' 
        else:                                               #Jika ada beberapa label
            bands = bands * len(labels)                     #Gandakan 'bands' untuk mencocokkan panjang 'labels' 
        return zip(labels, bands)                           #Kembalikan zip dari 'labels' dan 'bands' dengan panjang yang disesuaikan
       
    @staticmethod        
    def _axis_view_box_name(electrode: str,                                 #Mendefinisikan metode untuk menghasilkan nama berdasarkan electrode dan band
                            band: Optional[Frequency] = None) -> str:       #Parameter opsional band dengan default None dan mengembalikan string      
        """                                                                 #Docstring
        Create name composed from electrode and band.   
        Parameters                                                          #Parameter
        -----------
        electrode: str                                                      #Nama elektroda
        band: Frequency                                                     #Opsi pita frekuensi 
        Returns               
        -----------
        str                                                                 #Nama yang digabung dari 'electrode' dan 'band'
        """       
        return "{}{}".format(electrode, f"_{band.name}" if band else '')    #Gabungkan 'electrode' dan nama 'band' jika ada
              
    def _name_permutations(self, labels: List[str],                         #Mendefinisikan metode untuk menghasilkan permutasi nama
                           bands: Optional[List[Frequency]]) -> List[str]:  #Parameter opsional bands yang mengembalikan daftar string
        """                                                                 #Docstring
        Returns list of all names composed from labels and bands.     
        Parameters         
        -----------
        labels: List[str]                                                   #Daftar input berisi string label
        bands: List[Frequency], optional                                    #Daftar input opsional berisi objek Frequency
        Returns        
        -----------
        List[str]                                                           #Daftar output berisi string nama yang dihasilkan
        """      
        names = []                                                          #Inisialisasi daftar kosong untuk menyimpan nama yang dihasilkan
        for label in labels:                                                #Iterasi melalui setiap label dalam daftar labels
            for band in bands or [None]:                                    #Iterasi melalui setiap band atau gunakan [None] jika bands tidak disediakan
                names.append(self._axis_view_box_name(label, band))         #Menghasilkan dan menambahkan nama ke daftar
        return names                                                        #Mengembalikan daftar nama yang dihasilkan
                  
    def _default_electrode(self) -> None:           #Mendefinisikan metode untuk mengatur electrode default
        """                                         #Docstring
        Select TP9 as main and active series.      
        Returns      
        -----------
        None                                        #Tidak mengembalikan nilai
        """       
        self.active_series.append('TP9')            #Menambahkan 'TP9' ke daftar seri aktif
        self.main_series = 'TP9'                    #Mengatur 'TP9' sebagai seri utama
        self.checkboxTP9.blockSignals(True)         #Menonaktifkan sinyal dari checkboxTP9 sementara
        self.checkboxTP9.setChecked(True)           #Menandai checkboxTP9 sebagai dicentang
        self.checkboxTP9.blockSignals(False)        #Mengaktifkan kembali sinyal untuk checkboxTP9
      
    def _default_band(self) -> None:                        #Mendefinisikan metode untuk mengatur band default
        """                                                 #Docstring
        Select Frequency.GAMMA as main and active band.     
        Returns                                   
        -----------
        None                                                #Tidak mengembalikan nilai
        """    
        self.active_bands.append(Frequency.GAMMA)           #Menambahkan Frequency.GAMMA ke daftar band aktif
        self.main_band = Frequency.GAMMA                    #Mengatur Frequency.GAMMA sebagai band utama
        self.checkboxGamma.blockSignals(True)               #Menonaktifkan sinyal dari checkboxGamma sementara
        self.checkboxGamma.setChecked(True)                 #Menandai checkboxGamma sebagai dicentang
        self.checkboxGamma.blockSignals(False)              #Mengaktifkan kembali sinyal untuk checkboxGamma
                 
    def _set_limits(self):                                              #Mendefinisikan metode untuk mengatur batas-batas view box
        """                                                             #Docstring
        Set limits of view box.       
        Returns                
        ------------
        None                                                            #Tidak mengembalikan nilai
        """       
        limits = self.viewBox1.childrenBounds()                         #Mendapatkan batas-batas dari viewBox1
        y_min = min([x.childrenBounds()[1][0]                           #Mencari nilai y_min terkecil dari semua view box
                     for x in self.view_boxes + [self.viewBox1]])     
        y_max = max([x.childrenBounds()[1][1]                           #Mencari nilai y_max terbesar dari semua view box
                     for x in self.view_boxes + [self.viewBox1]])         
        for viewBox in self.view_boxes + [self.viewBox1]:               #Iterasi melalui semua view box
            viewBox.setLimits(xMin=limits[0][0],                        #Mengatur batas minimum x
                              xMax=limits[0][1],                        #Mengatur batas maksimum x
                              yMin=y_min + y_min / 100,                 #Mengatur batas minimum y dengan sedikit penambahan
                              yMax=y_max + y_min / 100)                 #Mengatur batas maksimum y dengan sedikit penambahan
                                 
    def _update_geometry(self) -> None:                                 #Mendefinisikan metode bernama _update_geometry untuk memperbarui geometri dari semua viewBox
        """                                                             #Docstring
        Update geometry of views.                                  
        Returns                                     
        -------------
        None                                                            #Tidak mengembalikan nilai
        """                                  
        for viewBox in self.view_boxes:                                 #Loop melalui setiap viewBox di view_boxes
            viewBox.setGeometry(self.viewBox1.sceneBoundingRect())      #Menyetel geometri setiap viewBox agar sesuai dengan ukuran viewBox1
                                                               
    def _get_colour(self, electrode: str,                               #Mendefinisikan metode untuk mendapatkan warna berdasarkan elektrode dan (opsional) frekuensi
                    band: Optional[Frequency] = None) -> str:           #'Electrode` adalah string, dan `band` adalah opsi objek Frequency atau None
        """                                                             #Docstring
        Return colour for series from settings.                          
        Parameters                                                        
        --------------
        electrode: str                                                  #Parameter `electrode` adalah string yang mewakili nama elektrode
        band: Frequency, optional                                       #Parameter `band` adalah objek dari tipe `Frequency` (opsional),
        Returns                                                         
        --------------
        str                                                             #Mengembalikan warna (string) dari pengaturan berdasarkan input elektrode dan frekuens
        """                                                             
        if (self.electrodes_group.exclusive()                           #Jika group elektroda diatur ke mode eksklusif (satu pilihan aktif) 
                and not self.frequency_group.exclusive()):              #Dan group frekuensi tidak eksklusif (lebih dari satu pilihan bisa aktif)
            return self.colours[band.name.upper()]                      #Kembalikan warna berdasarkan nama band frekuensi dalam huruf besar
        else:                                                           #Jika kondisi di atas tidak terpenuhi
            return self.colours[electrode.upper()]                      #Kembalikan warna berdasarkan nama elektrode dalam huruf besar
                                                                    
    def _set_main_axis(self) -> None:                                   #Mendefinisikan metode untuk mengatur sumbu utama dalam plot
        """                                                             #Docstring
        Set main axis.                                          
        Returns                    
        --------------
        None                                                            #Tidak mengembalikan nilai
        """        
        if self.main_series not in self.active_series:                              #Jika `main_series` belum ada di `active_series`
            self.active_series.append(self.main_series)                             #Tambahkan ke dalam `active_series`
        if self.plotItem in self.graphicsLayout.scene().items():                    #Jika `plotItem` ada di item scene `graphicsLayout`
            self.graphicsLayout.removeItem(self.plotItem)                           #Hapus item tersebut
        self.graphicsLayout.addItem(item=self.plotItem, row=2, col=1, rowspan=1,    #Tambahkan `plotItem` ke `graphicsLayout` pada posisi tertentu (baris 2, kolom 1, dengan span 1x1)
                                    colspan=1)                
        axis = self.plotItem.getAxis("left")                                        #Ambil sumbu vertikal kiri dari `plotItem`
        axis.setPen(self._get_colour(self.main_series, self.main_band))             #Atur warna garis (pen) pada sumbu kiri berdasarkan warna utama dari `main_series` dan `main_band`
        axis.setLabel(color=self._get_colour(self.main_series, self.main_band),     #Atur label sumbu kiri dengan warna dan teks berdasarkan `main_series` dan `main_band`
                      text=self._axis_view_box_name(self.main_series,       
                                                    self.main_band))         
                           
    def _prepare_canvas(self) -> None:                          #Mendefinisikan fungsi untuk mempersiapkan kanvas untuk tampilan grafik
        """                                                     #Docstring
        Prepare canvas.     
        Reinitialise central widget and main components.   
        Returns      
        --------------
        None                                                    #Tidak mengembalikan nilai
        """                                           
        self.plotItem = pg.PlotItem(viewBox=ViewBoxCustom(                          #Membuat objek `PlotItem` baru dengan `ViewBoxCustom` yang diberi nama sesuai `main_series` dan `main_band`
                name=self._axis_view_box_name(self.main_series, self.main_band)))     
        self.plotItem.showGrid(False, False)                                        #Menonaktifkan grid (garis bantu) pada grafik
        self.viewBox1 = self.plotItem.vb                                            #Menyimpan `viewBox1` dari `plotItem` untuk digunakan lebih lanjut
        self._set_main_axis()                                                       #Memanggil fungsi untuk mengatur sumbu utama pada grafik
        self.plotItem.setAxisItems(                                                 #Menambahkan sumbu waktu di bagian bawah grafik
            {'bottom': TimeAxisItem(orientation='bottom')})                   
   
    def _clean(self):                                           #Mendefinisikan fungsi untuk membersihkan semua `viewBoxes` dari tampilan
        """                                                     #Docstring
        Clean all viewBoxes from scene.   
        Returns    
        --------------
        None                                                    #Tidak mengembalikan nilai 
        """                                                     
        if self.graphicsLayout.scene():                         #Jika ada scene yang terkait dengan `graphicsLayout`
            for vb in self.view_boxes:                          #Untuk setiap `viewBox` dalam daftar `view_boxes`
                self.graphicsLayout.scene().removeItem(vb)      #Hapus `viewBox` tersebut dari scene
        self.active_series = []                                 #Kosongkan daftar `active_series`
        self.axis_items = []                                    #Kosongkan daftar `axis_items`
        self.view_boxes = []                                    #Kosongkan daftar `view_boxes`
          
    def _plot(self) -> None:                                                #Mendefinisikan fungsi untuk menggambar seri pertama pada grafik
        """                                                                 #Docstring
        Plot the first series.      
        Add to view box a corresponding series, set boundaries and limits.    
        Returns    
        --------------
        None                                                                #Tidak mengembalikan nilai 
        """          
        self.viewBox1.addItem(self._get_plot_item(self.active_series[0],    #Menambahkan item grafik yang sesuai dengan seri aktif pertama dan band utama ke `viewBox1`
                                                  self.main_band))        
        self._set_limits()                                                  #Mengatur batas-batas dan limit grafik
        self.viewBox1.sigResized.connect(self._update_geometry)             #Menghubungkan sinyal `sigResized` dari `viewBox1` ke fungsi `_update_geometry` agar geometri diperbarui saat ukuran berubah
             
    def _autorange(self) -> None:                                               #Mendefinisikan fungsi untuk mengaktifkan auto-range untuk setiap `viewBox`
        """                                                                     #Docstring
        Autorange.              
        For each viewBox enable auto range.                 
        Returns   
        --------------
        None                                                                    #Tidak mengembalikan nilai
        """     
        for viewBox in self.view_boxes:                                         #Untuk setiap `viewBox` dalam daftar `view_boxes`
            viewBox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)        #Aktifkan auto-range untuk kedua sumbu X dan Y pada `viewBox`
                                   
    def _set_single_series(self, override: Optional[bool] = False) -> None:     #Mendefinisikan fungsi untuk mengatur satu seri data sebagai seri utama
        """                                                                     #Docstring
        Set single series.           
        Parameters      
        ---------------
        override: bool, optional                                                #Parameter opsional 'override' adalah boolean yang menentukan apakah main_series akan diatur ulang ke series pertama dari active_series atau tidak
            Set main_series to first from active_series    
        Returns    
        ---------------
        None                                                                    #Tidak mengembalikan nilai
        """  
        if self.data is None:                                                   #Jika data belum ada
            self.data = self._read_data()                                       #Bacalah data dari sumber dan simpan ke `self.data'
        if override:                                                            #Jika `override` diatur ke True
            if len(self.active_series) > 0:                                     #Jika ada seri aktif yang tersedia
                self.main_series = self.active_series[0]                        #Atur `main_series` menjadi seri pertama dari `active_series`
            if self.active_bands and self.main_band not in self.active_bands:   #Jika ada band aktif dan `main_band` tidak ada dalam `active_bands`
                self.main_band = self.active_bands[0]                           #Atur `main_band` menjadi band pertama dari `active_bands`
        self._prepare_canvas()                                                  #Siapkan kanvas untuk menampilkan grafik
        self._plot()                                                            #Gambar grafik dengan seri utama yang telah diatur
 
      
#Membaca Data Format CSV, EDF, BDF, MAT
    def _read_data(self) -> pd.DataFrame:                                            #Mendefinisikan metode _read_data yang mengembalikan objek pd.DataFrame
        """                                                                          #Docstring
        Read data file with recordings (CSV, EDF, BDF, MAT).   
        Returns     
        ---------------
        pd.DataFrame                                                                 #Mengembalikan hasil dalam bentuk DataFrame dari pandas                                                     
        """        
        # Check the file type by extension
        if self.current_file.endswith('.csv'):                                       #Memeriksa apakah ekstensi file saat ini adalah .csv
            # If CSV, read using pandas
            eeg = pd.read_csv(self.current_file, index_col=0)                        #Membaca file CSV ke dalam DataFrame
            eeg.index = pd.to_datetime((eeg.index * 1000000000).astype(np.int64))    #Mengonversi indeks menjadi datetime
            return eeg                                                               #Mengembalikan DataFrame
     
        elif self.current_file.endswith('.edf') or self.current_file.endswith('.bdf'):      #Memeriksa apakah ekstensi file saat ini adalah .edf atau .bdf
            # If EDF or BDF, read using pyedflib
            edf_reader = pyedflib.EdfReader(self.current_file)                              #Inisialisasi pembaca EDF
            n_signals = edf_reader.signals_in_file                                          #Mendapatkan jumlah sinyal
            signal_labels = edf_reader.getSignalLabels()                                    #Mendapatkan label sinyal
            signal_data = {}                                                                #Inisialisasi kamus untuk menyimpan data sinyal
             
            for i in range(n_signals):                                                      #Membaca setiap sinyal dan menyimpannya dalam kamus
                signal_data[signal_labels[i]] = edf_reader.readSignal(i)
            
            edf_reader._close()                                                             #Menutup pembaca EDF
            return pd.DataFrame(signal_data)                                                #Mengembalikan DataFrame dari sinyal
  
        elif self.current_file.endswith('.mat'):                                #Memeriksa apakah ekstensi file saat ini adalah .mat
            # If MAT, read using scipy.io.loadmat
            mat_data = loadmat(self.current_file, squeeze_me=True)              #Memuat data file MAT
            
            # Print the keys to understand the structure of the data
            print("Keys in MAT file:", mat_data.keys())                         #Menampilkan kunci file MAT untuk inspeksi
            
            # Extract 'time' and signal data
            if 'time' in mat_data:                                              #Mengekstrak data waktu
                time_data = mat_data['time']     
            else:                                                               #Menghasilkan error jika kunci 'time' tidak ditemukan
                raise ValueError("No 'time' key found in the MAT file.")

            # Collect the signals (TP9, AF7, AF8, TP10, Right_AUX)
            signals = {key: mat_data[key] for key in ['TP9', 'AF7', 'AF8', 'TP10', 'Right_AUX']}    #Mengekstrak sinyal

            # Create a DataFrame with 'time' as index and signals as columns
            eeg_df = pd.DataFrame(signals, index=pd.to_datetime(time_data * 1e9))                   #Mengonversi 'time' menjadi datetime
            
            return eeg_df                                                                           #Mengembalikan DataFrame
        else:                                              #Menghasilkan error untuk format file yang tidak didukung
            raise ValueError("Unsupported file format.")
 
 
    def _draw_readings(self) -> None:                                #Mendefinisikan metode _draw_readings untuk menggambar pembacaan file
        """                                                          #Docstring
        Draw readings from files.      
        Returns     
        ---------------
        None                                                         #Tidak mengembalikan nilai
        """    
        self.graphicsLayout = pg.GraphicsLayout()                    #Membuat layout grafik baru
        self.graphicsView.setCentralWidget(self.graphicsLayout)      #Menetapkan layout grafik sebagai widget pusat di tampilan grafik
        self._set_single_series()                                    #Mengatur seri tunggal untuk grafik
        self.graphicsLayout.nextColumn()                             #Pindah ke kolom berikutnya di layout grafik
        self.viewBox1.setMouseEnabled(x=True, y=True)                #Mengaktifkan fungsionalitas mouse untuk navigasi x dan y di viewBox1
        self.viewBox1.setMenuEnabled(False)                          #Menonaktifkan menu konteks pada viewBox1
        self._autorange()                                            #Menyesuaikan rentang otomatis pada grafik
        self._update_geometry()                                      #Memperbarui geometri tampilan grafik
     
    def _load_file(self):                         #Mendefinisikan metode _load_file untuk menggambar output sumbu utama dari file
        """                                       #Docstring
        Draw main axis output from file.  
        Returns  
        ---------------
        None                                      #Tidak mengembalikan nilai
        """       
        self.data = None                                                #Menginisialisasi data dengan None
        if self.graphicsLayout:                                         #Jika layout grafik ada, bersihkan layout tersebut
            self._clean()   
        self._draw_readings()                                           #Menggambar pembacaan dari file
        self.message.setText(f"Current file: {self.current_file}")      #Menampilkan nama file saat ini di pesan
        self._reselect_checkboxes()                                     #Menyusun ulang status checkbox
        self.radioTime.setDisabled(False)                               #Mengaktifkan radio button waktu
        self.radioTime.setChecked(True)                                 #Menandai radio button waktu                 
        self.radioFrequencySingle.setDisabled(False)                    #Mengaktifkan radio button frekuensi tunggal
        self.radioFrequencyMultiple.setDisabled(False)                  #Mengaktifkan radio button frekuensi ganda
        self.actionSpike_detecting.setDisabled(False)                   #Mengaktifkan opsi deteksi spike
        self.actionSpike_sorting.setDisabled(False)                     #Mengaktifkan opsi sorting spike
        self.actionFeature_extraction.setDisabled(False)                #Mengaktifkan opsi ekstraksi fitur
        self.actionClustering.setDisabled(False)                        #Mengaktifkan opsi clustering
                  
    def _toggle_frequency(self, disabled: Optional[bool] = True,            #Mendefinisikan fungsi dengan dua parameter opsional: 'disabled' dan 'exclusive'
                          exclusive: Optional[bool] = False) -> None:       
        """                                                                 #Docstring
        Toggle frequency bands checkboxes.                                  #Fungsi untuk mengatur perilaku checkbox pada pita frekuensi
        disabled && !exclusive == time domain                               #Jika checkbox dalam kondisi disabled dan tidak exclusive, maka mode yang aktif adalah time domain
        !disabled && exclusive == single frequency                          #Jika checkbox tidak disabled dan bersifat exclusive, maka hanya satu frekuensi yang dapat dipilih.
        !disabled && !exclusive == multiple frequencies                     #Jika checkbox tidak disabled dan tidak exclusive, maka pengguna bisa memilih beberapa pita frekuensi sekaligus
        Parameters   
        ---------------
        disabled: bool, optional                                            #Nilai boolean untuk mengatur apakah checkbox pita frekuensi dalam keadaan disabled (tidak aktif)
        exclusive: bool, optional                                           #Nilai boolean untuk mengatur apakah hanya satu frekuensi yang bisa dipilih (exclusive) atau beberapa (non-exclusive)
        Returns   
        ---------------
        None                                                                #Tidak mengembalikan nilai
        """   
        self.frequency_group.setExclusive(exclusive)                        #Menentukan apakah hanya satu frekuensi yang bisa dipilih di dalam grup frekuensi
        self.single_frequency = False                                       #Mengatur frekuensi tunggal menjadi False secara default
        self.main_series = 'TP9'                                            #Menetapkan elektroda utama untuk visualisasi sebagai TP9
        
        if not disabled and not exclusive:                                  #Jika frekuensi tidak dinonaktifkan dan tidak eksklusif
            self.electrodes_group.setExclusive(True)                        #Mengatur agar hanya satu elektroda yang bisa dipilih dalam satu waktu
        else:                                                               #Jika tidak, atur mode frekuensi tunggal menjadi True
            self.single_frequency = True                      
            self.electrodes_group.setExclusive(False)                       #Mengizinkan lebih dari satu elektroda yang dipilih
        self._clean()                                                       #Membersihkan elemen-elemen UI sebelumnya
        self._reselect_checkboxes()                                         #Memilih ulang checkbox berdasarkan kondisi terbaru
  
        if disabled:                                                        #Jika disabled True
            self.main_band = None                                           #Set frekuensi utama menjadi None (tidak ada frekuensi aktif)
            self.active_bands = []                                          #Kosongkan daftar frekuensi yang aktif
            self.checkboxGamma.blockSignals(True)                           #Hentikan sinyal untuk perubahan sementara pada checkbox Gamma
            self.checkboxGamma.setChecked(False)                            #Set checkbox Gamma menjadi tidak tercentang
            self.checkboxGamma.blockSignals(False)                          #Aktifkan kembali sinyal setelah perubahan
        else:                                                               #Jika kondisi sebelumnya tidak terpenuhi
            self.main_band = Frequency.GAMMA                                #Atur frekuensi utama menjadi Gamma
            self.active_bands = [Frequency.GAMMA]                           #Tambahkan Gamma ke daftar frekuensi yang aktif
            self.checkboxGamma.blockSignals(True)                           #Hentikan sinyal untuk sementara pada checkbox Gamma
            self.checkboxGamma.setChecked(True)                             #Set checkbox Gamma menjadi tercentang
            self.checkboxGamma.blockSignals(False)                          #Aktifkan kembali sinyal setelah perubahan
          
        self.checkboxGamma.setDisabled(disabled)                            #Nonaktifkan checkbox Gamma jika 'disabled' True
        self.checkboxAlpha.setDisabled(disabled)                            #Nonaktifkan checkbox Alpha jika 'disabled' True
        self.checkboxBeta.setDisabled(disabled)                             #Nonaktifkan checkbox Beta jika 'disabled' True
        self.checkboxTheta.setDisabled(disabled)                            #Nonaktifkan checkbox Theta jika 'disabled' True
        self.checkboxDelta.setDisabled(disabled)                            #Nonaktifkan checkbox Delta jika 'disabled' True
         
        if self.current_file != '':                                         #Jika ada file yang sedang dibuka:
            self._draw_readings()                                           #Visualisasikan pembacaan EEG dengan pengaturan yang baru
                                  
    def _get_plot_item(self, electrode: str,                                     #Mendefinisikan fungsi yang menerima nama elektroda dan frekuensi (opsional)
                       frequency: Optional[Frequency] = None                     #Parameter frekuensi bersifat opsional, jika tidak diberikan, akan dianggap None
                       ) -> pg.PlotCurveItem:                                    #Fungsi ini mengembalikan objek PlotCurveItem dari PyQtGraph untuk visualisasi data
        """                                                                      #Docstrimg
        Return PlotCurveItem with reading.    
        Parameters    
        ---------------
        electrode: str                                                           #Nama elektroda yang datanya akan diproses dan diplot
        frequency: Frequency, optional                                           #Frekuensi yang digunakan untuk transformasi sinyal, bersifat opsional
        Returns   
        ---------------
        pg.PlotCurveItem                                                         #Mengembalikan objek PlotCurveItem dari PyQtGraph yang merepresentasikan kurva plot dari data elektroda
        """  
        x = list(self.data.index.astype(np.int64))                               #Konversi indeks data menjadi daftar integer (waktu atau timestamp)
        y = list(self.data[electrode])                                           #Ambil data sinyal dari elektroda tertentu dan ubah menjadi daftar
        if frequency:                                                            #Jika frekuensi disediakan, lakukan transformasi sinyal
            transformer = Transformer(np.array(x), np.array(y), frequency)       #Buat objek transformer dengan x, y, dan frekuensi
            x = x                                                                #Waktu (x) tetap sama
            y = transformer.get_irfft()                                          #Lakukan inverse real fast Fourier transform pada data y
        pen = self._get_colour(electrode, frequency)                             #Tentukan warna garis untuk elektroda dan frekuensi tertentu
        return pg.PlotCurveItem(x=x, y=y, pen=pen, antialias=True)               #Kembalikan PlotCurveItem dengan data x, y, warna garis, dan anti-aliasing
         
    def _checkbox_state(self, checkbox: QCheckBox, label: List[str],             #Mendefinisikan fungsi untuk mengupdate status checkbox dan memproses label serta frekuensi yang terkait
                        band: Optional[List[Frequency]] = None) -> None:   
        """                                                                      #Docstring
        Slot for checkbox changeState signal.    
        If checkbox is checked new axis should be added in other case axis   
        should be removed.   
        Parameters  
        ---------------
        checkbox: QCheckBox                                                      #Checkbox yang statusnya akan diperiksa (centang atau tidak).
        label: List[str]                                                         #Daftar label yang terkait dengan sumbu atau data yang diolah
        band: List[Frequency], optional                                          #Daftar frekuensi yang terkait dengan checkbox, opsional
        Returns  
        ---------------
        None                                                                     #Tidak mengembalikan nilai
        """    
        if checkbox.isChecked():                                                 #Jika checkbox tercentang, tambahkan seri data baru
            self._add_series(label, band, checkbox)   
        else:                                                                    #Jika checkbox tidak tercentang, hapus seri data
            self._remove_series(label, band, checkbox)    
  
#Frekuensi Ganda  
    def _is_last_band(self, checkbox) -> bool:                                  #Mendefinisikan fungsi untuk memeriksa apakah band terakhir dipilih dalam mode frekuensi ganda
        """   
        Check if last band was selected in multiple frequency mode.   
        Parameters   
        ---------------
        checkbox: QCheckBox                                                     #Parameter checkbox yang statusnya akan diperiksa
        Returns    
        ---------------
        bool                                                                    #Mengembalikan True jika band terakhir dipilih, sebaliknya False
        """   
        return self.radioFrequencyMultiple.isChecked() and (                    #Memeriksa apakah mode frekuensi ganda aktif
                len(self.active_bands) > 1                                      #Memeriksa apakah lebih dari satu band aktif
                or checkbox.parent() == self.groupBox_2)                        #Memeriksa apakah checkbox berada di dalam grup tertentu
    
#Frekuensi Tunggal  
    def _is_last_single_electrode(self, checkbox) -> bool:                      #Mendefiniskan fungsi untuk memeriksa apakah elektroda terakhir dipilih dalam mode frekuensi tunggal
        """                                                                     #Docstring
        Check if last electrode was selected in single frequency mode.   
        Parameters        
        ---------------
        checkbox: QCheckBox                                                     #Parameter checkbox adalah QCheckBox yang statusnya akan diperiksa
        Returns            
        ---------------
        bool                                                                    #Mengembalikan bool yang menunjukkan apakah kondisi tertentu terpenuhi
        """     
        return self.radioFrequencySingle.isChecked() and (                      #Memeriksa apakah mode frekuensi tunggal aktif
                len(self.active_series) > 1                                     #Memeriksa apakah lebih dari satu elektroda aktif
                or checkbox.parent() == self.groupBox_3)                        #Memeriksa apakah checkbox berada di dalam grup tertentu
 
#Time Domain          
    def _is_last_electrode(self) -> bool:                                       #Mendefinisikan metode _is_last_electrode yang mengembalikan nilai boolean
        """                                                                     #Docstring
        Check if last electrode was selected in time mode.           
        Returns    
        ---------------
        bool                                                                    #Mengembalikan nilai boolean
        """   
        return self.radioTime.isChecked() and len(self.active_series) > 1       #Memeriksa apakah mode waktu aktif dan lebih dari satu elektroda aktif
  
    def _is_set_new_main_series(self) -> bool:                                  #Mendefinisikan metode _is_set_new_main_series yang mengembalikan nilai boolean
        """                                                                     #Docstring
        Check if new main series should be set.   
        Returns    
        ---------------
        bool                                                                    #Mengembalikan nilai boolean
        """    
        return (self.main_series not in self.active_series                      #Memeriksa apakah main_series tidak ada di active_series
                and len(self.active_series) > 0) or (                           #Memeriksa apakah ada lebih dari 0 active_series
                self.main_band not in self.active_bands                         #Memeriksa apakah main_band tidak ada di active_bands
                and len(self.active_bands) > 0)                                 #Memeriksa apakah ada lebih dari 0 active_bands
        
    def _is_unset_main_series(self, checkbox, labels) -> bool:                  #Mendefinisikan metode _is_unset_main_series yang mengembalikan nilai boolean
        """   
        Check if new main series should be set.    
        Parameters  
        ---------------
        checkbox: QCheckBox                                                     #Objek QCheckBox yang akan diperiksa
        labels: List[str]                                                       #Daftar label yang akan diperiksa
        Returns  
        ---------------
        bool                                                                    #Mengembalikan nilai boolean
        """  
        return (len(labels) == 1 and self.main_series in labels                 #Memeriksa apakah hanya ada satu label dan apakah main_series ada dalam label
                and checkbox.parent() == self.groupBox_2)                       #Memeriksa apakah checkbox terkait dengan groupBox_2
   
    def _is_toggle_electrode(self, bands: Optional[List[Frequency]],            #Mendefinisikan metode _is_toggle_electrode yang mengembalikan nilai boolean
                             labels: List[str]) -> bool:      
        """                                                                     #Docstring
        Check if new main series should be set.  
        Parameters  
        ---------------
        bands: List[Frequency], optional                                        #Daftar frekuensi yang akan diperiksa
        labels: List[str]                                                       #Daftar label yang akan diperiksa
        Returns      
        ---------------
        bool                                                                    #Mengembalikan nilai boolean
        """    
        return (len(labels) == 1 and self.main_band in bands                    #Memeriksa apakah hanya ada satu label dan apakah main_band ada di bands
                and self.electrodes_group.exclusive())                          #Memeriksa apakah electrodes_group bersifat eksklusif (hanya satu elektroda dapat dipilih)
         
    def _is_toggle_band(self, checkbox) -> bool:                                #Mendefinisikan metode _is_toggle_band yang mengembalikan nilai boolean
        """                                                                     #Docstring
        Check if new main series should be set.   
        Parameters   
        ---------------
        checkbox: QCheckBox                                                     #Objek QCheckBox yang akan diperiksa
        Returns  
        ---------------
        bool                                                                    #Mengembalikan nilai boolean
        """    
        return (checkbox.parent() == self.groupBox_3                            #Memeriksa apakah checkbox terkait dengan groupBox_3
                and self.frequency_group.exclusive())                           #Memeriksa apakah frequency_group bersifat eksklusif (hanya satu frekuensi dapat dipilih)
    
    def _remove_series(self, labels: List[str],                                 #Mendefinisikan metode _remove_series untuk menghapus sumbu dari tampilan
                       bands: Optional[List[Frequency]] = None,   
                       checkbox: Optional[QCheckBox] = None) -> None:   
        """                                                                     #Docstring
        Remove axis.  
        if electrodes_group.exclusive() and not frequency_group.exclusive() 
            multiple or time 
            remove(label, [band]) 
        if not electrodes_group.exclusive() and frequency_group.exclusive() 
            single 
            remove([label], band) 
        Parameters 
        ---------------
        labels: List[str]                                                       #Daftar label yang akan dihapus
        bands: List[Frequency], optional                                        #Daftar frekuensi yang akan dihapus (opsional)
        checkbox: CheckBox, optional                                            #Objek QCheckBox yang terkait (opsional)
        Returns 
        ---------------
        None                                                                    #Tidak mengembalikan nilai
        """                          
        #Memeriksa apakah ini adalah elektroda terakhir, elektroda tunggal terakhir, atau band terakhir
        if self._is_last_electrode()\
                or self._is_last_single_electrode(checkbox)\
                or self._is_last_band(checkbox): 
            #Menghapus item dari active_series atau active_bands berdasarkan parent checkbox
            if checkbox.parent() == self.groupBox_2: 
                self.active_series = difference(self.active_series, labels) 
            if checkbox.parent() == self.groupBox_3: 
                self.active_bands = difference(self.active_bands, bands) 
            #Memeriksa apakah perlu mengatur main series yang baru, toggle band, atau toggle electrode
            if self._is_unset_main_series(checkbox, labels)\
                    or self._is_toggle_band(checkbox)\
                    or self._is_toggle_electrode(bands, labels): 
                #Menghapus plotItem dari scene jika ada
                if self.plotItem in self.graphicsLayout.scene().items(): 
                    self.graphicsLayout.removeItem(self.plotItem) 
                #Mengatur single series yang baru jika diperlukan
                if self._is_set_new_main_series(): 
                    self._set_single_series(True) 
                    if checkbox.parent() == self.groupBox_2: 
                        labels = [self.main_series] 
                    if checkbox.parent() == self.groupBox_3: 
                        bands = [self.main_band] 
            #Menghapus axis_items yang sesuai dengan label dan band dari scene dan layout
            axis_items = [x for x in self.axis_items if x[0] in labels] 
            if len(bands) > 0: 
                axis_items = [x for x in axis_items if x[1] in bands] 
            elif self._is_toggle_band(checkbox): 
                axis_items = [x for x in self.axis_items] 
            for axis_item in axis_items: 
                self.axis_items.remove(axis_item) 
                self.graphicsLayout.scene().removeItem(axis_item[2]) 
                self.graphicsLayout.layout.removeItem(axis_item[2]) 
            #Menghapus view_boxes yang sesuai dengan label dan band dari scene
            view_boxes = [view_box 
                          for view_box in self.view_boxes 
                          if view_box.name in self._name_permutations(labels, 
                                                                      bands)] 
            #Mengatur XLink untuk view_boxes jika ada
            if self._is_toggle_band(checkbox): 
                view_boxes = [x for x in self.view_boxes] 
            for view_box in view_boxes:  
                self.view_boxes.remove(view_box)  
                self.graphicsLayout.scene().removeItem(view_box)  
            if len(self.view_boxes) > 0:  
                self.view_boxes[0].setXLink(self.viewBox1)  
                for i in range(1, len(self.view_boxes)):  
                    self.view_boxes[i].setXLink(self.view_boxes[i - 1])  
        #Mengatur checkbox untuk tetap terpilih jika tidak memenuhi kondisi di atas
        else: 
            checkbox.blockSignals(True) 
            checkbox.setChecked(True) 
            checkbox.blockSignals(False) 
        
    def _add_series(self, labels: List[str],                                    #Mendefinisikan fungsi _add_series dengan parameter labels untuk menambahkan data series dan sumbu ke grafik
                    bands: Optional[List[Frequency]] = None,                    #Parameter opsional bands
                    checkbox: Optional[QCheckBox] = None) -> None:              #Parameter opsional checkbox
        """                                                                     #Docstring
        Add axis.  
        When checkbox is selected new series should be added to chart along     #Jika checkbox dipilih, series baru akan ditambahkan
        with new axis. New limits and geometry have to be set. 
        Parameters  
        ---------------
        labels: List[str]                                                       #Label dari series yang akan ditambahkan
        bands: List[Frequency], optional                                        #Frekuensi band dari series yang ditambahkan (opsional)
        checkbox: CheckBox, optional                                            #Checkbox yang memicu penambahan series (opsional)
        Returns  
        ---------------
        None                                                                    #Tidak mengembalikan nilai
        """  
        extend_unique(self.active_bands, bands)                                 #Menambahkan band baru ke daftar active_bands jika belum ada
        extend_unique(self.active_series, labels)                               #Menambahkan label series baru ke daftar active_series jika belum ada
        if len(self.active_series) == 0:                                        #Jika tidak ada series aktif
            self._default_electrode()                                           #Setel elektroda default untuk tampilan
        if (len(self.active_series) == 1 and                                    #Jika hanya ada satu series aktif
                not self.electrodes_group.exclusive()):                         #Dan kelompok elektroda tidak eksklusif
            self._set_single_series(True)                                       #Aktifkan mode single series
        else:   
            if ((self.frequency_group.exclusive()                               #Jika kelompok frekuensi eksklusif
                and checkbox.parent() == self.groupBox_3)                       #Dan checkbox dari groupBox_3
                    or (self.electrodes_group.exclusive()                       #Atau kelompok elektroda eksklusif
                        and (checkbox.parent() == self.groupBox_2               #Dan checkbox dari groupBox_2
                             or len(self.active_bands) == 1))):                 #Atau ada satu frekuensi band aktif
                self._set_single_series(True)                                   #Aktifkan mode single series
                if (self.frequency_group.exclusive()                            #Jika kelompok frekuensi eksklusif
                        and checkbox.parent() == self.groupBox_3):              #Dan checkbox berasal dari groupBox_3
                    labels = [x for x in labels if x != self.main_series]       #Hapus main_series dari labels
                if (self.electrodes_group.exclusive()                           #Jika kelompok elektroda eksklusif
                        and (checkbox.parent() == self.groupBox_2               #Dan checkbox dari groupBox_2
                             or len(self.active_bands) == 1)):                  #Atau active_bands hanya berisi satu band
                    bands = [x for x in bands if x != self.main_band]           #Hapus main_band dari bands
                    if len(bands) == 0:                                         #Jika tidak ada band yang tersisa
                        labels = []                                             #Kosongkan labels
            for label, band in self.zip_longer(labels, bands):                              #Iterasi melalui kombinasi label dan band
                view_box = ViewBoxCustom(                                                   #Buat view_box baru untuk menampung series baru
                    name=self._axis_view_box_name(label, band))                             #Buat nama untuk view_box berdasarkan label dan band
                self.view_boxes.append(view_box)                                            #Tambahkan view_box ke daftar view_boxes
                self.axis_items.append(                                                     #Tambahkan axis baru ke daftar axis_items
                    (label, band, pg.AxisItem(                                              #Buat AxisItem baru di sisi kiri dengan warna yang sesuai
                        "left", pen=self._get_colour(label, band))))       
                index = len(self.axis_items) - 1                                            #Dapatkan indeks axis terbaru
                self.graphicsLayout.addItem(                                                #Tambahkan axis ke layout grafik
                    item=self.axis_items[index][2], row=2, rowspan=1, colspan=1)            
                self.graphicsLayout.scene().addItem(view_box)                               #Tambahkan view_box ke scene
                view_box.addItem(self._get_plot_item(label, band))                          #Tambahkan plot item yang sesuai ke view_box
                self.axis_items[index][2].linkToView(self.view_boxes[index])                #Hubungkan axis dengan view_box terkait
                self.view_boxes[0].setXLink(self.viewBox1)                                  #Hubungkan view_box pertama ke viewBox1
                for i in range(1, len(self.view_boxes)):                                    #Hubungkan view_box berikutnya ke view_box sebelumnya
                    self.view_boxes[i].setXLink(self.view_boxes[i - 1])                            
                self.axis_items[index][2].setLabel(                                         #Setel label untuk axis baru dengan warna yang sesuai
                    self._axis_view_box_name(label, band),                                  #Tentukan nama label menggunakan kombinasi label dan band
                    pen=self._get_colour(label, band),                                      #Atur warna garis sumbu sesuai dengan label dan band
                    color=self._get_colour(label, band))                                    #Atur warna teks label sesuai dengan label dan band
                self._set_limits()                                                          #Atur batas grafik setelah axis baru ditambahkan
  
#Jendela Deteksi Spike
    def _spike_detection_window(self):                                           #Mendefinisikan fungsi untuk membuka jendela deteksi spike
        """                                                                      #Docstring
        Open Spike Detection window.  
        Returns  
        ---------------
        None                                                                     #Tidak mengembalikan nilai
        """  
        self.spike_detection_window.set_values(self.data, self.spikes)           #Mengatur data dan spike untuk jendela deteksi spike
        self.spike_detection_window.plot_spikes(last=None)                       #Memplot spike di jendela, tanpa membatasi spike terakhir
        self.spike_detection_window.show()                                       #Menampilkan jendela deteksi spike
    
#Jendela Pengurutan Spike
    def _spike_sorting_window(self):                                             #Mendefinisikan fungsi untuk membuka jendela pengurutan spike                                     
        """                                                                      #Docstring
        Open Spike Sorting window. 
        Returns  
        ---------------
        None                                                                     #Tidak mengembalikan nilai
        """  
        self.spike_sorting_window.set_values(self.data, self.spikes)             #Mengatur data dan spike untuk jendela pengurutan spike
        self.spike_sorting_window.plot_sorted_spikes(last=None)                  #Memplot spike yang diurutkan, tanpa batas spike terakhir
        self.spike_sorting_window.show()                                         #Menampilkan jendela pengurutan spike
   
#Jendela Ekstraksi Fitur  
    def _feature_extraction_window(self):                                        #Mendefinisikan fungsi untuk membuka jendela ekstraksi fitur
        """                                                                      #Docstring
        Open Feature Extraction window. 
        Returns 
        ---------------
        None                                                                     #Tidak mengembalikan nilai
        """  
        self.feature_extraction_window.set_values(self.data, self.spikes)        #Mengatur data dan spike untuk jendela ekstraksi fitur
        self.feature_extraction_window.plot_features()                           #Memplot fitur yang diekstraksi
        self.feature_extraction_window.show()                                    #Menampilkan jendela ekstraksi fitur
   
#Jendela Pengelompokan Spike
    def _clustering_window(self):                                                #Mendefinisikan fungsi untuk membuka jendela klastering
        """                                                                      #Docstring
        Open Clustering window. 
        Returns  
        ---------------
        None                                                                     #Tidak mengembalikan nilai
        """   
        self.clustering_window.set_values(self.data, self.spikes)                #Mengatur data dan spike untuk jendela klastering
        self.clustering_window.plot_clusters()                                   #Memplot klaster berdasarkan data
        self.clustering_window.show()                                            #Menampilkan jendela klastering
    def _wave_clusters_window(self) -> None:                                     #Mendefinisikan fungsi untuk membuka jendela gelombang yang terklaster
        """                                                                      #Docstring
        Open Clustered wave window. 
        Returns 
        ---------------
        None                                                                     #Tidak mengembalikan nilai
        """   
        self.wave_clusters_window.set_values(self.data, self.spikes)             #Mengatur data dan spike untuk jendela gelombang yang terklaster
        self.wave_clusters_window.plot_clustered_waves()                         #Memplot gelombang yang terklaster
        self.wave_clusters_window.show()                                         #Menampilkan jendela gelombang yang terklaster
   
    @staticmethod                                                                
    def _find_minimum_index(data: np.array, start: int, end: int) -> int:        #Mendefinisikan metode statis yang mencari indeks elemen minimum dalam rentang yang ditentukan
        """                                                                      #Docstring
        Find index of minimum element in array.  
        Parameters  
        ---------------
        data: np.array                                                           #Menunjukkan bahwa parameter data adalah array numpy
        start: int                                                               #Menunjukkan bahwa parameter start adalah indeks awal dari rentang
        end: int                                                                 #Menunjukkan bahwa parameter end adalah indeks akhir dari rentang
        Returns  
        ---------------
        int                                                                      #Menunjukkan bahwa metode ini mengembalikan sebuah integer yang merupakan indeks dari elemen terkecil
        """  
        return np.where(data == np.amin(data[start:end]))[0]                     #Mengembalikan indeks dari elemen minimum dalam rentang yang ditentukan pada array data