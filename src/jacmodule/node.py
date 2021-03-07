#!/usr/bin/env python

import hashlib

class Node(object):
    data = {}
    next_node = None
    previous_node = None

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.key = hashlib.sha1(str.encode("{}:{}".format(ip, port)))

    def set_next(self,next_node):
        self.next_node = next_node

    def set_previous(sefl,previous):
        self.previous_node = previous_node

class BootstrapNode(Node):

    nodes = {}
    number_of_nodes = 0

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.key = hashlib.sha1(str.encode("{}:{}".format(ip, port)))
        self.nodes[self.key] = (ip, port)
        self.number_of_nodes += 1

    def __init__(self, base_node):
        self.ip = base_node.ip
        self.port = base_node.port
        self.key = base_node.key
        self.nodes[self.key] = (self.ip, self.port)
        self.number_of_nodes += 1
        
    def add_node(self, keynode, ip, port):
        self.nodes[keynode] = (ip, port)
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

    