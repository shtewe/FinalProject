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
def countLeval(Value):
       Value+=40
       count=0
       if Value < MaxV:
          Value=-1*MaxV
       elif Value >0:
          Value =0
       else:
          Value*=-1

       Value=(-1*MaxV)-Value
       while(Value>0):
          Value-=Step
          count+=1
       return count
"""
def CheackIfCloser(data):
   IsCloser=False
   IsGoAway=False
   IsStop=False


   if (data[-1]-data[-2]>0)and(data[-2]-data[-3]>0)and(data[-3]-data[-4]>0):
      IsCloser=True
   elif (data[-1]-data[-2]<0)and(data[-2]-data[-3]<0)and(data[-3]-data[-4]<0):
      IsGoAway=True
   elif (data[-1]-data[-2]==0)and(data[-2]-data[-3]==0)and(data[-3]-data[-4]==0):
      IsStop=True

   return IsCloser,IsGoAway,IsStop

"""
def CheackIfCloser(SavedAverg):
   IsCloser=False
   IsGoAway=False
#   IsStop=False
   NewLevel=countLeval(SavedAverg[-1])
   OldLevel=countLeval(SavedAverg[-2])

#   if ((SavedAverg[-1]-SavedAverg[-2])>0)and((SavedAverg[-2]-SavedAverg[-3])>0):
#      IsCloser=True
#   elif ((SavedAverg[-1]-SavedAverg[-2])<0)and((SavedAverg[-2]-SavedAverg[-3])<0):
#      IsGoAway=True
#   elif((SavedAverg[-1]-SavedAverg[-2])==0)and((SavedAverg[-2]-SavedAverg[-3])==0):
#      IsStop=True
   if (NewLevel>OldLevel):
      IsCloser=True
   else:
      IsGoAway=True
 #  else:
  #    IsStop=True
 


   return IsCloser,IsGoAway

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
    try:
      IntRSSI=int(RSSI)
    except ValueError:
      IntRSSI=int(PrevAverg)
    Data.append(IntRSSI)  
    if len(Data)==AverSize:
      PrevAverg=sum(Data)/AverSize
      print("ADDRESS: " +Addr)
      print("RSSI: %d\n"%(PrevAverg))
      Data=[]


    return PrevAverg,Data



def DirectionShow():
    CloseTo1,IsGoAway1= CheackIfCloser(SavedAverg1)
    CloseTo2,IsGoAway2= CheackIfCloser(SavedAverg2)
    CloseTo3,IsGoAway3= CheackIfCloser(SavedAverg3)
 #   if state2 !=-1:
    if (RecevierData[0])<(RecevierData[1]):
       if (CloseTo2 and CloseTo3 and IsGoAway1)or(CloseTo1 and IsGoAway2 and IsGoAway3)or((Averg1>Averg3)and IsGoAway1 and IsGoAway2 and IsGoAway3)or(CloseTo2 and CloseTo3 and CloseTo1 and (Averg1>Averg3)):
         GPIO.output(LeftPin,True)
         GPIO.output(RightPin,False)
         print("left1")
       else: 
         GPIO.output(LeftPin,False)
         GPIO.output(RightPin,True)
         print("right1")

    else:
      if (CloseTo2 and CloseTo3 and IsGoAway1)or(IsGoAway2 and IsGoAway3 and (Averg1>Averg3))or(CloseTo2 and CloseTo3 and CloseTo1 and (Averg1>Averg3))or(IsGoAway2 and IsGoAway3 and(Averg1>Averg3)and IsGoAway1) :
        GPIO.output(LeftPin,True)
        GPIO.output(RightPin,False)
        print("left2")
      else:
        GPIO.output(LeftPin,False)
        GPIO.output(RightPin,True)
        print("right2")

   # if PrevBarCount <BarCount:
    if CloseTo2 : 
       print("forward")
       GPIO.output(ForwardPin,True)
       GPIO.output(BackwardPin,False)
#    elif PrevBarCount>BarCount:
    else :
       GPIO.output(ForwardPin,False)
       GPIO.output(BackwardPin,True)
       print("backward")
   # elif IsStop2:
    #   GPIO.output(ForwardPin,False)
     #  GPIO.output(BackwardPin,False)
      # print("Stop")

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
         sleep(1)
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
    print(received_data)
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
         Averg1,data1=AvergRssi(Addres1,Dic_Addr_Rssi[Addres1],Averg1,AvergSize,data1)  # (Addr,RSSI,PrevAverg,AverSize,Data)
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
         Averg2,data2=AvergRssi(Addres2,Dic_Addr_Rssi[Addres2],Averg2,AvergSize,data2)
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
         Averg3,data3=AvergRssi(Addres3,Dic_Addr_Rssi[Addres3],Averg3,AvergSize,data3)
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


