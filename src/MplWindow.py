from datetime import timedelta                          #Mengimpor kelas timedelta dari modul datetime, digunakan untuk perhitungan waktu
from typing import Dict, Optional                       #Mengimpor tipe Dict dan Optional untuk anotasi tipe data
import pandas as pd                                     #Mengimpor pustaka pandas dengan alias pd, digunakan untuk manipulasi data dalam format DataFrame
from PyQt5 import uic, QtWidgets                        #Mengimpor modul uic dan QtWidgets dari PyQt5, digunakan untuk antarmuka pengguna berbasis Qt
from src.MplCanvas import MplCanvas                     #Mengimpor kelas MplCanvas dari modul src.MplCanvas, digunakan untuk rendering grafik
from src.spike import WAVE_SIZE                         #Mengimpor konstanta WAVE_SIZE dari modul src.spike, kemungkinan digunakan untuk ukuran gelombang dalam analisis sinyal
import numpy as np                                      #Pastikan ini ditambahkan di bagian atas file
import matplotlib.pyplot as plt                         #Pastikan ini ditambahkan di bagian atas file
from scipy.interpolate import griddata                  #Import griddata for interpolation
from matplotlib.colors import LinearSegmentedColormap   #Mengimpor modul LinearSegmentedColormap dari matplotlib.colors untuk membuat colormap kustom
from scipy.signal import welch                          #Mengimpor fungsi welch dari scipy.signal untuk melakukan estimasi spektrum densitas daya menggunakan metode Welch
from matplotlib.ticker import ScalarFormatter           #Mengimpor ScalarFormatter dari matplotlib.ticker untuk mengatur format angka pada sumbu grafik agar sesuai dengan skala tertentu

class MplWindow(QtWidgets.QMainWindow):             #Mendefinisikan kelas MplWindow yang mewarisi dari QtWidgets.QMainWindow, membuat jendela utama aplikasi
     
    def __init__(self, parent=None):                                        #Inisialisasi metode konstruktor kelas
        super().__init__(parent)                                            #Memanggil konstruktor dari kelas induk (QMainWindow) dengan parameter parent
        uic.loadUi("ui/spike_detection.ui", self)                           #Memuat file UI dari "spike_detection.ui" dan menerapkannya ke instance saat ini
        self.colours = parent.colours                                       #Menginisialisasi atribut colours dengan nilai dari parent
        self.values: pd.DataFrame = None                                    #Mendeklarasikan atribut values sebagai DataFrame pandas, diinisialisasi dengan None
        self.canvas: MplCanvas = None                                       #Mendeklarasikan atribut canvas sebagai MplCanvas, diinisialisasi dengan None
           
        # Menginisialisasi atribut coordinates dengan daftar tuple yang berisi koordinat dan label
        self.coordinates = [(0, 0, 'FP1'), (0, 1, 'FP2'), (0, 2, 'F3'),  (0, 3, 'F4'),
                            (1, 0, 'C3'),  (1, 1, 'C4'),  (1, 2, 'P3'),  (1, 3, 'P4'),
                            (2, 0, 'O1'),  (2, 1, 'O2'),  (2, 2, 'F7'),  (2, 3, 'F8'),
                            (3, 0, 'T3'),  (3, 1, 'T4'),  (3, 2, 'T5'),  (3, 3, 'T6')]
             
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
  
