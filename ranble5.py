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
SaveAvergL=5
data1=[0 for i in xrange(AvergSize)]
data2=[0 for i in xrange(AvergSize)]
data3=[0 for i in xrange(AvergSize)]
SavedAverg1=[0 for i in xrange(SaveAvergL)]
SavedAverg2=[0 for i in xrange(SaveAvergL)]
SavedAverg3=[0 for i in xrange(SaveAvergL)]
Addres1='3CA308A0264D'
Addres2='3CA3089EA12B' #target
Addres3='3CA3089EA63B'
Address=[Addres1,Addres2,Addres3]
DictData={Addres1:data1,Addres2:data2,Addres3:data3}
DictAverg={Addres1:SavedAverg1,Addres2:SavedAverg2,Addres3:SavedAverg3}
DictFlags={Addres1:False,Addres2:False,Addres3:False}
DictMedian={Addres1:[0,0],Addres2:[0,0],Addres3:[0,0]}
DictCon={Addres1:0,Addres3:0}


RecevierData=[0,0]
count=0
count2=0
Averg1=-40
Averg2=-40
Averg3=-40
WaitConToReciver=5
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

f4=1
f5=0
con1=1
con2=1
conect=5
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
def AvergRssi(Addr,RSSI,Averg,AverSize,Data,Median):
       Median[0]=Median[1]
       PrevAver=Averg[-1]
       Data.pop(0)
       Averg.pop(0)
       try:
         IntRSSI=int(RSSI)
       except ValueError:
         IntRSSI=int(PrevAverg)
       Data.append(IntRSSI)  
       PrevAver=sum(Data)/AverSize
       Averg.append(PrevAver)
       aray=sorted(Averg)
 #      Averg.pop()

      # n=len(aray)
       Median[1]=aray[AverSize/2]
      # print("Iam aray: %d"%Median[1])

#       Averg.append(PrevAver)
       print("ADDRESS: " +Addr)
       print("RSSI: %d\n"%(Median[1]))

       return Averg,Data,Median
def ConToReciver(adr,recevierData):
    success,received_data=SendCommand("AT+CON"+adr,"OK+CONNA",10)
    if success:
      Count=0
      print("Con To Reciver: "+adr)
      received_data =""
      while Count<WaitConToReciver:
        try:
          received_data +=ser.read()           #read serial por
          sleep(0.03)
          data_left =ser.inWaiting()          #check for remaining byte
          received_data += ser.read(data_left)
          Find_Index=received_data.find('START')
          if Find_Index!=-1:
            try:
              indexx=int(received_data[Find_Index+5])
              value=int(received_data[Find_Index+6:Find_Index+9])
            except ValueError:
              return False,recevierData
            recevierData[indexx-1]=value
            print("Iam rcevRssi: ")
            print(recevierData)
            GPIO.output(DisConPin,True)
            sleep(0.03)
            GPIO.output(DisConPin,False)
            return True,recevierData
          sleep(0.03)
        except ValueError:
          print("I Can't Read")
          return False,recevierData
    print("TimeOut")
    return False,recevierData



initialization()
sleep(1)
while True :

    success,received_data=SendCommand("AT+DISC?","OK+DISCE",10)
    if success:
     # print("nono: "+received_data)
      DictFlags={Addres1:False,Addres2:False,Addres3:False}
      Dic_Addr_Rssi,AddresList=FindBLE(received_data)
      for addres in AddresList:
          DictAverg[addres],DictData[addres],DictMedian[addres]= AvergRssi(addres,Dic_Addr_Rssi[addres],DictAverg[addres],AvergSize,DictData[addres],DictMedian[addres])
          DictFlags[addres]=True
         # aray=sorted(DictAverg[addres])
         # n=len(aray)
         # print("Iam aray: %d"%aray[n/2])
      if DictFlags[Addres2]:
          BarCount=display.ShowLCD_BarGraph(DictMedian[Addres2][1],-88,3,2)
         # print(DictMedian[Addres2])
          if (DictAverg[Addres2][-1]-DictMedian[Addres2][1])<2:
            GPIO.output(ForwardPin,False)
            GPIO.output(BackwardPin,True)
          elif  (DictAverg[Addres2][-1]-DictMedian[Addres2][1])>-2:
            GPIO.output(ForwardPin,True)
            GPIO.output(BackwardPin,False)
          else:
            GPIO.output(ForwardPin,False)
            GPIO.output(BackwardPin,False)

      if conect==10:
        if (DictCon[Addres1])and(DictCon[Addres3]):
           DictCon[Addres1]=0
           DictCon[Addres3]=0
           conect=0
        else:
           if DictFlags[Addres1]and not(DictCon[Addres1]):
              DictCon[Addres1],RecevierData= ConToReciver(Addres1,RecevierData)
              sleep(2)
           if DictFlags[Addres3]and not(DictCon[Addres3]):
              DictCon[Addres3],RecevierData= ConToReciver(Addres3,RecevierData)
              sleep(2)
      elif (DictFlags[Addres1] and DictFlags[Addres3]):
        conect+=1
     ## print("Iam Conecnt count ")
     ## print(conect)
     # for i in AddresList:
      #  print("Addres: "+i)
       # print("RSSI: "+Dic_Addr_Rssi[i])


