#!/bin/bash

# Starts a chord from 5 VMs
# $1: number of nodes
# $2: k factor
# $3: consistency policy
start() {

    # Find IPs of vm
    IPs=$(hostname -I)
    conda_path=$(which conda)
    path=${conda_path%/*}
    # Operations to be send
    # VMs
    jac="$path/python ./jacmodule/server.py"
    find_ip='IPs=$(hostname -I) && arrIP=(${IPs// / })'
    set_ip='export JACSERVER_IP=${arrIP[0]}' 
    join="$path/python ./jacmodule/cli.py join"

    # Main-node
    find_ip_main='IPs=$(hostname -I) && arrIP=(${IPs// / })'
    set_ip_main='export JACSERVER_IP=${arrIP[1]}'
    jac_main="$path/python ./src/jacmodule/server.py"
    join_main="$path/python ./src/jacmodule/cli.py join"

    # Start nodes in main VM
    for n in {1..2}
        do
            set_port="export JACSERVER_PORT=500$((n - 1))"
            ssh user@main-node "sh -c 'nohup $jac_main 500$((n - 1)) $2 $3 > /dev/null 2>&1 &'"
            ssh user@main-node "$find_ip_main && $set_ip_main && $set_port && $join_main"
        done

    # Start nodes in workers
    for i in 0 1 2 3
    do
        for n in {1..2}
        do
            set_port="export JACSERVER_PORT=500$((n - 1))"
            ssh user@node$i "sh -c 'nohup $jac 500$((n - 1)) $2 $3 > /dev/null 2>&1 &'"
            ssh user@node$i "$find_ip && $set_ip && $set_port && $join"
        done
    done
        
}

if [ $# -eq 0 -o $# -eq 1 ]
then
    echo "Please provide <number of nodes> <k factor> <consistency type>"
    exit
fi

if [ ! $(($1 % 5)) -eq 0 ]
then
    echo "This script works only for multiples of 5"
    exit
else
    echo "Starting $1 nodes..."
    start $1 $2 $3
    echo "New chord created"
fi

