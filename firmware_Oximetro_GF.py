#---importar las librerias necesarias-----------------------------------
from umachine import Pin, SPI, Timer, ADC, PWM  #importamoslos modulos exclusivos del esp32
from micropython import const
import utime
import network   # Creacion de red modo access point
import usocket as socket #creacion de  
import uselect as select
import aux as fc
#------

#-------------------------------Definicion de direcciones del AFE4400---------------------------------



#-------------------------------Definicion de comandos del AFE4400------------------------------------
RESET_SOFT = [0x00,0x00,0x08]  #resetea el AFE, ponetodos los registros a '0'
SPI_READ   = [0x00,0x00,0x01]  #Comando q inicia las converdiones del ads # no existe en AFE
DIAG_EN    = [0x00,0x00,0x04]  #Comando que inicia diagnostico conexion de LEDS  en afe'


#-------------------------------Definicion de Pines a utilizar del ESP32---------------------------------------
AFE_PDN = Pin(33, Pin.OUT, value = 1) #Activo bajo_apaga el AFE-no se utiliza
RESET= Pin(25, Pin.OUT, value = 1) #resetea el AFE Activo bajo-no se utiliza
drdy  = Pin(32, Pin.IN)          #pin de DATAREADY AFE nos indica q hay una muestra disponible para ser leida
SPISTE = Pin(27, Pin.OUT, value = 1)  #Habilita interfaz SPI activo bajo.
#DIAG_END  = Pin(18, Pin.IN)  #Indica fin de diagnostico.
#LED_ALM = Pin(19, Pin.IN) #fallo en la conexion del led
#PD_ALM = Pin(21, Pin.IN) #fallo en la conexion del fhotodiodo

led   = Pin(2)     #Indica mediante un led si es dispositivo esta encendico(fijo) o si requiere recargar(blink 1s)
batx = ADC(Pin(35))                  #Leer valor del ADC  divisor de tension del valor de bateria. <3.2 volt pagado,3.2 a 3.7 parpadea y mas de 3.7 encendido
batx.atten(ADC.ATTN_11DB)            #ADC.ATTN_11DB  atenuación 11dB (150mV - 2450mV), la bateria esta conectada a un divisor de tension batx=bat/2
batx.width(10)    

#-------------------------------Definicion de timers---------------------------------------------
tim_red = Timer(0)         #timer encargado de verificar si existe un mensaje nuevo en el buffer de recepcion cada 1 segundo
tim_bat = Timer(1)         #timer encargado de leer el nivel de bateria mediante el adc del pin 35
verificar = select.poll()  #lista de verificaciones de clientes conectados

#-------------------------------Definicion e inicializacion de variables-----------------------------------
buff_spi = []      #buffer q aloja las muestras del AFE recepcionadas por spi
buff_red = []      #Buffer q aloja los datos q son enviados al cliente
buff_full = 0      #flag que indica que el buffer de envio de daos esta lleno y listo para su envio
e=0                #almacena el numero de errores en la recepcion de muestras por spi
x=0                #contabiliza el numero de paquetes enviados
reg=bytearray(15)  #bytearray(x) con x entre 0 y 255 Registro que almacena la lectura actual del puerto spi
mensaje_recibido = False   #flag que indica la recepcion de un nuevo mensaje
tiempo=[]                  # lista para el calculo de demoras de las rutinas 
cantidad_muestreos = 0     #variable que contabiliza la cantidad de muestras buenas y nos permitira delimitar el buffer de envio
salir = False              #flag que indica que el cliente se desconecto y sale del bucle de recepcion de mensajes

#-------Inicializamos valor de bateria----------------------------------------
val_bat = int(batx.read_uv()/1000)  #lee valor de bateria y lo convierte en milivolts
_val_bat= int(val_bat*100/2100) #_val_bat es el porcentaje de carga 100% = 4200mV y 76% = 3200mV

#----------------------------Definicion de diccionarios clave:valor------------------------------------------------------
Registro_W = fc.AFE4400_REGISTROS_W  #una lista de los registros esribibles utiles
Registro_T= fc.AFE4400_Tiempos    #Registros de solo lectura 
Valor_W = fc.AFE4400_REG_INI      #Valores iniciales a grabar en los registros
#Config_W = {Registro_W:Valor_W for (Registro_W, Valor_W) in zip(Registro_W, Valor_W)} #generacion de diccionario clave:valor para la inicializacion
#Valor_R = []

