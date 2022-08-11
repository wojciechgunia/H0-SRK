from PySide6.QtWidgets import QApplication, QScrollArea, QWidget, QMenu, QTabWidget, QListWidget, QPushButton, QToolButton, QMessageBox, QLabel, QLineEdit, QFileDialog, QDialog, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QCloseEvent, QPixmap, QFileOpenEvent, QIcon, QAction, QPainter, QTransform, QImage
from PySide6.QtCore import Qt, SIGNAL, QObject, QSize, QEvent, QRectF, QRect
from functools import partial

fpath=""
f=""


#=============================Start=====================================================================================================================================
class StartWindow(QWidget):
   def __init__(self):
      super().__init__()

      self.path_edit = None
      self.setup()

   def setup(self):
      width = 400

      self.path_edit = QLineEdit("D:\\MG.srk", self)
      self.path_edit.setFixedWidth(200)
      self.path_edit.move(165, 61)
        
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
      fname=QFileDialog.getOpenFileName(self, 'Open file', 'D:\\', 'SRK files (*.srk)')
      if(fname[0]!=""):
         self.path_edit.setText(fname[0])

   def newfile(self):
      fname=QFileDialog.getSaveFileName(self, 'Create file', 'D:\\', 'SRK files (*.srk)')
      if(fname[0]!=""):
         self.path_edit.setText(fname[0])
         f = open(fname[0],'x')

   def openapp(self):
      fpath = self.path_edit.text()
      if(fpath.endswith(".srk")):
         self.hide()
         app_window.loaddata()
         app_window.show()
         tools_window.show()

   def getfpath(self):
      return self.path_edit.text()
