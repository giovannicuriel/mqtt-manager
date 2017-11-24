# this file contains functions to configure mosquitto ACL
# functions throw a generic RequestError Exception
# caller function can handle it acourding
import json
import requests
import OpenSSL
import os
import signal

import conf
import certUtils


class RequestError(Exception):
    def __init__(self, errorCode, message):
        self.message = message
        self.errorCode = errorCode


def reloadMosquittoConf():
    f = open(conf.mosquittoPIDfile, "r")
    os.kill(int(f.readline()), signal.SIGHUP)
    f.close()


# add or update device
def addDeviceACLRequest(requestData):
    if 'device' not in requestData.keys():
        raise RequestError(400, "missing device name")

    if 'topic' not in requestData.keys():
        raise RequestError(400, "missing device topic")

    deviceName = requestData['device']

    # remove the old device
    if requestData['action'] == 'update':
        if not removeDeviceACL(deviceName):
            raise RequestError(404, "No device with name " + deviceName
                                    + " found in ACL")

    topic = requestData['topic']

    # TODO: check if device aready exist?
    aclFile = open(conf.ACLfilePath, "a")

    # device can write on
    aclFile.write("user " + deviceName)
    aclFile.write("\ntopic write " + topic)
    aclFile.write("\n")

    aclFile.close()
    reloadMosquittoConf()


# remove a device from ACL file
# return True if the device was removed, return false otherwise
def removeDeviceACL(deviceName):
    userfound = False

    try:
        aclFile = open(conf.ACLfilePath, "r")
    except IOError:
        raise RequestError(500, 'an IOError occuried')
    newaclFile = open(conf.ACLfilePath + ".tmp", "w")
    for line in aclFile:
        if deviceName not in line:
            newaclFile.write(line)
        else:
            # skip the line and the next one
            line2 = aclFile.next()
            userfound = True
    aclFile.close()
    newaclFile.close()
    if not userfound:
        os.remove(conf.ACLfilePath + ".tmp")
        return False

    os.remove(conf.ACLfilePath)
    os.rename(conf.ACLfilePath + ".tmp", conf.ACLfilePath)
    return True


def removeDeviceACLRequest(requestData):
    if 'device' not in requestData.keys():
        raise RequestError(400, "missing device name")

    deviceName = requestData['device']
    if removeDeviceACL(deviceName):
        try:
            if 'crl' in requestData.keys():
                certUtils.saveCRL(conf.certsDir + "/ca.crl",
                                  requestData['crl'])
        except OpenSSL.crypto.Error:
            raise RequestError(400, "PEM formated CRL could not be decoded")

        reloadMosquittoConf()
    else:
        raise RequestError(404, "No device with name " + deviceName
                                + " found in ACL")


def updateCRL(requestData):
    if 'crl' not in requestData.keys():
        raise RequestError(400, "missing crl")

    try:
        certUtils.saveCRL(conf.certsDir + conf.CAName + ".crl",
                          requestData['crl'])
        reloadMosquittoConf()
    except OpenSSL.crypto.Error:
        raise RequestError(400, "PEM formated CRL could not be decoded")
