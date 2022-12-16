#Light Swarm Pi side

from __future__ import print_function
 
from builtins import chr
from builtins import str
from builtins import range
import sys  
import time 
import random
from datetime import datetime
import os
from threading import Thread
import paho.mqtt.client as paho
import json

import RPi.GPIO as GPIO #Import Raspberry Pi GPIO Library

from netifaces import interfaces, ifaddresses, AF_INET

from socket import *

#GPIO Pin definitions
BUTTON_GPIO = 16
LED_Y = 19

SDI   = 17
RCLK  = 18
SRCLK = 27



VERSIONNUMBER = 7
# packet type definitions
LIGHT_UPDATE_PACKET = 0
RESET_SWARM_PACKET = 1
CHANGE_TEST_PACKET = 2   # Not Implemented
RESET_ME_PACKET = 3
DEFINE_SERVER_LOGGER_PACKET = 4
LOG_TO_SERVER_PACKET = 5
MASTER_CHANGE_PACKET = 6
BLINK_BRIGHT_LED = 7

MYPORT = 2910

SWARMSIZE = 6

#Global Variables
global Log
global ct
global file
global now 
global ct1
global ct2
global ct3
global ct4
global ct5
global ct6
global ct7
global ct8
global flag
global avg_val
global code_H
global code_L
global code
global varid_1
global ip_w

ct1=0
ct2=0
ct3=0
ct4=0
ct5=0
ct6=0
ct7=0
ct8=[]
flag = False
avg_val=0

ct = 0

# we use BX matrix, ROW for anode, and COL for cathode
# ROW  ++++
code_H = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
# COL  ----
code_L = [0xfe,0xfd,0xfb,0xf7,0xef,0xdf,0xbf,0x7f]

code = [0x01,0x03,0x07,0x0f,0x1f,0x3f,0x7f,0xff]

#4digit 7Segment
placePin = (10, 6, 5, 25)
number = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90)

SDI_1 = 24
RCLK_1 = 23
SRCLK_1 = 20
varid_1 = 0


def setup():
    GPIO.setmode(GPIO.BCM)    # Number GPIOs by its BCM location
    GPIO.setup(SDI, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)
    GPIO.output(SDI, GPIO.LOW)
    GPIO.output(RCLK, GPIO.LOW)
    GPIO.output(SRCLK, GPIO.LOW)
    
    GPIO.setup(SDI_1, GPIO.OUT)
    GPIO.setup(RCLK_1, GPIO.OUT)
    GPIO.setup(SRCLK_1, GPIO.OUT)
    for i in placePin:
        GPIO.setup(i, GPIO.OUT)
    
# Shift the data to 74HC595
def hc595_shift(dat):
    global code_H
    global code_L
    
    for bit in range(0, 8): 
        GPIO.output(SDI, 0x80 & (dat << bit))
        GPIO.output(SRCLK, GPIO.HIGH)
        #time.sleep(0.001)
        GPIO.output(SRCLK, GPIO.LOW)
    GPIO.output(RCLK, GPIO.HIGH)
    #time.sleep(0.001)
    GPIO.output(RCLK, GPIO.LOW)

def mapping_func(val, In_min, In_max, Out_min, Out_max):
    return int((val - In_min)*(Out_max-Out_min)/(In_max-In_min)+Out_min)
    

def SendDEFINE_SERVER_LOGGER_PACKET(s):
    print("DEFINE_SERVER_LOGGER_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # get IP address
    for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            print('%s: %s' % (ifaceName, ', '.join(addresses)))
  
    # last interface (wlan0) grabbed 
    print(addresses) 
    myIP = addresses[0].split('.')
    print(myIP) 
    data= ["" for i in range(14)]

    
    data[0] = int("F0", 16).to_bytes(1,'little') 
    data[1] = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(myIP[0]).to_bytes(1,'little') # 1 octet of ip
    data[5] = int(myIP[1]).to_bytes(1,'little') # 2 octet of ip
    data[6] = int(myIP[2]).to_bytes(1,'little') # 3 octet of ip
    data[7] = int(myIP[3]).to_bytes(1,'little') # 4 octet of ip
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
    mymessage = ''.encode()  
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))

def SendRESET_SWARM_PACKET(s):
    print("RESET_SWARM_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    
    data[1] = int(RESET_SWARM_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(0x00).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    data[7] = int(0x00).to_bytes(1,'little')
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
    
    mymessage = ''.encode()  
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))

def parseLogPacket(message):
       
    incomingSwarmID = setAndReturnSwarmID((message[2]))
    print("Log From SwarmID:",(message[2]))
    print("Swarm Software Version:", (message[4]))
    
    print("StringLength:",(message[3]))
    logString = ""
    for i in range(0,(message[3])):
        logString = logString + chr((message[i+5]))


    #print("logString:", logString)
    return logString
    
