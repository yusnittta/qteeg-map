from datetime import timedelta                      #Mengimpor kelas timedelta dari modul datetime, digunakan untuk perhitungan waktu
from typing import Dict, Optional                   #Mengimpor tipe Dict dan Optional untuk anotasi tipe data
import pandas as pd                                 #Mengimpor pustaka pandas dengan alias pd, digunakan untuk manipulasi data dalam format DataFrame
from PyQt5 import uic, QtWidgets                    #Mengimpor modul uic dan QtWidgets dari PyQt5, digunakan untuk antarmuka pengguna berbasis Qt
from src.MplCanvas import MplCanvas                 #Mengimpor kelas MplCanvas dari modul src.MplCanvas, digunakan untuk rendering grafik
from src.spike import WAVE_SIZE                     #Mengimpor konstanta WAVE_SIZE dari modul src.spike, kemungkinan digunakan untuk ukuran gelombang dalam analisis sinyal
   
class MplWindow(QtWidgets.QMainWindow):             #Mendefinisikan kelas MplWindow yang mewarisi dari QtWidgets.QMainWindow, membuat jendela utama aplikasi
     
    def __init__(self, parent=None):                                        #Inisialisasi metode konstruktor kelas
        super().__init__(parent)                                            #Memanggil konstruktor dari kelas induk (QMainWindow) dengan parameter parent
        uic.loadUi("ui/spike_detection.ui", self)                           #Memuat file UI dari "spike_detection.ui" dan menerapkannya ke instance saat ini
        self.colours = parent.colours                                       #Menginisialisasi atribut colours dengan nilai dari parent
        self.values: pd.DataFrame = None                                    #Mendeklarasikan atribut values sebagai DataFrame pandas, diinisialisasi dengan None
        self.canvas: MplCanvas = None                                       #Mendeklarasikan atribut canvas sebagai MplCanvas, diinisialisasi dengan None
        self.coordinates = [(0, 0, 'TP9'), (0, 1, 'AF7'), (1, 0, 'AF8'),    #Menginisialisasi atribut coordinates dengan daftar tuple yang berisi koordinat dan label
                            (1, 1, 'TP10')]                                 
        self.spikes = {}                                                    #Menginisialisasi atribut spikes sebagai dictionary kosong
    
    def set_values(self, values: pd.DataFrame, spikes: Dict) -> None:       #Mendefinisikan metode set_values untuk mengatur nilai baru dan menginisialisasi ulang canvas
        """                                                                 #Docstring
        Set new values and reinitialise canvas.  
        Parameters  
        ---------------
        values: pandas.DataFrame                                            #Parameter 'values' bertipe pandas DataFrame
            DataFrame with eeg readings  
        spikes: Dict                                                        #Parameter 'spikes' bertipe dictionary
            Dictionary with Spike objects for each electrode.   
        Returns  
        ---------------
        None                                                                #Tidak mengembalikan nilai
        """  
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)           #Menginisialisasi atribut canvas dengan instance baru dari MplCanvas, dengan ukuran dan resolusi yang ditentukan
        self.setCentralWidget(self.canvas)                                  #Menetapkan canvas sebagai widget pusat jendela utama
        self.values = values                                                #Mengatur atribut values dengan DataFrame yang diberikan
        self.spikes = spikes                                                #Mengatur atribut spikes dengan dictionary yang diberikan
   
    def _get_last_readings(self, last: Optional[int] = None) -> pd.DataFrame:       #Mendefinisikan metode _get_last_readings untuk mendapatkan pembacaan terakhir dalam rentang waktu tertentu
        """                                                                         #Docstring
        Get last x seconds of readings  
        Parameters  
        ---------------
        last: int, optional                                                         #Parameter 'last' bertipe integer dan bersifat opsional
            Number of seconds to return data for.                                   #Jumlah detik data yang ingin dikembalikan
        Returns  
        ---------------
        pandas.DataFrame                                                            #Tipe data yang dikembalikan adalah DataFrame dari pandas
            DataFrame with eeg recordings.  
        """   
        data = self.values                                                          #Menyimpan DataFrame values ke dalam variabel lokal data
        if last:                                                                    #Memeriksa apakah parameter last diberikan (tidak None)
            end = data.index[-1].to_pydatetime()                                    #Mendapatkan timestamp akhir dari indeks DataFrame dan mengonversinya ke objek datetime Python
            data = data.loc[end - timedelta(seconds=last):end]                      #Memilih subset data berdasarkan rentang waktu terakhir yang ditentukan
        return data                                                                 #Mengembalikan DataFrame dengan pembacaan EEG yang relevan
  
