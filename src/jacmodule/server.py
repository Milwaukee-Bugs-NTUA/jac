#!/usr/bin/env python

from flask import Flask
from flask import request
import requests
from requests.adapters import HTTPAdapter
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
    global node, ip, port, kfactor,consistency
    bnode_ip = request.args.get("ip")
    bnode_port = int(request.args.get("port"))

    if ip == bnode_ip and port == bnode_port:
        node = BootstrapNode(ip, port, kfactor, consistency)
        return "New chord created"
    else:
        
        node = Node(ip, port, (bnode_ip, bnode_port), kfactor, consistency)
        
        # Communicate with bootstrap node
        url = "http://{}:{}/addNode".format(bnode_ip,bnode_port)
        r = requests.put(url, params={"ip":node.ip,"port":node.port})
        
        if r.status_code == 200:

            data = r.json()
            node.previous_node = ReferenceNode(data["previous"]["ip"],int(data["previous"]["port"]))
            node.next_node = ReferenceNode(data["next"]["ip"],int(data["next"]["port"]))
            
            # Inform neighboors
            # Receive keys from next
            url = "http://{}:{}/transferKeys".format(node.next_node.ip,node.next_node.port)
            r1 = requests.get(url, params={"keynode":node.key})

            if r1.status_code == 200:
                data = r1.json()["keys"]
                node.data = {d["key_hash"]:(d["key"],d["value"]) for d in data}
            
            # Inform previous
            url = "http://{}:{}/changeNext".format(node.previous_node.ip,node.previous_node.port)
            r2 = requests.put(url, params={"ip":node.ip,"port":node.port})
            
            # Inform next
            url = "http://{}:{}/changePrevious".format(node.next_node.ip,node.next_node.port)
            r3 = requests.put(url, params={"ip":node.ip,"port":node.port})

            # Tell next to delete unnecessary keys
            if r1.status_code == 200:
                url = "http://{}:{}/deleteKeys".format(node.next_node.ip,node.next_node.port)
                r4 = requests.delete(url, params={"keynode":node.key})

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
        # Send keys to next node
        if not node.data == {}:
            data_list = [{"key_hash":k,"key":v[0],"value":v[1]} for (k,v) in node.data.items()]
            data = {"keys":data_list}
            r = requests.post("http://{}:{}/send".format(node.next_node.ip,node.next_node.port), json=json.dumps(data))
        
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

@app.route('/kickout', methods=['DELETE'])
def kickout():
    global node
    if node.is_bootstrap():
        return "Bootstrap node is not allowed to be excluded!"
    else:
        # Communicate with bootstrap node
        node = None
        return "Node object deleted!"

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
    
    if key_value == "*":

        response = app.response_class(
            response=json.dumps([{"key": v[0],"value": v[1]} for v in node.data.values()]),
            status=200,
            mimetype='application/json'
        )
        
        return response

    else:

        key = hash_key(key_value)
        successor = node.successor(key_value)
        
        if successor.key == node.key:

            if key in node.data:
                
                if node.kfactor == 1:
                
                    return "Key pair {} found in node {}:{}!".format(node.data[key],node.ip,node.port)
                
                elif node.consistency_type == "chain-replication":
                    
                    s = requests.Session()
                    s.mount('http://', HTTPAdapter(max_retries=0))
                    url = "http://{}:{}/queryReplicas".format(node.next_node.ip,node.next_node.port)
                    r = s.get(url,params={"key":key_value})
                    return r.text, r.status_code
                
                elif node.consistency_type == "eventually":
                    
                    return "Key pair {} found in node {}:{}!".format(node.data[key],node.ip,node.port)
                        
            else:
                return "Key not found",404
        else:
            # Send key to successor
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=0))
            url = "http://{}:{}/query".format(successor.ip,successor.port)
            r = s.get(url,params={"key":key_value})
            return r.text

