#!/usr/bin/python
import json, requests
import OpenSSL
import re

from flask import Flask
from flask import request
from flask import make_response as fmake_response

#TODO: move this to a configuration file
defaultHeader = {'content-type':'application/json', 'Accept': 'application/json'}
CAName = "PROTOCOL"

app = Flask(__name__)
# CORS(app)
app.url_map.strict_slashes = False

def make_response(payload, status):
    resp = fmake_response(payload, status)
    resp.headers['content-type'] = 'application/json'
    return resp

def formatResponse(status, message=None):
    payload = None
    if message:
        payload = json.dumps({ 'message': message, 'status': status})
    elif status >= 200 and status < 300:
        payload = json.dumps({ 'message': 'ok', 'status': status})
    else:
        payload = json.dumps({ 'message': 'Request failed', 'status': status})
    return make_response(payload, status)

#update CRL
@app.route('/crl', methods=['GET'])
def createCRL():
    try:
        response = requests.get("http://localhost:5000/ca/" + CAName + "/crl",  headers=defaultHeader)
    except requests.exceptions.ConnectionError:
        return formatResponse(503,"Can't connect to EJBCA REST service.")
    try:
        newCRL = json.loads( response.content )['CRL']
        if processCRL(newCRL):
            return formatResponse(200)
        else:
            return formatResponse(500, "The CRL returned by EJBCA could not be decoded")
    except KeyError:
        return formatResponse(500,"Invalid answer returned from EJBCA.")
    

#receve a PEM CRL. If its valid, save to file
def processCRL(rawCrl):
    crl = "-----BEGIN X509 CRL-----\n" + re.sub("(.{64})", "\\1\n", rawCrl, 0, re.DOTALL)  + "\n-----END X509 CRL-----\n"
    
    try:
        crl_object = OpenSSL.crypto.load_crl(OpenSSL.crypto.FILETYPE_PEM, crl)
    except OpenSSL.crypto.Error:
        return False

    #list the revoked certificate serial numbers
    #for rvk in crl_object.get_revoked():
    #    print "Serial:", rvk.get_serial()

    crlFile = open(CAName + ".crl","w")
    crlFile.write(crl)
    crlFile.close()
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("9010"), threaded=True)
    