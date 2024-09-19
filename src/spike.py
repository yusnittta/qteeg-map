from scipy.stats import zscore                              #Mengimpor fungsi zscore dari modul scipy.stats untuk menghitung skor-z
from typing import Dict, Tuple                              #Mengimpor tipe data Dict dan Tuple dari modul typing untuk pengetikan statis
         
import numpy as np                                          #Mengimpor numpy sebagai np untuk operasi matematika dan array
import pandas as pd                                         #Mengimpor pandas sebagai pd untuk manipulasi dan analisis data
from scipy.stats import median_absolute_deviation           #Mengimpor fungsi median_absolute_deviation dari modul scipy.stats untuk menghitung deviasi absolut median
from sklearn.cluster import KMeans                          #Mengimpor KMeans dari modul sklearn.cluster untuk algoritma clustering    
  
#Independent Component Analysis (ICA)
from sklearn.decomposition import FastICA                   #Mengimpor FastICA dari modul sklearn.decomposition untuk Independent Component Analysis
from sklearn.preprocessing import StandardScaler            #Mengimpor StandardScaler dari modul sklearn.preprocessing untuk normalisasi data
      
MIN_TIME_BETWEEN_SPIKES = 0.03                              #Menentukan waktu minimum antara spike dalam detik (30ms)
SEARCH_PERIOD = 0.02                                        #Menentukan periode pencarian dalam detik (20ms)
SAMPLING = 256                                              #Menentukan frekuensi sampling dalam Hz (1 sampel setiap ~4ms)
SEARCH_SAMPLES = int(SEARCH_PERIOD * SAMPLING)              #Menghitung jumlah sampel dalam periode pencarian berdasarkan periode pencarian dan frekuensi sampling
WAVE_SIZE = int(MIN_TIME_BETWEEN_SPIKES * SAMPLING)         #Menghitung ukuran gelombang dalam jumlah sampel berdasarkan waktu minimum antara spike dan frekuensi sampling
  
