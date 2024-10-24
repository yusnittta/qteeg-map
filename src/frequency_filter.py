import numpy as np                     #Mengimpor pustaka numpy untuk operasi numerik, khususnya array
from src.frequency import Frequency    #Mengimpor kelas Frequency dari modul src.frequency

#Implementasi Filtering
class FrequencyFilter:                      #Mendefinisikan kelas FrequencyFilter
    def __init__(self, current: int = 50):  #Menginisialisasi kelas dengan nilai default 'current' sebesar 50
        self.current = current              #Menyimpan nilai 'current' sebagai variabel instansi yang dapat digunakan di seluruh metode dalam kelas

#Implementasi Band-Pass Filtering
    def band_pass(self, signal: np.array, fft_sample: np.array) -> np.array: #Fungsi untuk menerapkan filter band-pass
        """                         #Docstring
        Band-pass Filter.
        Parameters                  
        -----------
        signal: np.array            #Array numpy yang mewakili sinyal dalam domain waktu
        fft_sample: np.array        #Array numpy yang berisi hasil transformasi Fourier (Fast Fourier Transform) dari sinyal
        Returns                     
        -----------
        np.array                    #Array numpy yang berisi hasil dari operasi atau transformasi
        """      
        signal = signal.copy()              #Membuat salinan dari array sinyal agar tidak memodifikasi array aslinya
        signal[                             #Menerapkan filter band-pass dengan menetapkan nilai sinyal ke 0 jika frekuensi berada di luar rentang yang ditentukan oleh atribut `low` dan `high` atau sama dengan frekuensi `current`
            (fft_sample < self.low)         #Memilih frekuensi di bawah batas bawah
            | (fft_sample >= self.high)     #Memilih frekuensi di atas atau sama dengan batas atas
            | (fft_sample == self.current)  #Memilih frekuensi yang sama dengan `current'
        ] = 0                               #Set frekuensi terpilih menjadi 0
        return signal                       #Mengembalikan sinyal yang sudah difilter

#Implementasi Low-pass Filtering
    def low_pass(self, signal: np.array, fft_sample: np.array) -> np.array: #Fungsi untuk menerapkan filter low-pass
        """                         #Docstring
        Low-pass Filter.
        Parameters                  
        -----------
        signal: np.array            #Array numpy yang mewakili sinyal dalam domain waktu
        fft_sample: np.array        #Array numpy yang berisi hasil transformasi Fourier (Fast Fourier Transform) dari sinyal
        Returns                     #Hasil akhir dari pemanggil
        -----------
        np.array                    #Array numpy yang berisi hasil dari operasi atau transformasi
        """       
        signal = signal.copy()                  #Membuat salinan dari array sinyal agar tidak memodifikasi array aslinya
        signal[(fft_sample >= self.low)] = 0    #Menerapkan filter low-pass dengan menetapkan nilai sinyal ke 0 jika frekuensi lebih tinggi atau sama dengan batas frekuensi `low`
        return signal                           #Mengembalikan sinyal yang telah difilter

#Implementasi High-pass Filtering
    def high_pass(self, signal: np.array, fft_sample: np.array) -> np.array: #Fungsi untuk menerapkan filter high-pass
        """                         #Docstring
        High-pass Filter.
        Parameters                  
        -----------
        signal: np.array            #Array numpy yang mewakili sinyal dalam domain waktu
        fft_sample: np.array        #Array numpy yang berisi hasil transformasi Fourier (Fast Fourier Transform) dari sinyal
        Returns                     
        -----------
        np.array                    #Array numpy yang berisi hasil dari operasi atau transformasi
        """         
        signal = signal.copy()                  #Membuat salinan dari array sinyal agar tidak memodifikasi array aslinya
        signal[(fft_sample <= self.high)] = 0   #Menerapkan filter high-pass dengan menetapkan nilai sinyal ke 0 jika frekuensi lebih rendah atau sama dengan batas frekuensi `high`
        return signal                           #Mengembalikan sinyal yang telah difilter

#Pemisahan Sub-band Frekuensi

#Frekuensi Gamma (20-40 Hz)
class GammaFilter(FrequencyFilter):       #Mendefinisikan kelas GammaFilter yang mewarisi dari FrequencyFilter
    def __init__(self, current: int):     #Konstruktor untuk kelas GammaFilter yang menerima parameter integer 'current'
        super().__init__(current)         #Memanggil konstruktor kelas induk (FrequencyFilter) dengan parameter 'current'
        self.low = 20                     #Mengatur atribut 'low' dengan nilai 20, menentukan batas bawah filter
        self.high = 40                    #Mengatur atribut 'high' dengan nilai 40, menentukan batas atas filter

