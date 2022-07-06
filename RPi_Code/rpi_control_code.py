# import the necessary packages
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
from smbus2 import SMBus
from mlx90614 import MLX90614
import RPi.GPIO as GPIO
from time import sleep
import tkinter as tk
from tkinter import *
import threading
import http.client as hp
import urllib
master=tk.Tk()
master.geometry("300x300")
my_text=Text(master,height=10)
my_text.config(state=NORMAL)
key = "YFBCCM43F0BNF97F"
count=0
#import _thread
#import threading

GPIO.setwarnings(False)
#initialize temperature sensor bus and gpio
bus = SMBus(1)
sensor = MLX90614(bus, address=0x5a)

#Servo motor setup
GPIO.setmode(GPIO.BOARD)
servoPin = 15
GPIO.setup(servoPin, GPIO.OUT)
pwm = GPIO.PWM(servoPin, 50)


GPIO.setmode(GPIO.BOARD)

Motor1A=36
Motor1B=38
Motor1E=40

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)

GPIO.setmode(GPIO.BOARD)
trig=16
echo=18
GPIO.setup(trig,GPIO.OUT)
GPIO.setup(echo,GPIO.IN)


def message(msg):
    my_text.insert("0.0",msg)
    my_text.pack()
    #print("hello")
    master.update_idletasks()
    master.update()
    
def message_temp(temperature):
    my_text.insert("0.0",str(temperature))
    my_text.pack()
    #print("hello")
    master.update_idletasks()
    master.update()
    
def delete():
    my_text.delete("0.0",END)
    msg=""
    master.after(0000,message(msg))
    #print("delete")


def openGate():
	print ("Turning motor on")
	GPIO.output(Motor1A,GPIO.LOW)
	GPIO.output(Motor1B,GPIO.HIGH)
	GPIO.output(Motor1E,GPIO.HIGH)
	
	sleep(7)
	GPIO.output(Motor1A,GPIO.LOW)
	GPIO.output(Motor1B,GPIO.LOW)
	GPIO.output(Motor1E,GPIO.LOW)
    
    
def closeGate():
	print ("Closing door")
	GPIO.output(Motor1A,GPIO.HIGH)
	GPIO.output(Motor1B,GPIO.LOW)
	GPIO.output(Motor1E,GPIO.HIGH)
	
	sleep(2)
	GPIO.output(Motor1A,GPIO.LOW)
	GPIO.output(Motor1B,GPIO.LOW)
	GPIO.output(Motor1E,GPIO.LOW)
    
def sanitize_hand():
    flag1=0
    GPIO.output(trig,True)
    time.sleep(0.00001)
    GPIO.output(trig,False)
    while GPIO.input(echo)==0:
        pulse_start=time.time()
    while GPIO.input(echo)==1:
        pulse_end=time.time()
    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17150
    distance=round(distance+1.15,2)
    if(distance<12 and distance>5):
        print("Distance= ", distance, "cm. Dispensing sanitizer")
        pwm.start(2.5)
        pwm.ChangeDutyCycle(5)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(10)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(12.5)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(10)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(5)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(2.5)
        time.sleep(0.5)
        pwm.stop()
        flag1=1
    else:
        print("Please keep your hand near the sanitizer")
        msg="Please keep your hand near the sanitizer"
        master.after(2000,message(msg))
        master.after(2000,delete())
        master.after(3000,lambda:msg.delete(0,END))
        sleep(1)
    return flag1
        
    
#Apply Algorithm
def applyLogic():
    #pwm.start(0)
    temp = getTempData()
    temp=int(sensor.get_obj_temp())
    params = urllib.parse.urlencode({'field1': temp, 'key':key })
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = hp.HTTPConnection("api.thingspeak.com:80")
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print(temp)
        print(response.status, response.reason)
        data = response.read()
    except:
        print("connection failed")
    task=threading.Thread(target=temp)
    var=tk.StringVar()
    
    master.update()
    #gateOpen = threading.Thread(target=openGate)
    #gateOpen.start()
    if temp >= 37:
        print(temp," High temp")
        msg=" is your temperature. High temperature, Gate closed."
        master.after(2000,message(msg))
        master.after(2000,message_temp(temp))
        master.after(2000,delete())
        master.after(3000,lambda:msg.delete(0,END))
        sleep(1)
    else:
        print(temp," is within acceptable range. Gate opening")
        #count+=1
        msg=" is your temperature. Temperature is within acceptable range. Gate opening"
        master.after(2000,message(msg))
        master.after(2000,message_temp(temp))
        master.after(2000,delete())
        openGate()
        flag=0
        while(flag==0):
            flag=sanitize_hand()
        print("Gate is closing")
        msg="Gate closing"
        master.after(2000,message(msg))
        master.after(2000,delete())
        master.after(3000,lambda:msg.delete(0,END))
        closeGate()
        

def getTempData():
    temp = sensor.get_obj_temp()
    return temp

def closeEverything():
    closeGate()
    
#main function
if __name__=="__main__":
    while(True):
        applyLogic()
    

    
