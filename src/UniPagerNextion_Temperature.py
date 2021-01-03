#!/usr/bin/env python3

# Authors: Ralf Wilke and Moritz Holtz
# License: GNU General Public license Version 3

# Function: Connect to UniPager via Websocket and send UART commands to a
# Nextion display. Also receive touch events from Nextion Display and send
# them to the UniPager
# https://www.afu.rwth-aachen.de/unipager
# https://github.com/rwth-afu/UniPager

# Last change: 20.02.2018
# Last improvment: Implement StatusUpdate and RegEx for log line

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
import colorsys
import re
import netifaces
import shutil

DEBUG = False
mutex = threading.Lock()


def RGBTo565(Red, Green, Blue):
  val = math.floor(Red/8)*2048 + math.floor(Green/4)*32 + math.floor(Blue/8)
  return val

def debug(string):
  if DEBUG:
    print(string)

def Nextion_Write(NextComm):
    debug(NextComm)
    # For Hex Debugging of Data set to Display
    #debug(':'.join(hex(ord(x))[2:] for x in NextComm))
    mutex.acquire()
    serial_port.write(NextComm.encode("iso_8859_1"))
    serial_port.write(bytearray([255, 255, 255]))
    serial_port.flush()
    mutex.release()

def read_from_port(ser):
  global connected
  while not connected:
    connected = True
    count=0
    while True:
      data_str=ser.readline().rstrip()
      handle_data(data_str)

def handle_queue(queue_length):
  Nextion_Write('Status.NQueue.val=' + str(queue_length))

  # Update Backgroundcolor
  #  0 - 30 : Green, ColorCode 2016
  # 31 - 60 : Yellow, ColorCode 65504
  #    > 60 : Red, ColorCode 63488
  # HSV Colorspace: H is Hue = Color. Red is 0, Green is 0.3
  # Map 0 - 60 to 0 - 0.3
  hue = queue_length / 180
#  hue = 30 / 180

  if (hue > 0.3):
    hue = 0.3
  if (hue < 0.0):
    hue = 0.0
  # Invert value from 0 - 0.3, so 0 is green and 0.3 is red
  hue = 0.3 - hue
  rgbval = colorsys.hsv_to_rgb(hue, 1, 1)
  NextionColorCode = RGBTo565(255*rgbval[0], 255*rgbval[1], 255*rgbval[2])
  Nextion_Write('Status.NQueue.bco=' + str(NextionColorCode))

def handle_data(data):
  debug("DataHandler\n")
  debug(data)
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
  
  # Update Timeslot with every message
  Nextion_Write('Status.ActiveSlot.val=' + str(status['timeslot']))
  
  # Update Queue lenght with every message
  handle_queue(status['queue'])

  # Update enabled and disabled timeslot display
  for mytimeslot in range(0, 15+1):
    if (status['timeslots'][mytimeslot]):
      Nextion_Write('Status.Active' + str(mytimeslot) + '.val=1')
    else:
      Nextion_Write('Status.Active' + str(mytimeslot) + '.val=0')


def handle_statusupdate(statusupdate):
  if statusupdate[0] == 'connected':
    if statusupdate[1]:
      Nextion_Write("Status.pConnected.pic=1")
    else:
      Nextion_Write("Status.pConnected.pic=2")
  elif statusupdate[0] == 'transmitting':
    if statusupdate[1]:
      Nextion_Write("Status.pOnAir.pic=3")
    else:
      Nextion_Write("Status.pOnAir.pic=4")
  elif statusupdate[0] == 'queue':
    # Update queue
    handle_queue(statusupdate[1])
  elif statusupdate[0] == 'timeslot':
    # Update Timeslot
    Nextion_Write('Status.ActiveSlot.val=' + str(statusupdate[1]))
  elif statusupdate[0] == 'timeslots':
  # Update enabled and disabled timeslot display
    for mytimeslot in range(0, 15+1):
      if (statusupdate[1][mytimeslot]):
        Nextion_Write('Status.Active' + str(mytimeslot) + '.val=1')
      else:
        Nextion_Write('Status.Active' + str(mytimeslot) + '.val=0')
  elif statusupdate[0] == 'master':
    if statusupdate[1] != None:
      Nextion_Write('Status.TMaster.txt="' + statusupdate[1] + '"')
    else:
      Nextion_Write('Status.TMaster.txt=""')

