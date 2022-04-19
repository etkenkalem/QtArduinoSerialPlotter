

import random
import json
import copy
from PyQt5 import QtWidgets, QtCore, QtSerialPort
from PyQt5.QtWidgets import QPushButton, QMenu, QApplication,QShortcut

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


import pyqtgraph as pg #fast tutorial: https://www.pythonguis.com/tutorials/plotting-pyqtgrap/
import sys
import re
import qdarkstyle
import qtawesome as qta #run qta-browser from a shell to start the icon browser
from dragAndDrop import DDbutton, MacroButtonData


class subwindow(QtWidgets.QWidget):
    def createWindow(self,WindowWidth,WindowHeight,sp):
        parent=None
        #super(subwindow,self).__init__(parent)

        self.sp=sp

        self.setWindowFlags(QtCore.Qt.WindowType.SubWindow)
        self.resize(WindowWidth,WindowHeight)

        self.Vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.Vlayout)


        self.quitSc = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.quitSc.activated.connect(QApplication.instance().quit)

        self.initUI();


    def initUI(self):


        self.setAcceptDrops(True)

        self.buttons=[]

        self.menu=QMenu()
        self.menu.addAction
        self.openMacroAction = self.menu.addAction(qta.icon("fa.refresh",color="white",scale_factor=0.7),"Open a macro file",)
        self.openMacroAction.triggered.connect(self.openMacroFile)
        self.saveMacroAction = self.menu.addAction("Save this macro")
        self.saveMacroAction.triggered.connect(self.saveMacroFile)
        self.addButtonAction =self.menu.addAction("Add Button")
        self.addButtonAction.triggered.connect(self.addMacroButton)
        self.seperateWindowAction =self.menu.addAction("Seperate Button")
        self.seperateWindowAction.triggered.connect(self.seperateWindow)


        self.menuBtnEdit=QMenu()
        self.btnEditAction = self.menuBtnEdit.addAction(qta.icon("fa.edit",scale_factor=0.7,color="white"), "Edit")
        self.btnCloneAction =self.menuBtnEdit.addAction("Clone")
        self.btnDeleteAction =self.menuBtnEdit.addAction("Delete")





        self.setWindowTitle('Ctrl-rightClick to move buttons')
        #self.setGeometry(300, 300, 350, 240)
        with open('macroScreen.tkmacro', 'r') as file:
            self.macroFile=file
            jsonData=self.macroFile.read()
            if jsonData:
                print("openfile")
                jsonObj=json.loads(jsonData)

                self.macroFile.close()
                self.loadMacroButtons(jsonObj)


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.MouseButton.RightButton:
                print(obj.objectName(), "Right click")
                print(obj.getData())
                modifiers = QApplication.keyboardModifiers()
                if modifiers != Qt.KeyboardModifier.ControlModifier:

                    pos_= obj.pos()+event.pos()
                    #action = self.menuBtnEdit.exec_(event.pos())
                    action = self.menuBtnEdit.exec_(self.mapToGlobal(pos_))
                    if(action==self.btnEditAction):
                       self.editMacroButton(obj)
                    if(action==self.btnDeleteAction):
                       self.deleteMacroButton(obj)
                    if(action==self.btnCloneAction):
                        self.cloneMacroButton(obj)

            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                print("leftBtn")
                self.appendCommandTolist(obj)

        if event.type()==QtCore.QEvent.Shortcut:
            print("shortCUt",obj.buttonData.commandText)
            self.appendCommandTolist(obj)
        return QtCore.QObject.event(obj, event)

    def appendCommandTolist(self,btn):
        cmds=btn.buttonData.commandText.split("\n")
        print("test===>",cmds)
        self.sp.macroCommands.append(cmds)

    def mousePressEvent(self,e):
        super().mousePressEvent(e)

        if e.buttons()==Qt.MouseButton.RightButton:
            action = self.menu.exec_(self.mapToGlobal(e.pos()))







    def dragEnterEvent(self, e):
        e.accept()
    def dragMoveEvent(self,e):
        x=e.pos().x()-int(e.source().width()/2)
        y=e.pos().y()-int(e.source().height()/2)
        e.source().move(x,y)
        e.accept()


    def dropEvent(self, e):
        position = e.pos()
        print(e.source().objectName())
        x=e.pos().x()-int(e.source().width()/2)
        y=e.pos().y()-int(e.source().height()/2)

        e.source().move(x,y)
        e.setDropAction(Qt.MoveAction)
        e.accept()



    """
      ___ ___  _  _ _____ _____  _______    __  __ ___ _  _ _   _
     / __/ _ \| \| |_   _| __\ \/ /_   _|__|  \/  | __| \| | | | |
    | (_| (_) | .` | | | | _| >  <  | ||___| |\/| | _|| .` | |_| |
     \___\___/|_|\_| |_| |___/_/\_\ |_|    |_|  |_|___|_|\_|\___/
    """

