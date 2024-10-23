import sys                                  #Mengimpor modul sistem untuk menangani argumen dan eksekusi aplikasi
from PyQt5 import QtWidgets, QtCore         #Mengimpor modul PyQt5 untuk widget dan fungsi inti Qt
from PyQt5.QtGui import QPalette, QColor    #Mengimpor modul untuk menangani palet warna dan warna
from src.MainWindow import MainWindow       #Mengimpor kelas MainWindow dari direktori sumber (src)

def prepare_palette() -> QPalette:          #Mendefinisikan fungsi untuk membuat dan mengembalikan palet warna (QPalette) yang telah disesuaikan
    """
    Dark colors palette.
    Returns
    -------
    QPalette
    """
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 60, 127))                   #Mengatur warna latar belakang jendela utama
    palette.setColor(QPalette.Base, QColor(169, 204, 227))                  #Mengatur warna latar belakang untuk kolom teks/input
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))            #Warna alternatif untuk elemen seperti item dalam daftar
    palette.setColor(QPalette.ToolTipBase, QtCore.Qt.white)                 #Warna dasar latar belakang tooltip
    palette.setColor(QPalette.Text, QtCore.Qt.black)                        #Warna teks di dalam kolom input
    palette.setColor(QPalette.WindowText, QtCore.Qt.white)                  #Warna teks untuk judul jendela dan label
    palette.setColor(QPalette.Button, QColor(40, 116, 166))                 #Warna default untuk tombol
    palette.setColor(QPalette.ButtonText, QtCore.Qt.white)                  #Warna teks di tombol
    palette.setColor(QPalette.BrightText, QtCore.Qt.red)                    #Warna teks yang sangat terang atau disorot
    palette.setColor(QPalette.Highlight, QColor(47, 101, 202))              #Warna latar belakang item yang dipilih (misalnya dalam daftar)
    palette.setColor(QPalette.HighlightedText, QtCore.Qt.white)             #Warna teks untuk item yang dipilih
    palette.setColor(QPalette.Disabled, QPalette.Base, QColor(15, 15, 15))  #Warna latar belakang untuk elemen yang dinonaktifkan
    return palette                                                          #Mengembalikan palet yang telah disiapkan

def main():
    app = QtWidgets.QApplication(sys.argv)  #Membuat aplikasi Qt
    app.setPalette(prepare_palette())       #Menerapkan palet warna yang telah disiapkan
    window = MainWindow()                   #Membuat jendela utama
    window.show()                           #Menampilkan jendela utama
    app.exec_()                             #Memulai event loop aplikasi

if __name__ == '__main__':      #Memeriksa apakah file ini dijalankan secara langsung, bukan diimpor sebagai modul
    main()                      #Titik masuk aplikasi