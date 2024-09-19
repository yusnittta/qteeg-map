# QtEEG-Map

Aplikasi sederhana untuk memvisualisasikan dan menganalisis rekaman EEG dari perangkat pemantauan otak.

<!--![QtEEG](assets/QtEEG.png) ![Spike detection](assets/detection.png)-->

Aplikasi ini memungkinkan Anda untuk merekam dan memvisualisasikan data raw EEG berformat CSV, EDF, BDF, dan MAT dari perangkat pemantauan otak secara real-time

#### Fitur dalam aplikasi:
1. Pra-pemrosesan menggunakan band-pass filtering
2. Dekomposisi menggunakan Fast Fourier Transform
3. Pemisahan sub-band frekuensi, yaitu Gamma, Alpha, Beta, Theta, dan Delta
4. Pengelompokan menggunakan Algoritma K-Means
5. Ploting data gulir 1D pada kanal elektroda TP9, TP10, AF7, dan AF8
6. Visualisasi pada tegangan, domain waktu, frekuensi tunggal, dan frekuensi ganda
7. Merekam pembacaan perangkat
8. Menampilkan pembacaan perangkat secara real-time
9. Deteksi, pengurutan, ekstraksi fitur, dan pengelompokan lonjakan sinyal
10. Stimuli generator
11. Transformasi menggunakan Fast Independent Component Analysis
12. Merekam dan memvisualisasikan data raw EEG berformat CSV, EDF, BDF, dan MAT

### Instalasi
Penggunaan paket [Poetry](https://python-poetry.org).<br/>
Untuk membuat ulang proyek, gunakan perintah:
```bash
poetry install
```

### Masalah Umum
https://github.com/alexandrebarachant/muse-lsl/blob/master/README.md#common-issues


##### Menggunakan File QRC
Untuk menggunakan file qrc dalam aplikasi perlu dikompilasi ke dalam Python terlebih dahulu.
```bash
pyrcc5 resources.qrc -o resources.py
```

### Penghargaan
- Menghubungkan, merekam, dan streaming data dari Muse S dilakukan menggunakan
https://github.com/alexandrebarachant/muse-lsl
- Analisis lonjakan sinyal menggunakan https://github.com/multichannelsystems/McsPyDataTools/blob/master/McsPyDataTools/docs/McsPy-Tutorial_DataAnalysis.ipynb
- Sumper inspirasi pengembangan perangkat lunak pengolahan sinyal EEG https://github.com/bartlomiej-chybowski/qteeg?tab=readme-ov-file

### Kontak
Jika ada masalah, harap laporkan masalah tersebut 