#Deteksi dan Plot Spike  
    def plot_spikes(self, last: Optional[int] = None) -> None:                      #Mendefinisikan metode plot_spikes untuk mendeteksi dan memplot spike
        """                                                                         #Docstring
        Detect and plot spikes.  
        Parameters  
        ---------------
        last: int, optional                                                         #Parameter 'last' bertipe integer dan bersifat opsional
            Analyse and plot last x seconds.  
        Returns   
        ---------------
        None                                                                        #Tidak mengembalikan nilai
        """  
        def _plot(axis_row: int, axis_col: int, column: str,                        #Mendefinisikan fungsi lokal _plot untuk memplot data pada posisi axis tertentu                  
                  xy_data: pd.Series) -> None:                                        
            #spike detection  
            self.spikes[column].set_data(xy_data)                                   #Mengatur data untuk deteksi spike dari objek Spike yang sesuai dengan kolom
            detected_spikes = self.spikes[column].detect()                          #Mendeteksi spike pada data yang telah diatur
            self.canvas.axes[axis_row, axis_col].scatter(                           #Memplot titik-titik spike yang terdeteksi pada sumbu yang sesuai
                detected_spikes.index.to_numpy(), detected_spikes.values,           #Mengatur ukuran dan warna titik-titik spike
                s=0.5, c='white') 
            #eeg data plot
            self.canvas.axes[axis_row, axis_col].plot(                              #Memplot data EEG pada sumbu yang sesuai
                xy_data.index.to_numpy(), xy_data.to_numpy(),                       #Mengatur warna dan lebar garis data EEG
                color=self.colours[column], linewidth=0.1)  
            self.canvas.axes[axis_row, axis_col].set_title(                         #Mengatur judul plot untuk sumbu yang sesuai.
                f"{column} (thresh:{self.spikes[column].spike_threshold:.2f}, "     #Menampilkan ambang batas dan tingkat kebisingan untuk setiap spike
                f"noise:{self.spikes[column].noise_level:.2f})", 
                color=self.colours[column])                                         #Menetapkan warna garis plot berdasarkan warna yang ditentukan untuk kolom saat ini dalam `self.colours`                    
   
        data = self._get_last_readings(last)                                        #Mendapatkan data pembacaan terakhir berdasarkan parameter `last` (jumlah detik) dari metode `_get_last_readings
        for row, col, col_name in self.coordinates:                                 #Iterasi melalui setiap koordinat yang didefinisikan dalam `self.coordinates`
            _plot(row, col, col_name, data.loc[:, col_name])                        #Memanggil fungsi `_plot` untuk menggambar data EEG pada subplot yang sesuai dengan nama kolom
        self.canvas.figure.subplots_adjust(wspace=0.3, hspace=0.3)                  #Menyesuaikan jarak antara subplot pada figure dengan ruang horizontal (`wspace`) dan vertikal (`hspace`) yang ditentukan
  
