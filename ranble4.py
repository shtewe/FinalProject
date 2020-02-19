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
RecevierData=[0,0]
count=0
count2=0
Averg1=-40
Averg2=-40
Averg3=-40

MinAverg=-50
DisConFlag=0
ConFlag=0
BarCount=0
PrevBarCount=0
TimeOut=0
MaxDelta=8
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
f4=1
f5=0
con1=1
con2=1
conect1=0
conect2=0
f2=0
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
      ## PrivData=int(Data[-1])
      # print( PrivData,PrevAverg)
     ##  if (((IntRSSI- PrivData >delta)or(PrivData-IntRSSI>delta))and (PrevAverg<MinAver)):
      ##   IntRSSI=int(PrevAverg)
       Data.append(IntRSSI)  
       PrevAverg=sum(Data)/AverSize
       print("ADDRESS: " +Addr)
       print("RSSI: %d\n"%(PrevAverg))

       return True,PrevAverg
    else:
       return False,PrevAverg



def DirectionShow():
    if (RecevierData[0])>(RecevierData[1]):
       if Averg1>Averg3:
         GPIO.output(LeftPin,True)
         GPIO.output(RightPin,False)
         print("left1")
       else:
         GPIO.output(LeftPin,False)
         GPIO.output(RightPin,True)
         print("right1")

    else:
      if Averg2>Averg3:
        GPIO.output(LeftPin,True)
        GPIO.output(RightPin,False)
        print("left2")
      else:
        GPIO.output(LeftPin,False)
        GPIO.output(RightPin,True)
        print("right2")

    if PrevBarCount <BarCount:
       print("forward")
       GPIO.output(ForwardPin,True)
       GPIO.output(BackwardPin,False)
    elif PrevBarCount>BarCount:
       GPIO.output(ForwardPin,False)
       GPIO.output(BackwardPin,True)
       print("backward")
def GetReceiverData(adr):
  
  cont=0
  while cont<20:
      
      ser.write("AT+CON"+adr)
      sleep(0.5)
      received_data =ser.read()           #read serial por
      sleep(0.03)
      data_left =ser.inWaiting()          #check for remaining byte
      received_data += ser.read(data_left)
      rcevRssi=received_data.find('START')
      DisConFlag=(rcevRssi!=-1)
      if DisConFlag:
        RecevierData[int(received_data[rcevRssi+5])-1]=int(received_data[rcevRssi+6:rcevRssi+9])
        print("Iam rcevRssi: ")
        print(RecevierData)
        GPIO.output(DisConPin,True)
        sleep(0.03)
        GPIO.output(DisConPin,False)
        DisConFlag=0
        return True
      else:
        cont+=1
  return False





while True :
      
    received_data =ser.read()           #read serial por
    sleep(0.03)
    data_left =ser.inWaiting()          #check for remaining byte
    received_data += ser.read(data_left)
     # temp=received_data.strip()
    Find_Index=received_data.find('OK+DIS0:')
    #print(Find_Index)
   # print(received_data)
  #  if ConFlag :
   #    if received_data.find('DONE')!=-1:
    #      ConFlag=0
     #     GPIO.output(7,False)

    #else:
   # rcevRssi=received_data.find('OK+CONNA')
   # if (rcevRssi!=-1):
    #    sleep(1)
     #   continue
  # # rcevRssi=received_data.find('START')
   ## DisConFlag=(rcevRssi!=-1)
   ## if DisConFlag:     
     ## RecevierData[int(received_data[rcevRssi+5])-1]=int(received_data[rcevRssi+6:rcevRssi+9])
     ## print("Iam rcevRssi: ")
     ## print(RecevierData)
      #print("Iam rcevRssi"+received_data[rcevRssi+5]+":"+received_data[rcevRssi+6:rcevRssi+9])
     ## GPIO.output(DisConPin,True)
     ## sleep(0.03)
     ## GPIO.output(DisConPin,False)
     ## DisConFlag=0
    #  ConFlag=0

 
    if (Find_Index!=-1):
     # print(received_data.split('OK+DIS0:'))
      Dic_Addr_Rssi= FindBLE(received_data)
      #print(Dic_Addr_Rssi)
      f1,Averg1=AvergRssi(Addres1,Dic_Addr_Rssi,MaxDelta,Averg1,AvergSize,data1,MinAverg)
      f2,Averg2=AvergRssi(Addres2,Dic_Addr_Rssi,MaxDelta,Averg2,AvergSize,data2,MinAverg)
      f3,Averg3=AvergRssi(Addres3,Dic_Addr_Rssi,MaxDelta,Averg3,AvergSize,data3,MinAverg)
     ## if flagRecv:
      ##  if f1:
       ##   ConFlag=1  
     ## elif f3:
      ##    ConFlag=3
     ## flagRecv=not flagRecv
      if f4:
     # if (f4)and((Averg2-data2[-1])<0):
        if f1 and con1:
          conect1=GetReceiverData(Addres1)
          if conect1:
             con1=0
        if f3 and con2:
          conect2=GetReceiverData(Addres3)
          if conect2:
             con2=0

        
      if f2:
          BarCount=display.ShowLCD_BarGraph(Averg2,-120,5,2)
         # print(BarCount)
          if(f5):
            DirectionShow()
          if (conect1 and conect2 and f4):
            f5=1
            f4=0
          else:
            if count2==40:
               count2=0
               f4=1
               con1=1
               con2=1

            else:
               count2+=1
          GPIO.output(OutOfRange,False)
          TimeOut=0
     
   # write_data=input("Please enter a command AT as string:\n")
   # print (write_data)
  # # if not  ConFlag:
    ser.write("AT+DISC?")              #transmit data serially
     # ser.write("AT+CON3CA308A0264D")
   ## else:
     # ConFlag=0
    ## if count ==1:
      ##  if ConFlag==1:
        ##  adr=Addres1
      ##  else:
        ##  adr=Addres3
      ##  ser.write("AT+CON"+adr)
      ##  count=0
      ##  ConFlag=0
    ## else:
      ##  count+=1
    PrevBarCount=BarCount
    if f2==0: 
      if  TimeOut==10:
         GPIO.output(OutOfRange,True)
         GPIO.output(LeftPin,False)
         GPIO.output(RightPin,False)
         GPIO.output(ForwardPin,False)
         GPIO.output(BackwardPin,False)
      else:
         TimeOut+=1
    sleep(1)


