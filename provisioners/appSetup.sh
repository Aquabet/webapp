#!/bin/bash

set -e

sudo unzip /tmp/webapp.zip -d /opt/webapp

sudo cp /tmp/webapp.service /etc/systemd/system/webapp.service

sudo systemctl daemon-reload

sudo systemctl enable webapp.service

sudo chown -R csye6225:csye6225 /opt/webapp

sudo -u csye6225 python3 -m venv /opt/webapp/venv

sudo -u csye6225 /opt/webapp/venv/bin/pip install --upgrade pip

sudo -u csye6225 /opt/webapp/venv/bin/pip install -r /opt/webapp/requirements.txt
