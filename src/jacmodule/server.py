#!/usr/bin/env python

from flask import Flask
from flask import request
import logging
import socket
import sys
import json

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def health_check():
    return 'Hello, World!\n'

@app.route('/query/<key>')
def query(key):
    return "Key pair ({key}, 42)\n".format(key)

@app.route('/insert/<key>/<value>')
def insert(key, value):
    return "Inserted keypair ({key},{value})!\n".format(key,value)

@app.route('/delete/<key>')
def delete(key):
    return 'Deleted key <key>!\n'

@app.route('/overlay')
def overlay():
    return 'Suppose that this is the topology!\n'

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...\n'  

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Please provide available port number")
        exit()
    ip = socket.gethostbyname(socket.gethostname())

    try:
        app.run(host=ip, port=sys.argv[1])
    except socket.error:
        print("Port {} is not available".format(sys.argv[1]))
        exit()

