#!/bin/bash

set -e

sudo groupadd csye6225
sudo useradd -r -g csye6225 -s /usr/sbin/nologin csye6225

sudo mkdir -p /opt/webapp
sudo chown -R csye6225:csye6225 /opt/webapp