#Plot Ekstraksi Fitur dengan FastICA
    def plot_features(self) -> None:                                                #Mendefinisikan metode untuk menggambar fitur yang diekstrak
        """                                                                         #Docstring
        Plot extracted feautres with FastICA. 
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

#Plot Ekstraksi Fitur dengan PCA
    def plot_pca_features(self) -> None:                                            #Mendefinisikan metode untuk menggambar fitur PCA yang diekstrak
        """                                                                         #Docstring
        Plot extracted features with PCA. 
        Returns  
        --------------- 
        None                                                                        #Tidak mengembalikan nilai
        """   
        def _plot(axis_row: int, axis_col: int, column: str,                        #Mendefinisikan fungsi internal untuk menggambar fitur PCA
                xy_data: pd.Series) -> None:  
            self.spikes[column].set_data(xy_data)                                   #Mengatur data spike untuk kolom yang diberikan
            features = self.spikes[column].extract_pca_features()                   #Mengekstrak fitur PCA dari spike untuk kolom yang diberikan
            self.canvas.axes[axis_row, axis_col].scatter(                           #Menggambar fitur sebagai scatter plot pada subplot yang sesuai
                features[:, 0], features[:, 1],  
                s=1.0, c='blue')                                                    #Menggunakan ukuran titik 1.0 dan warna biru untuk scatter plot
            self.canvas.axes[axis_row, axis_col].set_title(                         #Mengatur judul subplot
                "PC1 vs PC2", color=self.colours[column])                           #Menggunakan warna dari `self.colours` untuk judul subplot
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

#Plot Topographical Scalp Map  
    def plot_topoplot(self) -> None:                                                #Mendefinisikan metode untuk menggambar topographical scalp map
        """                                                                         #Docstring
        Plot 2D scalp topographical map of EEG power 
        for specific frequencies with a circular head shape.
        Returns
        -------
        None
        """
        #Memeriksa apakah data EEG ada dan memiliki 16 saluran
        if self.values is None or len(self.values.columns) != 16:  
            print("Failed to load EEG data or incorrect number of electrodes.")
            return
        #Membersihkan kanvas sebelumnya sebelum membuat plot baru
        self.canvas.figure.clear()
        #Mendefinisikan frekuensi untuk diplot
        freqs_to_plot = {
            'Delta (0-4 Hz)': (0, 4),
            'Theta (4-8 Hz)': (4, 8),
            'Alpha (8-13 Hz)': (8, 13),
            'Beta (14-30 Hz)': (14, 30),
            'Gamma (20-40 Hz)': (20, 40),
            'Total': (0, 40)
        }
        #Jumlah elektroda/saluran
        num_channels = len(self.values.columns)
        #Posisi elektroda dalam 2D
        electrode_pos = np.array([
            [-0.25, 1.0],       #FP1
            [0.25, 1.0],        #FP2
            [-0.5, 0.5],        #F3
            [0.5, 0.5],         #F4
            [-0.5, 0.0],        #C3 
            [0.5, 0.0],         #C4
            [-0.5, -0.5],       #P3
            [0.5, -0.5],        #P4
            [-0.25, -1.0],      #O1
            [0.25, -1.0],       #O2
            [-1.0, 0.5],        #F7
            [1.0, 0.5],         #F8
            [-1.0, 0.0],        #T3
            [1.0, 0.0],         #T4
            [-1.0, -0.5],       #T5
            [1.0, -0.5]         #T6
        ])
        #Membuat grid untuk interpolasi (kepala melingkar)
        grid_x, grid_y = np.mgrid[-1.2:1.2:100j, -1.2:1.2:100j]
        #Menetapkan ukuran angka sebelum subplot memanggil
        self.canvas.figure.set_size_inches(15, 10)
        #Membuat kisi sumbu untuk peta kulit kepala pada frekuensi yang berbeda (2 baris, 3 kolom)
        self.canvas.axes = self.canvas.figure.subplots(2, 3, sharey=True)
        #Membuat peta warna khusus
        colors = ["blue", "green", "yellow", "red"]
        cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
        for i, freq in enumerate(freqs_to_plot):
            #Menghitung daya pada frekuensi yang diberikan menggunakan FFT
            power = np.mean(np.abs(np.fft.fft(self.values.T, axis=1)), axis=1)
            if len(power) != num_channels:
                print(f"Mismatch in power values and number of electrodes for frequency {freq}.")
                return
            #Interpolasi nilai daya untuk menciptakan topografi yang halus
            grid_z = griddata(electrode_pos, power[:num_channels], (grid_x, grid_y), method='cubic', fill_value=np.nan)
            #Membuat topeng melingkar untuk membatasi plot ke area kepala
            mask = np.sqrt(grid_x**2 + grid_y**2) <= 1  #Lingkaran dengan jari-jari 1
            grid_z = np.ma.masked_where(~mask, grid_z)  #Menutupi segala sesuatu di luar lingkaran
            #Temukan posisi di kisi 2x3
            row = i // 3
            col = i % 3
            #Plot peta kulit kepala yang diinterpolasi dengan peta warna khusus
            im = self.canvas.axes[row, col].imshow(grid_z.T, extent=(-1.2, 1.2, -1.2, 1.2), origin='lower', cmap=cmap)
            #Menambahkan garis kontur di atas peta kulit kepala
            contour = self.canvas.axes[row, col].contour(grid_x, grid_y, grid_z, levels=10, linewidths=2, colors='black', alpha=0.5)
            #Menambahkan garis kepala melingkar
            head_circle = plt.Circle((0, 0), 1, color='black', fill=False, lw=20)
            self.canvas.axes[row, col].add_artist(head_circle)
            #Posisi elektroda overlay
            self.canvas.axes[row, col].scatter(electrode_pos[:, 0], electrode_pos[:, 1], c='black', s=300, marker='o')
            #Tandai label elektroda
            for j, (x, y) in enumerate(electrode_pos):
                self.canvas.axes[row, col].text(x, y, f"{self.values.columns[j]}", color="white", fontsize=12, ha='center', va='center')
            #Menetapkan judul untuk setiap plot
            self.canvas.axes[row, col].set_title(f'{freq}')
            #Menetapkan batas yang sama untuk semua sumbu untuk memastikan keseragaman
            self.canvas.axes[row, col].set_xlim(-1.2, 1.2)
            self.canvas.axes[row, col].set_ylim(-1.2, 1.2)
            #Menetapkan rasio aspek yang sama
            self.canvas.axes[row, col].set_aspect('equal', adjustable='box')
            #Menghapus tanda sumbu untuk kejelasan yang lebih baik
            self.canvas.axes[row, col].set_xticks([])
            self.canvas.axes[row, col].set_yticks([])
        #Membuat sumbu baru untuk skala warna (vertikal) agar sesuai dengan tinggi grid 2 baris
        cbar_ax = self.canvas.figure.add_axes([0.94, 0.2, 0.02, 0.6])                #Menyesuaikan ketinggian agar sesuai dengan kisi 2 baris
        #Menampilkan skala warna untuk skala daya
        cbar = self.canvas.figure.colorbar(im, cax=cbar_ax, orientation='vertical')  #Mengatur orientasi ke vertikal
        #Menetapkan label untuk skala warna di sisi kiri
        cbar.ax.yaxis.set_label_position('left')        #Memindahkan label ke sisi kiri
        cbar.set_label('Daya')                          #Label di sisi kiri
        #Menyesuaikan tata letak untuk mencegah tumpang tindih
        self.canvas.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2, wspace=0.4, hspace=0.3)
        #Menyegarkan kanvas untuk menampilkan plot baru
        self.canvas.draw()
        print("2D Scalp map with circular head successfully plotted.")

#Plot Power Spectral Density (PSD)
    def plot_spectrum(self) -> None:                        #Mendefinisikan metode untuk menggambar Power Spectral Density
        """                                                 #Docstring
        Plot Power Spectral Density (PSD).
        Returns
        -------
        None
        """
        if self.values is None:
            print("Tidak ada data EEG untuk diproses.")
            return
        eeg_data = self.values.to_numpy()                   #Mengubah DataFrame menjadi array numpy
        fs = 256                                            #Frekuensi pengambilan sampel, sesuaikan dengan dataset
        #Menghapus plot sebelumnya
        for ax in self.canvas.axes.flatten():
            ax.clear()
        #Daftar warna hex yang ditentukan untuk masing-masing channel
        colours = [
            '#2E2EFE',  #FP1
            '#00FF00',  #FP2
            '#FFFF00',  #F3
            '#FF0000',  #F4
            '#FF8000',  #C3
            '#800080',  #C4
            '#00FFFF',  #P3
            '#FF00FF',  #P4
            '#008080',  #O1
            '#FFD700',  #O2
            '#8B4513',  #F7
            '#708090',  #F8
            '#DC143C',  #T3
            '#00BFFF',  #T4
            '#FF69B4',  #T5
            '#7FFF00'   #T6
        ]
        #List nama channel
        channel_names = [
            'FP1', 'FP2', 'F3', 'F4', 'C3', 'C4', 
            'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 
            'T3', 'T4', 'T5', 'T6'
        ]
        #Loop untuk setiap channel EEG (16 channel)
        num_channels = eeg_data.shape[0]            #Mengasumsikan bentuk [n_channels, n_samples]
        for i in range(min(num_channels, 16)):      #Hanya plot 16 channel pertama
            channel_data = eeg_data[i, :]           #Mengambil data dari tiap channel
            #Menghitung PSD menggunakan metode Welch
            f, Pxx = welch(channel_data, fs=fs, nperseg=1024)
            #Mengeplot tiap channel di subplot yang sesuai (4x4 grid)
            ax = self.canvas.axes.flatten()[i]
            #Menentukan intensitas glow sebagai persentase dari Pxx
            glow_intensity = 0 * Pxx 
            #Mengeplot efek glow yang mengikuti garis spektrum
            ax.fill_between(f, Pxx - glow_intensity, Pxx + glow_intensity, color=colours[i], alpha=0.3)  #Efek glow
            ax.semilogy(f, Pxx, color=colours[i], label=channel_names[i])                                #Plot dengan warna yang ditentukan
            ax.set_xlabel('Frekuensi (Hz)')                  #Label sumbu X
            ax.set_ylabel('Daya (μV²/Hz)')                   #Label sumbu Y
            ax.legend(loc='upper right')                     #Menampilkan legenda di sudut kanan atas
            #Mengatur formatter untuk menghindari notasi ilmiah
            ax.yaxis.set_major_formatter(ScalarFormatter())  #Mengatur format sumbu Y
            ax.ticklabel_format(style='plain', axis='y')     #Menggunakan format biasa untuk label sumbu Y
        #Mengatur ulang layout agar tidak bertabrakan
        self.canvas.figure.tight_layout(pad=3.0)             #Menambahkan spasi antar plot
        #Render ulang canvas untuk menampilkan plot
        self.canvas.draw()                                   #Menggambar ulang canvas untuk memperbarui tampilan plot