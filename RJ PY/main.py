from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel, QLineEdit
from PySide6.QtGui import QCloseEvent, QPixmap
import serial

ser=serial.Serial(
port='COM3',
baudrate=9600,
parity=serial.PARITY_NONE,
stopbits=serial.STOPBITS_ONE,
bytesize=serial.EIGHTBITS,
timeout=1
)

if ser.isOpen():
     print(ser.name + ' is open...')

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.login_line_edit = None;

        self.setup()

    def setup(self):
        width = 400

        pix_label = QLabel(self)
        pixmap = QPixmap("C:\\Users\\wojte\\Pictures\\My Icons\\Picture_alt.png")
        pix_label.setPixmap(pixmap)
        pix_label.move((width-128)/2, 50)

        self.login_line_edit = QLineEdit("comand", self)
        self.login_line_edit.setFixedWidth(200)
        self.login_line_edit.move(100, 350)

        submit_btn = QPushButton("Submit", self)
        submit_btn.move((width - submit_btn.size().width())/2, 410)

        quit_btn = QPushButton("Quit", self)
        quit_btn.move(320, 570)


        submit_btn.clicked.connect(self.submit)
        quit_btn.clicked.connect(QApplication.instance().quit)

        self.setFixedSize(width, 600)
        self.setWindowTitle("Login Window")

        self.show()

    def closeEvent(self, event: QCloseEvent):
        should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if should_clouse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def submit(self):
        print(self.login_line_edit.text())
        ser.write(str.encode(str(self.login_line_edit.text())))

if __name__ == "__main__":
    app = QApplication([])

    login_window = LoginWindow()

    app.exec()
