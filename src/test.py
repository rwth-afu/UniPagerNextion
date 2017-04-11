import websocket
import json
import time
import serial
import time
import math
import sys
import threading
import io

WebSocketURL = "ws://localhost:8055/"

NextionPort = "/dev/ttyUSB0"
NextionBaud = 115200


connected  = False
serial_port = serial.Serial(NextionPort, NextionBaud, timeout=None)

def handleShutdown():
  print("This was Shutdown")
#  ws.send('"Shutdown"')

def handleRestart():
  print("This was Restart")
  ws.send('"Restart"')

def handleDefaultConfig():
  print("This was DefaultConfig")
#  ws.send('"DefaultConfig"')

def handleSaveConfig(sPayload):
  print("This was SaveConfig")
  PagerType, \
  DAPNET_Callsign,DAPNET_AuthKey,DAPNET_Master,DAPNET_Port, \
  Audio_ALSADevice,Audio_Level,Audio_TxDelay,Audio_Inverted,Audio_PTTType, \
  Audio_GPIO,Audio_SerialPort,Audio_PTTInverted, \
  RaspV1_Frequency,RaspV1_FrequencyCorretion,RaspV1_PAOutput, \
  STM32_SerialPort = sPayload.split(b'\x1d')

  PagerType = PagerType.decode(encoding='ASCII').replace('PagerType','')
  print("PagerType: ",PagerType)

  DAPNET_Callsign = DAPNET_Callsign.decode(encoding='ASCII').replace('DAPNET:Callsign','')
  print("DAPNET_Callsign: ",DAPNET_Callsign)

  DAPNET_AuthKey = DAPNET_AuthKey.decode(encoding='ASCII').replace('DAPNET:AuthKey','')
  print("DAPNET_AuthKey: ",DAPNET_AuthKey)

  DAPNET_Master = DAPNET_Master.decode(encoding='ASCII').replace('DAPNET:Master','')
  print("DAPNET_Master: ",DAPNET_Master)

  DAPNET_Port = DAPNET_Port.decode(encoding='ASCII').replace('DAPNET:Port','')
  print("DAPNET_Port: ",DAPNET_Port)




def handle_data(data):
  print("DataHandler\n")
  print(data)
  Command,Payload=data.split(b'\x03')
  Command=Command.decode(encoding='ASCII')
  print("Command",Command)
  if Command == "Shutdown":
    handleShutdown()

  elif Command == "Restart":
    handleRestart()
  elif Command == "DefaultConfig":
    handleDefaultConfig()
  elif Command == "SaveConfig":
    handleSaveConfig(Payload)
  else:
    print("Error, Datentype nicht bekannt")



def read_from_port(ser):
  global connected
  while not connected:
    connected = True
    count=0
    while True:
      data_str=ser.readline().rstrip()
      handle_data(data_str)

def on_message(ws, message):
    parsed_json = json.loads(message)

#    if Debug:
#       print(parsed_json)
#       print(parsed_json['Config']['master']['call'])
#       print(parsed_json['Config']['master']['server'])
#       Nextion_Write('xstr 0, 200, 100, 30, 1, RED, BLACK, 1, 1, 1, \"China\"')

#    if (parsed_json['Status']['transmitting']):
#          Nextion_Write("p2.pic=5")



def on_error(ws, error):
  print(error)

def on_close(ws):
  print("### closed ###")

def on_open(ws):
  print("### Connected ###")

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()


websocket.enableTrace(False)
ws = websocket.WebSocketApp(WebSocketURL,
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
ws.on_open = on_open

ws.run_forever()

