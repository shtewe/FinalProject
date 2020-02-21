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
AvergSize=3
SaveAvergL=3
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
MaxDelta=2
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
f5=1
con1=1
con2=1
conect1=0
conect2=0
f2=0
AddresList=[]
#CloseTo1=0
#CloseTo2=0
#CloseTo3=0
#def CheackIfCloser():
"""

   if ((data1[-1]-Averg1)>0)and((data1[-2]-Averg1)>0):
      Clos1=1
   elif ((data1[-1]-Averg1)<0)and((data1[-2]-Averg1)<0):
      Clos1=2
   else:
      Clos1=3

   if ((data2[-1]-Averg2)>0)and((data2[-2]-Averg2)>0):
      Clos2=1
   elif ((data2[-1]-Averg2)<0)and((data2[-2]-Averg2)<0):
      Clos2=2
   else:
      Clos2=3

   if ((data3[-1]-Averg3)>0)and((data3[-2]-Averg3)>0):
      Clos3=1
   elif ((data3[-1]-Averg3)<0)and((data3[-2]-Averg3)<0):
      Clos3=2
   else:
      Clos3=3

   return Clos1,Clos2,Clos3
"""
def CheackIfCloser():

   if ((SavedAverg1[-1]-SavedAverg1[-2])>0)and((SavedAverg1[-2]-SavedAverg1[-3])>0):
      Clos1=1
   elif ((SavedAverg1[-1]-SavedAverg1[-2])<0)and((SavedAverg1[-2]-SavedAverg1[-3])<0):
      Clos1=2
   else:
      Clos1=3

    

   if ((SavedAverg2[-1]-SavedAverg2[-2])>0)and((SavedAverg2[-2]-SavedAverg2[-3])>0):
      Clos2=1
   elif ((SavedAverg2[-1]-SavedAverg2[-2])<0)and((SavedAverg2[-2]-SavedAverg2[-3])<0):
      Clos2=2
   else:
      Clos2=3

   if ((SavedAverg3[-1]-SavedAverg3[-2])>0)and((SavedAverg3[-2]-SavedAverg3[-3])>0):
      Clos3=1
   elif ((SavedAverg3[-1]-SavedAverg3[-2])<0)and((SavedAverg3[-2]-SavedAverg3[-3])<0):
      Clos3=2
   else:
      Clos3=3

   return Clos1,Clos2,Clos3

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


def AvergRssi(Addr,RSSI,PrevAverg,AverSize,Data):
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

       return PrevAverg



def DirectionShow():
    CloseTo1,CloseTo2,CloseTo3= CheackIfCloser()
    if (RecevierData[0])<(RecevierData[1]):
       if (CloseTo2 and CloseTo3 and(not CloseTo1))or(CloseTo1 and(not(CloseTo2 and CloseTo3)))or((Averg1>Averg3)and(not(CloseTo1 and CloseTo2 and CloseTo3))):
         GPIO.output(LeftPin,True)
         GPIO.output(RightPin,False)
         print("left1")
       else:
         GPIO.output(LeftPin,False)
         GPIO.output(RightPin,True)
         print("right1")

    else:
      if (CloseTo2 and CloseTo3 and(not CloseTo1))or(not(CloseTo2 and CloseTo3)):
        GPIO.output(LeftPin,True)
        GPIO.output(RightPin,False)
        print("left2")
      else:
        GPIO.output(LeftPin,False)
        GPIO.output(RightPin,True)
        print("right2")

   # if PrevBarCount <BarCount:
    if CloseTo2==1 : 
       print("forward")
       GPIO.output(ForwardPin,True)
       GPIO.output(BackwardPin,False)
#    elif PrevBarCount>BarCount:
    elif CloseTo2==2:
       GPIO.output(ForwardPin,False)
       GPIO.output(BackwardPin,True)
       print("backward")
    else:
       GPIO.output(ForwardPin,False)
       GPIO.output(BackwardPin,False)
       print("Stop")

def GetReceiverData(adr):
  indexx=0
  value=0
  cont=0
 # received_data =ser.read()
  data_left =ser.inWaiting() 
  received_data = ser.read(data_left)
  while cont<5:
      try: 
         ser.write("AT+CON"+adr)
         sleep(0.5)
         received_data =ser.read()           #read serial por
         sleep(0.03)
         data_left =ser.inWaiting()          #check for remaining byte
         received_data += ser.read(data_left)
         rcevRssi=received_data.find('START')

      except ValueError:
         return False

      DisConFlag=(rcevRssi!=-1)
      if DisConFlag:
        try:
          indexx=int(received_data[rcevRssi+5])
          value=int(received_data[rcevRssi+6:rcevRssi+9])
        except ValueError:
          return False
        RecevierData[indexx-1]=value
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
      Dic_Addr_Rssi,AddresList= FindBLE(received_data)
      #print(Dic_Addr_Rssi)
      if Addres1 in AddresList:
         f1=1
        ## temp=Averg1
         SavedAverg1.pop(0)
         Averg1=AvergRssi(Addres1,Dic_Addr_Rssi[Addres1],Averg1,AvergSize,data1)  # (Addr,RSSI,PrevAverg,AverSize,Data)
         SavedAverg1.append(Averg1)
        ## if Averg1< MinAverg:
         ##   Delta=MinDelta
         ##else:
          ##  Delta=MaxDelta
        ## CloseTo1=(Averg1-temp)>Delta
      else:
         f1=0
      if Addres2 in AddresList:
         f2=1
        ## temp=Averg2
         SavedAverg2.pop(0)
         Averg2=AvergRssi(Addres2,Dic_Addr_Rssi[Addres2],Averg2,AvergSize,data2)
         SavedAverg2.append(Averg2)
        ## if Averg2< MinAverg:
         ##   Delta=MinDelta
        ## else:
         ##   Delta=MaxDelta         
         ##CloseTo2=(Averg2-temp)>Delta
      else:
         f2=0
      if Addres3 in AddresList:
         f3=1
       ##  temp=Averg3
         SavedAverg3.pop(0)
         Averg3=AvergRssi(Addres3,Dic_Addr_Rssi[Addres3],Averg3,AvergSize,data3)
         SavedAverg3.append(Averg3)

       ##  if Averg3< MinAverg:
        ##    Delta=MinDelta
        ## else:
         ##   Delta=MaxDelta
        ## CloseTo3=(Averg3-temp)>Delta
      else:
         f3=0
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
          BarCount=display.ShowLCD_BarGraph(Averg2,-88,3,2)
         # print(BarCount)
          if(f5):
            DirectionShow()
          if (conect1 and conect2 and f4):
            f5=1
           ## f4=0
          else:
            if count2==20:
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


