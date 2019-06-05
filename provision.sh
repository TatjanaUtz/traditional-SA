#!/bin/bash

# Add PPA
sudo add-apt-repository ppa:jonathonf/python-3.6

# Update all installed packages
sudo apt-get update -qq

# Install python 3.6
sudo apt-get -y install python3.6

# Install and upgrade pip
sudo apt-get -y install python3-pip
python3.6 -m pip install --upgrade pip

# Install PyQt4
sudo apt-get -y install python3-pyqt4

# Install requirements
pip install --user numpy==1.16.2
pip install --user simpy==2.3.1
pip install --user simso==0.8.5
pip install --user simsogui==0.8.1
