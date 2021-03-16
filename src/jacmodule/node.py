#!/usr/bin/env python

import hashlib

class ReferenceNode():
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.key = hashlib.sha1(str.encode("{}:{}".format(ip, port))).hexdigest()

class Node():
    data = {}
    next_node = None
    previous_node = None

    def __init__(self, ip, port, bnode):
        self.ip = ip
        self.port = port
        self.key = hashlib.sha1(str.encode("{}:{}".format(ip, port))).hexdigest()
        self.bnode = referenceNode(bnode[0],bnode[1])

    def is_bootstrap(self):
        return self.key == self.bnode.key

class BootstrapNode(Node):

    nodes = {}
    number_of_nodes = 0

    def __init__(self, ip, port):
        super().__init__(ip, port, (ip,port))
        self.nodes[self.key] = (ip, port)
        self.number_of_nodes += 1
        
    def add_node(self, ip, port):
        keynode = hashlib.sha1(str.encode("{}:{}".format(ip, port))).hexdigest()
        if not keynode in self.nodes:
            self.nodes[keynode] = (ip, port)
            self.number_of_nodes += 1
            return keynode
        else:
            return ""

    def next_index(self, index):
            return (index + 1) % self.number_of_nodes
    def previous_index(self, index):
            return (abs(index - 1)) % self.number_of_nodes

    def find_neighboors(self, keynode):
        temp = list(self.nodes.keys())
        temp.sort()
        for index, key in enumerate(temp):
            if key == keynode:
                return self.nodes[temp[self.previous_index(index)]], self.nodes[temp[self.next_index(index)]]

    def delete_node(self, keynode):
        if keynode in self.nodes:
            self.number_of_nodes -= 1
            del self.nodes[keynode]
            return keynode
        else:
            return ""
            
