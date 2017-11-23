# configuration file
import os

APIport = 9010

EJBCA_API_URL = os.environ.get("MQTTREST_EJBCA_URL", "http://ejbca:5583")

CAName = os.environ.get("MQTTREST_CA_NAME", "IOTmidCA")

keyLength = int(os.environ.get("MQTTREST_KEY_LENGHT", 2048))


ACLfilePath = "/usr/local/src/mosquitto-1.4.13/certs/access.acl"
certsDir = "/usr/local/src/mosquitto-1.4.13/certs/"

mosquittoPIDfile = '/usr/local/src/mosquitto-1.4.13/mosquitto.pid'
