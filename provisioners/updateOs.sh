#!/bin/bash

set -e

sudo apt-get clean

sudo apt-get update

sudo apt-get upgrade -y

sudo apt-get install -y --fix-missing unzip python3 python3-pip python3-venv yq