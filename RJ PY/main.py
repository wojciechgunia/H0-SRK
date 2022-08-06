from PySide6.QtWidgets import QApplication, QScrollArea, QWidget, QPushButton, QMessageBox, QLabel, QLineEdit, QFileDialog, QDialog, QComboBox, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QCloseEvent, QPixmap, QFileOpenEvent
from PySide6.QtCore import Qt, SIGNAL, QObject, QSize
from functools import partial
import serial
import serial.tools.list_ports

com=""
fpath=""
coms=[comport.device for comport in serial.tools.list_ports.comports()]
f=""


#=============================Start=====================================================================================================================================
class StartWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.path_edit = None
        self.com_id = None
        self.ser = None
        self.setup()

    def setup(self):
        width = 400

        self.path_edit = QLineEdit("D:\\New.rj", self)
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
            self.ser=serial.Serial(port=com,baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
            if self.ser.isOpen():
                print(self.ser.name + ' is open...')
            self.hide()
            app_window.loaddata()
            app_window.show()
            

    def getser(self):
        return self.ser

    def getfpath(self):
        return self.path_edit.text()
# =========================================App==================================================================================================================
class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.datatab = []
        self.command_line = None
        self.setup()

    def setup(self):
        width = 1200
        height = 800

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout2 = QHBoxLayout()
        layout2.setAlignment(Qt.AlignLeft)
        layout.addLayout(layout2)

        self.command_line = QLineEdit("", self)
        self.command_line.setFixedWidth(400)
        layout2.addWidget(self.command_line)

        exec_btn = QPushButton("Execute", self)
        exec_btn.setFixedWidth(120)
        layout2.addWidget(exec_btn)

        clear_btn = QPushButton("Clear", self)
        clear_btn.setFixedWidth(120)
        layout2.addWidget(clear_btn)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        exec_btn.clicked.connect(self.execcom)
        clear_btn.clicked.connect(self.clear)

        self.setFixedSize(width, height)
        self.setWindowTitle("App Window")

    def execcom(self):
        ser = start_window.getser()
        extext = self.command_line.text()
        extext = extext.replace('Ą','!')
        extext = extext.replace('ą','"')
        extext = extext.replace('Ę','#')
        extext = extext.replace('ę','$')
        extext = extext.replace('Ś','%')
        extext = extext.replace('ś','&')
        extext = extext.replace('Ć','{')
        extext = extext.replace('ć','}')
        extext = extext.replace('Ó','(')
        extext = extext.replace('ó',')')
        extext = extext.replace('Ż','*')
        extext = extext.replace('ż','+')
        extext = extext.replace('Ź',',')
        extext = extext.replace('ź','/')
        extext = extext.replace('Ń','<')
        extext = extext.replace('ń','>')
        extext = extext.replace('Ł','?')
        extext = extext.replace('ł','@')
        print(extext)
        ser.write(str.encode(str(extext)))

    def clear(self):
        ser = start_window.getser()
        ser.write(str.encode(";;;;;"))

    def closeEvent(self, event: QCloseEvent):
        should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if should_clouse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def loaddata(self):
        dataf = open(start_window.getfpath(), 'r', encoding="utf-8")
        self.datatab = dataf.readlines()
        for line in range(len(self.datatab)):
            self.datatab[line] = self.datatab[line].replace('\n','')
            self.datatab[line] = self.datatab[line].split(';')
        print(self.datatab)
        dataf.close()
        self.table.setRowCount(len(self.datatab))
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(['Czas przyjazdu','Czas odjazdu','Ze stacji','Do stacji','Peron','Tor','Nr pociągu','Przewoźnik', 'Opóźnienie', 'Opcje'])
        buttons=[]
        execb=[]
        delb=[]
        butlay=[]
        saveb=[]
        for row in range(len(self.datatab)):
            buttons.append(QWidget())
            execb.append(QPushButton("Play",self))
            delb.append(QPushButton("Delete",self))
            saveb.append(QPushButton("Save",self))
            execb[row].clicked.connect(partial(self.exebtn,row))
            delb[row].clicked.connect(partial(self.delbtn,row))
            saveb[row].clicked.connect(partial(self.savebtn,row))
            butlay.append(QHBoxLayout())
            butlay[row].setAlignment(Qt.AlignCenter)
            butlay[row].setContentsMargins(0,0,0,0)
            butlay[row].addWidget(execb[row])
            butlay[row].addWidget(delb[row])
            butlay[row].addWidget(saveb[row])
            buttons[row].setLayout(butlay[row])
            self.table.setItem(row, 0, QTableWidgetItem(str(self.datatab[row][3]+":"+self.datatab[row][4])))
            self.table.setItem(row, 1, QTableWidgetItem(str(self.datatab[row][5]+":"+self.datatab[row][6])))
            self.table.setItem(row, 2, QTableWidgetItem(str(self.datatab[row][7])))
            self.table.setItem(row, 3, QTableWidgetItem(str(self.datatab[row][8])))
            self.table.setItem(row, 4, QTableWidgetItem(str(self.datatab[row][1])))
            self.table.setItem(row, 5, QTableWidgetItem(str(self.datatab[row][2])))
            self.table.setItem(row, 6, QTableWidgetItem(str(self.datatab[row][9])))
            self.table.setItem(row, 7, QTableWidgetItem(str(self.datatab[row][10])))
            self.table.setItem(row, 8, QTableWidgetItem(str(self.datatab[row][12])))
            self.table.setCellWidget(row, 9, buttons[row])

    def exebtn(self, row):
        ser = start_window.getser()
        if self.datatab[row][11]=="F1":
            stacja = self.datatab[row][7]
        else:
            stacja = self.datatab[row][8]
        extext = self.datatab[row][0]+";"+self.datatab[row][5]+":"+self.datatab[row][6]+";"+stacja+";"+self.datatab[row][9]+";"+self.datatab[row][10]+";"+self.datatab[row][11]+";"+self.datatab[row][12]
        extext = extext.replace('Ą','!')
        extext = extext.replace('ą','"')
        extext = extext.replace('Ę','#')
        extext = extext.replace('ę','$')
        extext = extext.replace('Ś','%')
        extext = extext.replace('ś','&')
        extext = extext.replace('Ć','{')
        extext = extext.replace('ć','}')
        extext = extext.replace('Ó','(')
        extext = extext.replace('ó',')')
        extext = extext.replace('Ż','*')
        extext = extext.replace('ż','+')
        extext = extext.replace('Ź',',')
        extext = extext.replace('ź','/')
        extext = extext.replace('Ń','<')
        extext = extext.replace('ń','>')
        extext = extext.replace('Ł','?')
        extext = extext.replace('ł','@')
        print(extext)
        ser.write(str.encode(str(extext)))

    def delbtn(self, row):
        print("del"+str(row))

    def savebtn(self, row):
        print("save"+str(row))
#==============================main==========================================================================================================================

if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    app.exec()
