#!/bin/bash

# Starts a chord from 5 VMs
# $1: number of nodes
# $2: k factor
# $3: consistency policy
terminate() {

    conda_path=$(which conda)
    path=${conda_path%/*}
    # Operations to be send
    find_ip='IPs=$(hostname -I) && arrIP=(${IPs// / })'
    set_ip='export JACSERVER_IP=${arrIP[0]}'
    exit="$path/python ./jacmodule/cli.py exit"
    
    find_ip_main='IPs=$(hostname -I) && arrIP=(${IPs// / })'
    set_ip_main='export JACSERVER_IP=${arrIP[1]}'
    exit_main="$path/python ./src/jacmodule/cli.py exit"

    # Start nodes in main VM
    for n in 1 2
        do
            p=$(($n - 1))
            set_port="export JACSERVER_PORT=500$p"
            ssh user@main-node "$find_ip_main && $set_ip_main && $set_port && $exit_main"
        done

    # Start nodes in workers
    for i in 0 1 2 3
    do
        for n in 1 2
        do
            p=$(($n - 1))
            set_port="export JACSERVER_PORT=500$p"
            ssh user@node$i "$find_ip && $set_ip && $set_port && $exit"
        done
    done
        
}

if [ $# -eq 0 ]
then
    echo "Please provide <number of nodes>"
    exit
fi

if [ ! $(($1 % 5)) -eq 0 ]
then
    echo "This script works only for multiples of 5"
    exit
else
    echo "Terminating $1 nodes..."
    terminate $1
    echo "All nodes were terminated"
fi