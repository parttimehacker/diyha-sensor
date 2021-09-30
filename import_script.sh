#/usr/bin/bash
#
# import required python libraries

echo "Install Mqtt, psutil, pylint and screen"
sudo pip3 install paho-mqtt
sudo pip3 install psutil
sudo pip3 install pylint
sudo apt -y install screen

echo "Adafruit stuff"
sudo pip3 install adafruit-circuitpython-veml7700
sudo pip3 install adafruit-circuitpython-bme680
