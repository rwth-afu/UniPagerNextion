#!/usr/bin/python

import websocket
import thread
import time
import json
import RPi.GPIO as GPIO
import signal
import sys
import serial
import time
import struct
import logging

# User Configuration

NextionEnabled = True
LEDEnabled = True

GPIO_ConnLED_Pin = 16
GPIO_TXLED_Pin = 18

WebSocketURL = "ws://192.168.20.90:8055/"

NextionPort = "/dev/ttyAMA0"

Debug = False

# End User Configuration

k=struct.pack('B', 0xff)

logging.basicConfig()

def signal_handler(signal, frame):
    if LEDEnabled:    
        GPIO.output(GPIO_ConnLED_Pin, False)
        GPIO.output(GPIO_TXLED_Pin, False)
        #Reset GPIO pins to their default state
        GPIO.cleanup()
    if NextionEnabled:
        Nextion_Write("rest")
    print('Rustpager LED Control shutting down!')
    sys.exit(0)

def Nextion_Write(NextComm):
    ser.write(b''+NextComm)
    ser.write(k)
    ser.write(k)
    ser.write(k)

def on_message(ws, message):
    parsed_json = json.loads(message)

#    if Debug:
#       print(parsed_json)
#       print(parsed_json['Config']['master']['call'])
#       print(parsed_json['Config']['master']['server'])
#       Nextion_Write('xstr 0, 200, 100, 30, 1, RED, BLACK, 1, 1, 1, \"China\"')

    if (parsed_json['Status']['transmitting']):
           if NextionEnabled:
              Nextion_Write("p2.pic=5")
           if LEDEnabled:
              GPIO.output(GPIO_TXLED_Pin, True)
    else:
           if NextionEnabled:
              Nextion_Write("p2.pic=4")
           if LEDEnabled:
              GPIO.output(GPIO_TXLED_Pin, False)

    if (parsed_json['Status']['connected']):
           if NextionEnabled:
              Nextion_Write("p3.pic=3")
           if LEDEnabled:
              GPIO.output(GPIO_ConnLED_Pin, True)
    else:
           if NextionEnabled:
              Nextion_Write("p3.pic=2")
           if LEDEnabled:
              GPIO.output(GPIO_ConnLED_Pin, False)
  

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(*args):
            ws.send("\"GetStatus\"")
            ws.send("\"GetConfig\"")
            ws.send("\"GetVersion\"")
            time.sleep(10)
            print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
   
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
 
    if NextionEnabled:
        ser = serial.Serial(NextionPort)

    if LEDEnabled:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_TXLED_Pin, GPIO.OUT)
        GPIO.setup(GPIO_ConnLED_Pin, GPIO.OUT)

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(WebSocketURL,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()