#Implementasi FastICA dan KMeans Algorithm
class Spike:                                                #Mendefinisikan kelas Spike untuk menangani data spike
    def __init__(self, name: str):                          #Konstruktor untuk inisialisasi objek Spike dengan nama
        self.name = name                                    #Menyimpan nama spike
        self.spike_threshold: float = 0.                    #Menyimpan ambang batas spike, diinisialisasi dengan 0
        self.noise_level: float = 0.                        #Menyimpan tingkat kebisingan, diinisialisasi dengan 0
        self.data: pd.Series = None                         #Menyimpan data spike dalam format pandas Series, diinisialisasi dengan None
        self.spikes: np.array = None                        #Menyimpan array spike, diinisialisasi dengan None
        self.sorted_spikes: np.array = None                 #Menyimpan array spike yang telah diurutkan, diinisialisasi dengan None
        self.features: np.array = None                      #Menyimpan fitur dari spike, diinisialisasi dengan None
        self.clusters: np.array = None                      #Menyimpan hasil clustering spike, diinisialisasi dengan None
        self.scaler = StandardScaler()                      #Menginisialisasi scaler untuk normalisasi data
        self.ica = FastICA(n_components=2)                  #Menginisialisasi FastICA untuk Independent Component Analysis dengan 2 komponen
        self.kmeans = KMeans(n_clusters=3)                  #Menginisialisasi KMeans untuk clustering dengan 3 klaster
      
    def set_data(self, data: pd.Series) -> None:            #Mendefinisikan metode set_data untuk mengatur data baru
        """                                                 #Docstring
        Set new data.    
        Parameters   
        --------------- 
        data: pandas.Series                                    
            Data series with readings from single electrode.    
        Returns   
        ---------------
        None                                                #Tidak mengembalikan nilai
        """    
        self.data = data                                    #Menetapkan data baru ke atribut self.data
        self.spike_threshold: float = 0.                    #Mengatur ambang batas spike ke 0
        self.noise_level: float = 0.                        #Mengatur tingkat kebisingan ke 0
        self.spikes: np.array = None                        #Mengatur array spike menjadi None
        self.sorted_spikes: np.array = None                 #Mengatur array spike yang telah diurutkan menjadi None
        self.features: np.array = None                      #Mengatur array fitur menjadi None
       
    def _estimate_noise_level(self) -> None:                                            #Mendefinisikan metode _estimate_noise_level untuk memperkirakan tingkat kebisingan dan menentukan ambang batas spike
        """                                                                             #Docstring
        Estimate noise level and determine spike threshold.    
        Tingkat kebisingan diperoleh dengan menggunakan deviasi absolut median.
        Ambang batas spike sama dengan tingkat kebisingan dikalikan dengan pengali ambang batas.
        Returns   
        ---------------
        None                                                                            #Tidak mengembalikan nilai
        """    
        self.noise_level = median_absolute_deviation(self.data)                         #Menghitung tingkat kebisingan menggunakan deviasi absolut median dari data
        threshold_mul = -5 if self.noise_level <= (max(self.data) / 5) else -2          #Menentukan pengali ambang batas berdasarkan tingkat kebisingan, jika tingkat kebisingan kurang dari atau sama dengan 1/5 dari nilai maksimum data gunakan -5, jika tidak, gunakan -2
        self.spike_threshold = self.noise_level * threshold_mul                         #Menghitung ambang batas spike sebagai hasil kali tingkat kebisingan dan pengali ambang batas
           
    def _find_potential_spikes(self) -> np.array:                                       #Mendefinisikan metode _find_potential_spikes yang mengembalikan array numpy
        """                                                                             #Docstring
        Find potential spikes.   
        Langkah pertama adalah mengekstrak hanya rekaman yang melebihi ambang batas.
        Langkah kedua adalah menghapus spike potensial yang terlalu dekat
        satu sama lain.
        Returns  
        ---------------
        numpy.array     
            Numpy array with indexes of potential spikes.                               #Mengembalikan array numpy yang berisi indeks-indeks spike potensial
        """      
        data = self.data                                                        #Menyimpan data dari atribut self.data ke variabel lokal data
        potential_spikes = np.diff(                                             #Menentukan spike potensial dengan memeriksa perubahan melewati ambang ba
            ((data <= self.spike_threshold) |                                   #Mengevaluasi apakah nilai data lebih kecil atau sama dengan ambang batas spike atau lebih besar atau sama dengan ambang batas negatif
             (data >= -self.spike_threshold)).astype(int) > 0).nonzero()[0]  
        potential_spikes = potential_spikes[                                    #Menyaring spike potensial yang berada dalam batas ukuran gelombang
            (potential_spikes > WAVE_SIZE) &                                    #Memastikan bahwa spike potensial berada lebih dari ukuran gelombang dari awal data
            (potential_spikes < (len(self.data) - WAVE_SIZE))]                  #Memastikan bahwa spike potensial berada lebih dari ukuran gelombang dari akhir data
           
        def _insert_potential_spike():                                                  #Mendefinisikan fungsi lokal _insert_potential_spike untuk memeriksa jarak antar spike potensial untuk memastikan jarak minimal
            return np.insert(np.diff(potential_spikes) >= WAVE_SIZE, 0, True)           #Mengembalikan array dengan perbedaan antar elemen potential_spikes yang memadai jarak minimal WAVE_SIZE, ditambah True di awal
        min_spacing = _insert_potential_spike()                                         #Memanggil fungsi _insert_potential_spike untuk menentukan jarak minimal
        while not np.all(min_spacing):                                                  #Mengulangi proses hingga semua jarak antar spike memadai
            potential_spikes = potential_spikes[min_spacing]                            #Menyaring spike potensial berdasarkan jarak minimal
            min_spacing = _insert_potential_spike()                                     #Memanggil kembali fungsi _insert_potential_spike untuk memeriksa jarak baru
    
        return potential_spikes                                                         #Mengembalikan array dengan indeks spike potensial
  
