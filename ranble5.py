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
#ser.write("AT+SCAN0")
#sleep(0.03)


AvergSize=5
SaveAvergL=2
data1=[0 for i in xrange(AvergSize)]
data2=[0 for i in xrange(AvergSize)]
data3=[0 for i in xrange(AvergSize)]
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
DictData={Addres1:data1,Addres2:data2,Addres3:data3}
DictAverg={Addres1:Averg1,Addres2:Averg2,Addres3:Averg3}
DictFlags={Addres1:False,Addres2:False,Addres3:False}

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
    sleep(0.03)
    wait=0
    received_data =""

    while wait<TimeOut:
      # print("Iam Wait ",wait)
      # print("Iam koko ",received_data)
       try:
         received_data +=ser.read()           #read serial por
         sleep(0.03)
         data_left =ser.inWaiting()          #check for remaining byte
         received_data += ser.read(data_left)
         Find_Index=received_data.find(EndOfCommand)
         if Find_Index!=-1:
          return True,received_data 
         wait+=1
         sleep(0.03)
       except ValueError:
         print("I Can't Read")
         return False,-1
    print("TimeOut")
    return False,-1

def initialization():

   v,b=SendCommand("AT+RENEW","OK+RENEW",5)
   if v:
     print(b)
   v,b=SendCommand("AT+IMME1","OK+Set:1",10)
   if v:
    print(b)
   v,b=SendCommand("AT+ROLE1","OK+Set:1",10)
   if v:
    print(b)
   v,b=SendCommand("AT+PASS123456","OK+Set:123456",10)
   if v:
    print(b)
#   v,b=SendCommand("AT+RESET","OK+RESET",10)
#   if v:
#    print(b)
   v,b=SendCommand("AT+SCAN1","OK",10)
   if v:
    print(b)
#   v,b=SendCommand("AT+SCAN?","OK",10)
#   if v:
#    print(b)

def FindBLE(StrInput):
    dic={}
    adrList=[]
    temp=StrInput.split('OK+DIS0:')
    for  i in range(1,len(temp)):
       addr=temp[i][:12]
       if addr in Address:
         dic[addr]=temp[i][20:24]
         adrList.append(addr)
    return dic,adrList

     # temp=received_data.strip()
   ## Find_Index=received_data.find('OK+DIS0:')
    #print(Find_Index)
def AvergRssi(Addr,RSSI,PrevAverg,AverSize,Data):
       Data.pop(0)
       try:
         IntRSSI=int(RSSI)
       except ValueError:
         IntRSSI=int(PrevAverg)
       Data.append(IntRSSI)  
       PrevAverg=sum(Data)/AverSize
       print("ADDRESS: " +Addr)
       print("RSSI: %d\n"%(PrevAverg))

       return PrevAverg,Data
initialization()
while True :

    success,received_data=SendCommand("AT+DISC?","OK+DISCE",10)
    if success:
     # print("nono: "+received_data)
      DictFlags={Addres1:False,Addres2:False,Addres3:False}
      Dic_Addr_Rssi,AddresList=FindBLE(received_data)
      for addres in AddresList:
          DictAverg[addres],DictData[addres]= AvergRssi(addres,Dic_Addr_Rssi[addres],DictAverg[addres],AvergSize,DictData[addres])
          DictFlags[addres]=True
          print(sorted(DictData[addres]))
     # for i in AddresList:
      #  print("Addres: "+i)
       # print("RSSI: "+Dic_Addr_Rssi[i])