@app.route('/queryReplicas')
def query_replicas():
    global node

    key_value = request.args.get("key")
    k, v, replica_number = node.replicas[hash_key(key_value)]

    if not node.key == node.successor(key_value).key:
    
        if replica_number == node.kfactor - 1:
            return "Key pair {} found in node {}:{}!".format(node.replicas[hash_key(key_value)],node.ip,node.port)
        else:
                
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=0))
            url = "http://{}:{}/queryReplicas".format(node.next_node.ip,node.next_node.port)
            r = s.post(url,params={"key":key_value})

            if r.status_code == 200:
                return r.text
            elif r.status_code == 204:
                return "Key pair {} found in node {}:{}!".format(node.replicas[hash_key(key_value)],node.ip,node.port)
    else:
        return "Replica manager only have original data", 204


@app.route('/nextNode')
def next_node():
    global node
    if node == None:
        response = app.response_class(
            response=json.dumps({}),
            status=204,
            mimetype='application/json'
        )
    else:
        response = app.response_class(
            response=json.dumps({"ip":node.next_node.ip,"port":node.next_node.port}),
            status=200,
            mimetype='application/json'
        )
    return response

@app.route('/queryAll')
def query_all():
    global node

    data_list = [{"key":v[0], "value":v[1]} for v in node.data.values()]
    
    next_node = node.next_node

    if not next_node == None:

        while not next_node.key == node.key:
            # Find next node for query
            url = "http://{}:{}/nextNode".format(next_node.ip,next_node.port)
            r1 = requests.get(url)
            
            # Receive keys for next node
            url = "http://{}:{}/query".format(next_node.ip,next_node.port)
            r2 = requests.get(url, params={"key":"*"})

            # Update data_list
            if r2.status_code == 200:
                data_list = data_list + r2.json()

            # Update next node
            data = r1.json()
            next_node = ReferenceNode(data["ip"],data["port"])        

    response = app.response_class(
        response=json.dumps({"keys":data_list}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/insert',methods=['POST'])
def insert():
    global node    
    key_value = request.args.get("key")
    value = request.args.get("value")
    
    successor = node.successor(key_value)

    if successor.key == node.key:
        
        # Add key here
        node.add_key(key_value,value)

        if node.kfactor == 1:
            return "Key added successfully to node {}:{}!".format(node.ip,node.port)
        else:

            if node.consistency_type == "chain-replication":
                
                s = requests.Session()
                s.mount('http://', HTTPAdapter(max_retries=0))
                url = "http://{}:{}/insertReplicas".format(node.next_node.ip,node.next_node.port)
                r = s.post(url,params={"key":key_value,"value":value,"replica_number":1})
                
                return "Key added successfully to node {}:{}!".format(node.ip,node.port)
            
            elif node.consistency_type == "eventually":
                
                node.add_key(key_value,value)
                
                return "Eventually consistency is not Implemented Yet"
    else:
        
        # Send key to successor
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=0))
        url = "http://{}:{}/insert".format(successor.ip,successor.port)
        r = s.post(url,params={"key":key_value,"value":value})
        
        return r.text

@app.route('/insertReplicas',methods=['POST'])
def insert_replicas():
    global node

    key_value = request.args.get("key")
    value = request.args.get("value")
    replica_number = int(request.args.get("replica_number"))
    
    # Check if already have this key in data
    # Only edge case if kfactor >= number on nodes
    if not node.key == node.successor(key_value).key:

        # Update replica key
        node.add_replica(key_value, value, replica_number)

        if replica_number < node.kfactor - 1:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=0))
            url = "http://{}:{}/insertReplicas".format(node.next_node.ip,node.next_node.port)
            r = s.post(url,params={"key":key_value,"value":value,"replica_number":replica_number + 1})
            
            return r.text

    return "Key {} & its replicas added successfully".format(key_value)


@app.route('/send',methods=['POST'])
def send():
    global node        
    new_keys = json.loads(request.get_json())["keys"]
    for d in new_keys:
        node.data[d["key_hash"]] = (d["key"],d["value"])
    return "Keys transfered!"

