#!/usr/bin/env python3

from flask import Flask
from flask import request
import logging
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
    return f'Key pair ({key}, 42)\n'

@app.route('/insert/<key>/<value>')
def insert(key, value):
    return 'Inserted keypair ({key},{value})!\n'

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
    app.run()