#Deteksi Spike   
    def detect(self) -> pd.Series:                          #Mendefinisikan fungsi untuk mendeteksi spike untuk seri data dan menyimpan indeks spike
        """                                                 #Docstring
        Detect spikes for data series.   
        Save spike indexes.   
        Returns  
        ---------------
        pandas.Series  
            Pandas series with timestamps of spikes         #Mengembalikan seri pandas dengan timestamp dari spike
        """   
        self._estimate_noise_level()                                         #Menghitung level noise dan menentukan ambang batas spike
        self.spikes = np.array([                                             #Menentukan lokasi spike dengan mencari nilai minimum dalam jendela pencarian untuk setiap spike potensial
            index + np.argmin(self.data[index:index + SEARCH_SAMPLES])       #Untuk setiap indeks spike potensial yang ditemukan
            for index in self._find_potential_spikes()])                     #Menambahkan indeks minimum dalam jendela pencarian ke indeks spike potensial
        data = self.data * np.nan                                            #Membuat salinan data dengan nilai NaN
        data.iloc[self.spikes] = self.spike_threshold                        #Menetapkan nilai ambang batas spike pada posisi spike yang ditemukan
        return data.dropna()                                                 #Mengembalikan seri data dengan nilai NaN dihapus
  
#Pengurutan Spike
    def sort(self) -> Tuple[np.array, np.array]:                             #Mendefinisikan fungsi untuk melakukan sorting spike
        """                                                                  #Docstring
        Spike sorting.  
        Returns  
        ---------------
        Tuple[numpy.array, numpy.array]    
            Elemen pertama adalah array dengan data dari semua spike
            Elemen kedua adalah array dengan nilai rata-rata dari spike
        """     
        if self.spikes is None:                                              #Jika spikes belum terdeteksi, panggil fungsi detect untuk mendeteksi spikes
            _ = self.detect()      
        waves = []                                                           #Daftar untuk menyimpan gelombang (waves) dari setiap spike
        for index in self.spikes:                                            #Untuk setiap indeks spike
            waves.append(self.data.iloc[                                     #Ambil data dari sekitar indeks spike dan simpan dalam waves
                         (index - WAVE_SIZE):(index + WAVE_SIZE)])           #Dimulai dari (index - WAVE_SIZE) hingga (index + WAVE_SIZE)
        if len(waves):                                                       #Jika ada gelombang yang terdeteksi
            self.sorted_spikes = np.stack(waves)                             #Gabungkan semua gelombang menjadi array numpy dan simpan di sorted_spikes
            return self.sorted_spikes, self.sorted_spikes.mean(axis=0)       #Kembalikan array gelombang dan nilai rata-rata gelombang
        return np.array([]), np.array([])                                    #Jika tidak ada gelombang, kembalikan array kosong untuk keduanya
 
#Ekstraksi Fitur
    def extract_features(self) -> np.array:                                  #Mendefinisikan metode extract_features yang mengembalikan numpy.array
        """                                                                  #Docstring
        Extract features using FastICA.   
        Returns                                     
        ---------------  
        numpy.array                                                          #Mengembalikan array dengan fitur yang diekstrak
        """    
        if self.sorted_spikes is None:                                       #Jika spikes belum terurut, panggil fungsi sort untuk mengurutkan spike
            _ = self.sort()   
        scaled_spikes = self.scaler.fit_transform(self.sorted_spikes)        #Skalakan spike yang telah diurutkan menggunakan StandardScaler
        self.features = self.ica.fit_transform(scaled_spikes)                #Ekstrak fitur menggunakan FastICA dari spike yang telah diskalakan
        return self.features                                                 #Kembalikan array fitur yang diekstrak
   
#Pengelompokan Spike
    def cluster(self) -> np.array:                                           #Mendefinisikan metode cluster yang mengembalikan numpy.array
        """                                                                  #Docstring
        Return clusters.     
        Returns   
        ---------------
        numpy.array  
            Array with clusters.                                             #Mengembalikan array dengan fitur yang dikelompokkan
        """  
        if self.features is None:                                            #Jika fitur belum diekstrak, panggil fungsi extract_features untuk mengekstrak fitur
            _ = self.extract_features()      
        self.clusters = self.kmeans.fit_predict(self.features)               #Terapkan KMeans clustering pada fitur dan simpan hasil klaster
        return self.clusters, self.features                                  #Kembalikan array klaster dan fitur yang digunakan