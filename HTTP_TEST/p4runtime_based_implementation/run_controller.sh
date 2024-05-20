#!/bin/bash

# First: Execute the simple_switch_grpc command
sudo simple_switch_grpc \
    --log-file ss-log \
    --log-flush \
    --dump-packet-data 10000 \
    -i 0@s1-eth1 \
    -i 1@s1-eth2 \
    --no-p4 \
    --thrift-port 9090 \
    -- --cpu-port 510 &

# Wait for a few seconds to ensure the switch is up
sleep 5

# Second: Set environment variables and run make commands
export P4GUIDE="/home/anthony/HTTP_TEST/p4runtime_based_implementation/p4-guide"
export PYPKG_TESTLIB="$P4GUIDE/testlib"

cd $P4GUIDE/flowcache || { echo "Failed to change directory to $P4GUIDE/flowcache"; exit 1; }

# Execute make commands
make loadp4prog

# Wait for a few seconds to ensure the program is loaded
sleep 5

# Run the controller
make runcontroller