#---------Inicializacion del pwm que controla el led indicador de la bateria-------------------------------
#---------la frecuencia del pwm indica nivel de carga de la bateria y estado de conexion de wifi
"""
pwm2 = PWM(led)  #led azul conectado en placa depuracion, cambiar Pin(2) por led
duty_led = 512    
pwm2.duty(duty_led) #set duty cycle from 0 to 1023 as a ratio duty/1023, (256 = 25%)
freq_led = 10000 
pwm2.freq(freq_led) #set PWM frequency from 1Hz to 40MHz
utime.sleep_ms(1000) #energizamos el led durante 1 segundo
freq_led = 10  #led parpadeo rapido indica q no hay cliente conectado a la red wifi
pwm2.freq(freq_led)

"""
#----------------Modulo SPI-------------------------------------------------------------
#Configuramos el puerto SPI para la comunicacion con el ADS
spi = SPI(1, 1000000, polarity=0, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
spi.init(baudrate=1000000)

#----------------Modulo Network----------------------------------------------------------
#Creamos un punto de acceso WIFI al cual conectarnos desde la computadora que aloja el software cliente
ap_if = network.WLAN(network.AP_IF)  # instancia el objeto -ap_if- para controlar la interfaz AP
ap_if.config(essid='OXI_GF') # set the SSID of the access point
ap_if.active(True)
ap_if.config(txpower=11) #txpower  Maximum transmit power in dBm  level 2:20(integer or float)
ap_if.config(beacon_interval=4000) #configuramos la frecuencia del beacon debajo de los 0,5 Hz para luego filtrarla
                                  # son 4000 TU y 1 TU = 1024us entonces 0,24 hz (entre 100 y 60000 admite esp32) con 2000 tu 0,48Hz
#ap_if.config(channel=13) # , max_clients=1
#quitar los print luego de la depuracion
print(ap_if.config ('txpower'), "\n",ap_if.config ('beacon_interval'), "\n")
#----------------Modulo SOCKET-----------------------------------------------------------
#creamos un socket servidor capaz de aceptar clientes
ip = '192.168.4.1'      #'127.0.0.1' 192.168.4.1         
port = 9000
addr= (ip,port)         #addres direccion IP mas puerto
servidor = socket.socket() #
servidor.bind(addr)
servidor.listen(10)
servidor.setblocking(1)

#-------------------------------Definicion de funciones del ADS1299 (submodulos)-----------------------------------
def RESET_AFE():
    global RESET_SOFT
    #Disable_Read()
    WREG(fc.CONTROL0,RESET_SOFT)

def DIAG_AFE():
    global DIAG_EN
    #Disable_Read()
    WREG(fc.CONTROL0,DIAG_EN)

def Enable_Read():
    WREG(fc.CONTROL0,[0x00,0x00,0x01])
    
def Disable_Read():
    WREG(fc.CONTROL0,[0x00,0x00,0x00])

def RREG (Direccion):   #lee el registro pasado en el campo Direccion y lo retorna
     """ -Lee el Dato de  3 Bytes en la Direccion de regitro pasada
         - devuelve una lista de 3 bytes leidos
     """    
     SPISTE.value(0)
     spi.write(bytearray([Direccion]))
     Byte3 = spi.read(1)
     Byte2 = spi.read(1)
     Byte1 = spi.read(1)
     SPISTE.value(1)
     return [Byte3,Byte2,Byte1]
    
#----------------------------------------------------------------------------------
def WREG (Direccion, Dato): # escribe el Dato en el registro pasado en direccion
    """ Escribe el Dato pasado como lista de 3 Bytes en la Direccion de registro pasada como hexa
    """
    SPISTE.value(0)  
    spi.write(bytearray([Direccion]))
    spi.write(bytearray(Dato)) 
    SPISTE.value(1)
    
#----------------------------------------------------------------------------------
def AFE44xx_Default_Reg_Init(): #funcion que escribe en el AFE la configuracion inicial.
    global Config_W, Registro_W, Valor_W
    """Metodo para configuracion inicial del AFE
    """
    registroleido = []
    i = 0
    Disable_Read()
    for x in (Registro_W) :
        WREG (x,Valor_W[i] )
        i=i+1
    
    i = 0
    Enable_Read()
    for x in (Registro_W) :    
        registroleidoact = RREG(x)
        registroleido.append(registroleidoact)
        i=i+1

    print(registroleido) 
 
#----------------------------------------------------------------------------------        
"""
def LeerRegistros(): #no se utiliza
    #Metodo para escribir los registros de tiempos
    for s in Registro_R :
        Valor_R.append(RREG(s))
    return Valor_R    
"""
#----------------------------------------------------------------------------------    
def IniciarConversiones():
    #Enable_Read()
    print("iniciar conversiones")
    drdy.irq (handler=interrupcion_drdy, trigger=Pin.IRQ_FALLING ) #activamos la interrupcion en drdy utilizando el metodo irq()
    
#----------------------------------------------------------------------------------
def DetenerConversiones(): 
    #Disable_Read()
    drdy.irq (handler= None, trigger= Pin.IRQ_FALLING ) #desactivamos la interrupcion en drdy, probar con trigger=0 o None



#---------------------------Definicion de funciones del esp32---------------------------------------------
def EnviarDatos():   #funcion que verifica si el buffer de red esta lleno y envia los datos al cliente
    global mensaje_recibido, buff_full , cliente, buff_red ,e ,x
    x = 0
    print("enviar datos")
    while (mensaje_recibido == False): #mientras no halla un nuevo mensaje recibido enviara datos
        if buff_full == 1: # buff_red(603 Bytes) contiene encabezado[[0xFF + 0x08] + [bateria] + [100 muestras de 6 Bytes]] 
            #print("buffer lleno")
            #print(buff_red)
            x += 1
            cliente.sendall(bytearray(buff_red)) #buff_red es una lista, por lo que convierte cada valor de esa lista en un byte
            buff_full = 0
            #print("envie")
    #si recive un mensaje sale del while y detiene la adquisicion de datos
    print(x) #para depuracion
    drdy.irq (handler= None, trigger= Pin.IRQ_FALLING ) #desactivamos la interrupcion en drdy utilizando el metodo irq()
                                                        # probar con trigger=0 o None
#----------------------------------------------------------------------------------
def Conectado():  #envia [0xFF,0x01,nivelbat]
    global _val_bat  
    #configurar los registros y contestar con nivel de bateria
    encabezado = [0XFF, 0X01]
    _val_bat = 0x0F
    mensaje = bytearray(encabezado + [_val_bat])
    print(mensaje)
    cliente.sendall(mensaje) #envia el nivel de la bateria, el argumento debe ser un lista[] de modo q la funcion
    print("mensaje  de conectar enviado")                     #bytearray genere una lista de bytes
#----------------------------------------------------------------------------------
def AnalizarComando(_comando):
    global salir , Config_W,Valor_W , Registro_W, Registro_T
    
    if _comando == 0X01: #01 conectar
        salir = False
        print("comando 01 conectar")
        Conectado()
    
    elif _comando == 0X02 : #02 desconectar
        print("comando 02 desconectar")
        tim_red.deinit() #detenemos timer de red que verifica si hay mensajes nuevos
        verificar.unregister(cliente) #quitamos el cliente de la lista de verificaciones
        salir = True #encendemos el flag que nos saca del bucle, para esperar q un nuevo cliente se conecte
    
    elif _comando == 0X03 : #03 Resetear AFE
        print("comando 03 RESET")
        RESET_AFE()  #deja disable_read o sea modo escritura
        utime.sleep_ms(50)
        AFE44xx_Default_Reg_Init() # deja enable_read- modo lectura
        cliente.sendall(bytearray([0xFF, 0x03])) #respuesta que confirma q la operacion fue exitosa
        pass
    
    elif _comando == 0X04 : #04 Diagnostico
        print("comando 04 diagnostico")
        Disable_Read()
        WREG(fc.CONTROL0,DIAG_EN)
        utime.sleep_ms(50)
        Enable_Read()
        SPISTE.value(0)
        spi.write(bytearray([fc.DIAG]))
        registro = spi.read(3)
        SPISTE.value(1)
        print(registro)
        encabezado = [0XFF, 0X04]
        mensaje = []
        mensaje.extend(encabezado)
        mensaje.extend(registro)
        mensaje = bytearray(mensaje)
        print(mensaje)
        cliente.sendall(mensaje)
        pass
    
    elif _comando == 0X05 : #05 Setear TX
        print("comando 05 Setear TX")
        #Recibe [LEDCNTRL, LEDCNTRL_VAL] en BYtes, debe leer 1 byte y guardarlo en LEDCNTRL y 3 bytes y guardarlos en LEDCNTRL_VAL 
        mensaje = cliente.recv(4)
        print(mensaje)
        LEDCNTRL = mensaje[0]
        LEDCNTRL_VAL = mensaje[1:]
        Disable_Read()
        WREG(fc.LEDCNTRL,LEDCNTRL_VAL)
        print("voy a enviar")
        cliente.sendall(bytearray([0xFF, 0x05])) #respuesta que confirma q la operacion fue exitosa
        Enable_Read()
        print(RREG(fc.LEDCNTRL))
        pass
    
    elif _comando == 0X06 : #06 Setear RX
        print("comando 06 Setear RX")
        salir = False
        mensaje = cliente.recv(4)
        print(mensaje)
        TIA_AMB_GAIN = mensaje[0]
        TIA_AMB_GAIN_VAL = mensaje[1:]
        Disable_Read()
        WREG(fc.TIA_AMB_GAIN,TIA_AMB_GAIN_VAL)
        print("voy a enviar")
        cliente.sendall(bytearray([0xFF, 0x06])) #respuesta que confirma q la operacion fue exitosa
        Enable_Read()
        print(RREG(TIA_AMB_GAIN))
        pass
    
    elif _comando == 0X07 : #07 Setear Tiempos
        print("comando 07 Setear Tiempos")
        #salir = False
        Registro_T_VAL = cliente.recv(87)
        
        i = 0
        Disable_Read()
        for x in (Registro_T) :
            WREG (x,Registro_T_VAL[i:i+3] )
            i=i+3
        
        cliente.sendall(bytearray([0xFF, 0x07]))
        i = 0
        Enable_Read()
        registroleido = []
        for x in (Registro_W) :    
            registroleidoact = RREG(x)
            registroleido.append(registroleidoact)
            i=i+1
        print(registroleido)
        pass
        
        
    elif _comando == 0X08 : # comenzar el envio de los datos
        salir = False
        print("comando 08 comenzar envio de datos")
        IniciarConversiones()
        EnviarDatos()
        pass
    elif _comando == 0X09 : # 09 detener adquisiciones
        print("comando 09 detener")
        salir = False
        DetenerConversiones()
        cliente.sendall(bytearray([0xFF, 0x09]))
        pass
        
    else : #deberia enviar un mesaje indicando error en la recepcion y que se muestre mediante un widegtBox
        pass
#----------------------------------------------------------------------------------

# -----------------------Definicion de interrupciones (ISR)-------------------------------------
def interrupcion_drdy(pin): # interrupcion en el pin 34 conectado al drdy del ads1299 q indica q hay una muestra disponible para ser leida en el spi
    #Variables globales compartidas con el main
    #drdy.irq (handler= None, trigger= Pin.IRQ_FALLING ) #desactivamos la interrupcion en drdy (verificar si es necesario
    global reg , buff_red, buff_spi, cantidad_muestreos, buff_full, e, j, start, tiempo, val_bat, _val_bat
    _val_bat = 0x0A
    
    SPISTE.value(0)
    spi.write(bytearray([0x2E]))
    LED2_ALED2VAL_VAL = spi.read(3)
    spi.write(bytearray([0x2F]))
    LED1_ALED1VAL_VAL = spi.read(3)
    #spi.write(bytearray([RDATA])) #solicita se carguen los datos muestrados en el buffer spi para ser leidos
    #spi.readinto(reg)  #usar spi.readinto(reg) #guarda en reg lo que hay en el spi
    buff_spi.extend(LED2_ALED2VAL_VAL)
    buff_spi.extend(LED1_ALED1VAL_VAL)   #aca tenemos una lista con los bytes lpm
    cantidad_muestreos += 1
    
    if cantidad_muestreos == 100:
        buff_red= []
        buff_red.extend([0xFF,0x08]) #agregamos encabezado
        buff_red.append(_val_bat) #agregamos valor de bateria
        buff_red.extend(buff_spi) #extendemos el buff de red con las muestras
        buff_spi = []
        buff_full = 1
        cantidad_muestreos = 0
        
        #print("buffer lleno")
        #print(buff_red)
    #drdy.irq (handler=interrupcion_drdy, trigger=Pin.IRQ_FALLING ) #activamos la interrupcion en drdy utilizando el metodo irq()
#----------------------------------------------------------------------------------
def interrupcion_timred(Timer):#timer0  interrupcion cada 1 segundo para verificar si hay un mensaje nuevo del cliente
    #Variables globales compartidas con el main
    global events , mensaje_recibido
    events = verificar.poll(1)
    if events:
        mensaje_recibido = True
        events = None
#----------------------------------------------------------------------------------
def interrupcion_timadc(Timer):#timer1 timer que lee el nivel de bateria adc Pin35 y lo actualiza pwm en Pin 16
    global val_bat, pwm2, freq_led, batx, _val_bat
    
    val_bat = int(batx.read_uv()/1000)
    _val_bat= int(val_bat*100/2100) #_val_bat es el porcentaje de carga 100% = 4200mV y 76% = 3200mV
    if val_bat < 1600:
        freq_led = 1      #destello lento=Bateria baja
        pwm2.freq(freq_led) 
    else:
        freq_led = 10000  #Visiblemente fijo=Bateria OK
        pwm2.freq(freq_led)
        
    
#-------------------------------Programa--------------------------------------------------

#-------------------------------Inicializacion del AFE--------------------------------------------

RESET_AFE()
#utime.sleep_ms(50)
AFE44xx_Default_Reg_Init()
#Enable_Read()
#registroleido = RREG(0x01)
#print(registroleido)
#print('read: 1')
#utime.sleep_ms(50)
#registroleido = RREG(0x01)
#print(registroleido)
#AnalizarComando(4)
##Disable_Read()
#WREG(fc.CONTROL0,DIAG_EN)
#utime.sleep_ms(50)
#Enable_Read()
#registroleido = RREG(fc.DIAG)
#print(registroleido)
#IniciarConversiones()
#EnviarDatos()
#Activamoms timer de bateria

#tim_bat.init (period= 60000, mode=Timer.PERIODIC, callback=interrupcion_timadc) #Act.interrup.timer actualiza valor de bateria c/60 segundo

#--------------------------Verificamos si hay una estacion conectado a la red wifi--------------------------------------------------------------------
print ("Esperando conexion WIFI...") #depuracion
while True: #bucle de conexion wifi
     
     if (ap_if.isconnected() == True): #verifica si hay cliente wifi conectado
        freq_led = 10000               #cuando se detecta un cliente conectado se fija el led, si el nivel de bateria es bajo,
        #pwm2.freq(freq_led)            # lo actualiza el timer q lee el adc
        
        break #Sale del while si hay un cliente conectado
     else:
        
        continue #vuelve a repetir el while esperando un cliente
     

while True:  #bucle de conexion al socket,esperamos que un cliente se conecte mediante software al socket
    #print ("Esperando cliente...") #depuracion
    
    try:
        cliente, addrc = servidor.accept()  # cliente conectado al socket
        print ("Cliente conectado desde: ", addrc) #depuracion
        verificar.register(cliente, select.POLLIN)  #Agrego cliente a la lista de verificaciones para verificar si llega mensaje nuevo
        #--inicializamos timer de mensajes en la red---------------------
        tim_red.init (period= 1000, mode=Timer.PERIODIC, callback=interrupcion_timred) #Activo la interrupcion del timer
                                                                                       #para verificar si hay nuevo mensaje cada 1 segundo

        while True: #repite el bucle verificando si hay un nuevo mensaje recibido
            if mensaje_recibido: #flag que indica si hay algun mensaje entrante
                mensaje = cliente.recv(2)
                mensaje_recibido = False
                flag = mensaje[0]
                
                if flag == 0XFF: #si el mensaje es valido (FF) analiza el mensaje y responde, luego vuelve a esperar otro mensaje
                    mensaje_valido = True
                    comando = mensaje[1]  #mensaje de tamaño fijo de 2 bytes [0xFF,Comando]
                    #llamamos a la funcion analizar comando
                    AnalizarComando(comando)
                
                if salir:#el cliente se desconecto, asi q queda a la espera de otra conexion 
                    break #Sale del while y vuele a esperar conexion al socket.
            else:
                
                if (ap_if.isconnected() == False): # si el cliente esta desconectado por perdida de la conexion sale del while de socket para registrar un nuevo cliente
                    break  #sale del while y vuele a esperar conexion al socket.
                continue #vuelve a repetir el while esperando un mensaje entrante
        
         #-------------fin del while ---------------------------------------------
        
    except: #en caso de error, vuelve a repetir el bucle de conexion
        
        continue #vuelve a repetir el while esperando q un cliente se conecte al socket
    
 
 