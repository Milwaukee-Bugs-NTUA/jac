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
#log.disabled = True

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def health_check():
    global ip, port
    return "\nServer is up and running in {}:{} !".format(ip,port)

@app.route('/join', methods=['PUT'])
def join():
    global node, ip, port
    bnode_ip = request.args.get("ip")
    bnode_port = int(request.args.get("port"))

    if ip == bnode_ip and port == bnode_port:
        node = BootstrapNode(ip, port)
        return "New chord created"
    else:
        node = Node(ip, port, (bnode_ip, bnode_port))
        # Communicate with bootstrap node
        url = "http://{}:{}/addNode".format(bnode_ip,bnode_port)
        r = requests.put(url, params={"ip":node.ip,"port":node.port})
        if r.status_code == 200:
            data = r.json()
            node.previous_node = ReferenceNode(data["previous"]["ip"],int(data["previous"]["port"]))
            node.next_node = ReferenceNode(data["next"]["ip"],int(data["next"]["port"]))
            # Inform neighboors
            # Inform previous
            url = "http://{}:{}/changeNext".format(node.previous_node.ip,node.previous_node.port)
            r = requests.put(url, params={"ip":node.ip,"port":node.port})
            # Inform next
            url = "http://{}:{}/changePrevious".format(node.next_node.ip,node.next_node.port)
            r = requests.put(url, params={"ip":node.ip,"port":node.port})
            return "New node added successfully!"
        else:
            return r.text

@app.route('/changeNext',methods=['PUT'])
def change_next():
    new_ip = request.args.get("ip")
    new_port = int(request.args.get("port"))
    if new_ip == node.ip and node.port == new_port:
        node.next_node = None
    else:
        node.next_node = ReferenceNode(new_ip,new_port)
    return "Changed next node"

@app.route('/changePrevious',methods=['PUT'])
def change_previous():
    new_ip = request.args.get("ip")
    new_port = int(request.args.get("port"))
    if new_ip == node.ip and node.port == new_port:
        node.previous_node = None
    else:
        node.previous_node = ReferenceNode(new_ip,new_port)
    return "Changed previous node"

@app.route('/addNode', methods=['PUT'])
def add_node():
    global node
    if node.is_bootstrap():
        ip = request.args.get("ip")
        port = int(request.args.get("port"))
        keynode = node.add_node(ip, port)
        if keynode == -1:
            return "Node is already inside chord.", 405
        else:
            prev_node, next_node = node.find_neighboors(keynode)
            data = {"previous":{"ip":prev_node[0],"port":prev_node[1]}, "next":{"ip":next_node[0],"port":next_node[1]}}
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response
    else:
        return "I'm not the bootstrap server. Please contact {}:{}".format(node.bnode.ip,node.bnode.port), 301

@app.route('/depart', methods=['DELETE'])
def depart():
    global node
    if node.is_bootstrap():
        return "Bootstrap node is not allowed to depart!"
    else:
        # Communicate with bootstrap node
        url = "http://{}:{}/removeNode".format(node.bnode.ip,node.bnode.port)
        r = requests.delete(url, params={"keynode":node.key})
        # Inform neighboors
        # Inform Previous
        url = "http://{}:{}/changeNext".format(node.previous_node.ip,node.previous_node.port)
        requests.put(url, params={"ip":node.next_node.ip,"port":node.next_node.port})
        # Inform Next
        url = "http://{}:{}/changePrevious".format(node.next_node.ip,node.next_node.port)
        requests.put(url, params={"ip":node.previous_node.ip,"port":node.previous_node.port})
        node = None
        return r.text


@app.route('/removeNode', methods=['DELETE'])
def remove_node():
    global node
    if node.is_bootstrap():
        keynode = int(request.args.get("keynode"))
        if keynode == node.key:
            return "Bootstrap node is not allowed to depart!"
        res = node.delete_node(keynode)
        if res == -1:
            return "Node is not part of chord!"
        else:
            return "Node deleted succesfully!"
    else:
        return "I'm not the bootstrap server. Please contact {}:{}".format(node.bnode.ip,node.bnode.port), 301

@app.route('/query')
def query():
    global node
    key_value = request.args.get("key")
    key = hash_key(key_value)
    
    successor = node.successor(key_value)
    if successor.key == node.key:
        # Add key here
        if key in node.data:
            return "Key/Value pair ({},{}) found in node {}:{}!".format(key_value,node.data[key],node.ip,node.port)
        else:
            return "Key not found",404
    else:
        # Send key to successor
        url = "http://{}:{}/query".format(successor.ip,successor.port)
        r = requests.get(url,params={"key":key_value})
        return r.text

@app.route('/insert',methods=['POST'])
def insert():
    global node
    key_value = request.args.get("key")
    value = request.args.get("value")
    
    successor = node.successor(key_value)
    if successor.key == node.key:
        # Add key here
        node.data[hash_key(key_value)] = value
        return "Key added successfully to node {}:{}!".format(node.ip,node.port)
    else:
        # Send key to successor
        url = "http://{}:{}/insert".format(successor.ip,successor.port)
        r = requests.post(url,params={"key":key_value,"value":value})
        return r.text

@app.route('/delete')
def delete():
    key = request.args.get("key")  
    return 'Deleted key {}!'.format(key)

@app.route('/overlay')
def overlay():
    global node
    if node.is_bootstrap():
        response_text = "{} Nodes\n".format(node.number_of_nodes)
        l = list(node.nodes.keys())
        l.sort()
        for n in l:
            response_text += "{}: {}\n".format(n,node.nodes[n])
        return response_text
    else:
        url = "http://{}:{}/overlay".format(node.bnode.ip,node.bnode.port)
        r = requests.get(url)
        return r.text

@app.route('/shutdown', methods=['POST'])
def shutdown():
    # Notify bootstrap node
    global node
    if node == None:
        shutdown_server()
    else:
        if node.is_bootstrap():
            if node.number_of_nodes == 1:
                shutdown_server()
            else:
                return "Please shutdown all the other nodes first."
        else:
            url = "http://{}:{}/depart".format(node.ip,node.port)
            r = requests.delete(url)
            shutdown_server()
    return 'Server shutting down...'  

if __name__ == "__main__":

    if not len(sys.argv) == 2:
        print("Please provide available port number & bootstrap option")
        exit()

    ip = socket.gethostbyname(socket.gethostname())
    port = int(sys.argv[1])
    node = None

    try:
        app.run(host=ip, port=port)
    except socket.error:
        print("Port {} is not available".format(sys.argv[1]))
        exit()

