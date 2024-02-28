# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 23:27:22 2021

@author: April 2018 Update
"""
"""
Version 3.1 filtrando los paquetes de 10mil muestras

Un método como initUI restablece las propiedades de los widgets existentes y
 podría llamarse varias veces. Pero setupUi construye los widgets (y sus diseños),
 y solo debe llamarse una vez.

Insertando un PlotWidget de Pyqtgraph en un Layout de PyQt5
desde qtDesigner utilizando un widgwt Graphics View, boton derecho
widgets promocionados
nombre de la clase promocionada= PlotWidget
Archivo de cabecera= pyqtgraph
presionar "AÑADIR"
presionar "PROMOCIONAR"
Ayuda: http://www.pyqtgraph.org/documentation/how_to_use.html#command-line-use
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog, QStyleFactory
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer,QDateTime, QThread, pyqtSignal
#import PyQt5.QtWidgets
from scipy import signal
from scipy.signal import find_peaks #la funcion find_peaks para encontrar los picos

import Funciones_Oximetro_1_0 as fc
import pyqtgraph as pg
import numpy as np
import pandas as pd
import csv
import sys, socket, struct
import time
from random import randint
import mne
import functools
import openpyxl
import tempfile
from os import remove
#print(QStyleFactory.keys())
TIME_LIMIT = 100

