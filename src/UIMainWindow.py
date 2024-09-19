import abc                                                                  #Mengimpor modul abc untuk mendukung kelas abstrak dan metode dalam Python
import configparser                                                         #Mengimpor modul configparser untuk membaca dan menulis file konfigurasi
from typing import Optional, Dict                                           #Mengimpor Optional dan Dict dari modul typing untuk tipe data yang lebih fleksibel
import pyqtgraph as pg                                                      #Mengimpor pyqtgraph dengan alias pg untuk grafik dan visualisasi data
from PyQt5 import QtWidgets, uic                                            #Mengimpor modul QtWidgets dan uic dari PyQt5 untuk antarmuka pengguna grafis
from PyQt5.QtCore import QThread                                            #Mengimpor QThread dari QtCore untuk threading dalam aplikasi Qt
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QLabel    #Mengimpor kelas widget khusus dari PyQt5
import ui.resources  # noqa: F401                                           #Mengimpor modul resources dari direktori ui, menandakan tidak ada masalah dengan impor yang tidak digunakan
from src.MplWindow import MplWindow                                         #Mengimpor kelas MplWindow dari modul MplWindow dalam direktori src
from src.about import AboutWindow                                           #Mengimpor kelas AboutWindow dari modul about dalam direktori src
from src.frequency import Frequency                                         #Mengimpor kelas Frequency dari modul frequency dalam direktori src
from src.help import HelpWindow                                             #Mengimpor kelas HelpWindow dari modul help dalam direktori src
from src.settings import SettingsWindow                                     #Mengimpor kelas SettingsWindow dari modul settings dalam direktori src
from src.stream_worker import StreamWorker                                  #Mengimpor kelas StreamWorker dari modul stream_worker dalam direktori src
 
