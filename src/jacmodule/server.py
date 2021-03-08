#!/usr/bin/env python

from flask import Flask
from flask import request
import requests
import logging
import socket
import sys
import json
from node import *

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
    global node
    return "\nServer is up and running in {}:{} !".format(node.ip,node.port)

@app.route('/join', methods=['PUT'])
def join():
    global node
    if node.is_bootstrap():
        ip = request.args.get("ip")
        port = request.args.get("port")
        res = node.add_node(ip, port)
        if not res == "":
            return "Node added successfully!"
        else:
            return "Node is already inside chord."
    else:
        # Communicate with bootstrap node
        url = "http://{}:{}/join".format(node.bnode[0],node.bnode[1])
        return requests.put(url, params={"ip":node.ip,"port":str(node.port)}).text

@app.route('/depart', methods=['DELETE'])
def depart():
    global node
    if node.is_bootstrap():
        keynode = request.args.get("keynode")
        res = node.delete_node(keynode)
        if not res == "":
            return "Node is not part of chord!"
        else:
            return "Node deleted succesfully!"
    else:
        # Communicate with bootstrap node
        return "I'm the bootstrap node! Please contact {}:{}".format(node.bnode[0],node.bnode[1]), 301

@app.route("/dummy")
def dummy():
    global node
    return "{} Nodes\n{}\n".format(node.number_of_nodes,str(node.nodes))

@app.route('/query')
def query():
    key = request.args.get("key")
    return "Key pair ({}, 42)\n".format(key)

@app.route('/insert')
def insert():
    key = request.args.get("key")
    value = request.args.get("value")
    return "Inserted keypair ({},{})!".format(key,value)

@app.route('/delete')
def delete():
    key = request.args.get("key")  
    return 'Deleted key {}!'.format(key)

@app.route('/overlay')
def overlay():
    return 'Suppose that this is the topology!\n'

@app.route('/shutdown', methods=['POST'])
def shutdown():
    # Notify bootstrap node
    global node
    if node.is_bootstrap():
        if len(node.nodes) == 1:
            shutdown_server()
        else:
            return "Please shutdown all the other nodes first."
    else:
        url = "http://{}:{}/depart".format(node.bnode[0],node.bnode[1])
        r = requests.delete(url,params={"keynode":node.key})
        shutdown_server()
    return 'Server shutting down...\n'  

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Please provide available port number")
        exit()
    ip = socket.gethostbyname(socket.gethostname())
    port = sys.argv[1]
    bnode_ip = sys.argv[2]
    bnode_port = sys.argv[3]

    try:
        if (ip, port) == (bnode_ip,bnode_port):
            node = BootstrapNode(ip, port)
        else:
            node = Node(ip, port, (bnode_ip, bnode_port))
        app.run(host=ip, port=port)
    except socket.error:
        print("Port {} is not available".format(sys.argv[1]))
        exit()

