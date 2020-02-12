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
data=[0 for i in xrange(AvergSize)]
count=0
Averg=-40
MinAverg=-50
DisConFlag=0
ConFlag=0
TimeOut=0
Dic_Addr_Rssi={}
GPIO.output(DisConPin,False)
Addres1='3CA308A0264D'



def FindBLE(StrInput):
    dic={}
    temp=StrInput.split('OK+DIS0:')
    for  i in range(1,len(temp)):
       dic[temp[i][:12]]=temp[i][20:24]
    return dic










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
     # print(Dic_Addr_Rssi)
      #Addres=received_data[8+Find_Index:20+Find_Index] 
     # print( Addres,'3CA308A0264D',Addres=='3CA308A0264D')
     # rssi=received_data[28+Find_Index:32+Find_Index]
     # print("ADDRESS: " +Addres+"\n")
     # print("RSSI: "+rssi+"\n")
      if Addres1 in Dic_Addr_Rssi:
        # sleep(1)
         #ser.write("AT+CON3CA308A0264D")
         #sleep(0.03)
         ConFlag=1
         #RSSI=received_data[28+Find_Index:32+Find_Index]
         RSSI=Dic_Addr_Rssi[Addres1]
         data.pop(0)
         try:
           IntRSSI=int(RSSI)
         except ValueError:
           IntRSSI=int(Averg)
         PrivData=int(data[-1])
         if (((IntRSSI- PrivData >8)or(PrivData-IntRSSI>8))and (Averg<MinAverg)):
           IntRSSI=int(Averg)
         data.append(IntRSSI)
         print("ADDRESS: " +Addres1+"\n")
         Averg=sum(data)/AvergSize
         print("RSSI: %d\n"%(Averg))
         display.ShowLCD_BarGraph(Averg,-120,5,2)
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


