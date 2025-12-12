from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox,
                            QGroupBox, QFormLayout, QProgressBar, QPushButton,
                            QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import logging
import subprocess
from settings import Settings

logger = logging.getLogger(__name__)


class SettingsWindow(QWidget):
    initialization_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telly Spelly Settings")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Initialize settings
        self.settings = Settings()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Model settings group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(Settings.VALID_MODELS)
        current_model = self.settings.get('model', 'base')
        self.model_combo.setCurrentText(current_model)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addRow("Whisper Model:", self.model_combo)
        
        self.lang_combo = QComboBox()
        # Add all supported languages
        for code, name in Settings.VALID_LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        current_lang = self.settings.get('language', 'auto')
        # Find and set the current language
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        model_layout.addRow("Language:", self.lang_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Recording settings group
        recording_group = QGroupBox("Recording Settings")
        recording_layout = QFormLayout()
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["Default Microphone"])  # You can populate this with actual devices
        current_mic = self.settings.get('mic_index', 0)
        self.device_combo.setCurrentIndex(current_mic)
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        recording_layout.addRow("Input Device:", self.device_combo)
        
        recording_group.setLayout(recording_layout)
        layout.addWidget(recording_group)
        
        # Loading progress
        self.progress_group = QGroupBox("Model Loading")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Select a model to load")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        self.progress_group.setLayout(progress_layout)
        layout.addWidget(self.progress_group)
        
        # Add shortcuts group
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout()

        shortcuts_label = QLabel("Shortcuts are managed by the system.\nClick below to configure them.")
        shortcuts_layout.addWidget(shortcuts_label)

        open_shortcuts_btn = QPushButton("Open System Shortcuts Settings")
        open_shortcuts_btn.clicked.connect(self.open_system_shortcuts)
        shortcuts_layout.addWidget(open_shortcuts_btn)

        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)
        
        # Add stretch to keep widgets at the top
        layout.addStretch()
        
        # Set a reasonable size
        self.setMinimumWidth(300)
        
        # Initialize whisper model
        self.whisper_model = None
        self.current_model = None

    def on_language_changed(self, index):
        language_code = self.lang_combo.currentData()
        try:
            self.settings.set('language', language_code)
        except ValueError as e:
            logger.error(f"Failed to set language: {e}")
            QMessageBox.warning(self, "Error", str(e))

    def on_device_changed(self, index):
        try:
            self.settings.set('mic_index', index)
        except ValueError as e:
            logger.error(f"Failed to set microphone: {e}")
            QMessageBox.warning(self, "Error", str(e))

    def on_model_changed(self, model_name):
        if model_name == self.current_model:
            return
            
        try:
            self.settings.set('model', model_name)
        except ValueError as e:
            logger.error(f"Failed to set model: {e}")
            QMessageBox.warning(self, "Error", str(e))
            return

        self.progress_label.setText(f"Loading {model_name} model...")
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Load model in a separate thread to prevent UI freezing
        QTimer.singleShot(100, lambda: self.load_model(model_name))

    def load_model(self, model_name):
        try:
            import whisper
            self.whisper_model = whisper.load_model(model_name)
            self.current_model = model_name
            self.progress_label.setText(f"Model {model_name} loaded successfully")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.initialization_complete.emit()
        except Exception as e:
            logger.exception("Failed to load whisper model")
            self.progress_label.setText(f"Failed to load model: {str(e)}")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

    def open_system_shortcuts(self):
        """Open KDE System Settings to the shortcuts page"""
        try:
            # Try KDE 6 first, then KDE 5
            subprocess.Popen(['systemsettings', 'kcm_keys'], start_new_session=True)
        except FileNotFoundError:
            try:
                subprocess.Popen(['systemsettings5', 'kcm_keys'], start_new_session=True)
            except FileNotFoundError:
                QMessageBox.information(self, "Shortcuts",
                    "Could not open System Settings.\n\n"
                    "Please open System Settings manually and navigate to:\n"
                    "Shortcuts → Shortcuts → Telly Spelly") 