@app.route('/transferKeys')
def transfer_keys():
    global node        
    keynode = int(request.args.get("keynode"))

    if node.data == {}:
        response = app.response_class(
            response=json.dumps({"keys":[]}),
            status=204,
            mimetype='application/json'
        )
        return response
    else:
        data_list = [{"key_hash":k,"key":v[0],"value":v[1]} for (k,v) in node.data.items() if k <= keynode or k > node.key]
        data = {"keys":data_list}
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response

@app.route('/deleteKeys',methods=['DELETE'])
def delete_keys():

    global node        
    keynode = request.args.get("keynode")

    if not keynode == None:
        keynode = int(keynode)
        node.data = {k:v for (k,v) in node.data.items() if not(k <= keynode or k > node.key)}

    return "Keys deleted"

@app.route('/delete', methods=['DELETE'])
def delete():
    global node
    key_value = request.args.get("key")
    key = hash_key(key_value)
    
    successor = node.successor(key_value)
    if successor.key == node.key:
        # Add key here
        if key in node.data:
            if node.kfactor == 1:
                del node.data[key]
                return "Key '{}' deleted from node {}:{}!".format(key_value,node.ip,node.port)
            
            elif node.consistency_type == "chain-replication":
                
                del node.data[key]

                s = requests.Session()
                s.mount('http://', HTTPAdapter(max_retries=0))
                url = "http://{}:{}/deleteReplicas".format(node.next_node.ip,node.next_node.port)
                r = s.delete(url,params={"key":key_value,"replica_number":1})
                
                return r.text

            elif node.consistency_type == "chain-replication":
                del node.data[key]
                return "Key '{}' deleted from node {}:{}!".format(key_value,node.ip,node.port)
        else:
            return "Key not found",404
    else:
        # Send key to successor
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=0))
        url = "http://{}:{}/delete".format(successor.ip,successor.port)
        r = s.delete(url,params={"key":key_value})
        return r.text

@app.route('/deleteReplicas',methods=['DELETE'])
def delete_replicas():
    global node

    key_value = request.args.get("key")
    replica_number = int(request.args.get("replica_number"))
    

    # Edge case for kfactor >= number of nodes
    if not node.key == node.successor(key_value).key:
        
        # Delete replica key
        del node.replicas[hash_key(key_value)]

        if replica_number < node.kfactor - 1:
                
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=0))
            url = "http://{}:{}/deleteReplicas".format(node.next_node.ip,node.next_node.port)
            r = s.delete(url,params={"key":key_value,"replica_number":replica_number + 1})
            
            return r.text
    
    return "Key {} & its replicas deleted".format(key_value)

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

@app.route('/info')
def info():
    global node
    data = {
        "keys": [{"key_hash":k,"key":v[0],"value":v[1]} for (k,v) in node.data.items()],
        "replicas": [{"key_hash":k,"key":v[0],"value":v[1],"replica_num":v[2]} for (k,v) in node.replicas.items()],
        "previous": {
            "ip": node.previous_node.ip,
            "port": node.previous_node.port,
        },
        "next": { 
            "ip": node.next_node.ip,
            "port": node.next_node.port,
        },
    }
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

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
                for n in node.nodes:
                    url = "http://{}:{}/kickout".format(node.nodes[n][0],node.nodes[n][1])
                    requests.delete(url)
                    shutdown_server()
        else:
            url = "http://{}:{}/depart".format(node.ip,node.port)
            r = requests.delete(url)
            shutdown_server()
    return 'Server shutting down...'  

if __name__ == "__main__":

    if not len(sys.argv) == 4:
        print("Please provide available port number, replication factor & consistency type")
        exit()

    ip = socket.gethostbyname(socket.gethostname())
    port = int(sys.argv[1])
    kfactor = int(sys.argv[2])
    consistency = sys.argv[3]
    node = None

    try:
        app.run(host=ip, port=port)
    except socket.error:
        print("Port {} is not available".format(sys.argv[1]))
        exit()

