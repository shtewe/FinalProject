#!/usr/bin/env python

import serial
import lcddriver
from time import sleep
import RPi.GPIO as GPIO
 
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
DisConPin=7
LeftPin=13
RightPin=11
ForwardPin=12
BackwardPin=16
OutOfRange=15

GPIO.setup(ForwardPin, GPIO.OUT)
GPIO.setup(BackwardPin, GPIO.OUT)
GPIO.setup(OutOfRange, GPIO.OUT)
GPIO.setup(DisConPin, GPIO.OUT)
GPIO.setup(LeftPin, GPIO.OUT)
GPIO.setup(RightPin, GPIO.OUT)
display=lcddriver.lcd()
#GPIO.setwarnings(False)
display.lcd_display_string("The Target Range",1)

ser = serial.Serial ("/dev/ttyS0",9600,timeout=2) #Open port with baud rate
#ser.write("AT+RENEW")
#sleep(1)
#ser.write("AT+RESET")
#sleep(0.03)
#ser.write("AT+IMME1")
#sleep(0.03)
#ser.write("AT+ROLE1")
#sleep(0.03)
#ser.write("AT+PSWD123456")
#sleep(0.03)
AvergSize=5
SaveAvergL=2
data1=[]
data2=[]
data3=[]
SavedAverg1=[0 for i in xrange(SaveAvergL)]
SavedAverg2=[0 for i in xrange(SaveAvergL)]
SavedAverg3=[0 for i in xrange(SaveAvergL)]

RecevierData=[0,0]
count=0
count2=0
Averg1=-40
Averg2=-40
Averg3=-40

MinAverg=-45
DisConFlag=0
ConFlag=0
BarCount=0
PrevBarCount=0
TimeOut=0
MaxDelta=0
MinDelta=0
flagRecv=0
Dic_Addr_Rssi={}
GPIO.output(OutOfRange,False)
GPIO.output(DisConPin,False)
GPIO.output(LeftPin,False)
GPIO.output(RightPin,False)
GPIO.output(ForwardPin,False)
GPIO.output(BackwardPin,False)
Addres1='3CA308A0264D'
Addres2='3CA3089EA12B' #target
Addres3='3CA3089EA63B'
Address=[Addres1,Addres2,Addres3]
f4=1
f5=0
con1=1
con2=1
conect1=0
conect2=0
f2=0
Step=2
MaxV=-32
AddresList=[]
#CloseTo1=0
#CloseTo2=0
#CloseTo3=0

def SendCommand(command,EndOfCommand,TimeOut):
    ser.write(command)
    sleep(0.6)
    wait=0
    received_data =""
    while wait<TimeOut:
     # print("Iam Wait ",wait)
      try:
        received_data +=ser.read()           #read serial por
       # sleep(0.03)
        data_left =ser.inWaiting()          #check for remaining byte
        received_data += ser.read(data_left)
        Find_Index=received_data.find(EndOfCommand)
        if Find_Index!=-1:
          return True,received_data 
        wait+=1
        sleep(0.3)
      except ValueError:
          print("I Can't Read")
          return False,-1
    print("TimeOut")
    return False,-1


     

     # temp=received_data.strip()
   ## Find_Index=received_data.find('OK+DIS0:')
    #print(Find_Index)

       


while True :
   # ser.write("AT+DISC?")
   # sleep(0.6)
   # received_data =ser.read()           #read serial por
   # sleep(0.03)
   # data_left =ser.inWaiting()          #check for remaining byte
   # received_data += ser.read(data_left)

     # temp=received_data.strip()
   # Find_Index=received_data.find('OK+DIS0:')
    #print(Find_Index)
    success,received_data=SendCommand("AT+DISC?","OK+DISCE",10)
    if success:
      print("koko: "+received_data)


