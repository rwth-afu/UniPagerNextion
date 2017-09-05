#!/bin/sh -x

cp UniPagerNextion.py /usr/local/bin/unipagernextion.py
chmod 744 /usr/local/bin/unipagernextion.py
cp unipagernextion.py.example /etc/unipagernextionconfig.py
chmod 744 /etc/unipagernextionconfig.py
mkdir -p /usr/local/lib/systemd/system
cp unipagernextion.service /usr/local/lib/systemd/system/unipagernextion.service

systemctl daemon-reload
