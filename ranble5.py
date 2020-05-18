#!/usr/bin/env python

import serial
import lcddriver
from time import sleep
import RPi.GPIO as GPIO
 
 
 
 
##########################GPIO Control#################################
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

GPIO.output(OutOfRange,False)
GPIO.output(DisConPin,False)
GPIO.output(LeftPin,False)
GPIO.output(RightPin,False)
GPIO.output(ForwardPin,False)
GPIO.output(BackwardPin,False)


############Screan#############################################################

display=lcddriver.lcd()
display.lcd_display_string("The Target Range",1)

ser = serial.Serial ("/dev/ttyS0",9600,timeout=2) #Open port with baud rate

BarCount=0
PrevBarCount=0
MIN_RSSI=-80
MAX_RSSI=-60
numLevels=16
###############Addres##########################
SaveAvergL=5
SavedAverg1=[0 for i in xrange(SaveAvergL)]
SavedAverg2=[0 for i in xrange(SaveAvergL)]
SavedAverg3=[0 for i in xrange(SaveAvergL)]
Addres1='3CA308A0264D'
Addres2='3CA3089EA12B' #target
Addres3='3CA3089EA63B'
Address=[Addres1,Addres2,Addres3]
AddrName={Addres1:"Recevier 1 (on the right)",Addres2:"Target",Addres3:"Recevier 3 (on the left)"}
AddresList=[]
#######################Data################################################
AvergSize=5
Delta=5
data1=[0 for i in xrange(AvergSize)]
data2=[0 for i in xrange(AvergSize)]
data3=[0 for i in xrange(AvergSize)]
DictMedian={Addres1:[0,0],Addres2:[0,0],Addres3:[0,0]} #median filter is using after averg filter (maby we will not used)
DictAverg={Addres1:SavedAverg1,Addres2:SavedAverg2,Addres3:SavedAverg3} #data after filter
DictData={Addres1:data1,Addres2:data2,Addres3:data3} #data befor fliter

#Averg1=-40
#Averg2=-40
#Averg3=-40
#MinAverg=-45

########################Coniction to recevres#############################
DictFlags={Addres1:False,Addres2:False,Addres3:False} #flag to show if we find recever in scanning
DictCon={Addres1:0,Addres3:0} #for conction to recevers
RecevierData=[0,0]
#count=0
#count2=0

WaitConToReciver=5
#DisConFlag=0
#ConFlag=0
#MaxDelta=0
#MinDelta=0
#flagRecv=0
Dic_Addr_Rssi={} #after fun FindBLE
#f4=1
#f5=0
#con1=1
#con2=1
conect=0 #for next conection to recvers
#conect1=0
#conect2=0
#f2=0
#Step=2
#MaxV=-32

########for send Comand#############
#TimeOut=0



def SendCommand(command,EndOfCommand,TimeOut):
    ser.write(command) 
    sleep(0.03)
    wait=0
    received_data =""

    while wait<TimeOut:
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
   v,b=SendCommand("AT+ROLE1","OK+Set:1",10) #Master Mode
   if v:
    print(b)
   v,b=SendCommand("AT+PASS123456","OK+Set:123456",10) #passowerd
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

def FindBLE(StrInput): #func to git a dict of BLE address and RSSI values
    dic={}
    adrList=[]
    temp=StrInput.split('OK+DIS0:')
    for  i in range(1,len(temp)):
       addr=temp[i][:12]
       if addr in Address:
         dic[addr]=temp[i][20:24]
         adrList.append(addr)
    return dic,adrList #return a dic of rssi and list of addr


def AvergRssi(Addr,RSSI,Averg,AverSize,Data,Median):
       Median[0]=Median[1] #previous Value of Median filter
       PrevAver=Averg[-1]  #previous Value of Averg filter
       Data.pop(0)
       Averg.pop(0)
       try:
         IntRSSI=int(RSSI)
       except ValueError:
         IntRSSI=int(PrevAverg)
       Data.append(IntRSSI)  #adding a new value to end of the list 
       PrevAver=sum(Data)/AverSize  
       ############
       if((((PrevAver-IntRSSI)**2)>Delta) and (PrevAver<-66)):
           PrevAver=Averg[-1]     
       
       ###########
       Averg.append(PrevAver) 
       aray=sorted(Averg)
 #      Averg.pop()

      # n=len(aray)
      
      ####################################################################################
       #rec=AddrName[Addr]

       #print("From: " +rec)
       #print("RSSI: %d\n"%(Averg[-1]))
       
       #Median[1]=aray[AverSize/2] #get a new median Value
       #print("Iam a New Median : %d"%Median[1])
      #####################################################################################

        ######

       rec=AddrName[Addr]

       print("From: " +rec)
       print("RSSI: %d\n"%(Averg[-1]))
       print("Iam IntRSSI: %d\n"%(IntRSSI))
       ##Median[1]=aray[AverSize/2] #get a new median Value
       ##print("Iam a New Median : %d"%Median[1])
       print("#############################################")
       #####

#       Averg.append(PrevAver)
       #if Addr==Addres1:
        #  rec="Recevier 1 (on the right)"
       #elif Addr==Addres3:
       #   rec="Recevier 3 (on the left)"
       #else:
        #  rec="Target"


       return Averg,Data,Median #return a dic of averg, data after updating , adic of median filter