def buildLog(logString, swarmSize, SwarmID ):
    global file
    global ct
    global ct1
    global ct2
    global ct3
    global ct4
    global ct5
    global ct6
    global ct7
    global ct8
    global now
    global avg_val
    global varid_1
    swarmList = logString.split("|")
    ct7+=1

        #print(SwarmID)
    for i in range(0,swarmSize):
        swarmElement = swarmList[i].split(",")
        print("swarmElement=", swarmElement)
        if (ct>0):
            if (i==0):
                file.write("Message from master, IP:" + str(IP_w) + "\n")
            now = datetime.now()
            file.write(str(now)+","+str(swarmElement[5])+","+str(swarmElement[1])+","+str(swarmElement[3])+"\n")
            if ((SwarmID == 0) and i==0):
                ct1+=1
                master_str = str(SwarmID)
                avg_val = avg_val + int(swarmElement[3])
                value_str = str(swarmElement[3])
                count_str = str(ct1)
                nodered_data = {"Master_Node": master_str, "sensor_val": value_str, "Count": count_str}
                json_data = json.dumps(nodered_data)
                client.publish('sensor_val1',json_data,qos=1)
                #print("Published Sensor1 Data")
            elif (SwarmID == 1 and i==0):
                ct2+=1
                master_str = str(SwarmID)
                avg_val = avg_val + int(swarmElement[3])
                value_str = str(swarmElement[3])
                count_str = str(ct2)
                nodered_data = {"Master_Node": master_str, "sensor_val": value_str, "Count": count_str}
                json_data = json.dumps(nodered_data)
                client.publish('sensor_val2',json_data,qos=1)
                #print("Published Sensor2 Data")
            elif (SwarmID == 2 and i==0):
                ct3+=1
                master_str = str(SwarmID)
                avg_val = avg_val + int(swarmElement[3])
                value_str = str(swarmElement[3])
                count_str = str(ct3)
                nodered_data = {"Master_Node": master_str, "sensor_val": value_str, "Count": count_str}
                json_data = json.dumps(nodered_data)
                client.publish('sensor_val3',json_data,qos=1)
                #print("Published Sensor3 Data")
            elif (SwarmID == 3 and i==0):
                ct4+=1
                master_str = str(SwarmID)
                avg_val = avg_val + int(swarmElement[3])
                value_str = str(swarmElement[3])
                count_str = str(ct4)
                nodered_data = {"Master_Node": master_str, "sensor_val": value_str, "Count": count_str}
                json_data = json.dumps(nodered_data)
                client.publish('sensor_val4',json_data,qos=1)
                #print("Published Sensor4 Data")
            elif (SwarmID == 4 and i==0):
                ct5+=1
                master_str = str(SwarmID)
                avg_val = avg_val + int(swarmElement[3])
                value_str = str(swarmElement[3])
                count_str = str(ct5)
                nodered_data = {"Master_Node": master_str, "sensor_val": value_str, "Count": count_str}
                json_data = json.dumps(nodered_data)
                client.publish('sensor_val5',json_data,qos=1)
                #print("Published Sensor5 Data")
            elif (SwarmID == 5 and i==0):
                ct6+=1
                master_str = str(SwarmID)
                avg_val = avg_val + int(swarmElement[3])
                value_str = str(swarmElement[3])
                count_str = str(ct6)
                nodered_data = {"Master_Node": master_str, "sensor_val": value_str, "Count": count_str}
                json_data = json.dumps(nodered_data)
                client.publish('sensor_val6',json_data,qos=1)
                #print("Published Sensor6 Data")
        
            #print(ch)
            #print(x1data)
            #print(x2data)
            #print(x3data)
        
        
    if (ct>0):    
        file.flush()
        if ((ct7%4) == 0):
           data_push = mapping_func((avg_val)/4, 1, 1024, 1, 8)
           avg_val = 0
           code_H.pop(0)
           code_H.append(code[data_push-1])
           


def matrix_plot():
    global ct
    global code_H
    global code_L
    global now
    
    t = ct
    
    while True:
        if(ct == t):
            for i in range(0, len(code_H)):
                hc595_shift(code_L[i])
                hc595_shift(code_H[i])
                time.sleep(0.001) 
            else:
                setup()
                t=ct
            


