# QtEEG-MAP

Aplikasi sederhana untuk memvisualisasikan dan menganalisis rekaman EEG dari perangkat pemantauan otak 16 kanal elektroda.

Aplikasi ini memungkinkan Anda untuk merekam dan memvisualisasikan data raw EEG berformat CSV, EDF, BDF, MAT, dan TXT dari perangkat pemantauan otak secara real-time.

#### Fitur dalam aplikasi:
1. Pra-pemrosesan menggunakan band-pass filtering
2. Transformasi menggunakan Fast Fourier Transform (FFT)
3. Pemisahan sub-band frekuensi Gamma, Alpha, Beta, Theta, dan Delta (dekomposisi)
4. Ploting data gulir 1D pada 16 kanal elektroda (FP1, FP2, F3, F4, C3, C4, P3, P4, O1, O2, F7, F8, T3, T4, T5, T6)
5. Visualisasi data gulir 1D pada tegangan, domain waktu, frekuensi tunggal, dan frekuensi ganda
6. Deteksi dan pengurutan spike
7. Ekstraksi fitur menggunakan Fast Independent Component Analysis (FastICA) dan Principal Component Analysis (PCA)
8. Klastering dengan Algoritma KMeans
9. Merekam dan memvisualisasikan data raw EEG berformat CSV, EDF, BDF, MAT, dan TXT
10. Ploting peta topografi kulit kepala 2D (topoplot)
11. Ploting Power Spectral Density (PSD) dengan Metode Welch

### Instalasi
Penggunaan paket [Poetry](https://python-poetry.org).<br/>
Untuk membuat ulang proyek, gunakan perintah:
```bash
poetry install
```

##### Menggunakan File QRC
Untuk menggunakan file qrc dalam aplikasi perlu dikompilasi ke dalam Python terlebih dahulu.
```bash
pyrcc5 resources.qrc -o resources.py
```

### Penghargaan
- Sumber proyek open source untuk melakukan perubahan, eksperimen, dan pengembangan: https://github.com/bartlomiej-chybowski/qteeg
- Tim penyedia dataset (direkam menggunakan perangkat Contec KT88)

### Kontak
Jika ada masalah atau izin penggunaan dataset dalam assets kami di luar fork dalam QtEEG-Map, harap hubungi kami. Jika ada masalah, mohon untuk melaporkannya.