class UIMainWindow(QtWidgets.QMainWindow):                                  #Mendefinisikan kelas UIMainWindow yang mewarisi dari QMainWindow
    
    def __init__(self, *args, **kwargs):                                    #Inisialisasi konstruktor untuk UIMainWindow
        super().__init__(*args, **kwargs)                                   #Memanggil konstruktor dari kelas induk (QMainWindow)
        uic.loadUi("ui/mainwindow.ui", self)                                #Memuat antarmuka pengguna dari file UI dan menghubungkannya dengan instance ini
        self.config = configparser.ConfigParser()                           #Membuat parser konfigurasi untuk membaca file konfigurasi
        self.colours: Dict[str, str] = {}                                   #Mendeklarasikan dictionary kosong untuk menyimpan warna
        self._read_settings()                                               #Memanggil metode untuk membaca pengaturan dari file konfigurasi
        self.current_file: str = ""                                         #Mendeklarasikan string kosong untuk menyimpan nama file saat ini
        self.electrodes_group: QButtonGroup = QButtonGroup(self)            #Membuat grup tombol untuk elektroda
        self.frequency_group: QButtonGroup = QButtonGroup(self)             #Membuat grup tombol untuk frekuensi
        self.graphicsLayout: pg.GraphicsLayout = pg.GraphicsLayout()        #Membuat layout grafik untuk menampilkan grafik
        self.main_series: str = 'TP9'                                       #Mendeklarasikan string untuk menyimpan seri utama
        self.main_band: Frequency = None                                    #Mendeklarasikan variabel untuk menyimpan objek Frequency, diinisialisasi sebagai None
        self.message: QLabel = QLabel()                                     #Membuat QLabel untuk menampilkan pesan status
        self.single_frequency: bool = False                                 #Mendeklarasikan boolean untuk menentukan apakah hanya satu frekuensi yang digunakan
        self.spike_detection_window = MplWindow(self)                       #Membuat instance jendela deteksi spike menggunakan MplWindow
        self.spike_sorting_window = MplWindow(self)                         #Membuat instance jendela sorting spike menggunakan MplWindow
        self.feature_extraction_window = MplWindow(self)                    #Membuat instance jendela ekstraksi fitur menggunakan MplWindow
        self.clustering_window = MplWindow(self)                            #Membuat instance jendela clustering menggunakan MplWindow
        self.wave_clusters_window = MplWindow(self)                         #Membuat instance jendela gelombang terklaster menggunakan MplWindow
        self.stream_thread: QThread = QThread()                             #Membuat thread untuk menangani streaming data
        self.stream_worker: StreamWorker = StreamWorker()                   #Membuat instance StreamWorker untuk menangani pemrosesan data streaming
        self._connect_menu()                                                #Memanggil metode untuk menghubungkan item menu dengan fungsinya
        self.graphicsView.setAntialiasing(True)                             #Mengaktifkan antialiasing untuk tampilan grafik
        self.graphicsView.setBackground('k')                                #Mengatur latar belakang tampilan grafik menjadi hitam
        self.statusbar.addPermanentWidget(self.message)                     #Menambahkan widget pesan status ke status bar
        self.statusbar.showMessage("Siap")                                  #Menampilkan pesan "Siap" di status bar
  
    @abc.abstractmethod  
    def _load_file(self):                                                   #Mendefinisikan metode abstrak yang bertanggung jawab untuk memuat file
        pass   
   
    @abc.abstractmethod   
    def _toggle_frequency(self, disabled: Optional[bool] = True,            #Mendefinisikan metode abstrak untuk menonaktifkan atau mengaktifkan frekuensi
                          exclusive: Optional[bool] = False) -> None:       #Parameter `disabled` untuk menentukan apakah frekuensi dinonaktifkan, dan `exclusive` untuk menentukan apakah hanya satu frekuensi yang eksklusif
        pass  
  
    @abc.abstractmethod  
    def _checkbox_state(self, checkbox: QCheckBox, label: str) -> None:     #Mendefinisikan metode abstrak untuk mengatur status checkbox berdasarkan label
        pass  
  
    @abc.abstractmethod  
    def _spike_detection_window(self) -> None:                              #Mendefinisikan metode abstrak untuk menampilkan jendela deteksi spike
        pass  
  
    @abc.abstractmethod  
    def _spike_sorting_window(self) -> None:                                #Mendefinisikan metode abstrak untuk menampilkan jendela sorting spike
        pass  
  
    @abc.abstractmethod  
    def _clustering_window(self) -> None:                                   #Mendefinisikan metode abstrak untuk menampilkan jendela clustering
        pass  
  
    @abc.abstractmethod   
    def _wave_clusters_window(self) -> None:                                #Mendefinisikan metode abstrak untuk menampilkan jendela gelombang terklaster
        pass   
   
    @abc.abstractmethod  
    def _feature_extraction_window(self) -> None:                           #Mendefinisikan metode abstrak untuk menampilkan jendela ekstraksi fitur
        pass   
  
    def _report_progress(self, message: str) -> None:                       #Mendefinisikan metode untuk melaporkan pesan ke status bar
        """                                                                 #Docstring
        Slot to report message.  
        Parameters  
        ---------------
        message: str                                                        #Parameter `message` bertipe string yang berisi pesan yang akan dilaporkan
        Returns  
        ---------------
        None                                                                #Tidak mengembalikan nilai
        """  
        self.statusbar.showMessage(message)                                 #Menampilkan pesan di status bar aplikasi
  
    def _close_stream(self) -> None:                                        #Mendefinisikan metode untuk menutup stream dari perangkat
        """                                                                 #Docstring
        Close stream from device. 
        Returns 
        ---------------
        None                                                                #Tidak mengembalikan nilai
        """ 
        self.stream_worker.finish()                                         #Menghentikan proses di `stream_worker`
        self.stream_thread.quit()                                           #Menghentikan thread dengan mengirimkan sinyal `quit`
        self.stream_thread.wait()                                           #Menunggu hingga thread selesai menjalankan tugasnya
        self._report_progress('Disconnected')                               #Melaporkan status 'Disconnected' di status bar
        self.actionStream.setDisabled(False)                                #Mengaktifkan kembali aksi 'Stream' di antarmuka pengguna
        self.actionDisconnect.setDisabled(True)                             #Menonaktifkan aksi 'Disconnect' di antarmuka pengguna
  
    def _stream_thread(self) -> None:                                               #Mendefinisikan metode untuk membuat thread streaming
        """                                                                         #Docstring
        Create thread for streaming functionality. 
        Returns 
        ---------------
        None                                                                        #Tidak mengembalikan nilai
        """   
        self.stream_thread = QThread()                                              #Membuat instance dari `QThread` untuk menangani streaming
        self.stream_worker = StreamWorker()                                         #Membuat instance dari `StreamWorker` yang akan dijalankan di dalam thread                      
        self.stream_worker.moveToThread(self.stream_thread)                         #Memindahkan `stream_worker` ke dalam `stream_thread`
        self.stream_thread.started.connect(self.stream_worker.run)                  #Menghubungkan sinyal `started` dari thread ke metode `run` dari `stream_worker'
        self.stream_worker.finished.connect(self.stream_thread.quit)                #Menghubungkan sinyal `finished` dari `stream_worker` untuk menghentikan thread
        self.stream_worker.finished.connect(self.stream_worker.deleteLater)         #Menghubungkan sinyal `finished` untuk menghapus `stream_worker` setelah selesai
        self.stream_thread.finished.connect(self.stream_thread.deleteLater)         #Menghubungkan sinyal `finished` untuk menghapus `stream_thread` setelah selesai
        self.stream_worker.progress.connect(self._report_progress)                  #Menghubungkan sinyal `progress` dari `stream_worker` ke metode `_report_progress`
        self.stream_thread.start()                                                  #Memulai thread streaming
        self.actionStream.setDisabled(True)                                         #Menonaktifkan aksi 'Stream' di antarmuka pengguna saat streaming dimulai
        self.actionDisconnect.setDisabled(False)                                    #Mengaktifkan aksi 'Disconnect' di antarmuka pengguna saat streaming dimulai
        self.stream_thread.finished.connect(                                        #Menghubungkan sinyal `finished` dari thread untuk melaporkan status 'Disconnected'
            lambda: self._report_progress('Disconnected')                           #Menggunakan lambda untuk melaporkan status 'Disconnected' setelah thread selesai
        ) 
   
    def _about_dialog(self) -> None:                #Mendefinisikan metode untuk membuka dialog 'About'    
        """                                         #Docstring
        Open about dialog.  
        Returns 
        ---------------
        None                                        #Tidak mengembalikan nilai
        """   
        dialog = AboutWindow(self)                  #Membuat instance dari kelas `AboutWindow`, sebuah jendela dialog tentang aplikasi
        dialog.exec()                               #Menjalankan dialog secara modal, menunggu hingga dialog ditutup sebelum melanjutkan eksekusi
  
    def _help_dialog(self) -> None:                 #Mendefinisikan metode untuk membuka dialog 'Help'
        """                                         #Docstring
        Open help dialog window.  
        Returns    
        ----------------
        None                                        #Tidak mengembalikan nilai
        """ 
        dialog = HelpWindow(self)                   #Membuat instance dari kelas `HelpWindow`, sebuah jendela dialog bantuan
        dialog.exec()                               #Menjalankan dialog secara modal, menunggu hingga dialog ditutup sebelum melanjutkan eksekusi
  
    def _read_settings(self):
        self.config.read('settings.ini')
        if len(self.config.sections()) == 0:
            self._create_default_settings()
        for key, value in self.config['electrodes'].items():
            self.colours[key.upper()] = value
        for key, value in self.config['bands'].items():
            self.colours[key.upper()] = value

    def _create_default_settings(self):
        """
        Create and save default settings file.

        Returns
        -------
        None
        """
        self.config['electrodes'] = {
            'TP9': '#2E2EFE',
            'AF7': '#00FF00',
            'AF8': '#FFFF00',
            'TP10': '#FF0000',
        }
        self.config['bands'] = {
            'Gamma': '#2E2EFE',
            'Beta': '#00FF00',
            'Alpha': '#FFFF00',
            'Theta': '#FF0000',
            'Delta': '#962A51'
        }
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

    def _settings_dialog(self) -> None:
        """
        Open about dialog.

        Returns
        -------
        None
        """
        dialog = SettingsWindow(self)
        dialog.settings(self.config)
        dialog.exec()

    def _connect_menu(self) -> None:
        """
        Connect all slots to menu positions.

        Returns
        -------
        None
        """
        self.actionSpike_detecting.triggered.connect(
            self._spike_detection_window)
        self.actionSpike_sorting.triggered.connect(
            self._spike_sorting_window)
        self.actionFeature_extraction.triggered.connect(
            self._feature_extraction_window)
        self.actionClustering.triggered.connect(
            self._clustering_window)
        self.actionClustering.triggered.connect(
            self._wave_clusters_window)
        self.actionClose.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self._open_file_name_dialog)
        self.actionSettings.triggered.connect(self._settings_dialog)
        self.actionAbout.triggered.connect(self._about_dialog)
        self.actionHelp.triggered.connect(self._help_dialog)
        self.actionStream.triggered.connect(self._stream_thread)
        self.actionDisconnect.triggered.connect(self._close_stream)

    def _open_file_name_dialog(self) -> None:
        """
        Open file dialog.

        Returns
        -------
        None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.current_file, _ = QFileDialog.getOpenFileName(
            self,
            caption="QFileDialog.getOpenFileName()",
            directory="./assets",
            filter="Data Files (*.csv *.edf *.bdf *.mat);;Comma Separated Values (*.csv);;EDF Files (*.edf);;BDF Files (*.bdf);;MAT Files (*.mat)",
            options=options)

        self._load_file()

    def _reselect_checkboxes(self) -> None:
        """
        Reselect all checkboxes to default state.

        Returns
        -------
        None
        """
        for checkbox, state, disabled in [
            (self.checkboxTP9, True, False),
            (self.checkboxAF7, False, False),
            (self.checkboxAF8, False, False),
            (self.checkboxTP10, False, False),
            (self.checkboxGamma, False, True),
            (self.checkboxAlpha, False, True),
            (self.checkboxBeta, False, True),
            (self.checkboxTheta, False, True),
            (self.checkboxDelta, False, True),
        ]:
            checkbox.blockSignals(True)
            checkbox.setChecked(state)
            checkbox.setDisabled(disabled)
            checkbox.blockSignals(False)

    def _prepare_modes(self) -> None:
        """
        Prepare mode radio buttons.

        Returns
        -------
        None
        """
        self.radioTime.setDisabled(True)
        self.radioFrequencySingle.setDisabled(True)
        self.radioFrequencyMultiple.setDisabled(True)
        self.radioTime.setChecked(True)

        self.radioTime.toggled.connect(
            lambda: self._toggle_frequency(True, False))
        self.radioFrequencySingle.toggled.connect(
            lambda: self._toggle_frequency(False, True))
        self.radioFrequencyMultiple.toggled.connect(
            lambda: self._toggle_frequency(False, False))

    def _prepare_frequency_bands(self, disabled: bool = True,
                                 exclusive: bool = False) -> None:
        """
        Prepare frequency bands checkboxes.

        Parameters
        ----------
        disabled: bool
        exclusive: bool

        Returns
        -------
        None
        """
        self.frequency_group.addButton(self.checkboxGamma)
        self.frequency_group.addButton(self.checkboxBeta)
        self.frequency_group.addButton(self.checkboxAlpha)
        self.frequency_group.addButton(self.checkboxTheta)
        self.frequency_group.addButton(self.checkboxDelta)

        self._toggle_frequency(disabled, exclusive)

        self.checkboxGamma.toggled.connect(
            lambda: self._checkbox_state(self.checkboxGamma, self.active_series,
                                         [Frequency.GAMMA]))
        self.checkboxBeta.toggled.connect(
            lambda: self._checkbox_state(self.checkboxBeta, self.active_series,
                                         [Frequency.BETA]))
        self.checkboxAlpha.toggled.connect(
            lambda: self._checkbox_state(self.checkboxAlpha, self.active_series,
                                         [Frequency.ALPHA]))
        self.checkboxTheta.toggled.connect(
            lambda: self._checkbox_state(self.checkboxTheta, self.active_series,
                                         [Frequency.THETA]))
        self.checkboxDelta.toggled.connect(
            lambda: self._checkbox_state(self.checkboxDelta, self.active_series,
                                         [Frequency.DELTA]))

    def _prepare_electrodes(self) -> None:
        """
        Prepare electrodes checkboxes.

        Connect function (slot) to state change event of checkbox (signal).

        Returns
        -------
        None
        """
        self.electrodes_group.addButton(self.checkboxTP9)
        self.electrodes_group.addButton(self.checkboxAF7)
        self.electrodes_group.addButton(self.checkboxAF8)
        self.electrodes_group.addButton(self.checkboxTP10)
        self.electrodes_group.setExclusive(False)

        self.checkboxTP9.setChecked(True)
        self.checkboxTP9.toggled.connect(
            lambda: self._checkbox_state(self.checkboxTP9, ['TP9'],
                                         self.active_bands))
        self.checkboxTP9.setDisabled(True)

        self.checkboxAF7.setChecked(False)
        self.checkboxAF7.toggled.connect(
            lambda: self._checkbox_state(self.checkboxAF7, ['AF7'],
                                         self.active_bands))
        self.checkboxAF7.setDisabled(True)

        self.checkboxAF8.setChecked(False)
        self.checkboxAF8.toggled.connect(
            lambda: self._checkbox_state(self.checkboxAF8, ['AF8'],
                                         self.active_bands))
        self.checkboxAF8.setDisabled(True)

        self.checkboxTP10.setChecked(False)
        self.checkboxTP10.toggled.connect(
            lambda: self._checkbox_state(self.checkboxTP10, ['TP10'],
                                         self.active_bands))
        self.checkboxTP10.setDisabled(True)