# =========================================App==================================================================================================================class AppWindow(QWidget):
class AppWindow(QWidget): 
   def __init__(self):
      super().__init__()

      self.blocks=[]
      self.labels=[]
      self.ksizeX=25
      self.ksizeY=25
      self.wsizeX=1200
      self.wsizeY=600
      self.selected=""

      self.setup()
      
      
      

   def setup(self):
      width = 1300
      height = 700

      layout = QHBoxLayout()
      layout.setAlignment(Qt.AlignCenter)
      self.setLayout(layout)
      layout.setAlignment(Qt.AlignLeft)

      self.layout = QGridLayout()
      self.layout.setSpacing(0)
      self.layout.setAlignment(Qt.AlignCenter)

      self.win = QWidget()
      self.win.setLayout(self.layout)
      self.win.setFixedSize(self.wsizeX,self.wsizeY)
      layout.addWidget(self.win)
      
      for i in range(int(self.wsizeX/self.ksizeX)):
         labell=[]
         for j in range(int(self.wsizeY/self.ksizeY)):
            labell.append(QLabel(self))
            labell[j].setStyleSheet("border: 1px solid white;")
            labell[j].setFixedSize(self.ksizeX,self.ksizeY)
            labell[j].installEventFilter(self)
            self.layout.addWidget(labell[j],j,i)
         self.labels.append(labell)

      self.setMinimumSize(width, height)
      self.setGeometry(50, 50, 1200, 600)
      self.setWindowTitle("SRK H0")
      self.setStyleSheet("background-color: black;color: white;")

   def closeEvent(self, event: QCloseEvent):
      for i in self.labels:
         for j in i:
            j.setStyleSheet("border: 0;")
      self.setStyleSheet("background-color: white;color: black;")
      should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
      if should_clouse == QMessageBox.StandardButton.Yes:
         dataf = open(start_window.getfpath(), 'w', encoding="utf-8")
         for line in self.blocks:
            line = ';'.join(line)
            line = line + "\n"
            dataf.write(line)
         dataf.close()
         tools_window.close()
         event.accept()
      else:
         self.setStyleSheet("background-color: black;color: white;")
         for i in self.labels:
            for j in i:
               j.setStyleSheet("border: 1px solid white;")
         event.ignore()

   def eventFilter(self, source, event):
      if event.type() == QEvent.ContextMenu:
         menu = QMenu()
         tor=menu.addAction('Usuń')
         tor.triggered.connect(partial(self.delelem, source))
         menu.exec(event.globalPos())

         return True

      if event.type() == QEvent.MouseButtonPress:
         if self.selected!="" :
            self.selected.setStyleSheet("border: 1px solid white;")
         if self.selected!=source:
            self.selected=source
            self.selected.setStyleSheet("border: 2px solid green;")
         else:
            self.selected=""

         return True
      
      return super().eventFilter(source, event)

   def delelem(self,source):
      source.setPixmap(QPixmap())
      index = self.indextodel(source)
      self.delinfile(index[0],index[1])

   def delinfile(self,x,y):
      for i in range(1,len(self.blocks)):
         if self.blocks[i][1]==str(x) and self.blocks[i][2]==str(y):
            self.blocks.pop(i)
            break

   def indexelem(self):
      for i in range(len(self.labels)):
         for j in range(len(self.labels[i])):
            if self.labels[i][j]==self.selected:
               return [i,j]

   def indextodel(self, source):
      for i in range(len(self.labels)):
         for j in range(len(self.labels[i])):
            if self.labels[i][j]==source:
               return [i,j]

   def loaddata(self):
      dataf = open(start_window.getfpath(), 'r', encoding="utf-8")
      self.blocks=dataf.readlines()
      for i in range(len(self.blocks)):
         self.blocks[i]=self.blocks[i].replace("\n","")
         self.blocks[i]=self.blocks[i].split(";")
      dataf.close()
      for i in self.blocks:
         if i[0]=="1":
            if i[5]=="Prosty":
               icon=QIcon(QIcon(".\\svg\\E1.svg"))
            else:
               icon=QIcon(QIcon(".\\svg\\E6.svg"))
            self.drawBlock(i[1],i[2],i[4],"", icon)

         if i[0]=="2":
            if i[5]=="Sem":
               icon=QIcon(QIcon(".\\svg\\S1.svg"))
            elif i[5]=="Sem+m":
               icon=QIcon(QIcon(".\\svg\\S2.svg"))
            elif i[5]=="To":
               icon=QIcon(QIcon(".\\svg\\S3.svg"))
            else:
               icon=QIcon(QIcon(".\\svg\\S4.svg"))
            self.drawBlock(i[1],i[2],i[4],"", icon)

         if i[0]=="3":
            icon=QIcon(QIcon(".\\svg\\B2.svg"))
            self.drawBlock(i[1],i[2],i[4],"", icon)

         if i[0]=="4":
            icon=QIcon(QIcon(".\\svg\\E2Z.svg"))
            self.drawBlock(i[1],i[2],i[4],i[5], icon)

         if i[0]=="5":
            if i[5]=="Wk":
               icon=QIcon(QIcon(".\\svg\\E3Z.svg"))
            elif i[5]=="End-Track":
               icon=QIcon(QIcon(".\\svg\\E5K.svg"))
            elif i[5]=="man-sign":
               icon=QIcon(QIcon(".\\svg\\E4.svg"))
            elif i[5]=="PerL":
               icon=QIcon(QIcon(".\\svg\\I1.svg"))
            elif i[5]=="PerC":
               icon=QIcon(QIcon(".\\svg\\I2.svg"))
            elif i[5]=="PerP":
               icon=QIcon(QIcon(".\\svg\\I3.svg"))
            elif i[5]=="Nast":
               icon=QIcon(QIcon(".\\svg\\I4.svg"))
            self.drawBlock(i[1],i[2],i[4],"", icon)

   def drawBlock(self, x, y, pos, posr, icon):
      x=int(x)
      y=int(y)
      pixmap=icon.pixmap(icon.actualSize(QSize(self.ksizeX,self.ksizeY)))
      rot=0.0
      sc=1
      if posr=="Lewy":
         sc=-1
      if pos=="Lewo":
         rot=180.0
      elif pos=="Góra":
         rot=270.0
      elif pos=="Dół":
         rot=90.0
      piximg=pixmap.toImage()
      piximg=piximg.transformed(QTransform().scale(1,sc))
      piximg=piximg.transformed(QTransform().rotate(rot))
      self.labels[x][y].setPixmap(QPixmap().fromImage(piximg))

   def addtrack(self, pos, type, cont, itname):
      if self.selected!="":
         place=self.indexelem()
         if type=="Prosty":
            icon=QIcon(QIcon(".\\svg\\E1.svg"))
         else:
            icon=QIcon(QIcon(".\\svg\\E6.svg"))
         self.drawBlock(str(place[0]),str(place[1]),pos,"", icon)
         self.delinfile(place[0],place[1])
         self.blocks.append(["1",str(place[0]),str(place[1]),itname,pos,type,cont])

   def addsem(self, name, type, itb, ita, pos):
      if self.selected!="":
         place=self.indexelem()
         if type=="Sem":
            icon=QIcon(QIcon(".\\svg\\S1.svg"))
         elif type=="Sem+m":
            icon=QIcon(QIcon(".\\svg\\S2.svg"))
         elif type=="To":
            icon=QIcon(QIcon(".\\svg\\S3.svg"))
         else:
            icon=QIcon(QIcon(".\\svg\\S4.svg"))
         self.delinfile(place[0],place[1])
         self.drawBlock(str(place[0]),str(place[1]),pos,"", icon)
         self.blocks.append(["2",str(place[0]),str(place[1]),name,pos,type,itb,ita])

   def addBL(self, name, sem, it1, it2, pos):
      if self.selected!="":
         place=self.indexelem()
         icon=QIcon(QIcon(".\\svg\\B2.svg"))
         self.delinfile(place[0],place[1])
         self.drawBlock(str(place[0]),str(place[1]),pos,"", icon)
         self.blocks.append(["3",str(place[0]),str(place[1]),name,pos,sem,it1,it2])

   def addCR(self, pos, posr, itname, cont):
      if self.selected!="":
         place=self.indexelem()
         icon=QIcon(QIcon(".\\svg\\E2Z.svg"))
         self.delinfile(place[0],place[1])
         self.drawBlock(str(place[0]),str(place[1]),pos,posr, icon)
         self.blocks.append(["4",str(place[0]),str(place[1]),itname,pos,posr,cont])

   def addEl(self, itname, sel, pos):
      if self.selected!="":
         place=self.indexelem()
         if sel=="Wk":
            icon=QIcon(QIcon(".\\svg\\E3Z.svg"))
         elif sel=="End-Track":
            icon=QIcon(QIcon(".\\svg\\E5K.svg"))
         elif sel=="man-sign":
            icon=QIcon(QIcon(".\\svg\\E4.svg"))
         elif sel=="PerL":
            icon=QIcon(QIcon(".\\svg\\I1.svg"))
         elif sel=="PerC":
            icon=QIcon(QIcon(".\\svg\\I2.svg"))
         elif sel=="PerP":
            icon=QIcon(QIcon(".\\svg\\I3.svg"))
         elif sel=="Nast":
            icon=QIcon(QIcon(".\\svg\\I4.svg"))
         self.delinfile(place[0],place[1])
         self.drawBlock(str(place[0]),str(place[1]),pos,"", icon)
         self.blocks.append(["5",str(place[0]),str(place[1]),itname,pos,sel])
      



