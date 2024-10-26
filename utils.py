import os
import sys
import logging
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QMetaObject, Q_ARG

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PopupManager(QObject):
    show_popup_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.show_popup_signal.connect(self._show_popup)

    @pyqtSlot(str, str)
    def show_popup_message(self, title, text):
        logger.info(f"show_popup_message called with title: {title}, text: {text}")
        self.show_popup_signal.emit(title, text)

    def _show_popup(self, title, text):
        logger.info("_show_popup function started")
        app = QApplication.instance()
        if app is None:
            logger.info("No QApplication instance found, creating a new one")
            app = QApplication([])
        else:
            logger.info("Existing QApplication instance found")
        
        logger.info("Creating QMessageBox")
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        logger.info("Setting window flags")
        msg.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        logger.info("Getting screen geometry")
        screen = app.primaryScreen().geometry()
        
        logger.info("Calculating position")
        x = screen.width() - msg.width()
        y = (screen.height() - msg.height()) // 2
        
        logger.info(f"Moving message box to position: ({x}, {y})")
        msg.move(x, y)
        
        logger.info("Showing message box")
        msg.show()
        msg.raise_()
        msg.activateWindow()
        
        logger.info("Executing message box")
        msg.exec()
        logger.info("Message box closed")

popup_manager = PopupManager()

def show_popup_message(title, text):
    QMetaObject.invokeMethod(popup_manager, "show_popup_message",
                             Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, title),
                             Q_ARG(str, text))
