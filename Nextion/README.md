# Dependencies
sudo apt-get install python-serial

# Usage
For horizontal aligment 90 deg. of the display:
./nextion.py NX4024T032.tft

For horizontal aligment 270 deg. of the display:
./nextion.py NX4024T032_270deg.tft

Edit the line

#PORT = '/dev/ttyAMA0'
PORT = '/dev/ttyUSB0'

according to your needs.