def handle_version(version):
  debug('Status.tVersionUniP.txt=' + version)
  Nextion_Write('Status.tVersionUniP.txt="' + str(version) + '"')


def handle_config_master(config_master):
  debug('Handle Master Config')
  Nextion_Write('Status.TMaster.txt="' + config_master['server'] + '"')
  Nextion_Write('Status.NPort.val=' + str(config_master['port']))
  Nextion_Write('Status.TCallsign.txt="' + config_master['call'] + '"')

  Nextion_Write('SetupDAPNET.TMaster.txt="' + config_master['server'] + '"')
  Nextion_Write('SetupDAPNET.NPort.val=' + str(config_master['port']))
  Nextion_Write('SetupDAPNET.TCallsign.txt="' + config_master['call'] + '"')
  Nextion_Write('SetupDAPNET.TAuthKey.txt="' + config_master['auth'] + '"')


def handle_config_transmitter(config_transmitter):
  debug('Handle Transmitter Config')

  debug(config_transmitter)

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
  debug('Handle Raspager Config')

  debug(config_raspager)

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
  debug('Handle PTT Config')

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
  debug("Hier ist ein Loginhalt angekommen")
  debug(log[1])

# Example:
# {"Log":[3,"Received Message { id: 135, mtype: AlphaNum, speed: Baud(1200), addr: 165856, func: Func3, data: \"XTIME=0921200218XTIME=0921200218\" }"]}
# Regex: '.*data: (.*) }.*'
  dataexpression = '.*data: (.*) \}.*'
  m = re.search(dataexpression, log[1])
  if m:
    log_data = m.group(1)
    log_data_stripped = log_data.strip('"')
    log_data_stripped_cropped = log_data_stripped[:96]
    debug (log_data_stripped_cropped)
    Nextion_Write('Status.LogLine1.txt="' + log_data_stripped_cropped + '"')

def get_temperature(OW_SENSOR_PATH):
  """ get the temperature from the OW sensor """
  with open(OW_SENSOR_PATH, 'r') as f:
    lines = f.readlines()
    retval = lines[0].split(' ')
    retval = int(retval[1], 16) << 8 | int(retval[0], 16)
    retval /= 16.
    return retval
  raise Exception("Could not open OW sensor file")

def temperature_display():
  while True:
    temp1 = get_temperature('/sys/bus/w1/devices/' + temp1id + '/w1_slave')
    temp2 = get_temperature('/sys/bus/w1/devices/' + temp2id + '/w1_slave')
    Nextion_Write('Status.Temp1Val.txt="' + "{:.1f}".format(temp1) + '°C"')
    Nextion_Write('Status.Temp2Val.txt="' + "{:.1f}".format(temp2) + '°C"')
    time.sleep(5)

def setTempDisplayVisibilityandDescription(visibility):
  if visibility:
    Nextion_Write('Status.Temp1Txt.txt="' + temp1desc + '"')
    Nextion_Write('Status.Temp2Txt.txt="' + temp2desc + '"')
    Nextion_Write('vis Temp1Txt,1')
    Nextion_Write('vis Temp1Val,1')
    Nextion_Write('vis Temp2Txt,1')
    Nextion_Write('vis Temp2Val,1')
    Nextion_Write('Status.TempEnabled.val=1')
  else:
    Nextion_Write('vis Temp1Txt,0')
    Nextion_Write('vis Temp1Val,0')
    Nextion_Write('vis Temp2Txt,0')
    Nextion_Write('vis Temp2Val,0')
    Nextion_Write('Status.TempEnabled.val=0')

