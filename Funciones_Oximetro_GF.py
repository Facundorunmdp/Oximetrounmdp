# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 23:06:43 2022

@author: Roldan Facundo in April 2018 Update
"""
#lista con los valores de CF en pF
list_cf=[5, 10, 20, 25, 30, 35,45,50,55,60,70,75,80,85,95,100,155,160,170,175,180,185,195,200,205,210,220,225,230,235,245,250 ]


# CONTROL0 - Registro de escritura únicamente
CONTROL0 = 0x00
CONTROL0_VAL = 0x000000
#bits de CONTROL0
SPI_READB = 0x000001        # Lectura SPI (ERROR)
TIM_CNT_RST = 0x000002      # Reinicio del contador del temporizador
DIAG_EN = 0x000004          # Habilitación de diagnóstico
SW_RST = 0x000008           # Reinicio de software

# CONTROL1 - Registro de lectura/escritura
CONTROL1 = 0x1E
TIMEREN = 0x000100           # Habilitación del temporizador
CONTROL1_VAL = (TIMEREN + 0x000002)
SAMPLE_LED2_SAMPLE_LED1 = 0x000000    # Relojes en pines ALM
LED2_PULSE_LED1_PULSE = 0x000200      # Relojes en pines ALM
SAMPLE_LED2_SAMPLE_LED1_PULSE = 0x000400  # Relojes en pines ALM
LED2_CONVERT_LED1_CONVERT = 0x000600  # Relojes en pines ALM
LED2_AMBIENT_LED1_AMBIENT = 0x000800  # Relojes en pines ALM
NO_OUTPUT_NO_OUTPUT = 0x000A00        # Relojes en pines ALM

SPARE = 0x1F #No habilitado

TIAGAIN = 0x20
TIAGAIN_VAL = 0x000000
TIA_AMB_GAIN = 0x21
TIA_AMB_GAIN_VAL = 0x000000
"/esto aparentemente no se usa"
#bits2-0
RF_LED2_500K = 0x000000    # Programar RF para LED2
RF_LED2_250K = 0x000001    # Programar RF para LED2
RF_LED2_100K = 0x000002    # Programar RF para LED2
RF_LED2_50K = 0x000003     # Programar RF para LED2
RF_LED2_25K = 0x000004     # Programar RF para LED2
RF_LED2_10K = 0x000005     # Programar RF para LED2
RF_LED2_1M = 0x000006      # Programar RF para LED2
RF_LED2_NONE = 0x000007    # Programar RF para LED2
#bits 7-3
CF_LED2_5P = 0x000000      # Program CF for LED2 5pFarad
CF_LED2_5P_5P = 0x000008   # 10% de brillo para LED2
CF_LED2_15P_5P = 0x000010  # 15% de brillo para LED2
CF_LED2_20P_5P = 0x000018  # 20% de brillo para LED2
CF_LED2_25P_5P = 0x000020  # 25% de brillo para LED2
CF_LED2_30P_5P = 0x000028  # 30% de brillo para LED2
CF_LED2_40P_5P = 0x000030  # 40% de brillo para LED2
CF_LED2_45P_5P = 0x000038  # 45% de brillo para LED2
CF_LED2_50P_5P = 0x000040  # 50% de brillo para LED2
CF_LED2_55P_5P = 0x000048    # 55% de brillo para LED2
CF_LED2_65P_5P = 0x000050    # 65% de brillo para LED2
CF_LED2_70P_5P = 0x000058    # 70% de brillo para LED2
CF_LED2_75P_5P = 0x000060    # 75% de brillo para LED2
CF_LED2_80P_5P = 0x000068    # 80% de brillo para LED2
CF_LED2_90P_5P = 0x000070    # 90% de brillo para LED2
CF_LED2_95P_5P = 0x000078    # 95% de brillo para LED2
CF_LED2_150P_5P = 0x000080   # 150% de brillo para LED2
CF_LED2_155P_5P = 0x000088   # 155% de brillo para LED2
CF_LED2_165P_5P = 0x000090   # 165% de brillo para LED2
CF_LED2_170P_5P = 0x000098   # 170% de brillo para LED2
CF_LED2_175P_5P = 0x0000A0   # 175% de brillo para LED2
CF_LED2_180P_5P = 0x0000A8   # 180% de brillo para LED2
CF_LED2_190P_5P = 0x0000B0   # 190% de brillo para LED2
CF_LED2_195P_5P = 0x0000B8   # 195% de brillo para LED2
CF_LED2_200P_5P = 0x0000C0   # 200% de brillo para LED2
CF_LED2_205P_5P = 0x0000C8   # 205% de brillo para LED2
CF_LED2_215P_5P = 0x0000D0   # 215% de brillo para LED2
CF_LED2_220P_5P = 0x0000D8   # 220% de brillo para LED2
CF_LED2_225P_5P = 0x0000E0   # 225% de brillo para LED2
CF_LED2_230P_5P = 0x0000E8   # 230% de brillo para LED2
CF_LED2_240P_5P = 0x0000F0   # 240% de brillo para LED2
CF_LED2_245P_5P = 0x0000F8   # 245% de brillo para LED2

#Stage 2 gain setting bits 10-8
STG2GAIN_LED2_0DB = 0x000000 # Configuración de ganancia del LED2 en 0 dB
STG2GAIN_LED2_3DB = 0x000100 # Configuración de ganancia del LED2 en 3 dB
STG2GAIN_LED2_6DB = 0x000200 # Configuración de ganancia del LED2 en 6 dB
STG2GAIN_LED2_9DB = 0x000300 # Configuración de ganancia del LED2 en 9 dB
STG2GAIN_LED2_12DB = 0x000400 # Configuración de ganancia del LED2 en 12 dB
STG2GAIN_LED2 = 0x000700 # Configuración de ganancia del LED2 en general
#bit 14
STAGE2EN_LED2 = 0x004000 # Habilitación de etapa 2 para LED2
#bits 19-16
AMBDAC_0uA = 0x000000 # Valor del DAC ambiental en 0 uA
AMBDAC_1uA = 0x010000 # Valor del DAC ambiental en 1 uA
AMBDAC_2uA = 0x020000 # Valor del DAC ambiental en 2 uA
AMBDAC_3uA = 0x030000 # Valor del DAC ambiental en 3 uA
AMBDAC_4uA = 0x040000 # Valor del DAC ambiental en 4 uA
AMBDAC_5uA = 0x050000 # Valor del DAC ambiental en 5 uA
AMBDAC_6uA = 0x060000 # Valor del DAC ambiental en 6 uA
AMBDAC_7uA = 0x070000 # Valor del DAC ambiental en 7 uA
AMBDAC_8uA = 0x080000 # Valor del DAC ambiental en 8 uA
AMBDAC_9uA = 0x090000 # Valor del DAC ambiental en 9 uA
AMBDAC_10uA = 0x0A0000 # Valor del DAC ambiental en 10 uA
"/hasta aca no se usa"
# Constante para controlar los LED
LEDCNTRL = 0x22
LEDCNTRL_VAL = 0x0164FF # Valor asociado a LEDCNTRL
LED2_CURRENT = 0x0000FF # Programa la corriente para el LED2
LED1_CURRENT = 0x00FF00 # Programa la corriente para el LED1
# Rango de corriente para LED, según el tipo de LED
LED_RANGE_0 = 0x000000 # rango completo,  150mA / 100mA / 200mA / 150mA
LED_RANGE_1 = 0x010000 # rango medio, 75mA  / 50mA  / 100mA / 75mA
LED_RANGE_2 = 0x020000 # rango completo,150mA / 100mA / 200mA / 150mA
LED_RANGE_3 = 0x030000 # apagado,  OFF   / OFF   / OFF   / OFF

# CONTROL2 register
CONTROL2 = 0x23
CONTROL2_VAL = 0x020100
PDN_AFE_OFF = 0x000000  # AFE power-down (Powered on)
PDN_AFE_ON = 0x000001  # AFE power-down (Powered off)
PDN_RX_OFF = 0x000000  # Rx power-down (Powered on)
PDN_RX_ON = 0x000002  # Rx power-down (Powered off)
PDN_TX_OFF = 0x000000  # Tx power-down (Powered on)
PDN_TX_ON = 0x000004  # Tx power-down (Powered off)
XTAL_ENABLE = 0x000000  # The crystal module is enabled
XTAL_DISABLE = 0x000200  # The crystal module is disabled
DIGOUT_TRISTATE_DISABLE = 0x000000  # Digital tristate disabled esto se utiliza cuando se comparte el bus spi
DIGOUT_TRISTATE_ENABLE = 0x000400  # Digital tristate enabled
TXBRGMOD_H_BRIDGE = 0x000000  # Tx bridge mode
TXBRGMOD_PUSH_PULL = 0x000800  # Tx bridge mode
ADC_BYP_DISABLE = 0x000000  # ADC bypass mode enable
ADC_BYP_ENABLE = 0x008000  # ADC bypass mode enable
RST_CLK_ON_PD_ALM_PIN_DISABLE = 0x000000  # RST CLK on PD_ALM pin disable
RST_CLK_ON_PD_ALM_PIN_ENABLE = 0x010000  # RST CLK on PD_ALM pin enable
TX_REF_0 = 0x000000  # Tx reference voltage - 0.75V
TX_REF_1 = 0x020000  # Tx reference voltage - 0.5V
TX_REF_2 = 0x040000  # Tx reference voltage - 1.0V
TX_REF_3 = 0x060000  # Tx reference voltage - 0.75V

# ALARM register
ALARM = 0x29
ALARM_VAL = 0x000000
ALMPINCLKEN = 0x000080  # Alarm pin clock enable (Enables CLKALMPIN)

# Read only registers
LED2VAL = 0x2A
ALED2VAL = 0x2B
LED1VAL = 0x2C
ALED1VAL = 0x2D
LED2_ALED2VAL = 0x2E
LED1_ALED1VAL = 0x2F
DIAG = 0x30

# End of Read only registers

#Registros del 01-1D
PRF = 500 #Pulse repetition frequency 62.5 a 5000 SPS
DUTYCYCLE = 25
def List_time( _PRF = 500, _DUTYCYCLE = 25):
    """Modificamos el codigo de  Ti ya que tiene un error en los flancos descendentes
    para esto, cuando utiliza adcreset_delay y suma 2, le debemos sumar 1"""
    PRF = _PRF
    DUTYCYCLE = _DUTYCYCLE
    AFECLK = 4000000  #Reloj del AFE 4MHz
    PRP = int((AFECLK/PRF) - 1)    # for 100HZ - 39999 /500hz 7999
    
    DELTA = int(((PRP + 1) * DUTYCYCLE) / 100)   # for 100HZ - 8000
    CONV_DELTA = int((PRP + 1) / 4)              # for 100HZ - 10000
    ADCRESET_DELAY = 5
    
    LED2STC = 0x01
    LED2STC_VAL = int(((PRP + 1) * 3) / 4 + 80)   # for 100HZ - 30080
    
    LED2ENDC = 0x02
    LED2ENDC_VAL = LED2STC_VAL - 80 + DELTA - 2   # for 100HZ - 37998
    LED2LEDSTC = 0x03
    LED2LEDSTC_VAL = LED2STC_VAL - 80            # for 100HZ - 30000
    LED2LEDENDC = 0x04
    LED2LEDENDC_VAL = LED2ENDC_VAL + 1           # for 100HZ - 37999
    ALED2STC = 0x05
    ALED2STC_VAL = 80                           # for 100HZ - 80
    ALED2ENDC = 0x06
    ALED2ENDC_VAL = DELTA - 2                   # for 100HZ - 7998
    LED1STC = 0x07
    LED1STC_VAL = int((PRP + 1) / 4 + 80)       # for 100HZ - 10080
    LED1ENDC = 0x08
    LED1ENDC_VAL = LED1STC_VAL - 80 + DELTA - 2  # for 100HZ - 17998
    LED1LEDSTC = 0x09
    LED1LEDSTC_VAL = LED1STC_VAL - 80           # for 100HZ - 10000
    LED1LEDENDC = 0x0A
    LED1LEDENDC_VAL = LED1ENDC_VAL + 1          # for 100HZ - 17999
    ALED1STC = 0x0B
    ALED1STC_VAL = int((PRP + 1) / 2 + 80)     # for 100HZ - 20080
    ALED1ENDC = 0x0C
    ALED1ENDC_VAL = ALED1STC_VAL - 80 + DELTA - 2  # for 100HZ - 27998
    
    LED2CONVST = 0x0D
    LED2CONVST_VAL = ADCRESET_DELAY + 1        # for 100HZ - 6
    LED2CONVEND = 0x0E
    LED2CONVEND_VAL = (LED2CONVST_VAL-(ADCRESET_DELAY+1)+CONV_DELTA-1) # for 100HZ - 9999
    ALED2CONVST = 0x0F
    ALED2CONVST_VAL = CONV_DELTA + ADCRESET_DELAY + 1  # for 100HZ - 10006
    ALED2CONVEND = 0x10
    ALED2CONVEND_VAL = ALED2CONVST_VAL - (ADCRESET_DELAY + 1) + CONV_DELTA - 1  # for 100HZ - 19999
    LED1CONVST = 0x11
    LED1CONVST_VAL = (CONV_DELTA * 2) + (ADCRESET_DELAY + 1)  # for 100HZ - 20006
    LED1CONVEND = 0x12
    LED1CONVEND_VAL = LED1CONVST_VAL - (ADCRESET_DELAY + 1) + CONV_DELTA - 1  # for 100HZ - 29999
    ALED1CONVST = 0x13
    ALED1CONVST_VAL = (CONV_DELTA * 3) + (ADCRESET_DELAY + 1)  # for 100HZ - 30006
    ALED1CONVEND = 0x14
    ALED1CONVEND_VAL = ALED1CONVST_VAL - (ADCRESET_DELAY + 1) + CONV_DELTA - 1  # for 100HZ - 39999
    ADCRSTSTCT0 = 0x15
    ADCRSTSTCT0_VAL = 0  # for 100HZ - 0
    ADCRSTENDCT0 = 0x16
    ADCRSTENDCT0_VAL = ADCRSTSTCT0_VAL + ADCRESET_DELAY  # for 100HZ - 5
    ADCRSTSTCT1 = 0x17
    ADCRSTSTCT1_VAL = CONV_DELTA  # for 100HZ - 10000
    ADCRSTENDCT1 = 0x18
    ADCRSTENDCT1_VAL = ADCRSTSTCT1_VAL + ADCRESET_DELAY  # for 100HZ - 10005
    ADCRSTSTCT2 = 0x19
    ADCRSTSTCT2_VAL = CONV_DELTA * 2  # for 100HZ - 20000
    ADCRSTENDCT2 = 0x1A
    ADCRSTENDCT2_VAL = ADCRSTSTCT2_VAL + ADCRESET_DELAY  # for 100HZ - 20005
    ADCRSTSTCT3 = 0x1B
    ADCRSTSTCT3_VAL = CONV_DELTA * 3  # for 100HZ - 30000
    ADCRSTENDCT3 = 0x1C
    ADCRSTENDCT3_VAL = ADCRSTSTCT3_VAL + ADCRESET_DELAY  # for 100HZ - 30005
    PRPCOUNT = 0x1D
    PRPCOUNT_VAL = PRP # set the pulse repetition period (in number of
    #clock cycles of the 4-MHz clock). The PRPCOUNT value must be set in the range of 800 to 64000.
    #generamos una lista con los valores de los registros
    Tiempos = [
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
        PRPCOUNT_VAL]
    return Tiempos    

"""
AFE44xx_Current_Register_Settings = [
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
PRP,
CONTROL1_VAL,
0x000000,
TIAGAIN_VAL,
TIA_AMB_GAIN_VAL,
LEDCNTRL_VAL,
CONTROL2_VAL
]

