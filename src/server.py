#!/usr/bin/env python3

from flask import Flask
from flask import request
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def hello_world():
    return 'Hello, World!\n'

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...\n'

if __name__ == "__main__":
    app.run()
