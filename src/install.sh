#!/bin/sh -x

cp UniPagerNextion.py /usr/local/bin/unipagernextion.py
cp config.py.example /etc/unipagernextionconfig.py
mkdir -p /usr/local/lib/systemd/system
cp unipagernextion.service /usr/local/lib/systemd/system/unipagernextion.service

systemctl daemon-reload
