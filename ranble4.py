#!/usr/bin/env python

import serial
import lcddriver
from time import sleep
import RPi.GPIO as GPIO
 
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
DisConPin=7
GPIO.setup(DisConPin, GPIO.OUT)
display=lcddriver.lcd()
#GPIO.setwarnings(False)
display.lcd_display_string("The Target Range",1)

ser = serial.Serial ("/dev/ttyS0",9600, timeout=2) #Open port with baud rate
#ser.write("AT+RENEW")
#sleep(1)
ser.write("AT+RESET")
sleep(0.03)
ser.write("AT+IMME1")
sleep(0.03)
ser.write("AT+ROLE1")
sleep(0.03)
ser.write("AT+PSWD123456")
sleep(0.03)
AvergSize=5
data1=[0 for i in xrange(AvergSize)]
data2=[0 for i in xrange(AvergSize)]
data3=[0 for i in xrange(AvergSize)]
count=0
Averg1=-40
Averg2=-40
Averg3=-40

MinAverg=-50
DisConFlag=0
ConFlag=0
TimeOut=0
MaxDelta=8
Dic_Addr_Rssi={}
GPIO.output(DisConPin,False)
Addres1='3CA308A0264D'
Addres2='3CA3089EA12B' #target
Addres3='3CA3089EA63B'


def FindBLE(StrInput):
    dic={}
    temp=StrInput.split('OK+DIS0:')
    for  i in range(1,len(temp)):
       dic[temp[i][:12]]=temp[i][20:24]
    return dic


def AvergRssi(Addr,DictAddrRssi,delta,PrevAverg,AverSize,Data,MinAver):
    if Addr in DictAddrRssi:
       RSSI=DictAddrRssi[Addr]
       Data.pop(0)
       try:
         IntRSSI=int(RSSI)
       except ValueError:
         IntRSSI=int(PrevAverg)
       PrivData=int(Data[-1])
       if (((IntRSSI- PrivData >delta)or(PrivData-IntRSSI>delta))and (PrevAverg<MinAver)):
         IntRSSI=int(PrevAverg)
       Data.append(IntRSSI)  
       PrevAverg=sum(Data)/AverSize
       print("ADDRESS: " +Addr)
       print("RSSI: %d\n"%(PrevAverg))

       return True,PrevAverg
    else:
       return False,PrevAverg









while True :
  
    received_data =ser.read()           #read serial por
    sleep(0.03)
    data_left =ser.inWaiting()          #check for remaining byte
    received_data += ser.read(data_left)
     # temp=received_data.strip()
    Find_Index=received_data.find('OK+DIS0:')
   # print(Find_Index)
    #print(received_data.split())
  #  if ConFlag :
   #    if received_data.find('DONE')!=-1:
    #      ConFlag=0
     #     GPIO.output(7,False)

    #else:
    rcevRssi=received_data.find('START1')
    DisConFlag=(rcevRssi!=-1)
    if DisConFlag:
      print("Iam rcevRssi: "+received_data[rcevRssi+6:rcevRssi+9])
      GPIO.output(DisConPin,True)
      sleep(0.03)
      GPIO.output(DisConPin,False)
      DisConFlag=0
    #  ConFlag=0

 
    if (Find_Index!=-1):
     # print(received_data.split('OK+DIS0:'))
      Dic_Addr_Rssi= FindBLE(received_data)
      #print(Dic_Addr_Rssi)
      f1,Averg1=AvergRssi(Addres1,Dic_Addr_Rssi,MaxDelta,Averg1,AvergSize,data1,MinAverg)
      f2,Averg2=AvergRssi(Addres2,Dic_Addr_Rssi,MaxDelta,Averg2,AvergSize,data2,MinAverg)
      f3,Averg3=AvergRssi(Addres3,Dic_Addr_Rssi,MaxDelta,Averg3,AvergSize,data3,MinAverg)
   
      if f1:
       # ConFlag=1
        display.ShowLCD_BarGraph(Averg1,-120,5,2)
   # write_data=input("Please enter a command AT as string:\n")
   # print (write_data)
    if not  ConFlag:
      ser.write("AT+DISC?")              #transmit data serially
     # ser.write("AT+CON3CA308A0264D")
    else:
     # ConFlag=0
     if count ==1:
        ser.write("AT+CON"+Addres1)
        count=0
        ConFlag=0
     else:
        count+=1
     

    sleep(1)


