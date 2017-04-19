#!/bin/sh -x

rm /usr/local/bin/unipagernextion.py
rm -i /etc/unipagernextionconfig.py
rm /usr/local/lib/systemd/system/unipagernextion.service

systemctl daemon-reload

