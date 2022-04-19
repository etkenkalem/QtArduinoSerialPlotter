#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this program, we can press on a button with a left mouse
click or drag and drop the button with  the right mouse click.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
import os


import qdarkstyle
from PyQt5.QtCore import Qt, QMimeData,QPoint,QSize
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QDialogButtonBox, QDialog, QLabel, QVBoxLayout,QHBoxLayout, QLineEdit,QMenu,QPlainTextEdit,QFormLayout

import qtawesome as qta #run qta-browser from a shell to start the icon browser


class MacroButtonData(object):
    def __init__(self):
        self.buttonText=""
        self.commandText=""
        self.iconName=""
        self.shortCut=""
        self.width=120
        self.height=55
        self.buttonSize=QSize(120,55)
        self.x=0
        self.y=0
        self.buttonPos=QPoint(0,0)



class DDbutton(QPushButton):

    def __init__(self, title, parent,initialData=MacroButtonData()):
        super().__init__(title, parent)

        self.buttonData=initialData
        self.refresh()



    def refresh(self):
        self.setText(self.buttonData.buttonText)
        self.resize(self.buttonData.buttonSize)
        try:
            self.setIcon(qta.icon(self.buttonData.iconName,color="white",scale_factor=0.8))
        except:
            self.setIcon(qta.icon("mdi.help",color="white",scale_factor=0.8))
        s= min(self.height(),self.width())
        s-=4
        self.setIconSize(QSize(s,s))


    def showEditDialog(self,pos):
        print("show edit dialog")

        self.buttonData=CustomDialog.get_data(self,pos,self.getData())
        self.refresh()




        return self.buttonData

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.MouseButton.RightButton:
            return
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            self.move(self.mapFromGlobal(e.pos()))
            mimeData = QMimeData()

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.rect().topLeft())
            dropAction = drag.exec_(Qt.DropAction.MoveAction)





    def mousePressEvent(self, e):
            if e.button() == Qt.RightButton:
                print("nebu")
            #dialog= CustomDialog(self)
            #dialog.move(e.globalX(),e.globalY()+50)

    '''
    def keyPressEvent(self,e):
        super().keyPressEvent(e)
        print(e.key())
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.moveMode=1
    def keyReleaseEvent(self,e):
        super().keyReleaseEvent(e)
        self.moveMode=0
    '''



    def getData(self):
        return self.buttonData






class CustomDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Macro Button")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.txtCmd=QPlainTextEdit("G28\n",self)
        self.txtCmd.setFixedHeight(80)


        self.txtBtnText = QLineEdit("Home")
        self.txtShortcut = QLineEdit("Ctrl+w")

        hBox=QHBoxLayout()
        self.txtIconName =QLineEdit("fa.refresh")
        icn=qta.icon("fa.search",color="white",scale_factor=0.8)
        self.btnIconShow=QPushButton(icon=icn,text="")
        self.btnIconShow.clicked.connect(lambda e: os.system("qta-browser &"))
        hBox.addWidget(self.txtIconName)
        hBox.addWidget(self.btnIconShow)


        hBoxSize=QHBoxLayout()
        self.txtButtonWidth=QLineEdit("120")
        self.txtButtonHeight=QLineEdit("70")
        hBoxSize.addWidget(self.txtButtonWidth)
        hBoxSize.addWidget(self.txtButtonHeight)


        self.formLay=QFormLayout()
        self.formLay.addRow(QLabel("Button Text"),self.txtBtnText)
        self.formLay.addRow(QLabel("Command"),self.txtCmd)
        self.formLay.addRow(QLabel("Shortcut"),self.txtShortcut)
        self.formLay.addRow(QLabel("Icon"),hBox)
        self.formLay.addRow(QLabel("Size"),hBoxSize)

        self.layout.addLayout(self.formLay)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)


    def get_data(parent=None,position=QPoint(100,100),btnData=MacroButtonData()):
        dialog=CustomDialog(parent)
        dialog.txtCmd.setPlainText(btnData.commandText)
        dialog.txtIconName.setText(btnData.iconName)
        dialog.txtBtnText.setText(btnData.buttonText)
        dialog.txtShortcut.setText(btnData.shortCut)
        dialog.txtButtonWidth.setText(str(btnData.buttonSize.width()))
        dialog.txtButtonHeight.setText(str(btnData.buttonSize.height()))


        dialog.resize(360,150)
        dialog.move(position.x()-170,position.y())
        res= dialog.exec_()
        if res:
            btnData.commandText=dialog.txtCmd.toPlainText()
            btnData.iconName=dialog.txtIconName.text()
            btnData.buttonText=dialog.txtBtnText.text()
            btnData.shortCut=dialog.txtShortcut.text()
            btnData.buttonSize=QSize(int(dialog.txtButtonWidth.text()),int(dialog.txtButtonHeight.text()))
            btnData.height=int(dialog.txtButtonHeight.text())
            btnData.width=int(dialog.txtButtonWidth.text())


        return btnData
