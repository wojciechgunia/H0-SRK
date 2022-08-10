from PySide6.QtWidgets import QApplication, QScrollArea, QWidget, QMenu, QTabWidget, QListWidget, QPushButton, QToolButton, QMessageBox, QLabel, QLineEdit, QFileDialog, QDialog, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QCloseEvent, QPixmap, QFileOpenEvent, QIcon, QAction
from PySide6.QtCore import Qt, SIGNAL, QObject, QSize, QEvent
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
      self.setup()
      

   def setup(self):
      width = 1300
      height = 700

      layout = QHBoxLayout()
      self.setLayout(layout)
      layout.setAlignment(Qt.AlignLeft)

      self.layout = QGridLayout(self)
      self.layout.setSpacing(0)

      self.win = QWidget()
      self.win.setLayout(self.layout)
      self.win.setFixedSize(1200,600)
      layout.addWidget(self.win)
      
      for i in range(60):
         labell=[]
         for j in range(30):
            labell.append(QPushButton(self))
            labell[j].setIcon(QIcon(".\\svg\\N.svg"))
            labell[j].setIconSize(QSize(20,20))
            labell[j].setStyleSheet("border: 1px solid white;")
            labell[j].setFixedSize(20,20)
            labell[j].installEventFilter(self)
            self.layout.addWidget(labell[j],j,i)
         self.labels.append(labell)

      self.setMinimumSize(width, height)
      self.setGeometry(50, 50, 1200, 600)
      self.setWindowTitle("SRK H0")
      self.setStyleSheet("background-color: black;color: white;")

   def closeEvent(self, event: QCloseEvent):
      self.setStyleSheet("background-color: white;color: black;")
      should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
      if should_clouse == QMessageBox.StandardButton.Yes:
         event.accept()
      else:
         self.setStyleSheet("background-color: black;color: white;")
         event.ignore()

   def eventFilter(self, source, event):
      if event.type() == QEvent.ContextMenu:
         menu = QMenu()
         tor=menu.addAction('Usuń')
         tor.triggered.connect(lambda: source.setIcon(QIcon(".\\svg\\N.svg")))

         menu.exec(event.globalPos())


         return True
      
      return super().eventFilter(source, event)

   def loaddata(self):
        dataf = open(start_window.getfpath(), 'r', encoding="utf-8")

#===============================tools=========================================================================================================================
class Tools(QWidget): 
   def __init__(self):
      super().__init__()
      self.setup()
      

   def setup(self):
      width = 200
      height = 600

      layout = QVBoxLayout(self)
      self.setLayout(layout)

      self.setFixedSize(width, height)
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

      tab1con = QComboBox(self)
      tab1con.addItems(["Kontrolowany","Nie kontrolowany"])
      tab1layout.addWidget(tab1con)

      tab1label = QLabel("Iz/It name")
      tab1layout.addWidget(tab1label)
      self.tab1it = QLineEdit(self)
      tab1layout.addWidget(self.tab1it)

      tab1poz = QComboBox(self)
      tab1poz.addItems(["Poziomo","Pionowo"])
      tab1layout.addWidget(tab1poz)

      tab1btn = QPushButton("Dodaj",self)
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
      
      tab2poz = QComboBox(self)
      tab2poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab2layout.addWidget(tab2poz)

      tab2rodz = QComboBox(self)
      tab2rodz.addItems(["Sem","Sem+m","man","To"])
      tab2layout.addWidget(tab2rodz)

      tab2btn = QPushButton("Dodaj",self)
      tab2layout.addWidget(tab2btn)
      self.tab2.setLayout(tab2layout)


      tab3layout = QVBoxLayout(self)
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

      tab3poz = QComboBox(self)
      tab3poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab3layout.addWidget(tab3poz)
      tab3btn = QPushButton("Dodaj",self)
      tab3layout.addWidget(tab3btn)
      self.tab3.setLayout(tab3layout)



      tab4layout = QVBoxLayout(self)
      tab4layout.setAlignment(Qt.AlignTop)

      tab4con = QComboBox(self)
      tab4con.addItems(["Kontrolowany","Nie kontrolowany"])
      tab4layout.addWidget(tab4con)

      tab4label = QLabel("Iz/It name")
      tab4layout.addWidget(tab4label)
      self.tab4it = QLineEdit(self)
      tab4layout.addWidget(self.tab4it)

      tab4poz = QComboBox(self)
      tab4poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab4layout.addWidget(tab4poz)
      tab4btn = QPushButton("Dodaj",self)
      tab4layout.addWidget(tab4btn)
      self.tab4.setLayout(tab4layout)

      tab5layout = QVBoxLayout(self)
      tab5layout.setAlignment(Qt.AlignTop)

      tab5label = QLabel("Iz/It name / Name")
      tab5layout.addWidget(tab5label)
      self.tab5it = QLineEdit(self)
      tab5layout.addWidget(self.tab5it)

      tab5sel = QComboBox(self)
      tab5sel.addItems(["Wk", "End-Track", "man-sign"])
      tab5layout.addWidget(tab5sel)

      tab5poz = QComboBox(self)
      tab5poz.addItems(["Prawo","Lewo","Góra","Dół"])
      tab5layout.addWidget(tab5poz)

      tab5btn = QPushButton("Dodaj",self)
      tab5layout.addWidget(tab5btn)
      self.tab5.setLayout(tab5layout)

      layout.addWidget(self.tabs)
#==============================main==========================================================================================================================

if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    tools_window = Tools()
    app.exec()