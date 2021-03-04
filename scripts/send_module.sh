#!/bin/bash

if [[ -z "${VMNAME}" ]]
then
    echo "Please provide a vm name"
    echo "Usage: export VMNAME=<vmname> && ./send_module.sh"
    exit  
fi

# Zip source code & scripts folder
tar --exclude="../src/__pycache__" -czvf ../code.tar.gz ../scripts ../src
# Send tarball to main-node
scp ../code.tar.gz user@$VMNAME:.
# Uncompressed tarballs
ssh user@$VMNAME 'tar -xzf ./code.tar.gz && rm ./code.tar.gz'

# Distribute code to nodes
ssh user@$VMNAME './scripts/distribute_module.sh'


