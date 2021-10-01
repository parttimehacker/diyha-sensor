# sensor
Do It yourself environment sensors code base. Python3 application running on Raspberry Pi Zero W.

## Description: 
This is my updated **Raspberry Pi** project that implements an multi-environment sensor platform for my "do it yourself home automation" system.  The application requires **Raspbian OS** and is written in **python3**. I usually create a **systemd service** so the application runs at boot.

## Installation: 
Installation is a three step process. First clone the repository, and then install dependent software with the **requiements.txt** file. 

- Step 1 - clone this repository
```
git clone https://github.com/parttimehacker/sensor.git
```
- Step 2 - Install required software - MQTT and RPI.GPIO libraries
```
cd clock
pip install -r requirements.txt
```
- Step 3 - Install required software - MQTT and RPI.GPIO libraries
```
cd pkg_classes
chmod +x ./import_script.sh
./import_script.sh
```
## Usage: 
You need to decide whether you want to manually run the application or have it started as part of the boot process. I recommend making a **Raspbian OS systemd service**, so the application starts when rebooted or controled by **systemctl** commands. The **systemd_script.sh** creates a admin directory in **/usr/local directory**. The application files are then copied to this new directory. The application will also require a log file in **/var/log directory** called admin.log
### Manual or Command Prompt
To manually run the application enter the following command (sudo may be required on your system)
```
sudo python3 sensor.py --mqtt <MQTT_BROKER> --location <ROOM>
```
- <MQTT_BROKER> I use the Open Source Mosquitto broker and bridge 
- Host names or IP address can be used.
- <ROOM> is the location in the house as an MQTT topic syntax
### Raspbian systemd Service
First edit the **clock systemd service** and replace the MQTT broker and room values with their host names or IP addresse. A systemd install script will move files and enable the applicaiton via **systemctl** commands.
- Run the script and provide the application name **admin** to setup systemd (the script uses a file name argument to create the service). 
```
vi sensor.service
./systemd_script.sh clock
```
This script also adds four aliases to the **.bash_aliases** in your home directory for convenience.
```
sudo systemctl start sensor
sudo systemctl stop sensor
sudo systemctl restart sensor
sudo systemctl -l status sensor
```
- You will need to login or reload the **.bashrc** script to enable the alias entries. For example:
```
cd
source .bashrc
```
### MQTT Topics and Messages
The application subscribes to multiple MQTT topics and publishes initialization messages. Three are handled locally and the rest are sent to the web server's API for processing.
- Two topics **diy/system/fire** and **diy/system/panic** are special cases and also email alerts
- The **diy/system/who** sends local server information to the web server's API. 
- The reset of the MQTT messages are translated to HTTP messages to the web server's API for processing.
- System message are initialized at startup and legacy messages are sent to a older running applications.
## Contributing: 
- Adafruit supplies most of my hardware. http://www.adafruit.com
- My "do it yourself home automation" system leverages the work from the Eclipse IOT Paho project. https://www.eclipse.org/paho/
- I use the PyCharm development environment https://www.jetbrains.com/pycharm/
## Credits: 
Developed by parttimehacker.
## License: 
MIT