#===============================tools=========================================================================================================================
class Tools(QWidget): 
   def __init__(self):
      super().__init__()
      self.setup()
      

   def setup(self):
      width = 200
      height = 600

      layout = QVBoxLayout()
      self.setLayout(layout)

      self.setFixedSize(width, height)
      self.setGeometry(1360, 50, width, height)
      self.setWindowTitle("Tools")
      self.tabs = QTabWidget()
      self.tab1 = QWidget()
      self.tab2 = QWidget()
      self.tab3 = QWidget()
      self.tab4 = QWidget()
      self.tab5 = QWidget()
      self.tabs.addTab(self.tab1,"Track")
      self.tabs.addTab(self.tab2,"Sem")
      self.tabs.addTab(self.tab3,"BL")
      self.tabs.addTab(self.tab4,"Cross")
      self.tabs.addTab(self.tab5,"Else")

      tab1layout = QVBoxLayout()
      tab1layout.setAlignment(Qt.AlignTop)

      self.tab1con = QComboBox(self)
      self.tab1con.addItems(["Kontrolowany","Nie kontrolowany"])
      tab1layout.addWidget(self.tab1con)

      self.tab1type = QComboBox(self)
      self.tab1type.addItems(["Prosty","Łuk"])
      tab1layout.addWidget(self.tab1type)

      tab1label = QLabel("Iz/It name")
      tab1layout.addWidget(tab1label)
      self.tab1it = QLineEdit(self)
      tab1layout.addWidget(self.tab1it)

      self.tab1poz = QComboBox(self)
      self.tab1poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab1layout.addWidget(self.tab1poz)

      tab1btn = QPushButton("Dodaj",self)
      tab1btn.clicked.connect(self.addtrack)
      tab1layout.addWidget(tab1btn)
      self.tab1.setLayout(tab1layout)
      

      tab2layout = QVBoxLayout()
      tab2layout.setAlignment(Qt.AlignTop)

      tab2label = QLabel("Name")
      tab2layout.addWidget(tab2label)
      self.tab2name = QLineEdit(self)
      tab2layout.addWidget(self.tab2name)

      tab2label2 = QLabel("It/Iz Before")
      tab2layout.addWidget(tab2label2)
      self.tab2itb = QLineEdit(self)
      tab2layout.addWidget(self.tab2itb)

      tab2label3 = QLabel("It/Iz After")
      tab2layout.addWidget(tab2label3)
      self.tab2ita = QLineEdit(self)
      tab2layout.addWidget(self.tab2ita)
      
      self.tab2poz = QComboBox(self)
      self.tab2poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab2layout.addWidget(self.tab2poz)

      self.tab2rodz = QComboBox(self)
      self.tab2rodz.addItems(["Sem","Sem+m","man","To"])
      tab2layout.addWidget(self.tab2rodz)

      tab2btn = QPushButton("Dodaj",self)
      tab2btn.clicked.connect(self.addsem)
      tab2layout.addWidget(tab2btn)
      self.tab2.setLayout(tab2layout)


      tab3layout = QVBoxLayout()
      tab3layout.setAlignment(Qt.AlignTop)

      tab3label = QLabel("Name")
      tab3layout.addWidget(tab3label)
      self.tab3name = QLineEdit(self)
      tab3layout.addWidget(self.tab3name)

      self.tab3.setLayout(tab3layout)
      tab3label2 = QLabel("It/Iz after BL")
      tab3layout.addWidget(tab3label2)
      self.tab3it1 = QLineEdit(self)
      tab3layout.addWidget(self.tab3it1)

      self.tab3.setLayout(tab3layout)
      tab3label3 = QLabel("Sem Ent")
      tab3layout.addWidget(tab3label3)
      self.tab3semw = QLineEdit(self)
      tab3layout.addWidget(self.tab3semw)

      self.tab3.setLayout(tab3layout)
      tab3label3 = QLabel("It/Iz Ko")
      tab3layout.addWidget(tab3label3)
      self.tab3it2 = QLineEdit(self)
      tab3layout.addWidget(self.tab3it2)

      self.tab3poz = QComboBox(self)
      self.tab3poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab3layout.addWidget(self.tab3poz)

      tab3btn = QPushButton("Dodaj",self)
      tab3btn.clicked.connect(self.addBL)
      tab3layout.addWidget(tab3btn)
      self.tab3.setLayout(tab3layout)



      tab4layout = QVBoxLayout()
      tab4layout.setAlignment(Qt.AlignTop)

      self.tab4con = QComboBox(self)
      self.tab4con.addItems(["Kontrolowany","Nie kontrolowany"])
      tab4layout.addWidget(self.tab4con)

      tab4label = QLabel("Iz/It name")
      tab4layout.addWidget(tab4label)
      self.tab4it = QLineEdit(self)
      tab4layout.addWidget(self.tab4it)

      self.tab4pozr = QComboBox(self)
      self.tab4pozr.addItems(["Prawy","Lewy"])
      tab4layout.addWidget(self.tab4pozr)

      self.tab4poz = QComboBox(self)
      self.tab4poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab4layout.addWidget(self.tab4poz)

      tab4btn = QPushButton("Dodaj",self)
      tab4btn.clicked.connect(self.addcross)
      tab4layout.addWidget(tab4btn)
      self.tab4.setLayout(tab4layout)

      tab5layout = QVBoxLayout()
      tab5layout.setAlignment(Qt.AlignTop)

      tab5label = QLabel("Iz/It name / Name")
      tab5layout.addWidget(tab5label)
      self.tab5it = QLineEdit(self)
      tab5layout.addWidget(self.tab5it)

      self.tab5sel = QComboBox(self)
      self.tab5sel.addItems(["Wk", "End-Track", "man-sign", "PerL", "PerC", "PerP", "Nast"])
      tab5layout.addWidget(self.tab5sel)

      self.tab5poz = QComboBox(self)
      self.tab5poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab5layout.addWidget(self.tab5poz)

      tab5btn = QPushButton("Dodaj",self)
      tab5btn.clicked.connect(self.addelse)
      tab5layout.addWidget(tab5btn)
      self.tab5.setLayout(tab5layout)

      layout.addWidget(self.tabs)

   def addtrack(self):
      app_window.addtrack(self.tab1poz.currentText(),self.tab1type.currentText(),self.tab1con.currentText(),self.tab1it.text())

   def addsem(self):
      app_window.addsem(self.tab2name.text(),self.tab2rodz.currentText(),self.tab2itb.text(),self.tab2ita.text(),self.tab2poz.currentText())

   def addBL(self):
      app_window.addBL(self.tab3name.text(),self.tab3semw.text(),self.tab3it1.text(),self.tab3it2.text(),self.tab3poz.currentText())

   def addcross(self):
      app_window.addCR(self.tab4poz.currentText(),self.tab4pozr.currentText(),self.tab4it.text(),self.tab4con.currentText())

   def addelse(self):
      app_window.addEl(self.tab5it.text(),self.tab5sel.currentText(),self.tab5poz.currentText())
#==============================main==========================================================================================================================

if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    tools_window = Tools()
    app.exec()