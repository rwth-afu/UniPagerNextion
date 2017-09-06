#!/bin/bash 
echo "Must be run as root!"
echo "Installing dependencies..."
apt-get install python3 python3-websocket python3-serial
echo "Installing UniPagerNextion..."
cp UniPagerNextion.py /usr/local/bin/unipagernextion.py
chmod 744 /usr/local/bin/unipagernextion.py
cp unipagernextion.py.example /etc/unipagernextionconfig.py
chmod 744 /etc/unipagernextionconfig.py
mkdir -p /usr/local/lib/systemd/system
cp unipagernextion.service /usr/local/lib/systemd/system/unipagernextion.service
systemctl daemon-reload

echo "Now edit /etc/unipagernextionconfig.py according to your needs."
echo "To start unipagernextion type:"
echo "systemctl start unipagernextion"

echo "To enable unipagernextion at every boot type:"
echo "systemctl enable unipagernextion"

