#!/bin/bash

# copy file into /usr directory
cp bluetooth /usr/bin/

# copy service file into /etc/systemd/system/
cp bluetooth.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable bluetooth && systemctl start bluetooth