#parent widget menu
    def openMacroFile(self):

        fname,_ =QtWidgets.QFileDialog.getOpenFileName(self,'Open File')
        if fname:
            self.macroFile=open(fname,'r')
            jsonData=self.macroFile.read()
            print("openfile")
            jsonObj=json.loads(jsonData)

            self.macroFile.close()
            self.loadMacroButtons(jsonObj)

    def loadMacroButtons(self,jsonObj):
        for c in  self.findChildren(DDbutton):
            c.setParent(None)
            c.deleteLater()

        for btnObj in jsonObj:
            print(btnObj)
            btnDataObj=btnObj["buttonData"]

            macroButtonData=MacroButtonData()
            macroButtonData.buttonText=btnDataObj["buttonText"]
            macroButtonData.buttonSize=QtCore.QSize(btnDataObj["width"],btnDataObj["height"])
            macroButtonData.iconName=btnDataObj["iconName"]
            macroButtonData.commandText=btnDataObj["commandText"]
            macroButtonData.shortCut=btnDataObj["shortCut"]

            button = DDbutton("btn",self,macroButtonData)
            button.setParent(self)
            button.installEventFilter(self)
            self.layout().addChildWidget(button)
            button.move(btnDataObj["x"],btnDataObj["y"])
            button.setShortcut(btnDataObj["shortCut"])


    def saveMacroFile(self):
        print("save file")
        macroButtons= self.findChildren(DDbutton)

        for mb in macroButtons:
            mb.buttonData.pos=mb.pos()
            mb.buttonData.x=mb.buttonData.pos.x()
            mb.buttonData.y=mb.buttonData.pos.y()
            mb.buttonData.width=mb.width()
            mb.buttonData.height=mb.height()


        jsonData=json.dumps(macroButtons, default=lambda o: o.__dict__, sort_keys=True, indent=1)
        with open('macroScreen.tkmacro', 'w') as file:
            file.write(jsonData)

    def addMacroButton(self,pos):
        button = DDbutton('Go Home2', self,MacroButtonData())
        button.setParent(self)
        button.installEventFilter(self)
        self.layout().addChildWidget(button)
        button.move(self.mapFromGlobal(self.menu.pos()))
        print("add macro button")

    def seperateWindow(self):
        if self.parent():
            self.seperateWindowAction.setText("Merge With Parent Window")
            self.setParent(None)
            self.setMaximumWidth(115200)
            self.show()
        else:
            self.seperateWindowAction.setText("Seperate Window")
            self.setParent(self.sp)
            self.sp.serialControlWrapper.addWidget(self)
            self.setMaximumWidth(140)
#            self.show()




#macro buttons menu
    def editMacroButton(self,btn):
        print(btn.objectName(),"editbutton")
        dataBtn=btn.showEditDialog(self.mapToGlobal(btn.pos()))
        btn.setShortcut(dataBtn.shortCut)
        print(dataBtn)

    def cloneMacroButton(self,btn):
        button = DDbutton('Go Home2', self,copy.deepcopy(btn.buttonData))

        button.setParent(self)
        button.installEventFilter(self)
        self.layout().addChildWidget(button)
        button.move(btn.pos().x()+int(btn.width()/2),btn.pos().y()+int(btn.height()/2))
        print("clone macro button")



    def deleteMacroButton(self,btn):
        btn.setParent(None)
        btn.deleteLater()
        #self.layout().removeWidget(btn)#not safe
        print(btn.objectName(),"deleteButton")
