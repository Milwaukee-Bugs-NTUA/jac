#!/usr/bin/env python

import hashlib

class Node():
    data = {}
    next_node = None
    previous_node = None

    def __init__(self, ip, port, bnode):
        self.ip = ip
        self.port = port
        self.key = hashlib.sha1(str.encode("{}:{}".format(ip, port)))
        self.bnode = bnode

    def set_next(self,next_node):
        self.next_node = next_node

    def set_previous(self,previous):
        self.previous_node = previous_node

    def is_bootstrap(self):
        return (self.ip,self.port) == self.bnode

class BootstrapNode(Node):

    nodes = {}
    number_of_nodes = 0

    def __init__(self, ip, port):
        super().__init__(ip, port, (ip,port))
        self.nodes[self.key] = (ip, port)
        self.number_of_nodes += 1
        
    def add_node(self, ip, port):
        self.nodes[hashlib.sha1(str.encode("{}:{}".format(ip, port)))] = (ip, port)
        self.number_of_nodes += 1

    def find_next(self, keynode):
        temp = self.nodes.keys()
        temp.sort()
        for index, key in enumerate(temp):
            if key == keynode:
                return self.nodes[temp[(index + 1) % self.number_of_nodes]]

    def delete_node(self, keynode):
        self.number_of_nodes -= 1
        del self.nodes[keynode]
