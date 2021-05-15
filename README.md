# J.A.C.: Just Another Chord implementation

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) <br/>
[![Python](https://img.shields.io/badge/Python-3.8-informational.svg)](https://www.python.org/downloads/release/python-385/)
[![Anaconda](https://img.shields.io/badge/Anaconda-2020.11-green.svg)](https://www.anaconda.com/products/individual)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/Milwaukee-Bugs-NTUA/jac/blob/master/LICENSE)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)


## 🎓 School of Electrical & Computer Engineering, NTUA <br/> Project for the course [Distributed Systems](https://www.ece.ntua.gr/en/undergraduate/courses/3377), Winter Semester 2020-2021

This repo was created for version control of the project implemented during [*Distributed Systems*](https://www.ece.ntua.gr/en/undergraduate/courses/3377) course in the department of Electrical & Computer Engireering School, NTUA. The main goal was the construction of file sharing application with multiple distributed nodes DHT. Further information can be found in the related pdf file (in greek).

## Overview

JAC is a distributed system that provides a look up service of key-value pairs, stored across a cluster of nodes. Any participating node can retrieve the value associated to a particular key or even the value of one of its replicas, if replication of data is enabled. JAC provides out of the box 2 types of consistency, *eventually consistency* & *chain-replication*. In more depth, each node offers the basic fuctionalities of a *Distributed Hash Table*, such as ```insert```, ```query``` & ```delete``` with some additional commands like ```overlay```, ```info``` and others. Further infromation about all the available commands can be found inside [Utilities.md]().

<img align="center" src="https://user-images.githubusercontent.com/45902117/118357115-1bfe6e80-b581-11eb-84a5-870a19784c34.gif" width="600"/>

```
jac-cli@ntua$ help
Usage:   COMMAND [OPTIONS] [ARGS]

Commands:
  delete   Deletes the specified <key>.
  depart   Makes current node to depart.
  exit     Makes current node to depart & exits from shell.
  help     Prints this message and exits.
  info     Displays info for current node.
  insert   Inserts the pair (<key>, <value>).
  join     Inserts a new node.
  overlay  Displays current network topology.
  query    Finds the value of <key>.
```

## References
[1] Stoica, Ion, et al. "Chord: A scalable peer-to-peer lookup service for internet applications." ACM SIGCOMM Computer Communication Review 31.4 (2001): 149-160.
