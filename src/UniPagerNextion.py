#!/usr/bin/env python3

import websocket
import json
import time
import serial
import time
import math
import sys
import threading
import io
import struct
import argparse
import signal

DEBUG = False

def Nextion_Write(NextComm):
#    print(NextComm)
    serial_port.write(NextComm.encode())
    serial_port.write((chr(255)).encode())
    serial_port.write((chr(255)).encode())
    serial_port.write((chr(255)).encode())
    serial_port.flush()

def read_from_port(ser):
  global connected
  while not connected:
    connected = True
    count=0
    while True:
      data_str=ser.readline().rstrip()
      handle_data(data_str)

def handle_data(data):
  print("DataHandler\n")
#  print(data)
#  print " ".join(hex(ord(n)) for n in data)
  data = data.replace(b'\x1d',b'\x0a')
  try:
    start = data.index(b'\x02')
  except ValueError:
    start = -1
  if (start != -1):
    start = start + 1
    data = data[start:]
    data = data.decode(encoding='ASCII')
    ws.send(data)

def handle_status(status):
  if (status['connected']):
    Nextion_Write("Status.pConnected.pic=1")
  else:
    Nextion_Write("Status.pConnected.pic=2")

  if (status['transmitting']):
    Nextion_Write("Status.pOnAir.pic=3")
  else:
    Nextion_Write("Status.pOnAir.pic=4")

  Nextion_Write('Status.ActiveSlot.val=' + str(status['timeslot']))

  for mytimeslot in range(0, 15+1):
    if (status['timeslots'][mytimeslot]):
      Nextion_Write('Status.Active' + str(mytimeslot) + '.val=1')
    else:
      Nextion_Write('Status.Active' + str(mytimeslot) + '.val=0')


def handle_version(version):
  print('Status.tVersionUniP.txt=' + version)
  Nextion_Write('Status.tVersionUniP.txt="' + str(version) + '"')

def handle_config_master(config_master):

  print('Handle Master Config')
  Nextion_Write('Status.TMaster.txt="' + config_master['server'] + '"')
  Nextion_Write('Status.NPort.val=' + str(config_master['port']))
  Nextion_Write('Status.TCallsign.txt="' + config_master['call'] + '"')

  Nextion_Write('SetupDAPNET.TMaster.txt="' + config_master['server'] + '"')
  Nextion_Write('SetupDAPNET.NPort.val=' + str(config_master['port']))
  Nextion_Write('SetupDAPNET.TCallsign.txt="' + config_master['call'] + '"')
  Nextion_Write('SetupDAPNET.TAuthKey.txt="' + config_master['auth'] + '"')



def handle_config_transmitter(config_transmitter):
  print('Handle Transmitter Config')

  print(config_transmitter)

  if (config_transmitter=='Dummy'):
    Nextion_Write('Status.PagerType.val=0')
  elif (config_transmitter=='Audio'):
    Nextion_Write('Status.PagerType.val=1')
  elif (config_transmitter=='Raspager'):
    Nextion_Write('Status.PagerType.val=2')
  elif (config_transmitter=='C9000'):
    Nextion_Write('Status.PagerType.val=3')
  elif (config_transmitter=='RFM69'):
    Nextion_Write('Status.PagerType.val=4')

  Nextion_Write('Status.TypeText.txt="' + config_transmitter + '"')


def handle_config_raspager(config_raspager):
  print('Handle Raspager Config')

  print(config_raspager)

  Nextion_Write('ConfigRasp.nFrequency.val=' + str(config_raspager['freq']))
  Nextion_Write('ConfigRasp.nFrequencyCorr.val=' + str(config_raspager['freq_corr']))
  Nextion_Write('ConfigRasp.nPAOutput.val=' + str(config_raspager['pa_output_level']))


def handle_config_rfm69(config_rfm69):
  Nextion_Write('ConfigRFM69.tSerialPort.txt="' + config_rfm69['port'] + '"')


def handle_config_audio(config_audio):
  Nextion_Write('ConfigAudio.tALSADevice.txt="' + config_audio['device'] + '"')

  Nextion_Write('ConfigAudio.AudioSlider.val=' + str(config_audio['level']))
  Nextion_Write('ConfigAudio.AudioLevel.val=' + str(config_audio['level']))
  Nextion_Write('ConfigAudio.NAudioLevel.val=' + str(config_audio['level']))

  Nextion_Write('ConfigAudio.TxDelay.val=' + str(config_audio['tx_delay']))
  Nextion_Write('ConfigAudio.NTxDelay.val=' + str(config_audio['tx_delay']))

  if(config_audio['inverted']):
    Nextion_Write('ConfigAudio.cAudioInverted.val=1')
  else:
    Nextion_Write('ConfigAudio.cAudioInverted.val=0')

