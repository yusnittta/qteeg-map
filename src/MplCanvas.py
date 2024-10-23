import matplotlib.pyplot as plt                                                  #Mengimpor matplotlib.pyplot sebagai plt untuk membuat grafik
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg                 #Mengimpor FigureCanvasQTAgg dari matplotlib.backends.backend_qt5agg untuk menggunakan Matplotlib di dalam aplikasi berbasis Qt
plt.style.use('dark_background')                                                 #Mengatur gaya visual plot menjadi latar belakang gelap dengan plt.style.use()
                                                                                
class MplCanvas(FigureCanvasQTAgg):                                              #Mendefinisikan kelas MplCanvas yang merupakan turunan dari FigureCanvasQTAgg untuk menampilkan grafik Matplotlib pada widget Qt
    def __init__(self, parent=None, width=10, height=6, dpi=100):                #Fungsi __init__ adalah konstruktor yang dijalankan saat objek kelas dibuat
        self.figure, self.axes = plt.subplots(nrows=4,                           #Membuat figure dan axes dengan subplots berukuran 2x2
                                              ncols=4,        
                                              figsize=(width, height),           #Ukuran canvas
                                              dpi=dpi,                           #Resolusi gambar
                                              tight_layout=True)                 #Menghindari overlap antar plot
        super(MplCanvas, self).__init__(self.figure)                             #Memanggil konstruktor kelas induk (FigureCanvasQTAgg) dan meneruskan figure yang telah dibuat