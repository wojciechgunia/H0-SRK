from platform import platform
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
        conff = open(".\\rj.conf",'r', encoding="utf-8")
        self.stationName = conff.readline().replace('\n','')
        self.platforms = conff.readlines()
        for i in range(len(self.platforms)):
            self.platforms[i]=self.platforms[i].replace('\n','')
            self.platforms[i]=self.platforms[i].split(";")
        #print(self.platforms)
        self.datatab = []
        self.command_line = None
        self.setup()
        

    def setup(self):
        width = 895
        height = 180

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout2 = QHBoxLayout()
        layout2.setAlignment(Qt.AlignLeft)
        layout.addLayout(layout2)

        self.command_line = QLineEdit("", self)
        self.command_line.setFixedWidth(400)
        layout2.addWidget(self.command_line)

        exec_btn = QPushButton("Execute", self)
        exec_btn.setFixedWidth(70)
        layout2.addWidget(exec_btn)

        save_btn = QPushButton("Save to file", self)
        save_btn.setFixedWidth(90)
        layout2.addWidget(save_btn)

        ref_btn = QPushButton("Refresh", self)
        ref_btn.setFixedWidth(70)
        layout2.addWidget(ref_btn)

        gapwidg = QWidget(self)
        gapwidg.setFixedSize(20,10)
        layout2.addWidget(gapwidg)

        clear_btn = QPushButton("Clear", self)
        clear_btn.setFixedWidth(70)
        layout2.addWidget(clear_btn)

        self.comboplat = QComboBox(self)
        for i in self.platforms:
            self.comboplat.addItem('P: '+str(i[0])+' T: '+str(i[1]))
        self.comboplat.setFixedWidth(90)
        layout2.addWidget(self.comboplat)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        exec_btn.clicked.connect(self.execcom)
        clear_btn.clicked.connect(self.clear)
        save_btn.clicked.connect(self.savetof)
        ref_btn.clicked.connect(self.refresh)

        self.setMinimumSize(width, height)
        self.setWindowTitle("Rozkład Jazdy H0")

    def polishchar(self,extext):
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
        return extext

    def getplatform(self, peron, tor):
        a=""
        for i in self.platforms:
            if(peron==i[0] and tor==i[1]):
                a=i[2]
        return a

    def getF(self, delay, endstation):
        #print(delay)
        if int(delay)>0:
            return "F2"
        elif endstation==self.stationName:
            return "F1"
        else:
            return "F0"

    def execcom(self):
        ser = start_window.getser()
        extext = self.command_line.text()
        extext = self.polishchar(extext)
        #print(extext)
        ser.write(str.encode(str(extext)))

    def clear(self):
        datplat=str(self.comboplat.currentText())
        datplat=datplat.split(" ")
        Per=self.getplatform(datplat[1], datplat[3])
        ser = start_window.getser()
        ser.write(str.encode(Per+";;;;;"))
        #print(Per+";;;;;")

    def closeEvent(self, event: QCloseEvent):
        should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if should_clouse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def savetof(self):
        dataf = open(start_window.getfpath(), 'w', encoding="utf-8")
        for line in self.datatab:
            line = ';'.join(line)
            line = line + "\n"
            dataf.write(line)


    def loaddata(self):
        dataf = open(start_window.getfpath(), 'r', encoding="utf-8")
        self.datatab = dataf.readlines()
        for line in range(len(self.datatab)):
            self.datatab[line] = self.datatab[line].replace('\n','')
            self.datatab[line] = self.datatab[line].split(';')
        #print(self.datatab)
        dataf.close()
        self.printtable()

    def sort(self, row):
        if row[11]=="F1":
            return (row[3], row[4])
        else:
            return (row[5], row[6])

    def printtable(self):
        self.datatab.sort(key=lambda row: self.sort(row))
        self.table.setRowCount(len(self.datatab)+1)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(['Przyjazd','Odjazd','Ze stacji','Do stacji','Peron','Tor','Nr pociągu','Przewoźnik', 'Opóźnienie', 'Opcje'])
        self.table.setColumnWidth(0,55)
        self.table.setColumnWidth(1,55)
        self.table.setColumnWidth(2,135)
        self.table.setColumnWidth(3,135)
        self.table.setColumnWidth(4,20)
        self.table.setColumnWidth(5,20)
        self.table.setColumnWidth(6,70)
        self.table.setColumnWidth(7,75)
        self.table.setColumnWidth(8,75)
        self.table.setColumnWidth(9,160)
        buttons=[]
        execb=[]
        delb=[]
        butlay=[]
        saveb=[]
        row=-1
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
        addwid = QWidget()
        addb = QPushButton("Add",self)
        addb.clicked.connect(self.addline)
        addlay = QHBoxLayout()
        addlay.setAlignment(Qt.AlignCenter)
        addlay.setContentsMargins(0,0,0,0)
        addlay.addWidget(addb)
        addwid.setLayout(addlay)
        self.table.setItem(row+1, 0, QTableWidgetItem(""))
        self.table.setItem(row+1, 1, QTableWidgetItem(""))
        self.table.setItem(row+1, 2, QTableWidgetItem(""))
        self.table.setItem(row+1, 3, QTableWidgetItem(""))
        self.table.setItem(row+1, 4, QTableWidgetItem(""))
        self.table.setItem(row+1, 5, QTableWidgetItem(""))
        self.table.setItem(row+1, 6, QTableWidgetItem(""))
        self.table.setItem(row+1, 7, QTableWidgetItem(""))
        self.table.setItem(row+1, 8, QTableWidgetItem(""))
        self.table.setCellWidget(row+1, 9, addwid)

    def exebtn(self, row):
        ser = start_window.getser()
        if self.datatab[row][8]==self.stationName:
            stacja = self.datatab[row][7]
            godzina = self.datatab[row][3]+":"+self.datatab[row][4]
        else:
            stacja = self.datatab[row][8]
            godzina = self.datatab[row][5]+":"+self.datatab[row][6]
        extext = self.datatab[row][0]+";"+godzina+";"+stacja+";"+self.datatab[row][9]+";"+self.datatab[row][10]+";"+self.datatab[row][11]+";"+self.datatab[row][12]
        extext = self.polishchar(extext)
        #print(extext)
        ser.write(str.encode(str(extext)))

    def delbtn(self, row):
        should_clouse = QMessageBox.question(self,"Delete item","Do you want to delete item?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if should_clouse == QMessageBox.StandardButton.Yes:
            del self.datatab[row]
            #print(self.datatab)
            self.printtable()




    def savebtn(self, row):
        self.datatab[row][1]=self.table.item(row, 4).text()
        self.datatab[row][2]=self.table.item(row, 5).text()
        self.datatab[row][3]=self.table.item(row, 0).text().split(":")[0]
        self.datatab[row][4]=self.table.item(row, 0).text().split(":")[1]
        self.datatab[row][5]=self.table.item(row, 1).text().split(":")[0]
        self.datatab[row][6]=self.table.item(row, 1).text().split(":")[1]
        self.datatab[row][7]=self.table.item(row, 2).text()
        self.datatab[row][8]=self.table.item(row, 3).text()
        self.datatab[row][9]=self.table.item(row, 6).text()
        self.datatab[row][10]=self.table.item(row, 7).text()
        self.datatab[row][12]=self.table.item(row, 8).text()
        self.datatab[row][0]=self.getplatform(self.table.item(row, 4).text(),self.table.item(row, 5).text())
        self.datatab[row][11]=self.getF(self.table.item(row, 8).text(),self.table.item(row, 3).text())
        #print(self.datatab)

    def addline(self):
        row = len(self.datatab)
        self.datatab.append([self.getplatform(self.table.item(row, 4).text(),self.table.item(row, 5).text()),self.table.item(row, 4).text(),self.table.item(row, 5).text(),self.table.item(row, 0).text()[0:2],self.table.item(row, 0).text()[3:5],self.table.item(row, 1).text()[0:2],self.table.item(row, 1).text()[3:5],self.table.item(row, 2).text(),self.table.item(row, 3).text(),self.table.item(row, 6).text(),self.table.item(row, 7).text(),self.getF(self.table.item(row, 8).text(),self.table.item(row, 3).text()),self.table.item(row, 8).text()])
        #print(self.datatab)
        self.printtable()

    def refresh(self):
        self.printtable()

#==============================main==========================================================================================================================

if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    app.exec()