def handle_config_ptt(config_ptt):
  print('Handle PTT Config')

  Nextion_Write('ConfigAudioPTT.nGPIO.val=' + str(config_ptt['gpio_pin']))

  if(config_ptt['inverted']):
    Nextion_Write('ConfigAudioPTT.cPTTInverted.val=1')
  else:
    Nextion_Write('ConfigAudioPTT.cPTTInverted.val=0')

  Nextion_Write('ConfigAudioPTT.tSerialPort.txt="' + config_ptt['serial_port'] + '"')

  if (config_ptt['method']=='Gpio'):
    Nextion_Write('ConfigAudioPTT.AudioPTTType.val=0')
    Nextion_Write('ConfigAudioPTT.RadioGPIO.val=1')
    Nextion_Write('ConfigAudioPTT.RadioDTR.val=0')
    Nextion_Write('ConfigAudioPTT.RadioRTS.val=0')

  elif (config_ptt['method']=='SerialDtr'):
    Nextion_Write('ConfigAudioPTT.AudioPTTType.val=1')
    Nextion_Write('ConfigAudioPTT.RadioGPIO.val=0')
    Nextion_Write('ConfigAudioPTT.RadioDTR.val=1')
    Nextion_Write('ConfigAudioPTT.RadioRTS.val=0')

  elif (config_ptt['method']=='SerialDrts'):
    Nextion_Write('ConfigAudioPTT.AudioPTTType.val=2')
    Nextion_Write('ConfigAudioPTT.RadioGPIO.val=0')
    Nextion_Write('ConfigAudioPTT.RadioDTR.val=0')
    Nextion_Write('ConfigAudioPTT.RadioRTS.val=1')

def handle_log(log):
  print("Hier ist ein Loginhalt angekommen")
  print(log)
  message=log[1]

  print(message['Received Message']['data']);

def on_message(ws, message):

  parsed_json = json.loads(message)
  print(parsed_json)

  try:
    status = parsed_json['Status']
    handle_status(status)
  except KeyError:
    pass


  try:
    version = parsed_json['Version']
    handle_version(version)
  except KeyError:
    pass


  try:
    config_master = parsed_json['Config']['master']
    handle_config_master(config_master)
  except KeyError:
    pass


  try:
    config_transmitter = parsed_json['Config']['transmitter']
    handle_config_transmitter(config_transmitter)
  except KeyError:
    pass


  try:
    config_raspager = parsed_json['Config']['raspager']
    handle_config_raspager(config_raspager)
  except KeyError:
    pass

  try:
    config_rfm69 = parsed_json['Config']['rfm69']
    handle_config_rfm69(config_rfm69)
  except KeyError:
    pass

#  try:
#    config_c9000 = parsed_json['Config']['c9000']
#    handle_config_c9000(config_c9000)
#  except KeyError:
#    pass


  try:
    config_audio = parsed_json['Config']['audio']
    handle_config_audio(config_audio)
  except KeyError:
    pass

  try:
    config_ptt = parsed_json['Config']['ptt']
    handle_config_ptt(config_ptt)
  except KeyError:
    pass

  try:
    log = parsed_json['Log']
    handle_log(log)
  except KeyError:
    pass


def on_error(ws, error):
  print(error)

def on_close(ws):
  print("### closed ###")

def on_open(ws):
  print("### Connected ###")
  ws.send("\"GetVersion\"")
  ws.send("\"GetConfig\"")


parser = argparse.ArgumentParser(description='Nextion Display Control')
parser.add_argument('--hostname', default='localhost',
                    help='The host running UniPager, default localhost')
parser.add_argument('--port', default='8055',
                    help='The port UniPager is listening, default 8055')
parser.add_argument('--serialport', dest='serialport', default='/dev/ttyUSB0', type=str,
                    help='Serial Port the Nextion Display is connected to, default /dev/ttyUSB0')
parser.add_argument('--serialspeed', dest='serialspeed', default='115200',
                    help='Serial Port Speed to the Nextion Display, default 115200 Baud')
parser.add_argument('--config', dest='config', default=None, type=str,
                    help='Config file')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Enable debug')

args = parser.parse_args()

DEBUG |= args.debug
if DEBUG: print("Debug enabled")
config = args.config
hostname = args.hostname
port = args.port
serialport = args.serialport
serialspeed = args.serialspeed

if not config is None:
	try:
		with open(config) as f:
			exec(f.read())
	except FileNotFoundError:
		print("Configfile %s not found" %config)
		sys.exit(1)
	except SyntaxError:
		print("Syntax error in configfile %s" %config)
		sys.exit(1)

WebSocketURL = "ws://%s:%s/" %(hostname, port)

NextionPort = serialport
NextionBaud = serialspeed


connected  = False
serial_port = serial.Serial(NextionPort, NextionBaud, timeout=None)


thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()


websocket.enableTrace(False)
ws = websocket.WebSocketApp(WebSocketURL,
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
ws.on_open = on_open

ws.run_forever()