def statusdisplay():
  while True:
    ifcounter = 0
    # Send IP config to Display
    for iface in netifaces.interfaces():
      if iface == 'lo':
        continue
      ifcounter = ifcounter + 1
      netifaces.ifaddresses(iface)
      ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
      debug(iface + ':' + ip)
      Nextion_Write('vis Iface' + str(ifcounter) + ',1')
      Nextion_Write('vis IP' + str(ifcounter) + ',1')
      Nextion_Write('OSStatus.IP' + str(ifcounter) + '.txt="' + ip + '"')
      Nextion_Write('OSStatus.Iface' + str(ifcounter) + '.txt="' + iface + '"')
      Nextion_Write('OSStatus.If' + str(ifcounter) + 'enabled.val=1')

    # Disable visibility for non existent interfaces, max 3
    for i in range(ifcounter,3):
      Nextion_Write('vis Iface' + str(i+1) + ',0')
      Nextion_Write('vis IP' + str(i+1 ) + ',0')
      Nextion_Write('OSStatus.If' + str(i+1) + 'enabled.val=0')

    # Send Disk usage to Display
    total, used, free = shutil.disk_usage("/")
    Nextion_Write('OSStatus.DiskSpace.txt="' +
                  'Total: ' + "{:.1f}".format(total // (2**30)) + ' GiB  ' +
                  'Used: '  + "{:.1f}".format(used // (2 ** 30)) + ' GiB  ' +
                  'Free: '  + "{:.1f}".format(free // (2 ** 30)) + ' GiB' +
                  '"')
    Nextion_Write('OSStatus.DiskSpaceBar.val=' + str(round(used/total*100)))
    time.sleep(10)

def on_message(ws, message):

  if message == "Restart":
    return

  try:
    parsed_json = json.loads(message)
  except ValueError as e:
    debug("JSON parse error")
    return

  debug(parsed_json)

  try:
    status = parsed_json['Status']
    handle_status(status)
  except KeyError:
    pass


  try:
    statusupdate = parsed_json['StatusUpdate']
    handle_statusupdate(statusupdate)
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

# since now, no C9000 has ever had a Nextion display, so here just a placeholder
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
  ws.send("\"GetStatus\"")


parser = argparse.ArgumentParser(description='Nextion Display Control')
parser.add_argument('--hostname', default='localhost',
                    help='The host running UniPager, default localhost')
parser.add_argument('--port', default='8055',
                    help='The port UniPager is listening, default 8055')
parser.add_argument('--serialport', dest='serialport', default='/dev/ttyUSB0', type=str,
                    help='Serial Port the Nextion Display is connected to, default /dev/ttyUSB0')
parser.add_argument('--serialspeed', dest='serialspeed', default='115200',
                    help='Serial Port Speed to the Nextion Display, default 115200 Baud')
parser.add_argument('--minbacklight', dest='minbacklight', default='10',
                    help='Minimum Percentage of backlight')
parser.add_argument('--maxbacklight', dest='maxbacklight', default='100',
                    help='Maximum Percentage of backlight')
parser.add_argument('--tempdisplay', dest='tempdisplay', default=False,
                    help='Enable temperature Display', action='store_true')
parser.add_argument('--Temp1ID', dest='temp1id', default='',
                    help='Complete ID of 1Wire bus sensor ID in /sys/bus/w1/devices for Temp Sensor 1')
parser.add_argument('--Temp1Desc', dest='temp1desc', default='',
                    help='Description to display for sensor Temp 1 on display, multiline with \n')
parser.add_argument('--Temp2ID', dest='temp2id', default='',
                    help='Complete ID of 1Wire bus sensor ID in /sys/bus/w1/devices for Temp Sensor 2')
parser.add_argument('--Temp2Desc', dest='temp2desc', default='',
                    help='Description to display for sensor Temp 2 on display, multiline with \n')
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
minbacklight = args.minbacklight
maxbacklight = args.maxbacklight
tempdisplay = args.tempdisplay
temp1id = args.temp1id
temp1desc = args.temp1desc
temp2id = args.temp2id
temp2desc = args.temp2desc

if not (config is None):
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

if int(minbacklight) < 0 or int(minbacklight) > 100:
	print('Minimum Backlight setting is NOT between 0 and 100');
if int(maxbacklight) < 0 or int(maxbacklight) > 100:
        print('Maximum Backlight setting is NOT between 0 and 100');
if int(maxbacklight) < int(minbacklight):
	print('Maximum Backlight setting is lower than minimum Backlight setting. This does not make sense!')

connected  = False
serial_port = serial.Serial(NextionPort, NextionBaud, timeout=None)

setTempDisplayVisibilityandDescription(tempdisplay)


threadreadport = threading.Thread(target=read_from_port, args=(serial_port,)).start()
threadtemp = threading.Thread(target=temperature_display).start()
threatstatus = threading.Thread(target=statusdisplay).start()

# Set minimum and maximum backlight
Nextion_Write('Status.DimMinimum.val=' + str(minbacklight))
Nextion_Write('Status.DimMaximum.val=' + str(maxbacklight))

# Set dim value of display to minimum value
Nextion_Write('dim=Status.DimMaximum.val')
Nextion_Write('Status.DimTimeout.en=1')

websocket.enableTrace(False)
ws = websocket.WebSocketApp(WebSocketURL,
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
ws.on_open = on_open

ws.run_forever()