#Plot Spike Terurut
    def plot_sorted_spikes(self, last: Optional[int] = None) -> None:               #Mendefinisikan metode untuk mendeteksi dan menggambar spike yang telah diurutkan
        """                                                                         #Docstring
        Detect and plot spikes.  
        Parameters  
        ---------------
        last: int, optional                                                         #Parameter opsional untuk menentukan jumlah detik terakhir dari data yang akan dianalisis dan digambar
            Analyse and plot last x seconds. 
        Returns 
        ---------------
        None                                                                        #Tidak mengembalikan nilai
        """ 
        def _plot(axis_row: int, axis_col: int, column: str,                        #Mendefinisikan fungsi internal untuk menggambar spike yang telah diurutkan
                  xy_data: pd.Series) -> None:  
            self.spikes[column].set_data(xy_data)                                   #Mengatur data spike untuk kolom yang diberikan
            sorted_spikes = self.spikes[column].sort()                              #Mengurutkan spike untuk kolom yang diberikan
            for wave in sorted_spikes[0]:                                           #Iterasi melalui setiap gelombang spike yang diurutkan
                self.canvas.axes[axis_row, axis_col].plot(                          #Menggambar gelombang spike pada subplot yang sesuai
                    range(-WAVE_SIZE, WAVE_SIZE), wave,   
                    color='white', linewidth=0.1)                                   #Menggunakan warna putih dan ketebalan garis 0.1 untuk gelombang spike
            if len(sorted_spikes[1]):                                               #Memeriksa apakah ada gelombang spike yang diurutkan kedua
                self.canvas.axes[axis_row, axis_col].plot(                          #Menggambar gelombang spike kedua pada subplot yang sesuai
                    range(-WAVE_SIZE, WAVE_SIZE), sorted_spikes[1],  
                    color='red', linewidth=0.5)                                     #Menggunakan warna merah dan ketebalan garis 0.5 untuk gelombang spike kedua
    
        data = self._get_last_readings(last)                                        #Mendapatkan data pembacaan terakhir berdasarkan parameter `last`
        for row, col, col_name in self.coordinates:                                 #Iterasi melalui setiap koordinat yang didefinisikan dalam `self.coordinates`
            _plot(row, col, col_name, data.loc[:, col_name])                        #Memanggil fungsi `_plot` untuk menggambar spike yang telah diurutkan pada subplot yang sesuai dengan nama kolom
        self.canvas.figure.subplots_adjust(wspace=0.2, hspace=0.2)                  #Menyesuaikan jarak antara subplot pada figure dengan ruang horizontal (`wspace`) dan vertikal (`hspace`) yang ditentukan
  
#Plot Ekstraksi Fitur
    def plot_features(self) -> None:                                                #Mendefinisikan metode untuk menggambar fitur yang diekstrak
        """                                                                         #Docstring
        Plot extracted feautres.  
        Returns  
        ---------------
        None                                                                        #Tidak mengembalikan nilai
        """   
        def _plot(axis_row: int, axis_col: int, column: str,                        #Mendefinisikan fungsi internal untuk menggambar fitur
                  xy_data: pd.Series) -> None:  
            self.spikes[column].set_data(xy_data)                                   #Mengatur data spike untuk kolom yang diberikan
            features = self.spikes[column].extract_features()                       #Mengekstrak fitur dari spike untuk kolom yang diberikan
            self.canvas.axes[axis_row, axis_col].scatter(                           #Menggambar fitur sebagai scatter plot pada subplot yang sesuai
                features[:, 0], features[:, 1],  
                s=1.0, c='white')                                                   #Menggunakan ukuran titik 1.0 dan warna putih untuk scatter plot
            self.canvas.axes[axis_row, axis_col].set_title(                         #Mengatur judul subplot
                "IC1 vs IC2", color=self.colours[column])                           #Menggunakan warna dari `self.colours` untuk judul subplot
        for row, col, col_name in self.coordinates:                                 #Iterasi melalui setiap koordinat yang didefinisikan dalam `self.coordinates`
            _plot(row, col, col_name, self.values.loc[:, col_name])                 #Memanggil fungsi `_plot` untuk menggambar fitur pada subplot yang sesuai dengan nama kolom
        self.canvas.figure.subplots_adjust(wspace=0.2, hspace=0.2)                  #Menyesuaikan jarak antara subplot pada figure dengan ruang horizontal (`wspace`) dan vertikal (`hspace`) yang ditentukan
   