def ConToReciver(adr,recevierData):
    success,received_data=SendCommand("AT+CON"+adr,"OK+CONNA",10)
    received_data =""
    if success:
      Count=0
      recadr=AddrName[adr]
      print("Con To: "+recadr)
     # received_data =""
      while Count<WaitConToReciver:
        try:
          received_data +=ser.read()           #read serial por
          sleep(0.03)
          data_left =ser.inWaiting()          #check for remaining byte
          received_data += ser.read(data_left)
          print("Iam received_data in ConToReciver ")
          print(received_data)
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
          Find_Index=received_data.find('OK+CONNF')
          if Find_Index!=-1:
             return False,recevierData


          sleep(0.03)
        except ValueError:
          print("I Can't Read")
          return False,recevierData
        Count+=1
    print("TimeOut")
    return False,recevierData

def BarCount(rssi):
   if(rssi<=MIN_RSSI): #-100
      return 0
   elif(rssi>=MAX_RSSI): #-55
      return  numLevels 
   else:
      inputRange=MAX_RSSI-MIN_RSSI
      outputRange=numLevels 
      return (rssi-MIN_RSSI)*outputRange/inputRange



   '''
    if Value>-50:
       count=16
    elif -50>=Value and Value>-60:
       count=14
    elif -60>=Value and Value>-65:
      count=10
    elif -65>=Value and Value>-70:
      count= 7
    elif -70>=Value and Value>-75:
      count= 5
    elif -75>= Value and Value>-80:
      count= 2
    else:
      count= 0
    print("Iam Value: ",Value,"Iam count: ",count)
    return count

    
    MaxV=-83
    if Value >-43:
      Value=-43
    elif Value <MaxV:
      Value=MaxV

    if Value>-55:
       count=10
       temp=-55
       step=2
    elif Value <=-55 and Value >=-73:
       count=3
       temp=-73
       step=3
    else:
       count=0
       temp=MaxV #83
       step=5

    while(temp<=Value):
        count+=1
        temp+=step
    if count>16:
       count=16
    
    return count
   '''
       
def CheackIfCloser(Addr,step=0):
    Bar=BarCount(DictAverg[Addr][-1])
    PrevBar=BarCount(DictAverg[Addr][-2])
    close=False
    goaway=False
   # print("Iam Bar and prevbar: ",Bar,PrevBar)
    if (Bar-PrevBar)<=(-1*step):
         goaway=True
    elif (Bar-PrevBar)>=step:
         close=True
    return close,goaway


def DirectionShow():
   # CloseTo1,IsGoAway1= CheackIfCloser(Addres1)
    CloseTo2,IsGoAway2= CheackIfCloser(Addres2)
   # CloseTo3,IsGoAway3= CheackIfCloser(Addres3)
    if CloseTo2 :
       print("forward")
       GPIO.output(ForwardPin,True)
       GPIO.output(BackwardPin,False)
    elif IsGoAway2:
       GPIO.output(ForwardPin,False)
       GPIO.output(BackwardPin,True)
       print("backward")


'''
def DirectionShow():
    CloseTo1,IsGoAway1= CheackIfCloser(Addres1)
    CloseTo2,IsGoAway2= CheackIfCloser(Addres2)
    CloseTo3,IsGoAway3= CheackIfCloser(Addres3)
    if (RecevierData[0])>(RecevierData[1]):
       if (CloseTo2 and CloseTo3 and IsGoAway1)or(CloseTo1 and IsGoAway2 and IsGoAway3)or((DictAverg[Addres1][-1]>DictAverg[Addres3][-1])and IsGoAway1 and IsGoAway2 and IsGoAway3) :
         GPIO.output(LeftPin,True)
         GPIO.output(RightPin,False)
         print("left1")
       else:
         GPIO.output(LeftPin,False)
         GPIO.output(RightPin,True)
         print("right1")
    else:
      if (DictAverg[Addres1][-1]>DictAverg[Addres3][-1])and((CloseTo2 and CloseTo3 and IsGoAway1)or(IsGoAway2 and IsGoAway3)):
        GPIO.output(LeftPin,True)
        GPIO.output(RightPin,False)
        print("left2")
      else:
        GPIO.output(LeftPin,False)
        GPIO.output(RightPin,True)
        print("right2")
    if CloseTo2 :
       print("forward")
       GPIO.output(ForwardPin,True)
       GPIO.output(BackwardPin,False)
    elif IsGoAway2:
       GPIO.output(ForwardPin,False)
       GPIO.output(BackwardPin,True)
       print("backward")

'''



initialization()
sleep(1)
#display.ShowLCD_BarGraph(5,2)

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
         # BarCount=display.ShowLCD_BarGraph(DictMedian[Addres2][1],-88,3,2)
         # print(DictMedian[Addres2])
          #Bar=BarCount(DictMedian[Addres2][1])
          #PrevBar=BarCount(DictMedian[Addres2][0])
         
          Bar=BarCount(DictAverg[Addres2][-1])
          PrevBar=BarCount(DictAverg[Addres2][-2])
          display.ShowLCD_BarGraph(Bar,2)
          DirectionShow()
         # print("Iam Bar and prevbar: ",Bar,PrevBar)
  
          sleep(1)
      if conect==10:
        if (DictCon[Addres1])and(DictCon[Addres3]):
          # DictCon[Addres1]=0
          # DictCon[Addres3]=0
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