class VentanaPrincipal(QMainWindow):

    def __init__(self):
        super(VentanaPrincipal, self).__init__()
        self.ip = '192.168.4.1'      #'127.0.0.1' 192.168.4.1         
        self.port = 9000  #esto es un atributo        
        #-------ventana principal---------------------------
        loadUi('Oximetro_1_0.ui', self)
        #ocultamos los dockWidgets
        self.dwinfo.hide()
        #Mostramos la hora actual del sistema
        time_= QDateTime.currentDateTime()
        timeDisplay = time_.toString('dddd dd-MM-yyyy hh:mm ')
        self.lblfecha.setText("Fecha: "+timeDisplay)
        
        #-----Inicializacion de variables necesarias---------------------------
        PRF = float(self.txtPRF.text()) # fecuencia de muestreo predeterminada
        Duty = float(self.txtDuty.text()) #Duty cicle predeterminado
        self.flag_datos = False #flag de disposicion de datos para graficar
        self.numero_canales = 2
        self.autorange = 0
        
        """        
-------------------------------------------------------------------------------
        """
        #---------timer fecha y nivel bateria---------------------------------
        self.timer0 = QTimer() # creamos un objeto QTimer que actualiza la hora del
        #sistema y el nivel de bateria cada 60 segundos
        self.timer0.setInterval(60000)
        self.timer0.timeout.connect(self.timer0_timeout) 
        """conectamos el timer con el metodo
          q realizara la tarea cuando finalice la cuenta"""
        #---------timer actualizacion grafico----------------------------
        self.timer1 = QTimer()  #timer que actualiza las curvas del grafico
        self.timer1.setInterval(200) #250 s/seg son 400 ms
                                    #500 s/seg  200 ms                                
                                    #1ks/seg    100 ms
        self.timer1.timeout.connect(self.update_plot_data)
        """        
----------------Accion de los Botones------------------------------------------
        """        
        
        #--Menu "Abrir"----------------
        self.actionabrir.triggered.connect(self.cargar_datos)
        #-----Acciones de los botones del menu principal----------------
        self.btnConectar.clicked.connect(self.conectar_handler) #boton conectar-desconectar    
        self.pblimpiarpantalla.clicked.connect(self.limpiar_pantalla) #boton limpiar pantalla
        self.pbinfo.clicked.connect(self.info)    #boton info , muestra informacion del archivo cargado    
            
        #---pestaña Configuracion--------------------
             #----pestaña diagnosticar----------------------------------
        self.btnResetAFE.clicked.connect(self.resetAFE) #boton reset del afe
        self.btnDiagnosticar.clicked.connect(self.diagnosticar) #boton diagnostico de conexion del afe
            #----pestaña Etapa TX----------------------------------
        """accion de la señal de los Slider:
            escribir el valor de corriente en lblCurrent2 y lblCurrent1"""
        self.Slider1.valueChanged.connect(self.modificarlbl1) #deslizables de intensidad de corriente a los led
        self.Slider2.valueChanged.connect(self.modificarlbl2)
        self.btnSetearTx.clicked.connect(self.setearTx)    
            
            #----pestaña Etapa RX----------------------------------
        """ responder a la accion de Slider3 en lblCurrent3"""
        self.Slider3.valueChanged.connect(self.modificarlbl3) #deslizable seleccion del capacitor
        self.btnSetearRx.clicked.connect(self.setearRx) #boton de seteo de recepcion 
            
            #----pestaña Etapa control de Tiempos------------------------------
        """leer los widgets txtPRF, txtDuty, txtPRP, calcular los tiempos
        y mostarlos en los txt0 a txt27"""
        #Lista de los txt donde se visualizaran los tiempos seteados en base a PRF y DutyCicle 
        self.labels_tiempos = [self.txt1,self.txt2,self.txt3,
                               self.txt4,self.txt5,self.txt6,self.txt7,
                               self.txt8,self.txt9,self.txt10,self.txt11,
                               self.txt12,self.txt13,self.txt14,self.txt15,
                               self.txt16,self.txt17,self.txt18,self.txt19,
                               self.txt20,self.txt21,self.txt22,self.txt23,
                               self.txt24,self.txt25,self.txt26,self.txt27,
                               self.txt28,self.txtPRP]
        self.btnSetearTiempos.clicked.connect(self.setearTiempos) #boton de seteo de tiempos    
        
                    
        #----------------------pestaña guardar---------------------------------
        self.pbguardarprueba.clicked.connect(self.guardar_prueba) #Boton para seleccionar donde guardar los datos
        #posiblemete obsoleto y se coloca un desplegable al presionar detener de la pestaña visualizacion
        #que pregunte si desea guardar los datos y que se despliegue un explorador para selecion de lugar y nombre de archivo.
        self.flag_guardar_datos = False
        #self.flag_guardar_config = False
        self.flag_guardar_observaciones = False
        
        
        #-------------------pestaña visualizar---------------------------------
        """pestaña Temporal y FFt se actualizan simultaneamente"""
        #pestaña fft se evaluara su utilizacion.
        #boton iniciar
        self.pbiniciarprueba.clicked.connect(self.Iniciar_handler)             #Requiere conexion o modo offline
        #boton pausar
        self.pbpausarprueba.clicked.connect(self.Pausa_handler)                #Requiere conexion o modo offline
        #boton detener
        self.pbdetenerprueba.clicked.connect(self.Detener)                     #Requiere conexion o modo offline
        
        #-------configuracion de seteos de las pestañas de  visualizacion
        #self.gvtemporal.setTitle("Rojo")
        #self.gvtemporal_1.setTitle("InfraRojo")
        self.gvfft.setTitle("FFT")
        self.gvtemporal.addLegend(offset=(900, 10))
        #self.gvtemporal.getAxis('left').setTextPen(pg.mkPen(color=(0, 0, 0, 0)))
       # self.gvtemporal_2.getAxis('left').setTextPen(pg.mkPen(color=(0, 0, 0, 0)))
        self.gvfft.getAxis('left').setTextPen(pg.mkPen(color=(0, 0, 0, 0)))
        #self.gvtemporal_1.addLegend(offset=(900, 10))
        self.gvfft.addLegend(offset=(900, 10))
        self.gvtemporal.showGrid(x=True,y=True, alpha=0.6)
        #self.gvtemporal_1.showGrid(x=True,y=True, alpha=0.6)
        self.gvtemporal_2.showGrid(x=True,y=True, alpha=0.6)
        self.gvfft.showGrid(x=True,y=True, alpha=1)
        self.gvfft.setLogMode(x=False, y=True) #
        self.gvfft.getPlotItem().ctrl.fftCheck.setChecked(True)
        self.gvfft.setXRange(0,25 )
        #self.gvtemporal_2.setTitle("Continua")
        self.gvtemporal.setXRange(0,20 )
        #self.gvtemporal_1.setXRange(0,20 )
        self.gvtemporal_2.setXRange(0,20 )
        self.gvfft.setLabel('bottom', 'Frec', units='Hz')
        self.gvtemporal.setLabel('bottom', 'Time', units='s')
        #self.gvtemporal_1.setLabel('bottom', 'Time', units='s')
        self.gvtemporal_2.setLabel('bottom', 'Time', units='s')
        #self.gvtemporal.AxisItem(orientation='left', text="mV")
        
        
       
    
    
    
    #-----------metodos de accion de los botones---------------------------------------------
    #---menu abrir--debe permitir cargar datos de estudio previo
    def cargar_datos(self):
        print("cargar datos")
        #debe reemplazarse .CSV por .xlsx que sera el nuevo formato de almacenamiento
        #luego utilizar pd.read_excel('data.xlsx') para cargar los datos
        self.archivo_offline, _ = QFileDialog.getOpenFileName(self, 'Abrir archivo', 'C:/', 'Text files (*.xlsx , *.xls)')
        print(self.archivo_offline,"\n", _)
        pass
     
    #--menu principal----------------------------------------------------------
    def conectar_handler(self):   
        """metodo que cambia el estado del boton conectar
            y llama al metodo conectar o desconectar"""
        if self.btnConectar.isChecked():
            self.btnConectar.setText('Desconectar')
            self.btnConectar.setStyleSheet("color: black; background-color : red; ")
            self.Conectar()
        else:
            
            self.btnConectar.setText('Conectar')
            self.btnConectar.setStyleSheet("color: black; background-color: green; ")  #border: none;
            self.Desconectar()
    
    def Conectar(self): 
        """Metodo del boton conectar
        #crear socket y conectarme al dispositivo 
        #enviar un mensaje con la configuracion predeterminada del AFE
        #solicitar estado de la bateria
        #el mensaje devuelto sera de 3 bytes [0XFF, 0X01, nivel de bateria]
        #leer el mensaje y actualizar el valor del nivel de bateria 
        #activar un timer de 60 segundos encargado de actualizar la hora 
        y solicitar al dispositivo el nivel de bateria
        """
        encabezado = [0XFF, 0X01]  #mensaje tipo [FF,01] 
        mensaje = encabezado
        self.comando = 'conectar'
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_cliente.connect((str(self.ip), int(self.port)))
        self.socket_cliente.send(bytearray(mensaje))
        print("mensaje enviado")
        #leer mensaje
        recibido = self.socket_cliente.recv(3)
        print(recibido)
        verificar = 0xFF
        if verificar == recibido[0] :
            print("verificacion correcta")
            #solo actualizar nivel de bateria y fecha
            self.nivelbateria = int(recibido[2])      #int
            #self.barBat.setMaximum(76,100)
            self.barBat.setValue(self.nivelbateria)
        print("estoy en conectar")
        print(self.nivelbateria)
        
        #self.timer0.start() #le indicamos que inicie el timer y le pasamos la cantidad 
                                # de ms que debera contar hasta finalizar y lanzar timeout    
    
    
    def Desconectar(self): #metodo del boton desconectar
        #enviar desconectar
        #dentener los timer
        self.comando = 'desconectar'
        encabezado = [0XFF, 0X02]
        mensaje = encabezado
        self.socket_cliente.send(bytearray(mensaje))
        print("cerrando socket")
        self.timer0.stop() #Detenemos el timer0
        self.timer1.stop() #self.socket_cliente.close()
        print("socket cerrado")
        #sys.exit(0) #habria q volver a probar esto
      
    def limpiar_pantalla(self):
        #solo son 2 canales siempre, clear elimina las curvas
        if self.ckmodo_offline.isChecked():
            self.gvtemporal.clear()
            self.gvtemporal_2.clear()
            self.gvfft.clear()
        else:
            self.gvtemporal.clear()
            self.gvtemporal_2.clear()
            self.gvfft.clear()
            
            pass
        QApplication.processEvents()
        pass
    
        #funcion del modo offline para mostrar info del archivo seleccionado
    def info(self,):
        # modificar *.csv por .xlsx dado el cambio de tipo de archivo
        #incluso no se necesitan los canales
        if self.ckmodo_offline.isChecked():#, header=None
            df1 = pd.read_excel(self.archivo_offline)
            y = np.array(df1)
            encabezado=y[0,:]
            canales = [int(x) for x in encabezado if np.isnan(x) == False]
            print(canales)
            archivotxt = self.archivo_offline.replace("_datos.xlsx",".txt")
            archivo = open(archivotxt, "r")
            linea1 = archivo.readline() #fecha
            linea2 = archivo.readline() #texto fecuencia de muestreo
            sFreq = int(archivo.readline())
            N = y.shape[0] -1
            duracion = N/sFreq
            
            archivo.close()
            self.txtinfo.setText("frecuencia de muestreo: "+str(sFreq)+ '\n'+"Canales activos: "+ str(canales)+'\n'+"duracion seg: "+str(duracion))#, sFreq, '\n',"Canales activos", canales,'\n')
        pass 
    #---pestaña Configuracion--------------------
        #----pestaña diagnosticar----------------------------------
    def resetAFE(self):
        """enviar solicitud de reseteo del AFE"""
        #debe enviar mensaje [0XFF, 0X03]
        #el mensaje devuelto sera de 2 bytes [0XFF, 0X03]
        #el dispositivo , luego del reset debe volver a escribir los registros
        #con los valores de inicializacion
        #devuelve [0XFF, 0X03] verificando la accion
        self.comando = 'resetAFE'
        encabezado = [0XFF, 0X03]
        CONTROL0 = 0x00
        RESET = [0x00,0x00,0x08]
        CONTROL0_VAL = RESET #MSB...LSB
        mensaje = bytearray(encabezado) # + [CONTROL0] + CONTROL0_VAL
        print(mensaje)
        self.socket_cliente.send(bytearray(mensaje))
        recibido = self.socket_cliente.recv(2)
        print(recibido)
        pass
    def diagnosticar(self):
        """enviar configuracion de registros para iniciar el diagnostico
        recibir el mensaje con el resultado del diagnostico
        cambiar el color del fondo de lo ck12 a ck0"""
        #enviar mensaje [0XFF, 0X04]
        #el mensaje devuelto sera de 5 bytes [0XFF, 0X04,DIAG]
        #DIAG = 0x30 es de 3 bytes
        self.comando = 'resetAFE'
        encabezado = [0XFF, 0X04]
        CONTROL0 = 0x00
        DIAG_EN    = [0x00,0x00,0x04]
        mensaje = bytearray(encabezado) # + [CONTROL0] + DIAG_EN
        #print(mensaje)
        
        self.socket_cliente.send(mensaje)
        recibido = self.socket_cliente.recv(5)
        #print(recibido)
        byte2 = recibido[3]
        #print(bin(byte2))
        byte1 = recibido[4]
        #print(bin(byte1))
        #bit12 a 0 
        
        PD_ALM = (16 & byte2) 
        LED_ALM = 8 & byte2 
        LED1OPEN = 4 & byte2
        LED2OPEN = 2 & byte2
        LEDSC = 1 & byte2
        OUTPSHGND = 128 & byte1
        OUTNSHGND = 64 & byte1
        PDOC = 32 & byte1
        PDSC = 16 & byte1
        INNSCGND = 8 & byte1
        INPSCGND = 4 & byte1
        INNSCLED = 2 & byte1
        INPSCLED = 1 & byte1
        
        LIST_DIAG = [  PD_ALM,
        LED_ALM ,
        LED1OPEN,
        LED2OPEN ,
        LEDSC ,
        OUTPSHGND,
        OUTNSHGND,
        PDOC ,
        PDSC ,
        INNSCGND ,
        INPSCGND ,
        INNSCLED,
        INPSCLED ]
        
        LIST_CK = [self.ck12,self.ck11,self.ck10,self.ck9,self.ck8,self.ck7,self.ck6,self.ck5,self.ck4,self.ck3,self.ck2,self.ck1,self.ck0 ]  
        i = 0
        #print(LIST_DIAG)
        for x in LIST_DIAG:
            if x > 0:
                LIST_CK[i].setStyleSheet("QCheckBox::indicator"
                                   "{"
                                   "background-color : red;"
                                   "}")
            else:
                LIST_CK[i].setStyleSheet("QCheckBox::indicator"
                                   "{"
                                   "background-color : lightgreen;"
                                   "}")
            i+=1    
       
        pass
    
    #----pestaña Etapa TX---------------------------------------------
    def modificarlbl1(self):
        val = self.Slider1.value()
        val = val/256*50
        self.lblCurrent1.setText(str("{:.2f}").format(val))
        pass
    def modificarlbl2(self):
        val = self.Slider2.value()
        #print(type(val))
        val = val/256*50
        self.lblCurrent2.setText(str("{:.2f}").format(val))
        pass
    
    def setearTx(self):
        """Leer los widgets Slider2 y Slider1 y generar el valor del registro
        enviar el registros LEDCNTRL y 
        recibir confirmacion"""
        #enviar mensaje [0XFF, 0X05,LEDCNTRL, LEDCNTRL_VAL]
        #el mensaje devuelto sera de 2 bytes [0XFF, 0X05]
        #LEDCNTRL = 0x22 y LEDCNTRL_VAL es de 3 bytes
        LEDCNTRL = 0x22
        Byte1 = self.Slider2.value() #bits 7:0
        Byte2 = self.Slider1.value() #bits 15:8
        Byte3 = 0x01 #bits 23:16
        print(hex(Byte3),hex(Byte2),hex(Byte1))
        LEDCNTRL_VAL = [Byte3,Byte2,Byte1] 
        encabezado = [0XFF, 0X05] 
        mensaje = bytearray(encabezado + [LEDCNTRL] + LEDCNTRL_VAL)
        print(mensaje)
        self.socket_cliente.send(mensaje)
        recibido = self.socket_cliente.recv(2)
        print(recibido)
        pass
        #----pestaña Etapa RX----------------------------------------------
    def modificarlbl3(self):
        val = self.Slider3.value()
        val_pF = fc.list_cf[val]
        self.lblCurrent3.setText(str(val_pF)+" pF")
        pass
    def setearRx(self):
        """leer los widgets ckEtapa2 , cbGetapa2, cbCorriente, cbRF, Slider3
        enviar configuracion de los registros TIA_AMB_GAIN y
        recibir confirmacion"""
        #enviar mensaje [0XFF, 0X05,TIA_AMB_GAIN , TIA_AMB_GAIN_VAL]
        #el mensaje devuelto sera de 2 bytes [0XFF, 0X06]
        #TIA_AMB_GAIN = 0x21 y TIA_AMB_GAIN_VAL es de 3 bytes
        TIA_AMB_GAIN = 0x21
        uA = self.cbCorriente.currentIndex() #bits 19:16
        Etapa2 = self.ckEtapa2.checkState() #bit 14
        if Etapa2 ==2:
            Etapa2 = 1
        GEtapa2 = self.cbGetapa2.currentIndex() #bits 10:8
        """ RFxCF < RxSampleTime/10  donde RxSampleTime = (LED2ENDC - LED2STC)/4Mhz"""
        CF = self.Slider3.value() #bits 7:3
        RF = self.cbRF.currentIndex() #bits 2:0
        tau = RF*CF*1e3
        print("verificar esto : ",tau)
        CF = CF<<3
        Byte1= CF|RF
        Etapa2= Etapa2<<6
        Byte2 = Etapa2|GEtapa2
        Byte3 = uA
        print(hex(Byte3),hex(Byte2),hex(Byte1))
        TIA_AMB_GAIN_VAL = [Byte3,Byte2,Byte1]
        encabezado = [0XFF, 0X06] #setearRx tipo 06
        mensaje = bytearray(encabezado + [TIA_AMB_GAIN] + TIA_AMB_GAIN_VAL)
        print(mensaje)
        self.socket_cliente.send(mensaje)
        recibido = self.socket_cliente.recv(2)
        print(recibido)
        pass
    
        #----pestaña Etapa control de Tiempos------------------------------
    def setearTiempos(self):
        """enviar configuracion de los registros 0x01 a 0x1D  y
        recibir confirmacion, dado que el tamaño de la lista de timepos"""
        #enviar mensaje [0XFF, 0X05,len_dato , dato]
        #el mensaje devuelto sera de 2 bytes [0XFF, 0X07]
        #registoros del  0x01 al 0x1D, la lista es de tamaño variable en valorores decimal
        #para resolverlo, 'encapsulamos, enviamos tamaño y leemos del otro lado y desencapsulamos "esto no funciono"
        #planteamos definir un metodo q convierta en 3 bytes cada decimal, de modo que del otro lado, conociendo 
        #el orden de envio de los datos solo restaria escribir los registros con los bytes enviados
        PRF = float(self.txtPRF.text())
        Duty = float(self.txtDuty.text())
        Tiempos= fc.List_time(PRF,Duty)
        #print(Tiempos)
        RxSampleTime = (Tiempos[1] - Tiempos[0])/4e-3
        print("verificar esto : ",RxSampleTime/10)                             #debuger 
        dato = []
        for i in range(len(Tiempos)):
            self.labels_tiempos[i].setText(str(Tiempos[i]))
            dato += self.int32to3bytes(Tiempos[i])
        #for i in range(0, len(dato), 3) :
            #print(dato[i:i+3])
            
        #print(dato)  #tamaño del dato = 87 bytes                                                           #debuger
        #len_dato = len(dato)
        #print(len_dato)                                                        #debuger
        encabezado = [0XFF, 0X07]
        mensaje = bytearray(encabezado + dato)
        #print(mensaje)                                                         #debuger
        self.socket_cliente.send(mensaje)
        recibido = self.socket_cliente.recv(2)
        print(recibido)        
        pass
    #--metodo para convertir int32 en 3 bytes----
    def int32to3bytes(self, int_32):
        """
        -Metodo que toma un entero de 32 bits como argumento
        -Devuelve una lista con los 3 Bytes del entero pasado

        Parameters
        ----------
        int_32 : TYPE intero de 32 bits
            DESCRIPTION.

        Returns
        -------
        list
            Retorna una lista de 3 Bytes del entero pasado.

        """
        data = int_32
        byte3 = data >>16
        byte2 = (data & 0x00FFFF) >>8
        byte1 = (data & 0x0000FF)
        return [byte3,byte2,byte1] 
    
    
   
    #----------------------pestaña guardar-------------------------------------
    def guardar_prueba(self):#debe mostrar el explorador de windows.
        """
        -Metodo q debe llamarse al seleccionar "si" de un cartel desplegable al presionar detener
        -nombrar el archivo (.txt) y seleccionar donde guardarlo.
        -En el se guardara "fecha", Frecuencia de muestro, 
        - almacenar fecha
        -frecuencia de muestreo
        -observaciones
        -si el checkbox de guardar datos esta seleccionado, crear el archivo 
        CSV donde se guardaran los datos
        """
        # esto deberia desplegarse al presionar detener
        #y guardar el archivo (.txt) y temporal csv como xlsx
        time_=QDateTime.currentDateTime()
        self.hora_estudio=time_.toString('dddd dd-MM-yyyy hh:mm ')
        self.archivo_configuracion, _ = QFileDialog.getSaveFileName(self, 'Guardar archivo', 'C:/', 'Text files (*.txt)')
        print(self.archivo_configuracion, _)
        RF = self.cbRF.currentText(); print(RF)
        CF = self.lblCurrent3.text() ; print(CF)
        led1 = self.lblCurrent1.text()
        led2 = self.lblCurrent2.text()
        
        #ceacion de archivo que almacena configuración (.txt)
        
        with open(self.archivo_configuracion, 'wt') as f:
            f.write("Fecha: "+self.hora_estudio + "\n")
            f.write("Frecuencia de muestreo " + "\n")
            f.write(self.txtPRF.text() + "\n")
            f.write("Observaciones: "+"\n" +"RF= "+RF +"\n"+"CF= "+CF + "\n" + "led1= "+led1 +"\n"+"led2= "+led2 +"\n")
        
        #☺aca debemos copiar los datos de csv a xlsx
        archivo_excel = self.archivo_configuracion.replace(".txt","_datos.xlsx")
        #pd.read_csv(self.archivo_temp).to_excel(archivo_excel, index=False) #convertir a excel y guardar en temporal
        #remove(self.archivo_temp)  #remover archivo
        #df1=pd.DataFrame(datos1,columns=['LED_ROJO', 'LED_INFRAROJO', 'ContinuaLedRojo','ContinuaLedIF'])
        self.dataY=mne.filter._overlap_add_filter( self.dataY,self.b_bandpass)
        dataframe = pd.DataFrame(self.dataY.T,columns=['LED_ROJO', 'LED_INFRAROJO'])

        #Guarda el DataFrame en un archivo Excel
        dataframe.to_excel(archivo_excel, index=False)
        print("Guardado")
        """
        self.archivo_datos = self.archivo_configuracion.replace(".txt","_datos.csv") 
        print(self.archivo_datos)
        with open(self.archivo_datos, 'w') as f:
            writer = csv.writer(f) """
        pass
    
    #-------------------pestaña visualizar---------------------------------    
    
    def Iniciar_handler(self):
        """
        -detiene timer0 que actualiza nivel de bateria
        -si modo offline activo, llama al metodo modo_offline()
        -Habilitar botones de pausa y detener
        -si modo online, llama al metodo Iniciar()
        """
        self.timer0.stop()
        if self.ckmodo_offline.isChecked(): #~Si el modo offline esta activado
            self.modo_offline(self.archivo_offline)
        
        else: #modo tiempo real
            
            #llamammos al metodo Iniciar() antiguo Datos() 
            self.Iniciar()
    
    
    def Pausa_handler(self):
        """
        -realiza un togle del boton de pausa entre pausa y detener
        -llama a los metodos Pausar() o Continuar()

        Returns
        -------
        None.

        """
        if self.pbpausarprueba.isChecked():
            self.pbpausarprueba.setText('Continuar')
            self.pbpausarprueba.setStyleSheet("color: black; background-color : red; }")
            self.Pausar()
        else:
            self.pbpausarprueba.setText('Pausar')
            self.pbpausarprueba.setStyleSheet("color: black; background-color: green; }")  #border: none;
            self.Continuar()
        pass
    
    def Pausar(self):
        """
        -Detiene la visualizacion con timer1

        Returns
        -------
        None.

        """
        self.timer1.stop()
        pass
    
    def Continuar(self):
        """
        -Activa timer1 para continuar la visualizacion

        Returns
        -------
        None.

        """
        self.timer1.start()
        pass
    
    def Detener (self):
        """
        -Detiene timer1 de visualizacion
        -Pone en false el flag de disponibilidad de datos
        -Detiene el envio de datos enviando un mensaje al dispositivo
        de la forma  [0XFF, 0X09], mensaje tipo 09
        -El dispositivo en viara  [0XFF, 0X09], leer los mensajes
        de entrada hasta encontrar el mensaje para limpiar el buffer de recepcion.
        -Limpia la pantalla
        -Deshabilita botones de pausa y detener.
        -Inicia timer0 para nivel de bateria.
        -Deberia desplegar una ventana q consulte el guardado de los datos
        
        Returns
        -------
        None.

        """
        #??? aca deberiamos preguntar si desea guardar los datos y llamar a guardar_prueba
        self.comando = 'detener'
        print("detenido") #debuger
        self.timer1.stop()
        self.flag_datos = False
        time.sleep(2)
        encabezado = [0XFF, 0X09]
        mensaje = bytearray(encabezado)
        self.socket_cliente.send(mensaje)
        #limpiaramos buffer
        codigo = False
        print("verifiacion de codigo") #debuger
        recibidoFF = self.socket_cliente.recv(1)
        #print("recibidoFF",recibidoFF) #debuger
        while codigo == False:
            QApplication.processEvents()
            if recibidoFF[0] == 0xFF:
                recibido09 = self.socket_cliente.recv(1)
                #print("recibido09",recibido09) #debuger
                if recibido09[0] == 0x09:
                    codigo = True
                    #print("codigo true") #debuger
                else:
                    recibidoFF = recibido09
            else:
                recibidoFF = self.socket_cliente.recv(1)
                #print("recibidoFF",recibidoFF) #debuger
        
        print("Detenido satisfactoriamente", recibidoFF,"-",recibido09) #debuger       
            
        #Limpiamos la pantalla
        
        self.gvtemporal.clear()
        self.gvtemporal_2.clear()
        #self.curva_continua.clear()
        self.gvfft.clear()
        #for i in range(self.numero_canales): #self.numero_canales
            #self.canales[i].clear()
           # self.canales_psd[i].clear()
        QApplication.processEvents() #ejecuta los procesos en cola de modo q la aplicacion responda
        #bloqeuar boton de pausa y detener
        #aca deveriamos preguntar si desea guardar y vrear e archivo xlsx
        #self.archivo_datos_xlsx, _ = QFileDialog.getSaveFileName(self, 'Guardar archivo', 'C:/', 'Text files (*.xlsx)')
        self.guardar_prueba()
        #self.timer0.start()
        pass

   
    
    #-------------------pestaña visualizar-------------------------------------    
    
    #----metodos para solicicitud y recepcion de datos-------------------------
    def Iniciar(self):
        """
        -Generacion de las curvas donde se actualizaran los datos para visualizar
        -GENERACION DE ARCHIVO TEMPORAL DE LOS DATOS y configuracion (.csv y .txt)
        -Coloca comando en 'datos'
        -Genera las variables donde se almacenaran los datos recibidos.
        -self.dataY es una matriz de 2 filas por 10000 columnas y es donde se 
        almacenaran los datos recibidos.
        -self._copy es una copia de la matriz self.dataY donde se aplicaran los 
        filtros si esta habilitada la opcion y sera la utilizada por el metodo
        update_plot_data(), para graficar. Esto en necesario para aplicar el filtro
        sobre toda la matriz una sola vez.
        -Siempre se recibiran 2 canales de datos de 3 bytes y 100 muestras.
        -Se calculan los coeficientes de los filtros.
        -Se envia el mensaje tipo 08 [0XFF, 0X08]
        -Se crea un objeto de la clase External (hilo)
        -Se invoca el atributo signal de la clase External, que conecta con el metodo procesar_datos()
        -Se inicia el hilo de recepcion de los datos.
        -

        Returns
        -------
        None.

        """
               
        #self.canales = [] # curvas temporales
        self.canales_psd = []  #Curvas FFT
        color_led = ['r', 'b']
        names = ['LED_ROJO', 'LED_INFRAROJO']
        #curvas temporales
        self.curva_rojo = self.gvtemporal.plot(pen = 'r', name=('LED_ROJO'))
        self.curva_irojo = self.gvtemporal.plot(pen = 'b', name=('LED_INFRAROJO'))
        self.curva_continua = self.gvtemporal_2.plot(pen = 'k', name=('Snagre estacionaria'))
        
        for i in range(self.numero_canales):#creamos curvas FFT
            d = self.gvfft.plot(pen = color_led[i],name=(names[i],2-i))
            self.gvfft.addItem(d)
            self.canales_psd.append(d)
               
        #creamos archivo csv temporal,en carpeta Temp del sistema
        carpeta_temporal = tempfile.gettempdir() #acceder a carpeta temporal
        print(carpeta_temporal)
        self.archivo_temp = carpeta_temporal+'/temp.csv'
        df = pd.DataFrame(columns=['LED_ROJO', 'LED_INFRAROJO', 'ContinuaLedRojo','ContinuaLedIF'])        
        df.to_csv(self.archivo_temp, index=False) #creamos las columnas de canales activos
        
        
        #este metodo debe recibir las cadenas de datos y almacenarlos en un archivo
        #en formato de 24 bits, 
        
        self.comando = 'datos'
        self.sFreq = float(self.txtPRF.text())
        self.timer1.start()
        
        #??? Habria que limpiar variables q no se utilizan y verificar extremo izq de los punteros
        #configuramos variables y buffers q almacenen los datos 
        self.NP20_seg = int(self.sFreq * 20)#cantidad de muestras segun frec de muestreo para 20 seg de datos
        self.mveinte = int(-1*self.NP20_seg)
        self.dos_seg = int(self.sFreq * 2)#cantidad de muestras para 2 seg de datos
        self.promediar = False
        #creamos un np array de 4 elementos y 20 seg de muestras donde se almacenaran los datos a graficar 
        self.dataY = [[],[]] #np.zeros((self.numero_canales,self.NP20_seg,)) 
        self.continua =  []
        self._copy = self.dataY #creamos la copia para los datos filtrados
        #creamos2 punteros que seran los limites de nuestros datos a visualizar
        self.A= 0
        self.B = self.NP20_seg
        self.N = 0 #! CORREGIR NOMBRE PORQUE SINO NO VAS A SABER QUE ES!!!! (RODRI)
        self.P = 0 #??? CONTADOR DE PAQUETES
        self.min = []
        #--generacion coeficientes de filtros----------
        #--Filtro Notch-------------------------------------
        numtaps_seg=3.3/0.5
        numtaps_notch = int(numtaps_seg* self.sFreq)
        if numtaps_notch % 2 == 0:
            numtaps_notch = int(numtaps_notch + 1)
        stopband = [49,51]
        # 3301, stopband, pass_zero='bandstop', fs = sfreq
        self.b_notch = signal.firwin(numtaps_notch, stopband,pass_zero='bandstop', fs=self.sFreq)
        
        #--pasa banda-----------------------------
        numtaps_seg=3.3/1
        numtaps_pb = int(numtaps_seg*self.sFreq)
        if numtaps_pb % 2 == 0:
            numtaps_pb = int(numtaps_pb + 1)
            
        self.lfreq = float(self.txtpasabandainf.text())
        self.hfreq = float(self.txtpasabandasup.text())
        if self.lfreq <= 0:
            self.lfreq = 0.1
        passband = [self.lfreq , self.hfreq]
        self.b_bandpass = signal.firwin(numtaps_pb, passband,window='hamming', pass_zero='bandpass', fs=self.sFreq)
        
        print("coeficientes de filtros calculados")
        
        
        #enviamos el comando al dispositivo para que comienze a enviar los datos    
        encabezado = [0XFF, 0X08]
        mensaje = bytearray(encabezado)
        print(mensaje)
        self.socket_cliente.send(mensaje)
       
        #--------recepcion con hilo----------------------------------
        #inicia el hilo
         
        self.hilo_recepcion = External() #crea un objeto de la clase External definida abajo(un hilo)
        self.hilo_recepcion.senal.connect(self.procesar_datos) #invoca un atributo de la clase pyqtsignal del objeto countChanged perteneciente a la clase hilo
        self.hilo_recepcion.start()
        #---------------------------------------------
       
    
    #---procesamiento de datos------------------------------------------------
    
    def procesar_datos(self,_NIVEL_BATERIA,_datos):
        #??? 21/02/24
        #calcula valor AC y DC para cada latido
        #Calcular saturacion con 1 decimal
        #Agregar timestap en primera columna
        #Boton para inicio de grabacion
        #Almacenar los datos filtrados
        
        """
        -Metodo asociado a la señal emitida por el hilo.
        -Recibe un Byte con el nivel de bateria en microvolts.
        y una matriz de 100x2 con los datos de los canales rojo e infrarojo.
        -se traspone la matriz de datos en 2x100, para graficar
        
        -se propone almacenar todo el estudio directamente en un numpy
        - y generar ventanas desplazables.
        
        Parameters
        ----------
        _NIVEL_BATERIA : TYPE Byte
            DESCRIPTION.
        _datos : TYPE matriz 100x2
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.P += 1
        _datos = _datos #* -1 #negamos los datos por una cuestion de visualizacion
                
        _datos = _datos.T # trasponemos por compatibilidad con el graficador (2,100) 
       
        #agregamos la matriz de datos (2,100) a la matriz self.dataY        
        self.dataY = np.append(self.dataY, _datos, axis=1)          
        
        #generamos el vector temporal en funcion del tamaño del paquete y la fecuencia de muestreo
        num_muestras = self.dataY.shape[1]
        frecuencia_muestreo = self.sFreq  #Frecuencia de muestreo Hz
        self.vector_tiempo = np.arange(num_muestras) / frecuencia_muestreo #vector temporal para el eje x
        
       
        #crear punteros que se desplazen por la matriz de datos y tiempo
        if self.dataY.shape[1] >= (self.NP20_seg + 100):
            self.A +=  _datos.shape[1]
            self.B += _datos.shape[1]
            self.autorange += 1
            pass
        
        if self.autorange == 1: #ajustamos el eje de visualizacion en automatico
            self.gvtemporal.enableAutoRange(axis='xy')
            #self.gvtemporal_1.enableAutoRange(axis='xy')
            self.gvtemporal_2.enableAutoRange(axis='xy')
        
       
        # Genero una copia de 20segundos de datos
        self._copy = self.dataY[:,self.A:self.B] 
        #---APLICACION DE FILTROS----------------------------------------------
        if self.ckpasabanda.isChecked():
            self._copy = mne.filter._overlap_add_filter(self._copy,self.b_bandpass)
        if self.P == 5:
            self.P = 0
            minim = self.calcular_minimos(self.dataY[:,-500:])
            self.actualizar_vector_minimos(minim)
            
        
        
        #---APLICACION DE FILTROS----------------------------------------------
        #if self.ckpasabanda.isChecked():
            #self._copy = mne.filter._overlap_add_filter(self._copy,self.b_bandpass)
            
        
        
        """ 
        #print("PPM: ",len(self.max)*3)
        self.continua=self._copy
        #print(self._copy.shape[1])
        
        if self._copy.shape[1] > self.dos_seg*6:
            self.promediar = True
            # Inicializar una lista para almacenar los valores entre los máximos y mínimos
            self.valores_ac = []
            self.valores_dc = []
            for min_index, max_index in zip(self.min[10:-1], self.max[10:-1]):
                # Calcular la expresión para val_ac
                val_ac = ((abs(self.continua[1, max_index] - self.continua[1, min_index])) / abs(self.continua[1, max_index]))
                val_dc = 1 - val_ac #((abs(self.continua[1,min_index]))/abs(self.continua[1,max_index]))
    
                # Agregar el resultado a la lista
                self.valores_ac.append(val_ac)
                self.valores_dc.append(val_dc)
            if len(self.valores_ac) > 0:
                self.promedio_ac = np.mean(self.valores_ac)
                self.promedio_dc = np.mean(self.valores_dc)
                #print("promedio dc")
          """
        
        """
        print("tamaño continua: ",self.continua.shape[0])
       
        print("tamaño dataY: ",self.dataY.shape[1])
        print("tamaño _copy: ",self._copy.shape[1])
        print("tamaño -B-A: ",self.B ," : ", self.A)
        """
        #---APLICACION DE FILTROS----------------------------------------------
        """
        if self.ckpasabanda.isChecked():
            #start1 = time.time()
            self._copy = mne.filter._overlap_add_filter(self._copy,self.b_bandpass)
            #tiempo2 = time.time()- start1
            #print("filtrar datos-----")
        
        if self.cknotch.isChecked():
            self._copy = mne.filter._overlap_add_filter(self._copy,self.b_notch)
                 
        
        """
        
        #--flag q indica la disponibilidad de datos para graficar--------------
        self.flag_datos= True
        self.nivelbateria= _NIVEL_BATERIA
        
    #--------------------------------------------------------------------------
    
    
    #-----------metodos de ejecucion de los timeout de los timer---------------
       
    def calcular_minimos(self, data):
        """
        Recibe las ultimas 500 muestras adquiridas.
        calculamos la posicion de los maximos y minimos de las ultimos N muestras 
         N = len(data); 
         Return: vector unidimensional 1x500"""
        _max, _ = find_peaks(data[1,:], distance=300) # [0, len(data)] + 1segundo
        _min, _ = find_peaks(-data[1,:], distance=300)        
        print(len(_min))
        print(type(_min[0]))
        print(_min)
        return _min
            
    def actualizar_vector_minimos(self, minimos):     
        """"
        Recibe vector de minimos de las ultimas 500 muestras adquiridas.
        debe tomar el vector de _min de 1x500 e ir appendeandolos modificando su posicion
        de modo de volver a su posicion absoluta 
        """
        minimos += self.N  
        #minimos= minimos.astype(int)
        self.min = np.append(self.min , minimos,axis=0); #
        self.min = self.min.astype(int)
        self.N += 500
        print(type(self.min[1])," - ",len(self.min))    
        print(self.min)
        
        #---Actualiza los datos de los graficos------
    def update_plot_data(self):
        """
        -timeout del timer1.
        -Genera el vector temporal
        -Actualiza las curvas de los graficos temporal y FFT
        -Actualiza el nivel de bateria
        
        Returns
        -------
        None.

        """
        if self.flag_datos is True:
            x= self.vector_tiempo
            #print("voy a graficar")
            self.curva_rojo.setData(x[self.A:self.B], self._copy[0,:])
            self.curva_irojo.setData(x[self.A:self.B], self._copy[1,:])
            
            self.curva_continua.setData(x[self.min], self.dataY[1,self.min])
            
            for i in range(self.numero_canales): #self.numero_canales = 2
                self.canales_psd[i].setData(x , self._copy[i,:])
               
            
            if self.promediar :
                self.txtcontinua.setText(f"{self.promedio_dc:.2%}")
                self.txtalterna.setText(f"{self.promedio_ac:.2%}")
            
            QApplication.processEvents()
            #self.barBat.setValue(self.nivelbateria)
           
        #Actualiza nivel de bateria----------
    def timer0_timeout(self): 
        """
        -Actualiza fecha y hora
        -enviar [0XFF, 0X01] .
        -Recibir [0XFF, 0X01, nivel de bateria] .
        -Actualizar nivel de bateria.

        Returns
        -------
        None.

        """
        print("timer0 activo")     #BUG 
        time_=QDateTime.currentDateTime()
        timeDisplay=time_.toString('dddd dd-MM-yyyy hh:mm ')
        self.lblfecha.setText(timeDisplay)
        QApplication.processEvents() #ejecuta los preocesos en cola de modo q la aplicacion responda
                
        #mensaje enviado de tamaño fijo 2 bytes
        encabezado = [0XFF, 0X01]  #mensaje tipo FF01[DATOS] 
        mensaje = encabezado
        self.socket_cliente.send(bytearray(mensaje))
        print("timer0 envio")
        #leer el mensaje recibido y guardar los registros de estados de electrodos y gpio
        #nivel de bateria (config 3 bit0 estado de electrodo bias  y mostrarlo
        recibido = self.socket_cliente.recv(3)
        print("timer0 recibio")
        mask= 0xFF #FF
        
        if (recibido[0] == mask) :
            self.nivelbateria = int(recibido[2])      #int
            self.barBat.setValue(self.nivelbateria)
            #nivel de bateria tiene q tener valor entre 76(3.2volts) y 100(4.2volts)
        QApplication.processEvents() #ejecuta los preocesos en cola de modo q la aplicacion responda
              
    
    
    #---Eventos de cierre de ventanas------------------------------------------
        
    def closeEvent(self, event):#evento de cierre de la ventana principal
        reply = QMessageBox.question(self,
                                 'Events - Slot',
                                 "Realmente desea cerrar la aplicacion",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            
            event.accept()
        else:
            event.ignore()
    
    #----evento de presion de teclas-------------------------------------------       
    def keyPressEvent(self, event):
        key = event.key()
        #if key == QtCore.Qt.Key_0:
        print("tecla ",key," presionada")
         
     
    #---------metodo del modo offline------------------------------------------
    def modo_offline(self,_datosoffline):
        #los datos se va a encotrar en un archivo de excel
        print("modo offline") # , header=None sep=',',names= [0,1,2,3],decimal='.',
        df1 = pd.read_excel(_datosoffline  )
        
        datos = df1.to_numpy().astype(float)
        #encabezado=y[0,:]
        #canales = 
        #[int(x) for x in encabezado if np.isnan(x) == False]
        #print(canales)
        #datos = np.delete(y,(0), axis = 0)
        datos = datos.T
        datos = datos[:,100:]
        filtrado = False
        print(datos.shape)
        archivo_filtrado = self.archivo_offline.replace("_datos.xlsx","")
        archivotxt = self.archivo_offline.replace("_datos.xlsx",".txt")
        archivo = open(archivotxt, "r")
        linea1 = archivo.readline() #fecha
        linea2 = archivo.readline() #texto fecuencia de muestreo
        sFreq = float(archivo.readline()) #frecuencia de muestreo
        archivo.close()
        try:
            time0 = float(self.txttime0.text())
        except:
            time0=0
        try:
            time1 = float(self.txttime1.text())
        except:
            time1 = datos.shape[1]
        
        N0 = int(time0*sFreq)
        N1 = int(time1*sFreq)
        print(N0,"--",N1)
        datos= datos[:,N0:N1] #Delimitamos el tamaño q se desea visualizar
        continua = datos
        
        #----Procesamiento de datos--------------------------------------------
        #seleccion del tipo de ventana del filtro
        _window = self.cbfiltro.currentText()
        print(_window)
        a=[4,5,6,7] #Para que las curvas originales y filtradas tengan distinto color
        
        #--Tamaño del filtro en funcion de la frecuencia de muestreo------
        numtaps_seg=3.3/1
        numtaps = int(numtaps_seg*sFreq) #int(numtaps_seg*sFreq +1)
        if numtaps % 2 == 0:
            numtaps =int(numtaps + 1)
        
        #--generacion coeficientes del filtra pasabanda------------
        lfreq = float(self.txtpasabandainf.text())
        hfreq = float(self.txtpasabandasup.text())
        if lfreq <= 0:
            lfreq = 0.1
        passband = [lfreq , hfreq] #, width=0.5 #,window='hamming' , pass_zero='bandpass'
        b_bandpass = signal.firwin(numtaps, passband, window=_window,  pass_zero='bandpass' , fs=sFreq)
        
        #Aplicacion del filtro
        if self.ckpasabanda.isChecked():
            #datos1 = signal.fftconvolve(datos[1,:], b_bandpass, mode='same')
            datos = mne.filter._overlap_add_filter(datos,b_bandpass)
            filtrado = True
            a=[0,1,2,3]
        
        
        #--generacion coeficientes de filtro notch----------
        """
        numtaps_notch_seg=3.3/0.5
        numtaps_notch = int(numtaps_notch_seg*sFreq) #int(numtaps_seg*sFreq +1)
        if numtaps_notch % 2 == 0:
            numtaps_notch =int(numtaps_notch + 1)
        
        stopband = [49,51] #49-51  #width=0.5,window='Hamming',
        b_notch = signal.firwin(numtaps_notch, stopband, pass_zero='bandstop', fs=sFreq)
        
        if self.cknotch.isChecked():
            #start = time.time()
            datos = mne.filter._overlap_add_filter(datos,b_notch)
            #tiempo = time.time()- start
            #print("tiempo total",float(tiempo*1000))
            filtrado = True
            a=[0,1,2,3]
            """
        #----------------Fin aplicacion de filtros------------------------------------------------------       
       
        
       #---procesamiento de datos continuos y alternos----
        #buscamos max y min de los 20segundos--------
        
        start = time.time()
        self.max, _max = find_peaks((continua[1,:]), distance=300)
        self.min, _min = find_peaks((-1*continua[1,:]), distance=300)
        total = time.time() - start
        print(len(self.max), len(self.min))
        print("maximos: \n",self.max)
        print("minimos: \n",self.min)
        
        #val_ac=((continua[1,self.min[len(self.max)-2]] - continua[1,self.max[len(self.max)-2]])/continua[1,self.min[len(self.max)-2]])
        #val_dc= ((continua[1,self.max[len(self.max)-2]])/continua[1,self.min[len(self.max)-2]])
        #self.txtcontinua.setText(f"{val_dc:.2%}")
        #self.txtalterna.setText(f"{val_ac:.2%}")
        #-----------------fin--------------------------------------------------
        
        # modificamos el vector de tiempo x
        N = datos.shape[1]
        #T = 1.0 / sFreq
        #x = np.linspace(0.0, N*T, N)
        #curvas = []
        curvas_psd = []
        x = np.arange(N) / sFreq
        
        self.curva_rojo = self.gvtemporal.plot(pen = 'r', name=('LED_ROJO'))
        self.curva_irojo = self.gvtemporal.plot(pen = 'b', name=('LED_INFRAROJO'))
        #self.curva_maximos = self.gvtemporal_2.plot(pen = None,symbol='x', name=('maximo'))
        self.curva_continua = self.gvtemporal_2.plot(pen = 'b', name=('Continua'))
        #self.curva_minimos = self.gvtemporal_2.plot(pen = 'r',symbol='x', name=('minimos'))
        
        for i in range(2):
            #c = self.gvtemporal.plot(pen=(a[i]),name=('Ch',i+1)) #,len(canales)*1.3
            d = self.gvfft.plot(pen=(a[i]),name=('Ch',i+1))
            #self.gvtemporal.addItem(c)
            self.gvfft.addItem(d)
            #curvas.append(c)
            curvas_psd.append(d)
        
        #AGREGAMOS LOS DATOS A LAS CURVAS PARA VISUALIZAR
                
        self.curva_rojo.setData(x, datos[0,:])
        #self.curva_rojo.setData(x[self.max], continua[0,self.max])
        self.curva_irojo.setData(x, datos[1,:])
        #self.curva_maximos.setData(x[self.max], continua[1,self.max])
        self.curva_continua.setData(x[self.min], continua[1,self.min])
        #self.curva_minimos.setData(x[self.min], continua[1,self.min])
        QApplication.processEvents() #ejecuta los preocesos en cola de modo q la aplicacion responda
        
        #start = time.time()
        for i in range(2): #self.numero_canales
            #curvas[i].setData(x,datos[i,:])
            curvas_psd[i].setData( x , datos[i,:]) #fftMode=True
        #total = time.time() - start
        #print(total)
        
        
        
        #  alamcenamiento de datos  
        archivo_filtrado = archivo_filtrado+"_filtrado.xlsx"
        #archivo_excel = archivo_filtrado.replace(".csv",".xlsx")
        print(archivo_filtrado)
        if filtrado == True:
            datos1 = datos.T
            df1=pd.DataFrame(datos1,columns=['LED_ROJO', 'LED_INFRAROJO'])
            #print(df1)
            df1.to_excel(archivo_filtrado, index=False)
            #Guarda el DataFrame en un archivo Excel
            #dataframe.to_excel(archivo_excel, index=False)
            print("Guardado")
        
        #OPTIMIZE
        #faltaria verificar el tamaño maximo del dataframe
        #se podria partir los datos si superan el tamaño maximo de filas y armar como si fuesen dos columnas
        #tamaño maximo de excel 1048576 x 16384 (fxc)
        """
        carpeta_temporal = tempfile.gettempdir() #acceder a carpeta temporal
        #carpeta_temporal = 'C:/Users/facun/Documents/Proyectos Labi/Oximetro/Datos'
        print(carpeta_temporal)
        archivo_excel = carpeta_temporal+'/archivo.xlsx' #Creo la ruta del archivo temporal
        pd.read_csv(archivo_filtrado).to_excel(archivo_excel, index=False) #convertir a excel y guardar en temporal
        remove(archivo_filtrado)  #remover archivo
        """
        #para convertir el csv a excel
        
        """pd.read_csv('data.csv').to_excel('data.xlsx', index=False) """
        
        #self.canales_offline = canales    
        #self.curvas_offline = curvas
        #self.curvas_psd_offline = curvas_psd
      
    
    """------Fin modo offline--------------------------------------------""" 
    
    
    
    
    
    #----subproceso de adquisicion de datos-----------------------------    
class External(QThread): #se crea la clase External que hereda de QThread
    """
    Esta línea importa Qthread que es una implementación de PyQt5  para dividir y
    ejecutar algunas partes (p. ej.: funciones, clases) de un programa en 
    segundo plano (también conocido como subprocesamiento múltiple). 
    Estas partes también se llaman hilos. Todos los PyQt5programas por defecto
    tienen un subproceso principal y los otros (subprocesos de trabajo) se utilizan
    para descargar tareas intensivas que consumen mucho tiempo y procesar en segundo
    plano mientras se mantiene el funcionamiento del programa principal.
    """
    print("hilo iniciado")
    senal = pyqtSignal(int,np.ndarray) #creamos el objeto de la clase pyqtSignal
    """
    La segunda importación pyqtSignal se usa para enviar datos (señales) entre el trabajador
    y los subprocesos principales. En este caso, lo usaremos para decirle al hilo principal 
    que hay datos listos para procesar y llamara a la funcion "procesar_datos"
    """
    def run(self):
        """
        -Este metodo lee datos del socket, mientras el comando sea 'datos'.
        -Los datos recibidos (603 Bytes) seran una lista con un encabezado [0xFF,0x08,NIVEL_BATERIA ]
        -y 100 muestras de 6 bytes de los registros LED2_ALED2VAL = 0x2E y
        LED1_ALED1VAL = 0x2F  (600 Bytes), de la forma[led2(0),led1(0),led2(1),led1(1).....,led2(99),led1(99)]
        donde led2(0) y sus homologos son 3 bytes, que deben ser convertidos a un entero de 32bits.
        -Genera la matriz de 100 filas(muestras) y 2 columnas(canales).
        -
        -Emite la seañal que invoca el metodo precesar_datos() y le pasa la matriz y el nivel de bateria.

        Returns
        -------
        None.

        """
        print("estoy en el hilo")
        print(main.comando)
        _paq_recib = 0
        _paq_error = 0
        while (main.comando == 'datos'):
            
            recibido = main.socket_cliente.recv(603) #recibimos
            #print("recibi")
            mask= 0xFF #FF Indicador de paquete valido
            _paq_recib += 1
            if (recibido[0]== mask and len(recibido)==603) :
                #print("verificacion correcta")                                 #debuger               
                #dato_valido = True
                codigo = recibido[1]
                NIVEL_BATERIA = recibido[2]
                data= recibido[3:] #datos recibidos
                #print(len(data))                                                #debuger
                datos=[] #paquete de 100 muestras de 2 canales en formato de 24bits
                #estructuramos los datos a 24bits
                for i in range(0,len(data),3): # convertimos los bytes recibidos en enteros de 24 bits con signo en complemento a dos
                    datos.append(int.from_bytes(data[i:i+3], byteorder='big' ,signed=True)) # y los vamos guardando en una lista de extension lendat/3
                # signed=True indica que se debe interpretar el número entero como un número con signo en complemento a dos.
                _NdataY = np.array(datos) #creamos un np array con la lista de enteros de 24 bits con signo
                _NdataY.shape = (100,2) #matrix de 100 filas y 2 columnas
                
                    
                
                self.senal.emit(NIVEL_BATERIA,_NdataY)    
            else:
                #print("dato no valido")
                _paq_error +=1
                pass
        
        print("hilo finalizado")
        print(_paq_recib,"-", _paq_error)






app = QApplication(sys.argv)
app.setStyle('Fusion')  #['windowsvista', 'Windows', 'Fusion']
main = VentanaPrincipal()
main.show()
sys.exit(app.exec_())













#fin del programa