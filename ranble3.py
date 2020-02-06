#!/usr/bin/env python

import serial
import lcddriver
from time import sleep

display=lcddriver.lcd()

display.lcd_display_string("The Target Range",1)

ser = serial.Serial ("/dev/ttyS0",9600) #Open port with baud rate
#ser.write("AT+RENEW")
#sleep(1)
ser.write("AT+RESET")
sleep(0.03)
ser.write("AT+IMME1")
sleep(0.03)
ser.write("AT+ROLE1")
sleep(0.03)
ser.write("AT+PSWD=1234")
sleep(0.03)
AvergSize=5
data=[0 for i in xrange(AvergSize)]
count=0
Averg=40
while True :
    received_data =ser.read()           #read serial port
    sleep(0.03)
    data_left =ser.inWaiting()          #check for remaining byte
    received_data += ser.read(data_left)
   # temp=received_data.strip()
    Find_Index=received_data.find('OK+DIS0:')
    print(Find_Index)
    if Find_Index!=-1:
      Addres=received_data[8+Find_Index:20+Find_Index] 
     # print( Addres,'3CA308A0264D',Addres=='3CA308A0264D')
      if Addres=='3CA308A0264D':
         RSSI=received_data[28+Find_Index:32+Find_Index]
         data.pop(0)
         try:
           IntRSSI=int(RSSI)
         except ValueError:
           IntRSSI=int(Averg)
         PrivData=int(data[-1])
         if (((IntRSSI- PrivData >8)or(PrivData-IntRSSI>8))and (Averg>55)):
           IntRSSI=int(Averg)
         data.append(IntRSSI)
         print("ADDRESS: " +Addres+"\n")
         Averg=sum(data)/AvergSize
         print("RSSI: %d\n"%(Averg))
         display.ShowLCD_BarGraph(Averg,-120,5,2)
   # write_data=input("Please enter a command AT as string:\n")
   # print (write_data)
    ser.write("AT+DISC?")              #transmit data serially
    sleep(1)
