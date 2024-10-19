#!/bin/bash

set -e

sudo apt-get clean

sudo apt-get update

sudo apt-get upgrade -y

sudo apt-get install -y --fix-missing unzip mysql-server python3 python3-pip python3-venv yq

sudo systemctl start mysql

sudo systemctl enable mysql
