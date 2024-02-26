# Registros AFE

#Definicion de registros

CONTROL0 = 0x00

LED2STC = 0x01
LED2ENDC = 0x02
LED2LEDSTC = 0x03
LED2LEDENDC = 0x04
ALED2STC = 0x05
ALED2ENDC = 0x06
LED1STC = 0x07
LED1ENDC = 0x08
LED1LEDSTC = 0x09
LED1LEDENDC = 0x0A
ALED1STC = 0x0B
ALED1ENDC = 0x0C
LED2CONVST = 0x0D
LED2CONVEND = 0x0E
ALED2CONVST = 0x0F
ALED2CONVEND = 0x10
LED1CONVST = 0x11
LED1CONVEND = 0x12
ALED1CONVST = 0x13
ALED1CONVEND = 0x14
ADCRSTSTCT0 = 0x15
ADCRSTENDCT0 = 0x16
ADCRSTSTCT1 = 0x17
ADCRSTENDCT1 = 0x18
ADCRSTSTCT2 = 0x19
ADCRSTENDCT2 = 0x1A
ADCRSTSTCT3 = 0x1B
ADCRSTENDCT3 = 0x1C
PRPCOUNT = 0x1D

CONTROL1 = 0x1E
TIA_AMB_GAIN = 0x21
LEDCNTRL = 0x22
CONTROL2 = 0x23
ALARM = 0x29

# Read only registers
LED2VAL = 0x2A
ALED2VAL = 0x2B
LED1VAL = 0x2C
ALED1VAL = 0x2D
LED2_ALED2VAL = 0x2E
LED1_ALED1VAL = 0x2F
DIAG = 0x30
# Fin de definicion de registros
#--------------------------------------------------------------------------------

#inicializacion de valores de los registros
#definidos como lista de 3 bytes, requerido para el metodo WREG()
CONTROL0_VAL = [0x00,0x00,0x00] #0x000000
#Registros del 01-1D se calculan en funcion de PRF,DUTYCYCLE y AFECLK
#PRF = 500 #Pulse repetition frequency 62.5 a 5000 SPS
#DUTYCYCLE = 25
#AFECLK = 4000000  #Reloj del AFE 4MHz
PRP =  [0, 31, 63]           #int((AFECLK/PRF) - 1)    # for 100HZ - 39999 /500hz 7999
#DELTA = int(((PRP + 1) * DUTYCYCLE) / 100)   # for 100HZ - 8000
#CONV_DELTA = int((PRP + 1) / 4)              # for 100HZ - 10000
#ADCRESET_DELAY = 5
#--------------01-al-1D------------------------------------------
LED2STC_VAL = [0, 23, 192] #int(((PRP + 1) * 3) / 4 + 80)   # for 100HZ - 30080
LED2ENDC_VAL = [0, 31, 62] #LED2STC_VAL - 80 + DELTA - 2   # for 100HZ - 37998
LED2LEDSTC_VAL = [0, 23, 112] #LED2STC_VAL - 80            # for 100HZ - 30000
LED2LEDENDC_VAL = [0, 31, 63]#LED2ENDC_VAL + 1           # for 100HZ - 37999
ALED2STC_VAL = [0, 0, 80] #80                           # for 100HZ - 80
ALED2ENDC_VAL = [0, 7, 206]#DELTA - 2                   # for 100HZ - 7998
LED1STC_VAL =[0, 8, 32]# int((PRP + 1) / 4 + 80)       # for 100HZ - 10080
LED1ENDC_VAL = [0, 15, 158]#LED1STC_VAL - 80 + DELTA - 2  # for 100HZ - 17998
LED1LEDSTC_VAL = [0, 7, 208]#LED1STC_VAL - 80           # for 100HZ - 10000
LED1LEDENDC_VAL = [0, 15, 159]#LED1ENDC_VAL + 1          # for 100HZ - 17999
ALED1STC_VAL = [0, 15, 240]#int((PRP + 1) / 2 + 80)     # for 100HZ - 20080
ALED1ENDC_VAL = [0, 23, 110]#ALED1STC_VAL - 80 + DELTA - 2  # for 100HZ - 27998
LED2CONVST_VAL = [0, 0, 6]#ADCRESET_DELAY + 1        # for 100HZ - 6
LED2CONVEND_VAL = [0, 7, 207]#(LED2CONVST_VAL-(ADCRESET_DELAY+1)+CONV_DELTA-1) # for 100HZ - 9999
ALED2CONVST_VAL = [0, 7, 214]#CONV_DELTA + ADCRESET_DELAY + 1  # for 100HZ - 10006
ALED2CONVEND_VAL = [0, 15, 159]#ALED2CONVST_VAL - (ADCRESET_DELAY + 1) + CONV_DELTA - 1  # for 100HZ - 19999
LED1CONVST_VAL = [0, 15, 166]#(CONV_DELTA * 2) + (ADCRESET_DELAY + 1)  # for 100HZ - 20006
LED1CONVEND_VAL =[0, 23, 111]# LED1CONVST_VAL - (ADCRESET_DELAY + 1) + CONV_DELTA - 1  # for 100HZ - 29999
ALED1CONVST_VAL = [0, 23, 118]#(CONV_DELTA * 3) + (ADCRESET_DELAY + 1)  # for 100HZ - 30006
ALED1CONVEND_VAL = [0, 31, 63]#ALED1CONVST_VAL - (ADCRESET_DELAY + 1) + CONV_DELTA - 1  # for 100HZ - 39999
ADCRSTSTCT0_VAL =[0, 0, 0]# 0  # for 100HZ - 0
ADCRSTENDCT0_VAL = [0, 0, 5] #ADCRSTSTCT0_VAL + ADCRESET_DELAY  # for 100HZ - 5
ADCRSTSTCT1_VAL = [0, 7, 208]#CONV_DELTA  # for 100HZ - 10000
ADCRSTENDCT1_VAL = [0, 7, 213] #ADCRSTSTCT1_VAL + ADCRESET_DELAY  # for 100HZ - 10005
ADCRSTSTCT2_VAL = [0, 15, 160]#CONV_DELTA * 2  # for 100HZ - 20000
ADCRSTENDCT2_VAL = [0, 15, 165]#ADCRSTSTCT2_VAL + ADCRESET_DELAY  # for 100HZ - 20005
ADCRSTSTCT3_VAL = [0, 23, 112]#CONV_DELTA * 3  # for 100HZ - 30000
ADCRSTENDCT3_VAL = [0, 23, 117]#ADCRSTSTCT3_VAL + ADCRESET_DELAY  # for 100HZ - 30005
PRPCOUNT_VAL = PRP # set the pulse repetition period (in number of
    #clock cycles of the 4-MHz clock). The PRPCOUNT value must be set in the range of 800 to 64000.
    #generamos una lista con los valores de los registros