"""
"""
        ----Botones ventana configuracion------
        btnConectar
        barBat    self.barBat.setMaximum(100)  self.barBat.setValue(count)
        lblTime
        --pestana datos del paciente
        lblfecha
        txtnombre
        txtemail
        txtObservaciones
        pbGuardarDatos
        --pestana configuracion
        cbMuestreo
        pbreferencial
        pbBipolar
        pbConfiguracion
        pbVisualizar
        --pestana pruebas
          --pestaña registros
          cbcfg1samples
          cbcfg2origen
          cbcfg2amplitud
          cbcfg2frecuencia
          cbcfg3medicion
          cbcfg3referencia
          cbcfg3buffer
          cbcfg3sensar
          cbcfg4modo
          cbcfg4comparador
          
          cbsrb1
          cbloffumbral
          cbloffmagnitud
          cblofffrecuencia
          cbch1estado
          cbch2estado
          cbch3estado
          cbch4estado
          cbch1ganancia
          cbch2ganancia
          cbch3ganancia
          cbch4ganancia
          cbch1srb2
          cbch2srb2
          cbch3srb2
          cbch4srb2
          cbch1entrada
          cbch2entrada
          cbch3entrada
          cbch4entrada
          
          cksenspch1
          cksenspch2
          cksenspch3
          cksenspch4
          cksensnch1
          cksensnch2
          cksensnch3
          cksensnch4
          
          ckloffpch1
          ckloffpch2
          ckloffpch3
          ckloffpch4
          ckloffnch1
          ckloffnch2
          ckloffnch3
          ckloffnch4
          ckflipnch1
          ckflipnch2
          ckflipnch3
          ckflipnch4
          
          pbguardarregistros  #debe guardar los registros en sus variables y en el archivo local,ademas enviar mensaje al dispositivo con los registros 
          pbverregistros   #eviar mensaje al despisitivo para solicitar los registros, guardarlos en sus variables y mostra dwregistros con los valores obtenidos
          pbverestadoelec     #
          dwregistros
          dwelectrodos
          twregistros
          
          
          cbgpio1c
          cbgpio2c
          cbgpio3c
          cbgpio4c
          cbgpio1d
          cbgpio2d
          cbgpio3d
          cbgpio4d
         
          pbiniciarprueba  
          pbpausarprueba
          pbdetenerprueba
        ------------------------------------
        -----Botones ventana visualizacion-------
        btnConectar
        btnDatos
        btnDetener
        btnPausa
        btnContinuar
        """
     