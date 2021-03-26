#!/bin/bash

echo > ../transactions/results_eventually.txt
echo > ../transactions/results_chain-replication.txt

for consistency in "chain-replication" "eventually"
do
    echo "---- Experiment for k = 3 & consistency policy \"$consistency\" ----"
    ./start-chord.sh 3 $consistency
    ./experiment_requests.sh $consistency
    ./terminate-chord.sh
    echo "---------------------------------------------------------------------"
done
