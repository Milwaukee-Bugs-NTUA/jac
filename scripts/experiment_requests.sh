#!/bin/bash

# Files 
nodes="./nodes.txt"
keys="../transactions/requests.txt"

# Operations
conda_path=$(which conda)
path=${conda_path%/*}
# Operations to be send
find_ip='IPs=$(hostname -I) && arrIP=(${IPs// / })'
set_ip='export JACSERVER_IP=${arrIP[0]}'
cli="$path/python ./jacmodule/cli.py"

find_ip_main='IPs=$(hostname -I) && arrIP=(${IPs// / })'
set_ip_main='export JACSERVER_IP=${arrIP[1]}'
cli_main="$path/python ./src/jacmodule/cli.py"

while IFS= read -r -u 4 node_port && IFS= read -r -u 5 request;
do
	# Read node & port
	IFS=' '
	read -a arr <<< "$node_port"
	node=${arr[0]}
	port=$((${arr[1]}))

    # Read key pair
	IFS=','
	read -a arr <<< "$request"
	command=${arr[0]}
	key=${arr[1]}

    if [ "$command" = "insert" ]
    then
        value=$((${arr[2]}))
    fi


	set_port="export JACSERVER_PORT=$port"

	if [ "$node" = "main-node" ]
	then
        if [ "$command" = "insert" ]
        then
            ssh user@$node "$find_ip_main && $set_ip_main && $set_port && $cli_main $command \"$key\" $value" >> ../transactions/results_$1.txt
        else
            ssh user@$node "$find_ip_main && $set_ip_main && $set_port && $cli_main $command \"$key\"" >> ../transactions/results_$1.txt
        fi
	else
        if [ "$command" = "insert" ]
        then
      		ssh user@$node "$find_ip && $set_ip && $set_port && $cli $command \"$key\" $value" >> ../transactions/results_$1.txt
        else
        	ssh user@$node "$find_ip && $set_ip && $set_port && $cli $command \"$key\"" >> ../transactions/results_$1.txt
        fi
	fi

done 4<$nodes 5<$keys