#Frekuensi Beta (14-30 Hz)
class BetaFilter(FrequencyFilter):        #Mendefinisikan kelas BetaFilter yang mewarisi dari FrequencyFilter
    def __init__(self, current: int):     #Konstruktor untuk kelas BetaFilter yang menerima parameter integer 'current'
        super().__init__(current)         #Memanggil konstruktor kelas induk (FrequencyFilter) dengan parameter 'current'
        self.low = 14                     #Mengatur atribut 'low' dengan nilai 14, menentukan batas bawah filter
        self.high = 30                    #Mengatur atribut 'high' dengan nilai 30, menentukan batas atas filter

#Frekuensi Alpha (8-13 Hz)
class AlphaFilter(FrequencyFilter):       #Mendefinisikan kelas AlphaFilter yang mewarisi dari FrequencyFilter
    def __init__(self, current: int):     #Konstruktor untuk kelas AlphaFilter yang menerima parameter integer 'current'
        super().__init__(current)         #Memanggil konstruktor kelas induk (FrequencyFilter) dengan parameter 'current'
        self.low = 8                      #Mengatur atribut 'low' dengan nilai 8, menentukan batas bawah filter
        self.high = 13                    #Mengatur atribut 'high' dengan nilai 13, menentukan batas atas filter

#Frekuensi Tetha (4-8 Hz)
class ThetaFilter(FrequencyFilter):       #Mendefinisikan kelas TethaFilter yang mewarisi dari FrequencyFilter
    def __init__(self, current: int):     #Konstruktor untuk kelas TethaFilter yang menerima parameter integer 'current'
        super().__init__(current)         #Memanggil konstruktor kelas induk (FrequencyFilter) dengan parameter 'current'
        self.low = 4                      #Mengatur atribut 'low' dengan nilai 4, menentukan batas bawah filter
        self.high = 8                     #Mengatur atribut 'high' dengan nilai 8, menentukan batas atas filter

#Frekuensi Delta (0-4 Hz)
class DeltaFilter(FrequencyFilter):       #Mendefinisikan kelas TethaFilter yang mewarisi dari FrequencyFilter
    def __init__(self, current: int):     #Konstruktor untuk kelas TethaFilter yang menerima parameter integer 'current'
        super().__init__(current)         #Memanggil konstruktor kelas induk (FrequencyFilter) dengan parameter 'current'
        self.low = 0                      #Mengatur atribut 'low' dengan nilai 0, menentukan batas bawah filter
        self.high = 4                     #Mengatur atribut 'high' dengan nilai 4, menentukan batas atas filter

#Pembuat Filter
class FilterFactory:                                         #Mendefinisikan kelas FilterFactory yang akan digunakan untuk membuat filter berdasarkan frekuensi
    def __init__(self, frequency: Frequency) -> None:        #Konstruktor untuk FilterFactory yang menerima parameter 'frequency' bertipe Frequency
        self.frequency = frequency                           #Menyimpan parameter 'frequency' dalam atribut kelas 'frequency'
    def get_filter(self, current: int) -> FrequencyFilter:   #Metode untuk mendapatkan objek FrequencyFilter berdasarkan nilai 'current'
        """                                                  #Docstring
        Return FrequencyFilter child for band.               #Mengembalikan objek turunan dari FrequencyFilter berdasarkan frekuensi
        Parameters                                           
        -----------
        current: int                                         #Parameter 'current' akan diteruskan ke konstruktor filter
        Returns                                              
        -----------
        FrequencyFilter                                      #Mengembalikan objek dari tipe FrequencyFilter
        """       
        if self.frequency == Frequency.GAMMA:                #Jika frekuensi yang disimpan adalah GAMMA
            return GammaFilter(current)                      #Kembalikan objek GammaFilter yang diinisialisasi dengan 'current'
        elif self.frequency == Frequency.BETA:               #Jika frekuensi yang disimpan adalah BETA
            return BetaFilter(current)                       #Kembalikan objek BetaFilter yang diinisialisasi dengan 'current'
        elif self.frequency == Frequency.ALPHA:              #Jika frekuensi yang disimpan adalah ALPHA
            return AlphaFilter(current)                      #Kembalikan objek AlphaFilter yang diinisialisasi dengan 'current'
        elif self.frequency == Frequency.THETA:              #Jika frekuensi yang disimpan adalah TETHA
            return ThetaFilter(current)                      #Kembalikan objek TethaFilter yang diinisialisasi dengan 'current'
        elif self.frequency == Frequency.DELTA:              #Jika frekuensi yang disimpan adalah DELTA
            return DeltaFilter(current)                      #Kembalikan objek DeltaFilter yang diinisialisasi dengan 'current'