#!/bin/bash

# Files 
nodes="./nodes.txt"
keys="../test_data/query.txt"

# Operations
conda_path=$(which conda)
path=${conda_path%/*}
# Operations to be send
find_ip='IPs=$(hostname -I) && arrIP=(${IPs// / })'
set_ip='export JACSERVER_IP=${arrIP[0]}'
query="$path/python ./jacmodule/cli.py query"

find_ip_main='IPs=$(hostname -I) && arrIP=(${IPs// / })'
set_ip_main='export JACSERVER_IP=${arrIP[1]}'
query_main="$path/python ./src/jacmodule/cli.py query"

start=`date +%s`
while IFS= read -r -u 4 node_port && IFS= read -r -u 5 key;
do
	# Read node & port
	IFS=' '
	read -a arr <<< "$node_port"
	node=${arr[0]}
	port=$((${arr[1]}))

	set_port="export JACSERVER_PORT=$port"

	if [ "$node" = "main-node" ]
	then
		ssh user@$node "$find_ip_main && $set_ip_main && $set_port && $query_main \"$key\""
	else
		ssh user@$node "$find_ip && $set_ip && $set_port && $query \"$key\""
	fi

done 4<$nodes 5<$keys
end=`date +%s`

runtime=$((end-start))
echo $runtime >> ../test_data/query_times.txt