#----Fin de inicializacion de registros 01 al 1D---------------------------------------------    
# Inicializacion de registros 1E , 21al 23 y 29
CONTROL1_VAL = [0x00,0x01,0x02] #0x000102 
TIA_AMB_GAIN_VAL =[0x00,0x00,0x00] # 0x000000
LEDCNTRL_VAL = [0x01,0x64,0xFF] #0x0164FF
CONTROL2_VAL =[0x02,0x01,0x00] # 0x020100 
ALARM_VAL = [0x00,0x00,0x00] #0x000000





#------------Definicion de listas utiles------------------------------------------------
AFE4400_Other = [CONTROL1 , TIA_AMB_GAIN , LEDCNTRL , CONTROL2 , ALARM ]

AFE4400_Tiempos = [
LED2STC,
LED2ENDC,
LED2LEDSTC,
LED2LEDENDC,
ALED2STC,
ALED2ENDC,
LED1STC,
LED1ENDC,
LED1LEDSTC,
LED1LEDENDC,
ALED1STC,
ALED1ENDC,
LED2CONVST,
LED2CONVEND,
ALED2CONVST,
ALED2CONVEND,
LED1CONVST,
LED1CONVEND,
ALED1CONVST,
ALED1CONVEND,
ADCRSTSTCT0,
ADCRSTENDCT0,
ADCRSTSTCT1,
ADCRSTENDCT1,
ADCRSTSTCT2,
ADCRSTENDCT2,
ADCRSTSTCT3,
ADCRSTENDCT3,
PRPCOUNT         ]

AFE4400_REGISTROS_W = [CONTROL0] + AFE4400_Tiempos + AFE4400_Other
                     


AFE4400_REG_TIEMP_VAL = [
  LED2STC_VAL,
  LED2ENDC_VAL,
  LED2LEDSTC_VAL,
  LED2LEDENDC_VAL,
  ALED2STC_VAL,
  ALED2ENDC_VAL,
  LED1STC_VAL,
  LED1ENDC_VAL,
  LED1LEDSTC_VAL,
  LED1LEDENDC_VAL,
  ALED1STC_VAL,
  ALED1ENDC_VAL,
  LED2CONVST_VAL,
  LED2CONVEND_VAL,
  ALED2CONVST_VAL,
  ALED2CONVEND_VAL,
  LED1CONVST_VAL,
  LED1CONVEND_VAL,
  ALED1CONVST_VAL,
  ALED1CONVEND_VAL,
  ADCRSTSTCT0_VAL,
  ADCRSTENDCT0_VAL,
  ADCRSTSTCT1_VAL,
  ADCRSTENDCT1_VAL,
  ADCRSTSTCT2_VAL,
  ADCRSTENDCT2_VAL,
  ADCRSTSTCT3_VAL,
  ADCRSTENDCT3_VAL,
  PRPCOUNT_VAL           ]

AFE4400_REG_INI = [
  CONTROL0_VAL,    
  LED2STC_VAL,
  LED2ENDC_VAL,
  LED2LEDSTC_VAL,
  LED2LEDENDC_VAL,
  ALED2STC_VAL,
  ALED2ENDC_VAL,
  LED1STC_VAL,
  LED1ENDC_VAL,
  LED1LEDSTC_VAL,
  LED1LEDENDC_VAL,
  ALED1STC_VAL,
  ALED1ENDC_VAL,
  LED2CONVST_VAL,
  LED2CONVEND_VAL,
  ALED2CONVST_VAL,
  ALED2CONVEND_VAL,
  LED1CONVST_VAL,
  LED1CONVEND_VAL,
  ALED1CONVST_VAL,
  ALED1CONVEND_VAL,
  ADCRSTSTCT0_VAL,
  ADCRSTENDCT0_VAL,
  ADCRSTSTCT1_VAL,
  ADCRSTENDCT1_VAL,
  ADCRSTSTCT2_VAL,
  ADCRSTENDCT2_VAL,
  ADCRSTSTCT3_VAL,
  ADCRSTENDCT3_VAL,
  PRPCOUNT_VAL,
  CONTROL1_VAL,
  TIA_AMB_GAIN_VAL,
  LEDCNTRL_VAL,
  CONTROL2_VAL,
  ALARM_VAL
                          ]