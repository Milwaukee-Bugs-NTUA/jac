#!/bin/bash

if [[ -z "${HOSTNAME}" ]]
then
    echo "Please provide a hostname"
    echo "Usage: export HOSTNAME=<hostname> && ./send_module.sh"
    exit  
fi

# Zip source code & scripts folder
tar --exclude="../src/__pycache__" -czvf ../code.tar.gz ../scripts ../src
# Send tarball to main-node
scp ../code.tar.gz user@$HOSTNAME:.
# Uncompressed tarballs
ssh user@$HOSTNAME 'tar -xzf ./code.tar.gz && rm ./code.tar.gz'

# Distribute code to nodes
ssh user@$HOSTNAME './scripts/distribute_module.sh'