def setAndReturnSwarmID(incomingID):
 
        for i in range(0,SWARMSIZE):
            if (swarmStatus[i][5] == incomingID):
                return i
            else:
                if (swarmStatus[i][5] == 0):  # not in the system, so put it in
        
                    swarmStatus[i][5] = incomingID;
                    print("incomingID %d " % incomingID)
                    print("assigned #%d" % i)
                    return i
        
      
        # if we get here, then we have a new swarm member.   
        # Delete the oldest swarm member and add the new one in 
        # (this will probably be the one that dropped out)
      
        oldTime = time.time();
        oldSwarmID = 0
        for i in range(0,SWARMSIZE):
            if (oldTime > swarmStatus[i][1]):
                ldTime = swarmStatus[i][1]
                oldSwarmID = i

     
     

        # remove the old one and put this one in....
        swarmStatus[oldSwarmID][5] = incomingID;
        # the rest will be filled in by Light Packet Receive
        print("oldSwarmID %i" % oldSwarmID)
     
        return oldSwarmID 

# set up sockets for UDP

s=socket(AF_INET, SOCK_DGRAM)
host = 'localhost';
s.bind(('',MYPORT))

print("--------------")
print("LightSwarm Logger")
print("Version ", VERSIONNUMBER)
print("--------------")

