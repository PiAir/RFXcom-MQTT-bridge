RFXcom-MQTT-bridge
==================

Directly connect your RFXCOM usb dongle to a MQTT broker. This script will post recived events to the MQTT broker and also let you control lighting2 devices such as NEXA switches and dimmers.  

Requires:

https://github.com/woudt/pyRFXtrx

and 

sudo apt-get install mosquitto-clients python-mosquitto


Update 5-1-2017
==================

* Fixed a couple of problems in the script so it creates MQTT that can be parsed by OpenHab
* Added code so the script can be run as a deamon. Big thanks to http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
You can now use:

sudo ./RFXcom-MQTT-service.sh start - start the service.

sudo ./RFXcom-MQTT-service.sh status - check the service's status.

sudo ./RFXcom-MQTT-service.sh stop - stop the service.

All output is logged to /tmp/rfxcom.log

