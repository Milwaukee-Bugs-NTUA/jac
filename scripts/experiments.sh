#!/bin/bash

echo > ../transactions/insert_times.txt
echo > ../transactions/query_times.txt

echo "--- Experiment for k = 1 ----"
./start-chord.sh 1 chain-replication
./experiment_insert.sh
./experiment_query.sh
./terminate-chord.sh
echo "-----------------------------"

for k in 3 5
do
    for consistency in "chain-replication" "eventually"
    do
        echo "---- Experiment for k = $k & consistency policy \"$consistency\" ----"
        ./start-chord.sh $k $consistency
        ./experiment_insert.sh
        ./experiment_query.sh
        ./terminate-chord.sh
        echo "---------------------------------------------------------------------"
    done
done