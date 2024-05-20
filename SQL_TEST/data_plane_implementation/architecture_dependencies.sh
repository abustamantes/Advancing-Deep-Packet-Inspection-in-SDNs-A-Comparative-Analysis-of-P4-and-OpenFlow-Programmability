#!/bin/bash

# Start the simple_switch with the specified interfaces and P4 program
simple_switch -i 0@s1-eth1 -i 1@ens37 sql_dpi.json &

# Define the path to the CLI and the port it uses
CLI_PATH="simple_switch_CLI"
THRIFT_PORT=9090

# Define the file with the table commands
COMMAND_FILE="rules_list.txt"

# Check if the command file exists
if [ ! -f "$COMMAND_FILE" ]; then
    echo "Command file not found: $COMMAND_FILE"
    exit 1
fi

# Loop through each line in the command file and execute it
while IFS= read -r line
do
    echo $line | $CLI_PATH --thrift-port $THRIFT_PORT
done < "$COMMAND_FILE"
