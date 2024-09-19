from typing import Tuple                                            #Mengimpor Tuple dari typing untuk tipe kembalian
from scipy.fftpack import fft, rfft, irfft, fftfreq                 #Mengimpor fungsi Fourier Transform dari scipy.fftpack
import numpy as np                                                  #Mengimpor numpy sebagai np untuk manipulasi array
from src.frequency import Frequency                                 #Mengimpor kelas Frequency dari modul frequency
from src.frequency_filter import FilterFactory                      #Mengimpor FilterFactory dari modul frequency_filter
   
#Fast Fourier Transform (FFT)
class Transformer:                                                       #Mendefinisikan kelas Transformer
    def __init__(self,                                                   #Inisialisasi objek Transformer dengan parameter x, y, dan frequency
                 x: np.array,  
                 y: np.array,  
                 frequency: Frequency) -> None:  
        self.x = x                                                       #Menyimpan x, y, dan frequency sebagai atribut kelas
        self.y = y  
        self.freq = frequency   
   
    def get_fft_freq(self, sampling: int = 0.004) -> np.array:           #Fungsi untuk mendapatkan frekuensi sampel DFT
        """                                                              #Docstring
        Get Discrete Fourier Transform sample frequencies.  
        MuseS sampling is 250Hz   
        Parameters    
        ----------------
        sampling: int                                                    #Tipe parameter sampling sebagai integer
        Returns  
        ---------------
        np.array                                                         
            frequencies spectrum                                         #Mengembalikan spektrum frekuensi dalam TFD
            # TODO: check if spectrum is the correct word                #Periksa apakah 'spektrum' adalah istilah yang tepat
        """   
        return fftfreq(self.x.size, sampling)                            #Mengembalikan frekuensi sampel menggunakan fftfreq
   
    def get_fft(self) -> Tuple[np.array, np.array]:                      #Fungsi untuk mendapatkan Fourier Transform Diskrit dan spektrum amplitudo
        """                                                              #Docstring
        Get discrete Fourier Transform and amplitude spectrum.  
        Returns  
        -------------
        Tuple[np.array, np.array]     
            discrete Fourier Transform, amplitude spectrum               #Mengembalikan Transformasi Fourier Diskrit dan spektrum amplitudo
        """   
        y_fft = fft(self.y, self.x.size)                                 #Menghitung FFT dari array y dan ukurannya
        return y_fft, np.abs(y_fft)                                      #Mengembalikan hasil FFT dan nilai absolutnya sebagai spektrum amplitudo
    
    def get_rfft(self) -> np.array:                                      #Fungsi untuk mendapatkan DFT satu dimensi untuk input real
        """                                                              #Docstring
        Get one-dimensional discrete Fourier Transform for real input.   
        Returns   
        ---------------
        np.array   
        """   
        return rfft(self.y)                                              #Mengembalikan hasil RFFT dari array y
   
    def get_irfft(self, current: int = 50) -> np.array:                      #Fungsi untuk mendapatkan inversi dari Fourier Transform
        """                                                                  #Docstring
        Get inverted Fourier Transform. 
        Filter out frequencies for band. 
        Parameters 
        ---------------
        current: int 
        Returns 
        ---------------
        np.array 
        """ 
        freq_filter = FilterFactory(self.freq).get_filter(current)           #Mendapatkan filter frekuensi dari FilterFactory
        return irfft(freq_filter.band_pass(self.y, self.get_fft_freq()))     #Mengembalikan hasil irfft setelah penyaringan pita