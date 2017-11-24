#!/usr/bin/python
# This file is the mqtt-manager web entry point
# the purpose of functions here is to verify input and pass
# the requests to the controller class
# also, format responses to HTTP
import json
import requests

from flask import Flask
from flask import request
from flask import make_response as fmake_response

import conf
import DeviceController as dc

app = Flask(__name__)
app.url_map.strict_slashes = False


def make_response(payload, status):
    resp = fmake_response(payload, status)
    resp.headers['content-type'] = 'application/json'
    return resp


def formatResponse(status, message=None):
    payload = None
    if message:
        payload = json.dumps({'message': message, 'status': status})
    elif status >= 200 and status < 300:
        payload = json.dumps({'message': 'ok', 'status': status})
    else:
        payload = json.dumps({'message': 'Request failed', 'status': status})
    return make_response(payload, status)


@app.route('/notifyDeviceChange', methods=['POST'])
def notifyDeviceChange():
    try:
        requestData = json.loads(request.data)
    except ValueError:
        return formatResponse(400, 'malformed JSON')

    if 'action' not in requestData.keys():
        return formatResponse(400, "'Action' not specified ")

    if requestData['action'] in ['create', 'update']:
        try:
            dc.addDeviceACLRequest(requestData)
            return formatResponse(200)
        except dc.RequestError as err:
            return formatResponse(err.errorCode, err.message)

    elif requestData['action'] == 'delete':
        try:
            dc.removeDeviceACLRequest(requestData)
            return formatResponse(200, "Device " + requestData['device']
                                       + " removed from ACL")
        except dc.RequestError as err:
            return formatResponse(err.errorCode, err.message)

    else:
        return formatResponse(400, "'Action' " + requestData['action']
                                   + " not implemented")


# receive a PEM CRL. If its valid, save to file
@app.route('/crlupdate', methods=['POST'])
def updateCRL():
    try:
        requestData = json.loads(request.data)
    except ValueError:
        return formatResponse(400, 'malformed JSON')

    try:
        dc.updateCRL(requestData)
        return formatResponse(200)
    except dc.RequestError as err:
        return formatResponse(err.errorCode, err.message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(conf.APIport), threaded=True)
