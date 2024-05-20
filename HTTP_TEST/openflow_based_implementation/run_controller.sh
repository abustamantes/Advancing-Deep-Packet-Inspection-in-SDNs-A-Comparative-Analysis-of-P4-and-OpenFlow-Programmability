#!/bin/bash

# Define the directory where pox.py is located
POX_DIR="/home/anthony/pox"

# Change to the directory
cd "$POX_DIR" || { echo "Failed to change directory to $POX_DIR"; exit 1; }

# Execute the pox.py script with forwarding.http_controller
./pox.py forwarding.http_controller
