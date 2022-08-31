from asyncio.windows_events import NULL
from re import I
from PySide6.QtWidgets import QApplication, QScrollArea, QWidget, QMenu, QTabWidget, QListWidget, QPushButton, QToolButton, QMessageBox, QLabel, QLineEdit, QFileDialog, QDialog, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QCloseEvent, QPixmap, QFileOpenEvent, QIcon, QAction, QPainter, QTransform, QImage, QFont
from PySide6.QtCore import Qt, SIGNAL, QObject, QSize, QEvent, QRectF, QRect, QTimer, QThread, Signal
from functools import partial
import serial
import serial.tools.list_ports
from threading import Thread
from time import sleep

com=""
fpath=""
coms=[comport.device for comport in serial.tools.list_ports.comports()]
f=""


class TimerThread(QThread):
   update = Signal()

   def __init__(self, event):
      QThread.__init__(self)
      self.stopped = event

   def run(self):
      while not self.stopped: 
         sleep(0.8)
         self.update.emit()

   def stop(self):
      self.stopped = True

   def play(self):
      self.stopped = False

   def getStat(self):
      return self.stopped
         

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

      self.path_edit = QLineEdit("D:\\MG.srk", self)
      self.path_edit.setFixedWidth(200)
      self.path_edit.move(165, 61)

      self.com_id = QComboBox(self)
      self.com_id.addItems(coms)
      self.com_id.move(12, 21)
        
      openf_btn = QPushButton("Open file", self)
      openf_btn.move(10, 60)

      openapp_btn = QPushButton("Open App", self)
      openapp_btn.move(10, 100)
      openapp_btn.setFixedSize(160,40)

      quit_btn = QPushButton("Quit", self)
      quit_btn.move(320, 170)


      openf_btn.clicked.connect(self.openfile)
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

   def openapp(self):
      fpath = self.path_edit.text()
      com = self.com_id.currentText()
      if(fpath.endswith(".srk")):
         self.ser=serial.Serial(port=com,baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
         if self.ser.isOpen():
            print(self.ser.name + ' is open...')
         self.hide()
         app_window.loaddata()
         app_window.show()

   def getfpath(self):
      return self.path_edit.text()

   def getser(self):
        return self.ser
# =========================================App==================================================================================================================class AppWindow(QWidget):
class AppWindow(QWidget): 
   def __init__(self):
      super().__init__()

      self.blocks=[]
      self.ser = start_window.getser()
      self.writeserial=[]
      self.labels=[]
      self.ksizeX=22
      self.ksizeY=22
      self.wsizeX=1200
      self.wsizeY=600
      self.selected1=""
      self.selected2=""
      self.serialend=False
      #=================================
      self.przebiegi=[]
      self.manewry=[]
      self.iz=[]
      self.BLTab=[]
      #=================================

      for i in range(int(self.wsizeX/self.ksizeX)):
         blocksline=[]
         for j in range(int(self.wsizeY/self.ksizeY)):
            blocksline.append("")
         self.blocks.append(blocksline)

      self.setup()
      
      
      

   def setup(self):
      width = 1200
      height = 600

      self.layoutmain = QHBoxLayout()
      self.layoutmain.setAlignment(Qt.AlignHCenter)
      self.setLayout(self.layoutmain)


      self.layout = QGridLayout()
      self.layout.setSpacing(0)
      self.layout.setAlignment(Qt.AlignCenter)

      self.win = QWidget()
      self.win.setLayout(self.layout)
      self.win.setFixedSize(self.wsizeX,self.wsizeY)
      self.layoutmain.addWidget(self.win)
      
      for i in range(int(self.wsizeX/self.ksizeX)):
         labell=[]
         for j in range(int(self.wsizeY/self.ksizeY)):
            labell.append(QLabel(self))
            labell[j].setFixedSize(self.ksizeX,self.ksizeY)
            labell[j].installEventFilter(self)
            self.layout.addWidget(labell[j],j,i)
         self.labels.append(labell)

      self.setMinimumSize(width, height)
      self.setGeometry(50, 50, 1200, 600)
      self.setWindowTitle("SRK H0")
      self.setStyleSheet("""QWidget{background-color: black; color: white;} QLabel#Yellow{color: yellow} QLabel#Blue{color: rgb(3, 227, 252)} QLabel#Gray{color: rgb(176, 176, 176)}""")

   def closeEvent(self, event: QCloseEvent):
      self.setStyleSheet("background-color: white;color: black;")
      should_clouse = QMessageBox.question(self,"Close App","Do you want to close?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
      if should_clouse == QMessageBox.StandardButton.Yes:
         self.serialend=True
         event.accept()
      else:
         self.setStyleSheet("""QWidget{background-color: black; color: white;} QLabel#Yellow{color: yellow} QLabel#Blue{color: rgb(3, 227, 252)} QLabel#Gray{color: rgb(176, 176, 176)}""")
         event.ignore()

   def selclear(self):
      if self.selected1!="":
         self.selected1[0].setStyleSheet("border: 0px;")
         self.selected1=""
      if self.selected2!="":
         self.selected2[0].setStyleSheet("border: 0px;")
         self.selected2=""

   def eventFilter(self, source, event):
      if event.type() == QEvent.ContextMenu:
         ind=self.indexofelem(source)
         print(self.blocks[int(ind[0])][int(ind[1])])
         menu = QMenu()
         #tor=menu.addAction('Usuń')
         #tor.triggered.connect(partial(self.delelem, source))
         if self.blocks[int(ind[0])][int(ind[1])][0]=="1":
            RIZ=menu.addAction('Reset IZ/IT')
            RIZ.triggered.connect(partial(self.resetIZ,self.blocks[int(ind[0])][int(ind[1])][3]))
         if self.blocks[int(ind[0])][int(ind[1])][0]=="2":
            if self.blocks[int(ind[0])][int(ind[1])][5]=="Sem" or self.blocks[int(ind[0])][int(ind[1])][5]=="Sem+m":
               poc=menu.addAction('Pociąg')
               if self.selected1!="" and self.selected2!="":
                  x1,y1 = self.selected1[1],self.selected1[2]
                  x2,y2 = self.selected2[1],self.selected2[2]
                  l1,l2 = len(self.blocks[x1][y1])-1,len(self.blocks[x2][y2])-1
                  if (self.blocks[x1][y1][5]=="Sem" or self.blocks[x1][y1][5]=="Sem+m") and (self.blocks[x2][y2][5]=="Sem" or self.blocks[x2][y2][5]=="Sem+m" or (self.blocks[x2][y2][0]=="3" and self.blocks[x2][y2][6]=="0")) and self.blocks[x1][y1][4]==self.blocks[x2][y2][4]:
                     poc.setEnabled(True)
                  else:
                     poc.setEnabled(False)
               else:
                  poc.setEnabled(False)
               if poc:
                  poc.triggered.connect(self.pociag)
            if self.blocks[int(ind[0])][int(ind[1])][5]=="man" or self.blocks[int(ind[0])][int(ind[1])][5]=="Sem+m":
               man=menu.addAction('Manewr')
               if self.selected1!="" and self.selected2!="":
                  x1,y1 = self.selected1[1],self.selected1[2]
                  x2,y2 = self.selected2[1],self.selected2[2]
                  l1,l2 = len(self.blocks[x1][y1])-1,len(self.blocks[x2][y2])-1
                  if (self.blocks[x1][y1][5]=="man" or self.blocks[x1][y1][5]=="Sem+m") and (((self.blocks[x2][y2][5]=="man" or self.blocks[x2][y2][5]=="Sem+m") and self.blocks[x1][y1][4]==self.blocks[x2][y2][4]) or (self.blocks[x2][y2][0]=="5" and self.blocks[x2][y2][5]=="man-sign")):
                     man.setEnabled(True)
                  else:
                     man.setEnabled(False)
               else:
                  man.setEnabled(False)
               if man:
                  man.triggered.connect(self.manewr)
            menu.addSeparator()
            if self.blocks[int(ind[0])][int(ind[1])][5]=="Sem" or self.blocks[int(ind[0])][int(ind[1])][5]=="Sem+m":
               s1=menu.addAction('Stój')
               s1.triggered.connect(partial(self.setS1,ind))
               sz=menu.addAction('SZ')
               sz.triggered.connect(partial(self.setSZ,ind))
            if self.blocks[int(ind[0])][int(ind[1])][5]!="To":
               zdp=menu.addAction('ZDP')
               zdp.triggered.connect(partial(self.zdp,ind))
            
         if self.blocks[int(ind[0])][int(ind[1])][0]=="3":
            wbl=menu.addAction('Wbl')
            if self.blocks[int(ind[0])][int(ind[1])][6]!="1" and self.blocks[int(ind[0])][int(ind[1])][6]!="2" and self.blocks[int(ind[0])][int(ind[1])][6]!="21":
               wbl.setEnabled(False)
            if wbl:
               if self.blocks[int(ind[0])][int(ind[1])][6]=="2" or self.blocks[int(ind[0])][int(ind[1])][6]=="21":
                  wbl.setText("oWbl")
                  wbl.triggered.connect(partial(self.BL, int(ind[0]), int(ind[1]), 1))
               else:
                  wbl.triggered.connect(partial(self.BL, int(ind[0]), int(ind[1]), 2))

            poz=menu.addAction('Poz')
            if self.blocks[int(ind[0])][int(ind[1])][6]!="3" and self.blocks[int(ind[0])][int(ind[1])][6]!="31":
               poz.setEnabled(False)
            if poz:
               poz.triggered.connect(partial(self.BL, int(ind[0]), int(ind[1]), 4))
            ko=menu.addAction('Ko')
            if self.blocks[int(ind[0])][int(ind[1])][6]!="9":
               ko.setEnabled(False)
            if ko:
               ko.triggered.connect(partial(self.BL, int(ind[0]), int(ind[1]), 1))
            menu.addSeparator()
            poc=menu.addAction('Pociąg')
            poc.setEnabled(False)
            x1,y1 = 0,0
            x2,y2 = 0,0
            if self.selected1!="" and self.selected2!="":
               x1,y1 = self.selected1[1],self.selected1[2]
               x2,y2 = self.selected2[1],self.selected2[2]
               l1,l2 = len(self.blocks[x1][y1])-1,len(self.blocks[x2][y2])-1
               if (self.blocks[x1][y1][5]=="Sem" or self.blocks[x1][y1][5]=="Sem+m") and (self.blocks[x2][y2][5]=="Sem" or self.blocks[x2][y2][5]=="Sem+m" or (self.blocks[x2][y2][0]=="3" and self.blocks[x2][y2][6]=="0")) and self.blocks[x1][y1][4]==self.blocks[x2][y2][4]:
                  poc.setEnabled(True)
               else:
                  poc.setEnabled(False)
            else:
               poc.setEnabled(False)
            if poc:
               poc.triggered.connect(self.pociag)

         if self.blocks[int(ind[0])][int(ind[1])][0]=="4" and self.blocks[int(ind[0])][int(ind[1])][6]=="0":
            plus=menu.addAction('Plus (+)')
            plus.triggered.connect(partial(self.croschange, int(ind[0]), int(ind[1]), "1"))
            minus=menu.addAction('Minus (-)')
            minus.triggered.connect(partial(self.croschange, int(ind[0]), int(ind[1]), "0"))
         

         if self.blocks[int(ind[0])][int(ind[1])][0]=="5" and self.blocks[int(ind[0])][int(ind[1])][5]=="man-sign":
            man=menu.addAction('Manewr')
            if self.selected1!="" and self.selected2!="":
               x1,y1 = self.selected1[1],self.selected1[2]
               x2,y2 = self.selected2[1],self.selected2[2]
               l1,l2 = len(self.blocks[x1][y1])-1,len(self.blocks[x2][y2])-1
               if (self.blocks[x1][y1][5]=="man" or self.blocks[x1][y1][5]=="Sem+m") and (self.blocks[x2][y2][5]=="man" or self.blocks[x2][y2][5]=="Sem+m" or (self.blocks[x2][y2][0]=="5" and self.blocks[x2][y2][5]=="man-sign")):
                  man.setEnabled(True)
               else:
                  man.setEnabled(False)
            else:
               man.setEnabled(False)
            if man:
               man.triggered.connect(self.manewr)

         menu.exec(event.globalPos())

         return True

      if event.type() == QEvent.MouseButtonPress:
         ind=self.indexofelem(source)
         if self.blocks[int(ind[0])][int(ind[1])]!="":
            if self.blocks[int(ind[0])][int(ind[1])][0]!="1" and self.blocks[int(ind[0])][int(ind[1])][0]!="6" and self.blocks[int(ind[0])][int(ind[1])][0]!="5" or (self.blocks[int(ind[0])][int(ind[1])][0]=="5" and (self.blocks[int(ind[0])][int(ind[1])][5]=="man-sign" or self.blocks[int(ind[0])][int(ind[1])][5]=="Wk")):
               if self.selected1=="":
                  self.selected1=[source,int(ind[0]),int(ind[1])]
                  source.setStyleSheet("border: 2px solid green;")
               elif self.selected1!="" and self.selected2=="" and self.selected1!=[source,int(ind[0]),int(ind[1])]:
                  self.selected2=[source,int(ind[0]),int(ind[1])]
                  source.setStyleSheet("border: 2px solid green;")

         return True
      
      if event.type() == QEvent.MouseButtonDblClick:
         ind=self.indexofelem(source)
         if self.blocks[int(ind[0])][int(ind[1])]=="":
            self.selclear()

         elif self.blocks[int(ind[0])][int(ind[1])][0]=="4" and self.blocks[int(ind[0])][int(ind[1])][6]=="0":
            self.croschange(int(ind[0]), int(ind[1]), 2)
            self.selclear()

         return True
      
      return super().eventFilter(source, event)

   def indexofelem(self,source):
      for i in range(len(self.labels)):
         for j in range(len(self.labels[i])):
            if self.labels[i][j]==source:
               return [i,j]

   def setSZ(self,ind):
      extext=str(self.blocks[ind[0]][ind[1]][3])+"Sz"
      self.writeserial.append(extext)
      self.blocks[ind[0]][ind[1]][6]="0"
      self.blocks[ind[0]][ind[1]][7]="7"
      self.drawBlock(self.blocks[ind[0]][ind[1]][1],self.blocks[ind[0]][ind[1]][2])
      if len(self.blocks[ind[0]][ind[1]])==14 and self.blocks[ind[0]][ind[1]][13].getStat()==True:
         self.blocks[ind[0]][ind[1]].pop()
      if len(self.blocks[ind[0]][ind[1]])==13:
         self.blocks[ind[0]][ind[1]].append(TimerThread(False))
         self.blocks[ind[0]][ind[1]][13].update.connect(partial(self.blink,ind[0],ind[1]))
         self.blocks[ind[0]][ind[1]][13].start()

   def setS1(self,ind):
      extext=str(self.blocks[ind[0]][ind[1]][3])+"S1"
      self.writeserial.append(extext)
      if len(self.blocks[ind[0]][ind[1]])>13:
         self.blocks[ind[0]][ind[1]][13].stop()
      self.blocks[ind[0]][ind[1]][7]="0"
      if self.FindinPrzebiegi([ind[0],ind[1]])>0:
         self.blocks[ind[0]][ind[1]][6]="2"
      else:
         self.blocks[ind[0]][ind[1]][6]="0"
      self.drawBlock(self.blocks[ind[0]][ind[1]][1],self.blocks[ind[0]][ind[1]][2])
      

   def inPrzebiegi(self,elem):
      ile=0
      for i in self.przebiegi:
         ile=ile+i.count(elem)
      return ile

   def FindTo(self,sem):
      for i in range(len(self.blocks)):
         for j in range(len(self.blocks[i])):
            if self.blocks[i][j]!="" and self.blocks[i][j][0]=="2" and self.blocks[i][j][3] == sem:
               return i,j
      return -1,-1

   def FindSem(self,to):
      for i in range(len(self.blocks)):
         for j in range(len(self.blocks[i])):
            if self.blocks[i][j]!="" and self.blocks[i][j][0]=="2" and self.blocks[i][j][8] == to:
               if self.FindinPrzebiegi([int(self.blocks[i][j][1]),int(self.blocks[i][j][2])])>0:
                  return i,j
      return -1,-1

   def FindinPrzebiegi(self,elem):
      ile=0
      for i in self.przebiegi:
         for j in i:
            if j == elem:
               ile=ile+1
      return ile

   def zdp(self,ind):
      id=""
      place=""
      del1=False
      tr=self.blocks[int(ind[0])][int(ind[1])][6]
      for i in range(len(self.przebiegi)):
         if ind in self.przebiegi[i] and self.FindinPrzebiegi(ind)==1 and (self.przebiegi[i].index(ind) == len(self.przebiegi[i])-1 or self.przebiegi[i].index(ind) == 0) :
            id=i
            place=self.przebiegi[i].index(ind)
            self.blocks[ind[0]][ind[1]][6]="0"
            self.blocks[ind[0]][ind[1]][7]="0"
            self.changeSem(ind[0],ind[1])
            self.drawBlock(ind[0],ind[1])
            del1=True
         elif ind in self.przebiegi[i] and self.FindinPrzebiegi(ind)==2:
            if self.przebiegi[i].index(ind) != len(self.przebiegi[i])-1:
               id=i
               place=self.przebiegi[i].index(ind)
               del1=True
               self.blocks[ind[0]][ind[1]][6]="4"
               self.blocks[ind[0]][ind[1]][7]="0"
               self.changeSem(ind[0],ind[1])
               self.drawBlock(ind[0],ind[1])
               self.changeTo(self.blocks[ind[0]][ind[1]][8],"1","1")

         elif ind in self.przebiegi[i] and self.FindinPrzebiegi(ind)==1 and self.przebiegi[i].index(ind) != len(self.przebiegi[i])-1 and self.przebiegi[i].index(ind) != 0:
            id=i
            place=self.przebiegi[i].index(ind)
            self.blocks[ind[0]][ind[1]][6]="4"
            self.blocks[ind[0]][ind[1]][7]="0"
            self.changeSem(ind[0],ind[1])
            self.drawBlock(ind[0],ind[1])
         
      x=self.przebiegi[id][place][0]
      y=self.przebiegi[id][place][1]
      przebieg=self.przebiegi[id]
      if place == len(self.przebiegi[id])-1:
         kier=-1
         k=place-1
      else:
         self.changeTo(self.blocks[x][y][8],"0","0")
         kier=0
         if del1:
            k=place
         else:
            k=place+1

      if del1:
         przebieg.remove([ind[0],ind[1]])
      while True:
         j=self.przebiegi[id][k]
         if (self.blocks[j[0]][j[1]][0]=="2" and self.blocks[j[0]][j[1]][4]==self.blocks[x][y][4] and self.blocks[j[0]][j[1]][6]!="0") or (self.blocks[j[0]][j[1]][0]=="5" and self.blocks[j[0]][j[1]][5]=="man-sign" and self.blocks[j[0]][j[1]][6]=="3"):
            if(self.FindinPrzebiegi([j[0],j[1]])==1):
               self.blocks[j[0]][j[1]][6]="0"
               if self.blocks[j[0]][j[1]][0]=="2":
                  self.blocks[j[0]][j[1]][7]="0"
                  self.changeSem(j[0],j[1])
                  self.changeTo(self.blocks[j[0]][j[1]][8],"0","0")
               self.drawBlock(j[0],j[1])
            przebieg.remove([j[0],j[1]])
            break
         elif((self.blocks[j[0]][j[1]][0]=="3")):
            przebieg.remove([j[0],j[1]])
            break
         if self.blocks[j[0]][j[1]][0]=="2":
            self.blocks[j[0]][j[1]][7]="0"
            self.changeSem(j[0],j[1])
         self.blocks[j[0]][j[1]][6]="0"
         self.drawBlock(j[0],j[1])
         przebieg.remove([j[0],j[1]])
         k=k+kier
      if przebieg==[]:
         self.przebiegi.pop(id)
      else:
         self.przebiegi[id]=przebieg
      #print(self.przebiegi)
         
      
   
   def findPrzebieg(self,man):
      przebieg=[]
      croppot=[]
      rev=0
      nextcross=0
      xc=0
      yc=0
      changekier=0
      changeval=0
      zwrot=0
      if(self.blocks[self.selected2[1]][self.selected2[2]][4]=="Prawo" or self.blocks[self.selected2[1]][self.selected2[2]][4]=="Lewo"):
         changekier=1
      if self.blocks[self.selected2[1]][self.selected2[2]][0]=="3" or self.blocks[self.selected2[1]][self.selected2[2]][0]=="5":
         x,y=x1,y1=self.selected1[1],self.selected1[2]
         x2,y2=self.selected2[1],self.selected2[2]
         rev=1

      else:
         x,y=x1,y1=self.selected2[1],self.selected2[2]
         x2,y2=self.selected1[1],self.selected1[2]
         
      if(changekier==1):
         changeval=y2-y1
      else:
         changeval=x2-x1
      fin=2
      przebieg.append([x,y])
      while True:
         if changeval>0:
            if changekier==1:
               yc=1
            else:
               xc=1
         elif changeval<0:
            if changekier==1:
               yc=-1
            else:
               xc=-1
         else:
            xc=0
            yc=0
         #print(x,y)
         if self.blocks[x][y][6]!="0" and man==False and [x,y]!=[self.selected1[1],self.selected1[2]]:
            return [],[],0,0,0
         elif self.blocks[x][y][6]!="0" and self.blocks[x][y][6]!="2" and man==True and [x,y]!=[self.selected1[1],self.selected1[2]]:
            return [],[],0,0,0

         if self.labels[x][y]==self.labels[x2][y2]:
            #przebieg.append([x,y])
            fin=1
            break

         elif self.blocks[x][y][0]=="3":
            fin=fin+1
            przebieg=[]   
         if nextcross==1:
            if self.blocks[x][y][0]=="4":
               croppot.append([str(x),str(y),"0"])
            nextcross==0

         if ((self.blocks[x+xc][y+yc]=="" or self.blocks[x+xc][y+yc][0]=="6") or (xc==0 and yc==0)) and rev==0:
            if self.blocks[x1][y1][4]=="Prawo":
               x=x-1
            elif self.blocks[x1][y1][4]=="Lewo":
               x=x+1
            elif self.blocks[x1][y1][4]=="Góra":
               y=y-1
            else:
               y=y+1
            przebieg.append([x,y])
            if self.blocks[x][y][0]=="4":
               croppot.append([str(x),str(y),"1"])
               zwrot=1
            else:
               zwrot=0
         elif ((self.blocks[x+xc][y+yc]=="" or self.blocks[x+xc][y+yc][0]=="6") or (xc==0 and yc==0)) and rev==1:
            if self.blocks[x1][y1][4]=="Prawo":
               x=x+1
            elif self.blocks[x1][y1][4]=="Lewo":
               x=x-1
            elif self.blocks[x1][y1][4]=="Góra":
               y=y+1
            else:
               y=y-1
            przebieg.append([x,y])
            if self.blocks[x][y][0]=="4":
               croppot.append([str(x),str(y),"1"])
               zwrot=1
            else:
               zwrot=0
         else:
            if zwrot==1:
               zwrot=0
               croppot.pop()
               croppot.append([str(x-xc),str(y-yc),"0"])
            if self.blocks[x][y][0]=="4":
               croppot.append([str(x),str(y),"0"])
                  
            przebieg.append([x+xc,y+yc])
            x=x+xc
            y=y+yc
            changeval=changeval+(-xc)+(-yc)
            if changeval==0 or self.blocks[x+xc][y+yc]=="" or self.blocks[x+xc][y+yc][0]=="6":
               nextcross=1

      if rev==1:
         self.przebiegi.append(przebieg)
      else:
         przebieg = przebieg[::-1]
         self.przebiegi.append(przebieg)
      #print(self.przebiegi)
      return przebieg, croppot, fin, x1, y1

   def findSignal(self,x,y):
      #print(self.przebiegi)
      x2,y2=self.FindSem(self.blocks[x][y][3])
      if(x2!=-1 and y2!=-1):
         if self.blocks[x2][y2][7]=="0" and self.crossspeed==False:
            return "3"
         elif self.blocks[x2][y2][7]=="0" and self.crossspeed==True:
            self.crossspeed=False
            return "6"
         elif self.blocks[x2][y2][7]=="1" and self.crossspeed==False:
            return "1"
         elif self.blocks[x2][y2][7]=="1" and self.crossspeed==True:
            self.crossspeed=False
            return "4"
         elif (self.blocks[x2][y2][7]=="4" or self.blocks[x2][y2][7]=="3") and self.crossspeed==False:
            return "2"
         elif (self.blocks[x2][y2][7]=="4" or self.blocks[x2][y2][7]=="3") and self.crossspeed==True:
            self.crossspeed=False
            return "5"
      else:
         if self.crossspeed==True:
            self.crossspeed=False
            return "4"
         else:
            return "1"
      

   def pociag(self):
      przebieg, croppot, fin, x1, y1=self.findPrzebieg(False)
      
      if fin==1:
         for j in przebieg:
            a=[str(j[0]),str(j[1]),"0"]
            if a in croppot:
               if self.blocks[j[0]][j[1]][0]=="4":
                  self.croschange(j[0],j[1],"0")
            a=[str(j[0]),str(j[1]),"1"]
            if a in croppot:
               if self.blocks[j[0]][j[1]][0]=="4":
                  self.croschange(j[0],j[1],"1")

         przebiegr = przebieg[::-1]
         self.crossspeed=False
         for j in przebiegr:
            if [j[0],j[1]]==[self.selected1[1],self.selected1[2]]:
               if self.blocks[self.selected1[1]][self.selected1[2]][0]=="2":
                  self.blocks[self.selected1[1]][self.selected1[2]][6]="1"
                  syg=self.findSignal(self.selected1[1],self.selected1[2])
                  self.blocks[self.selected1[1]][self.selected1[2]][7]=syg
                  self.changeSem(self.selected1[1],self.selected1[2])
                  self.changeTo(self.blocks[self.selected1[1]][self.selected1[2]][8],"1","1")
            elif [j[0],j[1]]==[self.selected2[1],self.selected2[2]]:
               if self.blocks[self.selected2[1]][self.selected2[2]][0]=="2" and self.FindinPrzebiegi([self.selected2[1],self.selected2[2]])==1:
                  self.blocks[self.selected2[1]][self.selected2[2]][6]="4"
                  self.blocks[self.selected2[1]][self.selected2[2]][7]="0"
                  self.changeSem(self.selected2[1],self.selected2[2])
               elif self.blocks[self.selected2[1]][self.selected2[2]][0]=="2" and self.FindinPrzebiegi([self.selected2[1],self.selected2[2]])==2:
                  self.blocks[self.selected2[1]][self.selected2[2]][6]="1"
               elif self.blocks[self.selected2[1]][self.selected2[2]][0]=="3":
                  self.writeserial.append("B;"+self.blocks[self.selected2[1]][self.selected2[2]][3]+";DU")
                  print("B;"+self.blocks[self.selected2[1]][self.selected2[2]][3]+";DU")
            elif((self.blocks[j[0]][j[1]][0]=="2" and (self.blocks[j[0]][j[1]][5]=="Sem" or self.blocks[j[0]][j[1]][5]=="Sem+m") and self.blocks[j[0]][j[1]][4]==self.blocks[x1][y1][4])):
               self.blocks[j[0]][j[1]][6]="1"
               syg=self.findSignal(j[0],j[1])
               self.blocks[j[0]][j[1]][7]=syg
               self.changeSem(j[0],j[1])


            elif(self.blocks[j[0]][j[1]][0]!="2"):
               if self.blocks[j[0]][j[1]][0]=="4" and self.blocks[j[0]][j[1]][9]=="0":
                  self.crossspeed=True
               self.blocks[j[0]][j[1]][6]="1"

         if self.blocks[self.selected2[1]][self.selected2[2]][0]=="3":
            self.blocks[self.selected2[1]][self.selected2[2]][6]="0"
         

         for j in przebieg:
            self.drawBlock(j[0],j[1])

   def changeTo(self,ToName,tryb,sygnal):
         for i in self.blocks:
            for j in i:
               if j!="":
                  if j[0]=="2":
                     if j[3]==ToName:
                        if j[5]=="To":
                           j[6]=tryb
                           j[7]=sygnal
                           self.drawBlock(j[1],j[2])
                        else:
                           if j[6]=="1" and j[7]!="0":
                              if j[7]=="6" or j[7]=="4" or j[7]=="5":
                                 self.crossspeed=True
                              syg=self.findSignal(int(j[1]),int(j[2]))
                              j[7]=syg
                              self.drawBlock(j[1],j[2])
                              self.changeSem(j[1],j[2])

   
   
   def manewr(self):
      przebieg, croppot, fin, x1, y1=self.findPrzebieg(True)

         
      
      if fin==1:
         for j in przebieg:
            a=[str(j[0]),str(j[1]),"0"]
            if a in croppot:
               if self.blocks[j[0]][j[1]][0]=="4":
                  self.croschange(j[0],j[1],"0")
            a=[str(j[0]),str(j[1]),"1"]
            if a in croppot:
               if self.blocks[j[0]][j[1]][0]=="4":
                  self.croschange(j[0],j[1],"1")

         for j in przebieg:
            if((self.blocks[j[0]][j[1]][0]=="2" and (self.blocks[j[0]][j[1]][5]=="man" or self.blocks[j[0]][j[1]][5]=="Sem+m") and self.blocks[j[0]][j[1]][4]==self.blocks[x1][y1][4]) or self.blocks[j[0]][j[1]][0]!="2"):
               self.blocks[j[0]][j[1]][6]="3"
               if self.blocks[j[0]][j[1]][0]=="2":
                  self.blocks[j[0]][j[1]][7]="8"
                  self.changeSem(j[0],j[1])

         
         if self.blocks[self.selected2[1]][self.selected2[2]][0]=="2" and self.blocks[self.selected2[1]][self.selected2[2]][5]=="Sem+m" and self.FindinPrzebiegi([self.selected2[1],self.selected2[2]])==1:
            self.blocks[self.selected2[1]][self.selected2[2]][6]="4"
            self.blocks[self.selected2[1]][self.selected2[2]][7]="0"
            self.changeSem(self.selected2[1],self.selected2[2])

         if self.blocks[self.selected2[1]][self.selected2[2]][0]=="2" and self.FindinPrzebiegi([self.selected2[1],self.selected2[2]])==2:
            self.blocks[self.selected2[1]][self.selected2[2]][6]="3"
            self.blocks[self.selected2[1]][self.selected2[2]][7]="8"
            self.changeSem(self.selected2[1],self.selected2[2])

         if self.blocks[self.selected1[1]][self.selected1[2]][0]=="2":
            self.blocks[self.selected1[1]][self.selected1[2]][6]="3"
            self.blocks[self.selected1[1]][self.selected1[2]][7]="8"
            self.changeSem(self.selected1[1],self.selected1[2])
         
         for j in przebieg:
            self.drawBlock(j[0],j[1])

   def BL(self, x, y, opt):
      self.blocks[x][y][6]=str(opt)
      if self.selected2=="":
         self.selclear()
      if opt==0:
         self.blocks[x][y][9].stop()
      if opt==1:
          self.writeserial.append("B;"+self.blocks[x][y][3]+";Ko")
          print("B;"+self.blocks[x][y][3]+";Ko")
      elif opt==2:
         self.writeserial.append("B;"+self.blocks[x][y][3]+";WBL")
         print("B;"+self.blocks[x][y][3]+";WBL")
         self.blocks[x][y][9].play()
         self.blocks[x][y][9].start()
      elif opt==3:
         self.blocks[x][y][9].play()
         self.blocks[x][y][9].start()
      elif opt==4:
         self.writeserial.append("B;"+self.blocks[x][y][3]+";Poz")
         print("B;"+self.blocks[x][y][3]+";Poz")
         self.blocks[x][y][9].stop()
      elif opt==5:
         self.blocks[x][y][9].play()
         self.blocks[x][y][9].start()
      elif opt==6:
         self.blocks[x][y][9].stop()
      elif opt==7:
         self.blocks[x][y][9].stop()
      self.drawBlock(x,y)

   def blink(self, x, y):
      if self.blocks[x][y][7]=="7":
         self.blocks[x][y][7]="0"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      elif self.blocks[x][y][7]=="0" and self.blocks[x][y][13].getStat()==False:
         self.blocks[x][y][7]="7"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])

   def blinkBL(self, x, y):
      x=int(x)
      y=int(y)
      if self.blocks[x][y][6]=="2" and self.blocks[x][y][9].getStat()==False:
         self.blocks[x][y][6]="21"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      elif self.blocks[x][y][6]=="21":
         self.blocks[x][y][6]="2"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      elif self.blocks[x][y][6]=="3" and self.blocks[x][y][9].getStat()==False:
         self.blocks[x][y][6]="31"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      elif self.blocks[x][y][6]=="31":
         self.blocks[x][y][6]="3"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      elif self.blocks[x][y][6]=="5" and self.blocks[x][y][9].getStat()==False:
         self.blocks[x][y][6]="51"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      elif self.blocks[x][y][6]=="51":
         self.blocks[x][y][6]="5"
         self.drawBlock(self.blocks[x][y][1],self.blocks[x][y][2])
      
      

   def croschange(self, x, y, opt):
      if opt==2:
         if self.blocks[x][y][9]=="1":
            opt="0"
         else:
            opt="1"
      self.blocks[x][y][9]=opt
      self.drawBlock(x, y)

         

   def loaddata(self):
      self.Serial = Thread(target=self.readSerial)
      self.Serial.start()
      dataf = open(start_window.getfpath(), 'r', encoding="utf-8")
      self.blockses=dataf.readlines()
      for i in range(len(self.blockses)):
         self.blockses[i]=self.blockses[i].replace("\n","")
         self.blockses[i]=self.blockses[i].split(";")
         if i!=0:
            self.blocks[int(self.blockses[i][1])][int(self.blockses[i][2])]=self.blockses[i]
            if self.blockses[i][0]=="6":
               self.drawText(self.blockses[i][1],self.blockses[i][2])
            else:
               self.drawBlock(self.blockses[i][1],self.blockses[i][2])
            
      dataf.close() 
      for i in self.blocks:
         for j in i:
            if j!="" and j[0]=="1":
               if [j[3],"0"] not in self.iz:
                  self.iz.append([j[3],"0"])
            if j!="" and j[0]=="3":
               j.append(TimerThread(False))
               j[9].update.connect(partial(self.blinkBL,j[1],j[2]))
               self.BLTab.append(j)
            if j!="" and j[0]=="2":
               #print(j)
               if j[8]!="":
                  x,y=self.FindTo(j[8])
                  j.append(x)
                  j.append(y)
               else:
                  j.append(0)
                  j.append(0)
               self.changeSem(j[1],j[2])
      self.setStyleSheet("""QWidget{background-color: black; color: white;} QLabel#Yellow{color: yellow} QLabel#Blue{color: rgb(3, 227, 252)} QLabel#Gray{color: rgb(176, 176, 176)}""")


   def drawText(self, x, y):
      x=int(x)
      y=int(y)
      i=self.blocks[x][y]
      if i[5]=="Yellow":
         self.labels[x][y].setObjectName("Yellow")
      elif i[5]=="Blue":
         self.labels[x][y].setObjectName("Blue")
      elif i[5]=="White":
         self.labels[x][y].setObjectName("Gray")
      self.labels[x][y].setText(i[3])
      self.labels[x][y].setAutoFillBackground(True)
      self.labels[x][y].setFont(QFont('Arial', 8))

      if i[4]=="Lewo":
         self.labels[x][y].setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
      if i[4]=="Prawo":
         self.labels[x][y].setAlignment(Qt.AlignVCenter | Qt.AlignRight)
      elif i[4]=="Góra":
         self.labels[x][y].setAlignment(Qt.AlignBaseline)
      elif i[4]=="Dół":
         self.labels[x][y].setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
      else:
         self.labels[x][y].setAlignment(Qt.AlignCenter)

   def changeSem(self,x,y):
      i = self.blocks[int(x)][int(y)]
      if i[7]=="0":
         syg="S1"
      elif i[7]=="1":
         syg="S2"
      elif i[7]=="2":
         syg="S4"
      elif i[7]=="3":
         syg="S5"
      elif i[7]=="4":
         syg="S10"
      elif i[7]=="5":
         syg="S12"
      elif i[7]=="6":
         syg="S13"
      elif i[7]=="7":
         syg="Sz"
      elif i[7]=="8":
         syg="Ms2"
      extext=i[3]+syg
      self.writeserial.append(extext)

   def resetIZ(self,iz):
      for i in self.blocks:
         for j in i:
            if j!="" and j[0]!="6":
               if j[0]=="1" or j[0]=="4" or j[0]=="5":
                  if j[3]==iz:
                     self.delinprzebieg(int(j[1]),int(j[2]))
                     j[6]="0"
               if j[0]=="2" and (j[9]==iz or j[10]==iz):
                  self.delinprzebieg(int(j[1]),int(j[2]))
                  j[6]="0"
                  j[7]="0"
                  self.changeSem(j[1],j[2])
               self.drawBlock(j[1],j[2])
      self.IzChange(iz,"0")

   def delinprzebieg(self,x,y):
      for i in range(len(self.przebiegi)):
         for j in range(len(self.przebiegi[i])):
            if self.przebiegi[i][j] == [x,y]:
               self.przebiegi[i].pop(j)
               #print(self.przebiegi)
               break
         if len(self.przebiegi[i])==0:
            self.przebiegi.pop(i)
            break
         


   def changeIz(self,x,y,rev,ko):
      kier = self.blocks[int(x)][int(y)][4]
      xk=0
      yk=0
      if kier=="Prawo" and rev:
         kier="Lewo"
      elif kier=="Lewo" and rev:
         kier="Prawo"
      elif kier=="Dół" and rev:
         kier="Góra"
      elif kier=="Góra" and rev:
         kier="Dół"
      if kier=="Lewo":
         xk=-1
      elif kier=="Prawo":
         xk=1
      elif kier=="Góra":
         yk=-1
      elif kier=="Dół":
         yk=1
      xz=int(x)+xk
      yz=int(y)+yk
      turn=0
      if not ko and self.blocks[int(x)][int(y)][0]=="2":
         self.blocks[int(x)][int(y)][6]="2"
         self.changeTo(self.blocks[int(x)][int(y)][8],"2","2")
         self.delinprzebieg(int(x),int(y))
         self.drawBlock(int(x),int(y))
      if ko and self.blocks[int(x)][int(y)][0]=="2":
         if len(self.blocks[int(x)][int(y)])>13:
            self.blocks[int(x)][int(y)][13].stop()
         self.blocks[int(x)][int(y)][6]="0"
         self.changeTo(self.blocks[int(x)][int(y)][8],"0","0")
         self.drawBlock(int(x),int(y))
      while True:
         if self.blocks[xz][yz]=="":
            if xk==0:
               if self.blocks[xz+1][yz]!="" and self.blocks[xz][yz+1][0]!="6":
                  xk=1
                  yk=0
               elif self.blocks[xz-1][yz]!="" and self.blocks[xz][yz-1][0]!="6":
                  xk=-1
                  yk=0
            if yk==0:
               if self.blocks[xz][yz+1]!="" and self.blocks[xz+1][yz][0]!="6":
                  xk=0
                  yk=1
               elif self.blocks[xz][yz-1]!="" and self.blocks[xz-1][yz][0]!="6":
                  xk=0
                  yk=-1
         else:
            if (self.blocks[xz][yz][0]=="2" and (self.blocks[xz][yz][5]=="Sem" or self.blocks[xz][yz][5]=="Sem+m")) or self.blocks[xz][yz][0]=="3":
               if self.blocks[xz][yz][0]=="2" and self.blocks[xz][yz][6]=="0" and self.blocks[xz][yz][4]==kier:
                  self.blocks[xz][yz][6]="2"
                  self.changeTo(self.blocks[xz][yz][8],"2","2")
               elif self.blocks[xz][yz][0]=="2" and self.blocks[xz][yz][6]=="2" and self.blocks[xz][yz][4]==kier:
                  self.blocks[xz][yz][6]="0"
                  self.changeTo(self.blocks[xz][yz][8],"0","0")
               self.drawBlock(xz,yz)
               self.delinprzebieg(int(xz),int(yz))
               break
            if self.blocks[xz][yz][0]=="4" and self.blocks[xz][yz][9]=="0":
               turn=1
            if ko:
               self.blocks[xz][yz][6]="0"
            else:
               self.blocks[xz][yz][6]="2"
            if self.blocks[xz][yz][0]=="1" or self.blocks[xz][yz][0]=="5" or self.blocks[xz][yz][0]=="4":
               self.drawBlock(xz,yz)
            if turn==1:
               if self.blocks[xz][yz][4]=="Prawo" or self.blocks[xz][yz][4]=="Lewo":
                  if self.blocks[xz][yz+1]!="" and self.blocks[xz][yz+1][0]!="6":
                     xk=0
                     yk=1
                  elif self.blocks[xz][yz-1]!="" and self.blocks[xz][yz-1][0]!="6":
                     xk=0
                     yk=-1
               else:
                  if self.blocks[xz+1][yz]!="" and self.blocks[xz+1][yz][0]!="6":
                     xk=1
                     yk=0
                  elif self.blocks[xz-1][yz]!="" and self.blocks[xz-1][yz][0]!="6":
                     xk=-1
                     yk=0
            self.delinprzebieg(int(xz),int(yz))
            xz=xz+xk
            yz=yz+yk

         

   def IzChange(self,iz,opt):
      for i in self.iz:
         if i[0]==iz:
            i[1]=opt

   def IzCheck(self,iz):
      for i in self.iz:
         if i[0]==iz:
            return i[1]

   def findinblocks(self,name):
      for i in self.blocks:
         for j in i:
            if j!="" and (j[0]=="2" or j[0]=="3") and j[3]==name:
               return j[1],j[2]
   
   def findBL(self,namesem):
      for i in self.blocks:
         for j in i:
            if j!="" and j[0]=="3" and j[5]==namesem:
               return j[1],j[2]

   def findBL2(self,name):
      for i in self.blocks:
         for j in i:
            if j!="" and j[0]=="3" and j[3]==name:
               return int(j[1]),int(j[2])

   def readSerial(self):
      while True:
         ser = start_window.getser()
         data_raw = ser.readline().decode()
         data_raw = data_raw.replace("\n","")
         data_raw = data_raw.replace("\r","")
         data_raw=data_raw.split(";")
         if len(self.writeserial)>0:
            ser.write(str.encode(str(self.writeserial[0])))
            self.writeserial.pop(0)
         if data_raw!="":
            
            if data_raw[0]=="B":
               if len(data_raw)==3:
                  x,y=self.findBL2(data_raw[1])
                  if data_raw[2]=="WBL" and self.blocks[x][y][6]=="1":
                     self.BL(x,y,3)
                  elif data_raw[2]=="Poz" and (self.blocks[x][y][6]=="2" or self.blocks[x][y][6]=="21"):
                     self.BL(x,y,0)
                  elif data_raw[2]=="DU" and self.blocks[x][y][6]=="4":
                     self.BL(x,y,5)
                  elif data_raw[2]=="PS" and (self.blocks[x][y][6]=="5" or self.blocks[x][y][6]=="51"):
                     self.BL(x,y,7)
                  elif data_raw[2]=="Ko" and self.blocks[x][y][6]=="6":
                     self.BL(x,y,1)
                  
            elif len(data_raw)==4 and data_raw[3]=="K":
               if self.IzCheck(data_raw[0])=="3" or self.IzCheck(data_raw[1])=="3":
                  x,y=self.findBL(data_raw[2])
                  if self.blocks[int(x)][int(y)][6]=="7":
                     self.BL(int(x),int(y),9)
               if self.IzCheck(data_raw[0])=="2" or self.IzCheck(data_raw[0])=="3":
                  x,y=self.findinblocks(data_raw[2])
                  self.IzChange(data_raw[0],"0")
                  self.changeIz(x,y,True,True)
               elif self.IzCheck(data_raw[1])=="2" or self.IzCheck(data_raw[1])=="3":
                  x,y=self.findinblocks(data_raw[2])
                  self.IzChange(data_raw[1],"0")
                  self.changeIz(x,y,False,True)
            elif len(data_raw)==4 and data_raw[3]=="S":
               if data_raw[0]==data_raw[1]:
                  if self.IzCheck(data_raw[0])!="1":
                     self.IzChange(data_raw[0],"3")
                     x,y=self.findinblocks(data_raw[2])
                     self.changeIz(x,y,True,False)
                  elif self.IzCheck(data_raw[0])!="1":
                     self.IzChange(data_raw[0],"3")
                     x,y=self.findinblocks(data_raw[2])
                     self.changeIz(x,y,True,False)

               else: 
                  if self.IzCheck(data_raw[0])=="1" or self.IzCheck(data_raw[0])=="3":
                     if self.IzCheck(data_raw[0])=="1":
                        self.IzChange(data_raw[0],"2")
                     self.IzChange(data_raw[1],"1")
                     x,y=self.findinblocks(data_raw[2])
                     self.PSCheck(data_raw[1])
                     self.changeIz(x,y,False,False)
                  elif self.IzCheck(data_raw[1])=="1" or self.IzCheck(data_raw[1])=="3":
                     if self.IzCheck(data_raw[1])=="1":
                        self.IzChange(data_raw[1],"2")
                     self.IzChange(data_raw[0],"1")
                     x,y=self.findinblocks(data_raw[2])
                     self.PSCheck(data_raw[0])
                     self.changeIz(x,y,True,False)
         if(self.serialend):
            break

   def PSCheck(self,izname):
      for i in self.BLTab:
         if i[8]==izname:
            for j in self.iz:
               if j[0]==i[7]:
                  if j[1]=="1":
                     self.writeserial.append("B;"+i[3]+";PS")
                     print("B;"+i[3]+";PS")
                     self.blocks[int(i[1])][int(i[2])][6]="6"
                     self.drawBlock(i[1],i[2])
                     return 0


   def drawBlock(self, x, y):
      x=int(x)
      y=int(y)
      opt=""
      i=self.blocks[x][y]
      if i[6]=="1":
         opt="D"
      elif i[6]=="2":
         opt="Z"
      elif i[6]=="3":
         opt="M"
      elif i[6]=="4":
         opt="ZZ"
      elif i[6]=="0" and i[0]=="2":
         if i[7]=="7":
            opt="SZ"
         else:
            opt=""
      else:
         opt=""
      
      if i[0]=="1":
            if i[5]=="Prosty":
               icon=QIcon(QIcon(".\\svg\\E1"+opt+".svg"))
            else:
               icon=QIcon(QIcon(".\\svg\\E6"+opt+".svg"))

      if i[0]=="2":
            if i[5]=="Sem" and opt!="M":
               icon=QIcon(QIcon(".\\svg\\S1"+opt+".svg"))
            elif i[5]=="Sem+m":
               icon=QIcon(QIcon(".\\svg\\S2"+opt+".svg"))
            elif i[5]=="To" and (opt=="D" or opt=="Z" or opt==""):
               icon=QIcon(QIcon(".\\svg\\S3"+opt+".svg"))
            elif i[5]=="man" and (opt=="M" or opt==""):
               icon=QIcon(QIcon(".\\svg\\S4"+opt+".svg"))

      if i[0]=="3":
            if i[6]=="0":
               icon=QIcon(QIcon(".\\svg\\B3.svg"))
            elif i[6]=="1":
               icon=QIcon(QIcon(".\\svg\\B1.svg"))
            elif i[6]=="2":
               icon=QIcon(QIcon(".\\svg\\B3.svg"))
            elif i[6]=="3":
               icon=QIcon(QIcon(".\\svg\\B23.svg"))
            elif i[6]=="4":
               icon=QIcon(QIcon(".\\svg\\B23.svg"))
            elif i[6]=="5":
               icon=QIcon(QIcon(".\\svg\\B24.svg"))
            elif i[6]=="6":
               icon=QIcon(QIcon(".\\svg\\B4.svg"))
            elif i[6]=="7":
               icon=QIcon(QIcon(".\\svg\\B24.svg"))
            elif i[6]=="21":
               icon=QIcon(QIcon(".\\svg\\B2.svg"))
            elif i[6]=="31":
               icon=QIcon(QIcon(".\\svg\\B22.svg"))
            elif i[6]=="51":
               icon=QIcon(QIcon(".\\svg\\B22.svg"))
            elif i[6]=="9":
               icon=QIcon(QIcon(".\\svg\\B24.svg"))
            

      if i[0]=="4":
            if i[9]=="1":
               icon=QIcon(QIcon(".\\svg\\E2Z1"+opt+".svg"))
            elif i[9]=="0":
               icon=QIcon(QIcon(".\\svg\\E2Z2"+opt+".svg"))
            elif i[9]=="3":
               icon=QIcon(QIcon(".\\svg\\E2O.svg"))

      if i[0]=="5":
            if i[5]=="Wk":
               if i[6]=="0":
                  icon=QIcon(QIcon(".\\svg\\E3Z.svg"))
               else:
                  icon=QIcon(QIcon(".\\svg\\E3O"+opt+".svg"))
            elif i[5]=="End-Track":
               icon=QIcon(QIcon(".\\svg\\E5K.svg"))
            elif i[5]=="man-sign":
               icon=QIcon(QIcon(".\\svg\\E4"+opt+".svg"))
            elif i[5]=="PerL":
               icon=QIcon(QIcon(".\\svg\\I1.svg"))
            elif i[5]=="PerC":
               icon=QIcon(QIcon(".\\svg\\I2.svg"))
            elif i[5]=="PerP":
               icon=QIcon(QIcon(".\\svg\\I3.svg"))
            elif i[5]=="Nast":
               icon=QIcon(QIcon(".\\svg\\I4.svg"))
      
      pixmap=icon.pixmap(icon.actualSize(QSize(self.ksizeX,self.ksizeY)))
      rot=0.0
      sc=1
      if i[5]=="Lewy":
         sc=-1
      if i[4]=="Lewo":
         rot=180.0
      elif i[4]=="Góra":
         rot=270.0
      elif i[4]=="Dół":
         rot=90.0
      piximg=pixmap.toImage()
      piximg=piximg.transformed(QTransform().scale(1,sc))
      piximg=piximg.transformed(QTransform().rotate(rot))
      self.labels[x][y].setPixmap(QPixmap().fromImage(piximg))

#==============================main==========================================================================================================================

if __name__ == "__main__":
    app = QApplication([])

    start_window = StartWindow()
    app_window = AppWindow()
    app.exec()