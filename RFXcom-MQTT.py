#!/usr/bin/python

from RFXtrx.pyserial import PySerialTransport
from RFXtrx import LightingDevice
import mosquitto,sys
import json
import thread
import time
from RFXtrx.lowlevel import Lighting2 

# Change when needed
PORT = '/dev/ttyUSB0'
LISTEN = True
PREFIX = "rfxcom"
MQTT_HOST = "192.168.0.37"

# Start the logging part of the script
# See: http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
# for source of this part of the code
import logging
import logging.handlers
import argparse
import sys

# Defaults
LOG_FILENAME = "/tmp/rfxcom.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="RFXcom-MQTT bridge service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-s", "--server", help="IP for MQTT server (default '" + MQTT_HOST + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log
if args.server:
	MQTT_HOST = args.server

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

i = 0

# Finished with the logging part
# Continue with the regular script

def on_connect(mosq, rc,a):
    mosq.subscribe(PREFIX+"/#", 0)

def on_message(a,mosq, msg):
    global transport
    try:
   
    	print("RECIEVED MQTT MESSAGE: "+msg.topic + " " + str(msg.payload))
    	topics = msg.topic.split("/")
    	name = topics[-2]
    	if topics[-1] == "set":
	    value = msg.payload.upper()
	    if value == "ON":
		value = 100
	    elif value == "OFF":
                value = 0
    	    value = int(value)
    	    #print "Set command"

    	    #Implemented support for Lightening2 only
	    if topics[-4] == "17":
		print "Seting Lighting2 level" 
		print topics
		print value
		pkt = Lighting2()
		#pkt.parse_id(topics[-3],topics[-2])
		code = topics[-2].split(":")
		pkt.id_combined = int(code[0],16)
		pkt.unitcode = int(code[1])
		pkt.subtype = int(topics[-3])
		pkt.packettype = int(topics[-4])
		device = LightingDevice(pkt)
		if value == 0:
		    device.send_off(transport)
		elif value == 100:
		    device.send_on(transport)
		else:
		    device.send_dim(transport,value)
    except:
        print "Error when parsing incomming message."
    
    return 
    
def ControlLoop():
    # schedule the client loop to handle messages, etc.
    print "Starting MQTT listener"
    client.loop_forever()
    print "Closing connection to MQTT"
    time.sleep(1)

transport = PySerialTransport(PORT, debug=True)
#transport.reset()
client = mosquitto.Mosquitto("RFXcom-client")
client.username_pw_set("","")
client.will_set(topic = "system/" + PREFIX, payload="Offline", qos=1, retain=True)

#Connect and notify others of our presence. 
client.connect(MQTT_HOST, keepalive=10)
client.publish("system/" + PREFIX, "Online",1,True)
client.on_connect = on_connect
client.on_message = on_message

#Start tread...
#thread.start_new_thread(ControlLoop,())
client.loop_start()

while True:
    event = transport.receive_blocking()

    if event == None:
	continue
    
    for value in event.values:
   
        topic = PREFIX +"/"+ str(event.device.packettype) + "/" + str(event.device.subtype) + "/" + str(event.device.id_string).replace(":","")+"/"+str(value).replace(" ","_")

	print topic + " " + str(event.values[value])

	#print "DEBUG"
	#print event.device.id_combined
	#print event.device.unitcode    

        client.publish(topic , event.values[value], 1)
    
    	print event 
    
    
client.disconnect() 