#Plot Pengelompokan Spike
    def plot_clusters(self) -> None:                                                #Mendefinisikan metode untuk menggambar cluster
        """                                                                         #Docstring
        Plot clusters.  
        Returns  
        ---------------
        None                                                                        #Tidak mengembalikan nilai
        """   
        def _plot(axis_row: int, axis_col: int, column: str,                        #Mendefinisikan fungsi internal untuk menggambar cluster pada subplot tertentu
                  xy_data: pd.Series) -> None:  
            self.spikes[column].set_data(xy_data)                                   #Mengatur data spike untuk kolom yang diberikan
            clusters, features = self.spikes[column].cluster()                      #Mengelompokkan data spike dan mendapatkan fitur dari cluster
            for i, c in zip(range(3), ['r', 'g', 'y']):                             #Iterasi melalui tiga cluster dengan warna yang sesuai (merah, hijau, kuning)
                cluster = clusters == i                                             #Menentukan data yang termasuk dalam cluster ke-i
                self.canvas.axes[axis_row, axis_col].scatter(                       #Menggambar data cluster pada subplot yang sesuai
                    features[cluster, 0], features[cluster, 1], s=1.0, c=c)         #Menggunakan warna `c` dan ukuran titik 1.0 untuk scatter plot
            self.canvas.axes[axis_row, axis_col].set_title(                         #Mengatur judul subplot dengan warna sesuai dengan kolom
                "Clusters", color=self.colours[column])   
        for row, col, col_name in self.coordinates:                                 #Iterasi melalui setiap koordinat yang didefinisikan dalam `self.coordinates`
            _plot(row, col, col_name, self.values.loc[:, col_name])                 #Memanggil fungsi `_plot` untuk menggambar cluster pada subplot yang sesuai dengan nama kolom
        self.canvas.figure.subplots_adjust(wspace=0.2, hspace=0.2)                  #Menyesuaikan jarak antara subplot pada figure dengan ruang horizontal (`wspace`) dan vertikal (`hspace`) yang ditentukan
 
#Plot Gelombang Terklaster
    def plot_clustered_waves(self) -> None:                                         #Mendefinisikan metode untuk menggambar gelombang yang terkelompok
        """                                                                         #Docstring
        Plot clustered waves.  
        Returns  
        ---------------
        None                                                                        #Tidak mengembalikan nilai
        """   
        def _plot(axis_row: int, axis_col: int, column: str) -> None:               #Mendefinisikan fungsi internal untuk menggambar gelombang terkelompok pada subplot tertentu
            clusters = self.spikes[column].clusters                                 #Mendapatkan informasi cluster dari spike untuk kolom yang diberikan
            sorted_spikes = self.spikes[column].sorted_spikes                       #Mendapatkan gelombang spike yang sudah diurutkan berdasarkan cluster
            for i, c in zip(range(3), ['r', 'g', 'y']):                             #Iterasi melalui tiga cluster dengan warna yang sesuai (merah, hijau, kuning)
                cluster = clusters == i                                             #Menentukan data yang termasuk dalam cluster ke-i
                for wave in sorted_spikes[cluster, :]:                              #Iterasi melalui gelombang yang termasuk dalam cluster ke-i
                    self.canvas.axes[axis_row, axis_col].plot(                      #Menggambar gelombang pada subplot yang sesuai
                        range(-WAVE_SIZE, WAVE_SIZE), wave,                         #Rentang x-axis dari -WAVE_SIZE hingga WAVE_SIZE
                        color=c, linewidth=0.1)                                     #Menggunakan warna `c` dan ketebalan garis 0.1 untuk plot gelombang
        for row, col, col_name in self.coordinates:                                 #Iterasi melalui setiap koordinat yang didefinisikan dalam `self.coordinates'
            _plot(row, col, col_name)                                               #Memanggil fungsi `_plot` untuk menggambar gelombang terkelompok pada subplot yang sesuai dengan nama kolom
        self.canvas.figure.subplots_adjust(wspace=0.2, hspace=0.2)                  #Menyesuaikan jarak antara subplot pada figure dengan ruang horizontal (`wspace`) dan vertikal (`hspace`) yang ditentukan