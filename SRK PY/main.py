from PySide6.QtWidgets import QApplication, QScrollArea, QWidget, QMenu, QListWidget, QPushButton, QToolButton, QMessageBox, QLabel, QLineEdit, QFileDialog, QDialog, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
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

#==============================main==========================================================================================================================

if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    app.exec()