#Button Callback function
def button_released_callback(channel):
    global ct
    global ct1
    global ct2
    global ct3
    global ct4
    global ct5
    global ct6
    global ct7
    global ct8
    global file
    global code_H
    global flag
    
    SendRESET_SWARM_PACKET(s)    
    ct7=0 
    ct8=[]
    flag=True
    if (ct>1):
        file.write("Node1 uptime,"+str(ct1)+"\n"+"Node2 uptime,"+str(ct2)+"\n"+"Node3 uptime,"+str(ct3)+"\n"+"Node4 uptime,"+str(ct4)+"\n"+"Node5 uptime,"+str(ct5)+"\n"+"Node6 uptime,"+str(ct6)+"\n")       
        ct1=0
        ct2=0
        ct3=0
        ct4=0
        ct5=0
        ct6=0
        code_H = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        file.close()
    ct+=1
    now = datetime.now()
    name = "/home/pi/data_log" + str(now) + ".csv"
    print("File created:" + str(name))
    file = open(name, "a")
    file.write("Time,Swarm ID,Master Status ,Light Reading\n")
    
    master_str1 = str(0)
    value_str = str(0)
    count_str = str(0)
    nodered_data = {"Master_Node": master_str1, "sensor_val": value_str, "Count": count_str}
    json_data = json.dumps(nodered_data)
    client.publish('sensor_val1',json_data,qos=1)
    print("Published Sensor1 Data")
    
    master_str2 = str(1)
    #value_str = str(0)
    #count_str = str(0)
    nodered_data = {"Master_Node": master_str2, "sensor_val": value_str, "Count": count_str}
    json_data = json.dumps(nodered_data)
    client.publish('sensor_val2',json_data,qos=1)
    print("Published Sensor2 Data")
    
    master_str3 = str(2)
    #value_str = str(0)
    #count_str = str(0)
    nodered_data = {"Master_Node": master_str3, "sensor_val": value_str, "Count": count_str}
    json_data = json.dumps(nodered_data)
    client.publish('sensor_val3',json_data,qos=1)
    print("Published Sensor3 Data")
    
    master_str4 = str(3)
    #value_str = str(0)
    #count_str = str(0)
    nodered_data = {"Master_Node": master_str4, "sensor_val": value_str, "Count": count_str}
    json_data = json.dumps(nodered_data)
    client.publish('sensor_val4',json_data,qos=1)
    print("Published Sensor4 Data")
    
    master_str5 = str(4)
    #value_str = str(0)
    #count_str = str(0)
    nodered_data = {"Master_Node": master_str5, "sensor_val": value_str, "Count": count_str}
    json_data = json.dumps(nodered_data)
    client.publish('sensor_val5',json_data,qos=1)
    print("Published Sensor5 Data")
    
    master_str6 = str(5)
    #value_str = str(0)
    #count_str = str(0)
    nodered_data = {"Master_Node": master_str6, "sensor_val": value_str, "Count": count_str}
    json_data = json.dumps(nodered_data)
    client.publish('sensor_val6',json_data,qos=1)
    print("Published Sensor6 Data")
    
    

    

    #if os.stat("/home/pi/data_log.csv").st_size == 0:
        #file.write("Time,Swarm ID,Master Status ,Light Reading\n")    
        
    GPIO.output(LED_Y, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(LED_Y, GPIO.LOW)

#4 Digit 7-Segment Display
        
def clearDisplay():
    for i in range(8):
        GPIO.output(SDI_1, 1)
        GPIO.output(SRCLK_1, GPIO.HIGH)
        GPIO.output(SRCLK_1, GPIO.LOW)
    GPIO.output(RCLK_1, GPIO.HIGH)
    GPIO.output(RCLK_1, GPIO.LOW)

def hc595_shift_1(data):
    for i in range(8):
        GPIO.output(SDI_1, 0x80 & (data << i))
        GPIO.output(SRCLK_1, GPIO.HIGH)
        GPIO.output(SRCLK_1, GPIO.LOW)
    GPIO.output(RCLK_1, GPIO.HIGH)
    GPIO.output(RCLK_1, GPIO.LOW)

def pickDigit(digit):
    for i in placePin:
        GPIO.output(i,GPIO.LOW)
    GPIO.output(placePin[digit], GPIO.HIGH)


def loop():
    global varid_1
    while True:
        #time.sleep(1)
        #print(varid_1)
        data = varid_1

        
        clearDisplay()
        pickDigit(0)
        hc595_shift_1(number[data % 10])

        clearDisplay()
        pickDigit(1)
        hc595_shift_1(number[data % 100//10])

        clearDisplay()
        pickDigit(2)
        hc595_shift_1(number[data % 1000//100])

        clearDisplay()
        pickDigit(3)
        hc595_shift_1(number[data % 10000//1000])
        



#Pin setup
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering

GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 26 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(LED_Y, GPIO.OUT)

GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_released_callback, bouncetime=300) #Interrupt on button
setup()

client = paho.Client()
#client.on_publish = on_publish
client.connect('broker.hivemq.com',1883)
client.loop_start()
# first send out DEFINE_SERVER_LOGGER_PACKET to tell swarm where to send logging information 

SendDEFINE_SERVER_LOGGER_PACKET(s)
time.sleep(3)
SendDEFINE_SERVER_LOGGER_PACKET(s)

# swarmStatus
swarmStatus = [[0 for x  in range(6)] for x in range(SWARMSIZE)]

# 6 items per swarm item

# 0 - NP  Not present, P = present, TO = time out
# 1 - timestamp of last LIGHT_UPDATE_PACKET received
# 2 - Master or slave status   M S
# 3 - Current Test Item - 0 - CC 1 - Lux 2 - Red 3 - Green  4 - Blue
# 4 - Current Test Direction  0 >=   1 <=
# 5 - IP Address of Swarm


for i in range(0,SWARMSIZE):
    swarmStatus[i][0] = "NP"
    swarmStatus[i][5] = 0


#300 seconds round
seconds_300_round = time.time() + 300.0

#120 seconds round
seconds_120_round = time.time() + 120.0

t1 = Thread(target = matrix_plot)
t6 = Thread(target=loop)
t6.start()

while(1) :
         
    # receive datclient (data, addr)
    d = s.recvfrom(1024)
    
    message = d[0]
    addr = d[1]
    #print("ct"+str(ct))
    if flag:
        
        if(ct==1):
            t1.start()
        flag = False
        

    if (len(message) == 14):


        if (message[1] == LIGHT_UPDATE_PACKET):
            incomingSwarmID = setAndReturnSwarmID((message[2]))
            swarmStatus[incomingSwarmID][0] = "P"
            swarmStatus[incomingSwarmID][1] = time.time()  
            #print("in LIGHT_UPDATE_PACKET")

        if ((message[1]) == RESET_SWARM_PACKET):
            print("Swarm RESET_SWARM_PACKET Received")
            print("received from addr:",addr)

        if ((message[1]) == RESET_ME_PACKET):
            print("Swarm RESET_ME_PACKET Received")
            print("received from addr:",addr)

        if ((message[1]) == DEFINE_SERVER_LOGGER_PACKET):
            print("Swarm DEFINE_SERVER_LOGGER_PACKET Received")
            print("received from addr:",addr)

        if ((message[1]) == MASTER_CHANGE_PACKET):
            print("Swarm MASTER_CHANGE_PACKET Received")
            print("received from addr:",addr)

        #for i in range(0,14):  
        #    print("ls["+str(i)+"]="+format((message[i]), "#04x"))

    else:
        if ((message[1]) == LOG_TO_SERVER_PACKET):
            print("Swarm LOG_TO_SERVER_PACKET Received")
            #print(addr)
            Ipsplit = str(addr)
            x = Ipsplit.split(",")
            y = x[0].split("(")
            currentMasterIP = y[1]
            IP_w = y[1]
            value = currentMasterIP.split('.')
            val = value[3].replace("'", "-").split("-")
            varid_1 = int(val[0])
            # process the Log Packet
            logString = parseLogPacket(message)
            buildLog(logString, SWARMSIZE , setAndReturnSwarmID((message[2])))
                                
        else:
            print("error message length = ",len(message))
         

    if (time.time() >  seconds_300_round):
        # do our 2 minute round
        print(">>>>doing 300 second task")
        SendDEFINE_SERVER_LOGGER_PACKET(s)
        seconds_300_round = time.time() + 300.0

   
    #print swarmStatus 


