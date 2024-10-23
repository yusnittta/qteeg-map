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
        self.main_series: str = 'FP1'                                       #Mendeklarasikan string untuk menyimpan seri utama
        self.main_band: Frequency = None                                    #Mendeklarasikan variabel untuk menyimpan objek Frequency, diinisialisasi sebagai None
        self.message: QLabel = QLabel()                                     #Membuat QLabel untuk menampilkan pesan status
        self.single_frequency: bool = False                                 #Mendeklarasikan boolean untuk menentukan apakah hanya satu frekuensi yang digunakan
        self.spike_detection_window = MplWindow(self)                       #Membuat instance jendela deteksi spike menggunakan MplWindow
        self.spike_sorting_window = MplWindow(self)                         #Membuat instance jendela sorting spike menggunakan MplWindow
        self.feature_extraction_window = MplWindow(self)                    #Membuat instance jendela ekstraksi fitur FastICA menggunakan MplWindow
        self.pca_extraction_window = MplWindow(self)                        #Membuat instance jendela ekstraksi fitur PCA menggunakan MplWindow
        self.clustering_window = MplWindow(self)                            #Membuat instance jendela clustering menggunakan MplWindow
        self.wave_clusters_window = MplWindow(self)                         #Membuat instance jendela gelombang terklaster menggunakan MplWindow
        self.topoplot_window = MplWindow(self)
        self.spectrum_window = MplWindow(self)
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
    def _feature_extraction_window(self) -> None:                           #Mendefinisikan metode abstrak untuk menampilkan jendela ekstraksi fitur dengan FastICA
        pass 

    @abc.abstractmethod 
    def _pca_extraction_window(self) -> None:                               #Mendefinisikan metode abstrak untuk menampilkan jendela ekstraksi fitur dengan PCA
        pass

    @abc.abstractmethod
    def _topoplot_window(self) -> None:
        pass

    @abc.abstractmethod
    def _spectrum_window(self) -> None:
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
            'FP1': '#2E2EFE',   # Biru Tua
            'FP2': '#00FF00',   # Hijau
            'F3': '#FFFF00',    # Kuning
            'F4': '#FF0000',    # Merah
            'C3': '#FF8000',    # Oranye
            'C4': '#800080',    # Ungu
            'P3': '#00FFFF',    # Cyan
            'P4': '#FF00FF',    # Magenta
            'O1': '#008080',    # Teal
            'O2': '#FFD700',    # Emas
            'F7': '#8B4513',    # Coklat
            'F8': '#708090',    # Abu-abu
            'T3': '#DC143C',    # Crimson
            'T4': '#00BFFF',    # Deep Sky Blue
            'T5': '#FF69B4',    # Hot Pink
            'T6': '#7FFF00'     # Chartreuse
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
        self.actionPCA_extraction.triggered.connect(
            self._pca_extraction_window)
        self.actionClustering.triggered.connect(
            self._clustering_window)
        self.actionClustering.triggered.connect(
            self._wave_clusters_window)
        self.actionTopoplot.triggered.connect(
            self._topoplot_window)
        self.actionSpectrum.triggered.connect(
            self._spectrum_window)
        self.actionClose.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self._open_file_name_dialog)
        self.actionSettings.triggered.connect(self._settings_dialog)
        self.actionAbout.triggered.connect(self._about_dialog)
        self.actionHelp.triggered.connect(self._help_dialog)

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
            filter="Data Files (*.csv *.edf *.bdf *.mat *.txt);;Comma Separated Values (*.csv);;EDF Files (*.edf);;BDF Files (*.bdf);;MAT Files (*.mat);;Text Files (*.txt)",
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
            (self.checkboxFP1, True, False),     # Checkbox untuk FP1
            (self.checkboxFP2, False, False),    # Checkbox untuk FP2
            (self.checkboxF3, False, False),     # Checkbox untuk F3
            (self.checkboxF4, False, False),     # Checkbox untuk F4
            (self.checkboxC3, False, False),     # Checkbox untuk C3
            (self.checkboxC4, False, False),     # Checkbox untuk C4
            (self.checkboxP3, False, False),     # Checkbox untuk P3
            (self.checkboxP4, False, False),     # Checkbox untuk P4
            (self.checkboxO1, False, False),     # Checkbox untuk O1
            (self.checkboxO2, False, False),     # Checkbox untuk O2
            (self.checkboxF7, False, False),     # Checkbox untuk F7
            (self.checkboxF8, False, False),     # Checkbox untuk F8
            (self.checkboxT3, False, False),     # Checkbox untuk T3
            (self.checkboxT4, False, False),     # Checkbox untuk T4
            (self.checkboxT5, False, False),     # Checkbox untuk T5
            (self.checkboxT6, False, False),     # Checkbox untuk T6
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
        self.electrodes_group.addButton(self.checkboxFP1)     # Checkbox untuk FP1
        self.electrodes_group.addButton(self.checkboxFP2)     # Checkbox untuk FP2
        self.electrodes_group.addButton(self.checkboxF3)      # Checkbox untuk F3
        self.electrodes_group.addButton(self.checkboxF4)      # Checkbox untuk F4
        self.electrodes_group.addButton(self.checkboxC3)      # Checkbox untuk C3
        self.electrodes_group.addButton(self.checkboxC4)      # Checkbox untuk C4
        self.electrodes_group.addButton(self.checkboxP3)      # Checkbox untuk P3
        self.electrodes_group.addButton(self.checkboxP4)      # Checkbox untuk P4
        self.electrodes_group.addButton(self.checkboxO1)      # Checkbox untuk O1
        self.electrodes_group.addButton(self.checkboxO2)      # Checkbox untuk O2
        self.electrodes_group.addButton(self.checkboxF7)      # Checkbox untuk F7
        self.electrodes_group.addButton(self.checkboxF8)      # Checkbox untuk F8
        self.electrodes_group.addButton(self.checkboxT3)      # Checkbox untuk T3
        self.electrodes_group.addButton(self.checkboxT4)      # Checkbox untuk T4
        self.electrodes_group.addButton(self.checkboxT5)      # Checkbox untuk T5
        self.electrodes_group.addButton(self.checkboxT6)      # Checkbox untuk T6

        self.electrodes_group.setExclusive(False)

        self.checkboxFP1.setChecked(True)
        self.checkboxFP1.toggled.connect(
            lambda: self._checkbox_state(self.checkboxFP1, ['FP1'],
                                         self.active_bands))
        self.checkboxFP1.setDisabled(True)

        self.checkboxFP2.setChecked(False)
        self.checkboxFP2.toggled.connect(
            lambda: self._checkbox_state(self.checkboxFP2, ['FP2'],
                                         self.active_bands))
        self.checkboxFP2.setDisabled(True)

        self.checkboxF3.setChecked(False)
        self.checkboxF3.toggled.connect(
            lambda: self._checkbox_state(self.checkboxF3, ['F3'],
                                         self.active_bands))
        self.checkboxF3.setDisabled(True)

        self.checkboxF4.setChecked(False)
        self.checkboxF4.toggled.connect(
            lambda: self._checkbox_state(self.checkboxF4, ['F4'],
                                         self.active_bands))
        self.checkboxF4.setDisabled(True)

        self.checkboxC3.setChecked(False)
        self.checkboxC3.toggled.connect(
            lambda: self._checkbox_state(self.checkboxC3, ['C3'],
                                         self.active_bands))
        self.checkboxC3.setDisabled(True)

        self.checkboxC4.setChecked(False)
        self.checkboxC4.toggled.connect(
            lambda: self._checkbox_state(self.checkboxC4, ['C4'],
                                         self.active_bands))
        self.checkboxC4.setDisabled(True)

        self.checkboxP3.setChecked(False)
        self.checkboxP3.toggled.connect(
            lambda: self._checkbox_state(self.checkboxP3, ['P3'],
                                         self.active_bands))
        self.checkboxP3.setDisabled(True)

        self.checkboxP4.setChecked(False)
        self.checkboxP4.toggled.connect(
            lambda: self._checkbox_state(self.checkboxP4, ['P4'],
                                         self.active_bands))
        self.checkboxP4.setDisabled(True)

        self.checkboxO1.setChecked(False)
        self.checkboxO1.toggled.connect(
            lambda: self._checkbox_state(self.checkboxO1, ['O1'],
                                         self.active_bands))
        self.checkboxO1.setDisabled(True)

        self.checkboxO2.setChecked(False)
        self.checkboxO2.toggled.connect(
            lambda: self._checkbox_state(self.checkboxO2, ['O2'],
                                         self.active_bands))
        self.checkboxO2.setDisabled(True)

        self.checkboxF7.setChecked(False)
        self.checkboxF7.toggled.connect(
            lambda: self._checkbox_state(self.checkboxF7, ['F7'],
                                         self.active_bands))
        self.checkboxF7.setDisabled(True)

        self.checkboxF8.setChecked(False)
        self.checkboxF8.toggled.connect(
            lambda: self._checkbox_state(self.checkboxF8, ['F8'],
                                         self.active_bands))
        self.checkboxF8.setDisabled(True)

        self.checkboxT3.setChecked(False)
        self.checkboxT3.toggled.connect(
            lambda: self._checkbox_state(self.checkboxT3, ['T3'],
                                         self.active_bands))
        self.checkboxT3.setDisabled(True)

        self.checkboxT4.setChecked(False)
        self.checkboxT4.toggled.connect(
            lambda: self._checkbox_state(self.checkboxT4, ['T4'],
                                         self.active_bands))
        self.checkboxT4.setDisabled(True)

        self.checkboxT5.setChecked(False)
        self.checkboxT5.toggled.connect(
            lambda: self._checkbox_state(self.checkboxT5, ['T5'],
                                         self.active_bands))
        self.checkboxT5.setDisabled(True)

        self.checkboxT6.setChecked(False)
        self.checkboxT6.toggled.connect(
            lambda: self._checkbox_state(self.checkboxT6, ['T6'],
                                         self.active_bands))
        self.checkboxT6.setDisabled(True)