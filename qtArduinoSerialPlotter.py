'''
==============================================
Title           :   Qt Arduino Serial Plotter
Author          :   Oğuz Ali CAN
Version         :   1.0, 02.04.2022
Requirement  :
                    pip install PyQt5
                    pip install pyqtgraph
                    pip install qdarkstyle
                    pip install qtawesome
==============================================
'''

import random
from PyQt5 import QtWidgets, QtCore, QtSerialPort
import pyqtgraph as pg #fast tutorial: https://www.pythonguis.com/tutorials/plotting-pyqtgrap/
import sys
import re
import qdarkstyle
import qtawesome as qta #run qta-browser from a shell to start the icon browser


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
               
        self.setWindowTitle('Arduino Serial QtPlotter')
        self.setGeometry(50, 50, 940, 580)
        self.statusBar().showMessage('Not Connected...')
        
        self.isGraphsInitiated=False       
        self.graphs=[]
        self.bufferSize=250
        self.labelBuffer=[] 
        
        layout = QtWidgets.QVBoxLayout(self)

        gLayoutToolbox=QtWidgets.QGroupBox("toolbox")    
        hBoxLayoutTool=QtWidgets.QHBoxLayout(gLayoutToolbox)
       
        self.btnSend = QtWidgets.QPushButton(qta.icon('mdi.send'),'Send',gLayoutToolbox,clicked=self.send)           
        #self.btnSend.setIcon(fa5_icon)
        self.btnSend.setIconSize(QtCore.QSize(13, 13))
        self.btnSend.setStyleSheet("padding:4px;")
        self.btnSend.setDisabled(True)            

        self.cmbPorts=QtWidgets.QComboBox(gLayoutToolbox)
        self.cmbRates=QtWidgets.QComboBox(gLayoutToolbox)
        
        lblBufferSize = QtWidgets.QLabel(gLayoutToolbox,text="Buffer Size:")  
        cmbBufferSizes=QtWidgets.QComboBox(gLayoutToolbox)
        cmbBufferSizes.setMinimumWidth(80)
        cmbBufferSizes.addItems(str(i) for i in range(250,10000,250))
        def changeBufferSize():
            self.bufferSize=int(cmbBufferSizes.currentText())
        cmbBufferSizes.currentTextChanged.connect(changeBufferSize)
        
        
        btnRefresh = QtWidgets.QPushButton(qta.icon('fa.refresh'),'Refresh',gLayoutToolbox,clicked=self.refresh)
        btnRefresh.setIconSize(QtCore.QSize(13, 13))
        btnRefresh.setStyleSheet("padding:4px;")
        
        btnConnect = QtWidgets.QPushButton(qta.icon('mdi.connection'),'Connect',gLayoutToolbox,clicked=self.connect)
        btnConnect.setIconSize(QtCore.QSize(13, 13))
        btnConnect.setStyleSheet("padding:4px;")
            
        self.cbMarkers=QtWidgets.QCheckBox("Show Markers" ,gLayoutToolbox)
        self.cbMarkers.toggled.connect(self.setMarker)
        self.cbMarkers.setChecked(False)

        self.text = QtWidgets.QLineEdit('enter text',gLayoutToolbox)
        self.text.setMaximumWidth(200)       
        self.text.returnPressed.connect(self.btnSend.click)
        self.findSerialPorts()    
        layout.addWidget(gLayoutToolbox,5)
                
        hBoxLayoutTool.addWidget(self.cmbPorts)
        hBoxLayoutTool.addWidget(self.cmbRates)
        hBoxLayoutTool.addWidget(btnRefresh)    
        hBoxLayoutTool.addWidget(btnConnect)    
        space=QtWidgets.QSpacerItem(10,1,hPolicy=QtWidgets.QSizePolicy.Policy.Expanding,vPolicy=QtWidgets.QSizePolicy.Policy.Minimum)               
        hBoxLayoutTool.addItem(space)
        hBoxLayoutTool.addWidget(lblBufferSize)
        hBoxLayoutTool.addWidget(cmbBufferSizes)
        hBoxLayoutTool.addWidget(self.cbMarkers)
        hBoxLayoutTool.addWidget(self.text)                
        hBoxLayoutTool.addWidget(self.btnSend) 
        
        self.gLayoutPlotBox=QtWidgets.QGroupBox("plotbox")

        
        self.hBoxWrapper=QtWidgets.QHBoxLayout(self.gLayoutPlotBox)
        
         
        
        #self.vBoxLayout=QtWidgets.QVBoxLayout(self.gLayoutPlotBox)
        self.vBoxLayout=QtWidgets.QVBoxLayout()#for graphs
        self.vBoxColorsLayout=QtWidgets.QVBoxLayout()#for graphs
        self.hBoxWrapper.addLayout(self.vBoxLayout)    
        self.hBoxWrapper.addLayout(self.vBoxColorsLayout)           
        
        self.serialData = QtWidgets.QLabel(self.gLayoutPlotBox)       
        self.serialData.setWordWrap(True)
        self.mouseLeft=True
        def l(e):
            self.mouseLeft=True
        def e(e):
            self.mouseLeft=False
        self.serialData.leaveEvent=l
        self.serialData.enterEvent=e
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.serialData)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(50)

        layout.addWidget( self.gLayoutPlotBox,95)
        layout.addWidget(self.scroll)

        widget = QtWidgets.QWidget()       
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def setColors(self,widget):
        color = QtWidgets.QColorDialog.getColor()
        pen = pg.mkPen(color=color)
        self.sender().setStyleSheet("background-color:"+color.name())
        indexs=self.sender().objectName().split(",")
        self.graphs[int(indexs[0])]["lines"][int(indexs[1])]["plot"].setPen(pen)
        

    def parseTheLine(self,text):        
        #text="pltr#[10,20,lbl1:10,20,lbl2]#[10,30,lbl3:20,30,lbl4]"        
        if not text.__contains__("pltr#"):
            return
        else:
            text=str(text).replace("pltr#","")

        strGraphs=text.split('#')       
        for i in range(len(strGraphs)):
            strGraph =strGraphs[i]                              
            strLines=re.search(r'[^\[]+(?=\])',strGraph)
            
            if not self.isGraphsInitiated:
                graphWidget = pg.PlotWidget(self.gLayoutPlotBox)
                #graphWidget = pg.plot()
                graphWidget.showGrid(x=True,y=True,alpha=0.5)
                graphWidget.addLegend()

                
                self.vBoxLayout.addWidget(graphWidget)
                graph={"lines":[],"graphWidget":None,"curvePoint":None}                           
                graph["graphWidget"]=graphWidget                
                self.graphs.append(graph)
                
           
            graph=self.graphs[i]           
            if not strLines:
                return
           
            strLines=strLines[0].split(":")
            
            for j in range(len(strLines)):
                strLine=strLines[j]
                strLineData= strLine.split(",")
                                 
                if not self.isGraphsInitiated:
                    label="lbl"+str(i+j)
                    if len(strLineData)>2 : label=strLineData[2] 

                    line={"x":[],"y":[],"label":label,"plot":None}                    
                    #pen = pg.mkPen(color=random.choices(range(256), k=3)) 
                    randColor=""
                    if len(strLineData)>3:
                        randColor="#"+strLineData[3]
                    else:                      
                        randColor="#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])


                    pen = pg.mkPen(color=randColor)    
                    line["plot"]=graph["graphWidget"].plot([],[],name=label,width=2,symbol="s",pen=pen)                    
                    if self.cbMarkers.isChecked():
                        line["plot"].setSymbolSize(5) 
                    else:
                        line["plot"].setSymbolSize(0)  
                    graph["lines"].append(line) 
                    
                    
                    lblColor=QtWidgets.QPushButton()
                    lblColor.setFixedWidth(10)
                    lblColor.setFixedHeight(10)
                    lblColor.setObjectName(str(i)+","+str(j))                   
                    lblColor.setStyleSheet("background-color:"+randColor)                    
                    lblColor.clicked.connect(self.setColors)
                    self.vBoxColorsLayout.addWidget(lblColor)

                    
                    def mouseMoved(e):
                        if not self.isGraphsInitiated:
                            return
                        
                        for graph in self.graphs:
                            vb=graph["graphWidget"].plotItem.vb
                            if graph["graphWidget"].sceneBoundingRect().contains(e):
                                mouse_point=vb.mapSceneToView(e)
                                #print(e.sender().objectName())
                                if self.sender()==graph["graphWidget"].scene():                                
                                    self.gLayoutPlotBox.setTitle("plotbox "+f"X： {mouse_point.x()} Y: {mouse_point.y()}")
                               
                    
                    graph["graphWidget"].scene().sigMouseMoved.connect(mouseMoved)
                   
                    
                            
                line= graph["lines"][j]                    
                x=strLineData[0]               
                y=strLineData[1]
                if(len(line["x"])>self.bufferSize):  
                    del  line["x"][0]           
                    del  line["y"][0]           
                line["x"].append(float(x))
                line["y"].append(float(y))
        self.isGraphsInitiated=True          
        
    def setMarker(self):
        for g in self.graphs:               
                for l in g["lines"]:                   
                    if self.sender().isChecked():
                        l["plot"].setSymbolSize(5) 
                    else:
                        l["plot"].setSymbolSize(0)      

    @QtCore.pyqtSlot()
    def receive(self):        
        while (self.serial.canReadLine()):
            text=self.serial.readLine().data().decode()
            self.labelBuffer.append(text)
            if len(self.labelBuffer)>(self.bufferSize/4):
                del self.labelBuffer[0]                     
            #self.serialData.setText(self.serialData.text()+text)
            self.serialData.setText("".join(self.labelBuffer))
            scrollBar = self.scroll.verticalScrollBar()
            if self.mouseLeft:
                scrollBar.setValue(scrollBar.maximum())
            text = text.rstrip('\r\n')                       
            self.parseTheLine(text)
            for i in range(len(self.graphs)):
                graph =self.graphs[i]
                for j in range(len(graph["lines"])):
                    line=graph["lines"][j]                                      
                    line["plot"].setData(line["x"],line["y"])            
           
    @QtCore.pyqtSlot()
    def send(self):   
       
        self.serial.write(str(self.text.text()+"\n").encode())
        self.serial.flush()
    
    @QtCore.pyqtSlot()
    def connect(self):
    
        if hasattr(self,'serial'):
            if self.serial.isOpen():                
                self.serial.close()                
                del self.serial                

        self.clearHistory()

        self.serial= QtSerialPort.QSerialPort(self.cmbPorts.currentText(),baudRate=self.cmbRates.currentData(),readyRead=self.receive)
              
        self.serial.open(QtCore.QIODevice.ReadWrite)   
        
        #reset the arduino
        self.serial.setDataTerminalReady(False)
        self.serial.setDataTerminalReady(True)    
        
        self.statusBar().showMessage('Connected...')
        self.btnSend.setDisabled(False)

    def clearHistory(self):
        self.serialData.clear()
        self.graphs.clear()
        self.isGraphsInitiated=False
        self.gLayoutPlotBox.setTitle("plotbox")
       

        for cnt in reversed(range(self.vBoxColorsLayout.count())):          
            widget = self.vBoxColorsLayout.takeAt(cnt).widget()
            if widget is not None:                 
                widget.deleteLater()

        for cnt in reversed(range(self.vBoxLayout.count())):          
            widget = self.vBoxLayout.takeAt(cnt).widget()
            if widget is not None:                 
                widget.deleteLater()

        self.statusBar().showMessage('Not Connected...')
        self.btnSend.setDisabled(True)

    @QtCore.pyqtSlot()
    def refresh(self):
        if hasattr(self,'serial'):        
            if self.serial.isOpen():
                #reset the arduino
                self.serial.setDataTerminalReady(False)
                self.serial.setDataTerminalReady(True) 
                self.serial.close()          
        
        self.clearHistory()        
        self.findSerialPorts()

    def closeEvent(self, event):
        if hasattr(self,'serial'):
             if self.serial.isOpen(): 
                 #reset the arduino
                self.serial.setDataTerminalReady(False)
                self.serial.setDataTerminalReady(True)
                self.serial.close()
                print("Serial Port Closed")
               


    def findSerialPorts(self):
        
        info_list = QtSerialPort.QSerialPortInfo()
        serial_list = info_list.availablePorts()
        serial_ports = [port.portName() for port in serial_list]
        '''        
        serial_ports_with_detail=[]
        for port in serial_ports:
            portDetail=port
            portinfo = QtSerialPort.QSerialPortInfo(portDetail)
            if portinfo.hasProductIdentifier():
                portDetail +="-"+ str(portinfo.vendorIdentifier())
            if portinfo.hasVendorIdentifier():
                portDetail +="-"+ str(portinfo.productIdentifier())
            serial_ports_with_detail.append(portDetail)
        '''
       
        print(serial_ports)       
        self.cmbPorts.clear()
        self.cmbPorts.addItems(serial_ports)
        
        self.cmbRates.clear()    
        self.cmbRates.addItem("1200",userData=QtSerialPort.QSerialPort.BaudRate.Baud1200)
        self.cmbRates.addItem("2400",QtSerialPort.QSerialPort.BaudRate.Baud2400)
        self.cmbRates.addItem("4800",QtSerialPort.QSerialPort.BaudRate.Baud4800)
        self.cmbRates.addItem("9600",QtSerialPort.QSerialPort.BaudRate.Baud9600)
        self.cmbRates.addItem("19200",QtSerialPort.QSerialPort.BaudRate.Baud19200)
        self.cmbRates.addItem("38400",QtSerialPort.QSerialPort.BaudRate.Baud38400)
        self.cmbRates.addItem("57600",QtSerialPort.QSerialPort.BaudRate.Baud57600)
        self.cmbRates.addItem("115200",QtSerialPort.QSerialPort.BaudRate.Baud115200)
        self.cmbRates.setCurrentText("115200")
        

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
w = MainWindow()
w.show()
sys.exit(app.exec_())

