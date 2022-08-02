from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel, QLineEdit, QFileDialog, QDialog, QComboBox, QVBoxLayout
from PySide6.QtGui import QCloseEvent, QPixmap, QFileOpenEvent
import serial
import serial.tools.list_ports

com=""
fpath=""
coms=[comport.device for comport in serial.tools.list_ports.comports()]
f=""
ser=""
# =========================================App==================================================================================================================
class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):
        width = 1200
        height = 800

        self.setFixedSize(width, height)
        self.setWindowTitle("Start Window")


    def closeEvent(self, event: QCloseEvent):
        should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if should_clouse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

#=============================Start=====================================================================================================================================
class StartWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.path_edit = None
        self.com_id = None
        self.setup()

    def setup(self):
        width = 400

        self.path_edit = QLineEdit("D:\\", self)
        self.path_edit.setFixedWidth(200)
        self.path_edit.move(165, 61)

        self.com_id = QComboBox(self)
        self.com_id.addItems(coms)
        self.com_id.move(12, 21)
        
        openf_btn = QPushButton("Open file", self)
        openf_btn.move(10, 60)

        newf_btn = QPushButton("New file", self)
        newf_btn.move(85, 60)

        openapp_btn = QPushButton("Open App", self)
        openapp_btn.move(10, 100)
        openapp_btn.setFixedSize(160,40)

        quit_btn = QPushButton("Quit", self)
        quit_btn.move(320, 170)


        openf_btn.clicked.connect(self.openfile)
        newf_btn.clicked.connect(self.newfile)
        quit_btn.clicked.connect(QApplication.instance().quit)
        openapp_btn.clicked.connect(self.openapp)

        self.setFixedSize(width, 200)
        self.setWindowTitle("Start Window")

        self.show()

    def closeEvent(self, event: QCloseEvent):
        should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if should_clouse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def submit(self):
        print(self.path_edit.text())
        # ser.write(str.encode(str(self.path_edit.text())))

    def openfile(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file', 'D:\\', 'RJ files (*.rj)')
        if(fname[0]!=""):
            self.path_edit.setText(fname[0])

    def newfile(self):
        fname=QFileDialog.getSaveFileName(self, 'Create file', 'D:\\', 'RJ files (*.rj)')
        if(fname[0]!=""):
            self.path_edit.setText(fname[0])
            f = open(fname[0],'x')

    def openapp(self):
        fpath = self.path_edit.text()
        com = self.com_id.currentText()
        if(fpath.endswith(".rj")):
            ser=serial.Serial(port=com,baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
            if ser.isOpen():
                print(ser.name + ' is open...')
            self.hide()
            app_window.show()


if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    app.exec()
