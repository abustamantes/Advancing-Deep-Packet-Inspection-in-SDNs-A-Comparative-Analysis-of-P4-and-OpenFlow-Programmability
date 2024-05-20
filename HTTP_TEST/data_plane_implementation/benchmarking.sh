#!/bin/bash

# The Python script to be executed
PYTHON_SCRIPT="http_dpi_client.py"

# Function to get the average CPU usage from mpstat
get_cpu_usage() {
  mpstat 1 1 | awk '/Average/ {print 100 - $NF}'
}

# Measure CPU usage before execution
cpu_usage_before=$(get_cpu_usage)
# Ensure minimum initial CPU usage for meaningful comparison
if (( $(echo "$cpu_usage_before < 1" | bc -l) )); then
  initial_cpu_adjusted=1
  cpu_usage_before=1
else
  initial_cpu_adjusted=0
fi
echo "CPU Usage Before Execution: ${cpu_usage_before}%"

# Record the start time in milliseconds
start_time=$(date +%s%3N)

# Execute the Python script and measure CPU and memory usage
/usr/bin/time -v python3 $PYTHON_SCRIPT 2> time_output.txt &
pid=$!

# Initialize CPU usage tracking
peak_cpu_usage=0

# Monitor the CPU usage while the process is running
while ps -p $pid > /dev/null; do
  cpu_usage=$(get_cpu_usage)
  echo "Current CPU Usage: ${cpu_usage}%"  # Debugging line to check CPU usage
  if (( $(echo "$cpu_usage > $peak_cpu_usage" | bc -l) )); then
    peak_cpu_usage=$cpu_usage
  fi
  sleep 1  # Adjust the sampling rate as needed
done

# Add 1% to peak CPU usage if initial CPU was adjusted
if (( $initial_cpu_adjusted == 1 )); then
  peak_cpu_usage=$(echo "$peak_cpu_usage + 1" | bc -l)
fi

# Record the end time in milliseconds
end_time=$(date +%s%3N)

# Calculate the execution time in milliseconds
execution_time=$((end_time - start_time))

# Calculate the CPU usage increment factor and format it to remove trailing zeros
cpu_usage_factor=$(echo "scale=2; $peak_cpu_usage / $cpu_usage_before" | bc -l)
cpu_usage_factor=$(printf "%.2f" $cpu_usage_factor)

# Extract CPU and memory usage information from the output of the time command
cpu_time=$(grep "User time" time_output.txt | awk '{print $4}')
max_memory=$(grep "Maximum resident set size" time_output.txt | awk '{print $6}')

echo
echo "-----------------------------"
echo "Execution Time: ${execution_time}ms"
echo "Peak CPU Usage During Execution: ${peak_cpu_usage}%"
echo "CPU Usage Increment Factor: ${cpu_usage_factor}"
echo "CPU Time: ${cpu_time}s"
echo "Maximum Memory Usage: ${max_memory}KB"
echo "-----------------------------"

# Clean up the temporary file
rm time_output.txt
