#!/bin/bash

# Function to get the average CPU usage from mpstat
get_cpu_usage() {
  mpstat 1 1 | awk '/Average/ {print 100 - $NF}'
}

# Function to execute a Python script and measure its CPU and memory usage
measure_script() {
  local PYTHON_SCRIPT=$1
  local LOG_FILE="time_output_${PYTHON_SCRIPT%.py}.txt"

  echo "Executing $PYTHON_SCRIPT"

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
  /usr/bin/time -v python3 $PYTHON_SCRIPT 2> $LOG_FILE &
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
  cpu_time=$(grep "User time" $LOG_FILE | awk '{print $4}')
  max_memory=$(grep "Maximum resident set size" $LOG_FILE | awk '{print $6}')

  echo "Execution Time: ${execution_time}ms"
  echo "Peak CPU Usage During Execution: ${peak_cpu_usage}%"
  echo "CPU Usage Increment Factor: ${cpu_usage_factor}"
  echo "CPU Time: ${cpu_time}s"
  echo "Maximum Memory Usage: ${max_memory}KB"
  echo

  # Clean up the temporary file
  rm $LOG_FILE

  # Accumulate the results
  total_execution_time=$((total_execution_time + execution_time))
  total_cpu_time=$(echo "$total_cpu_time + $cpu_time" | bc)
  if (( max_memory > total_max_memory )); then
    total_max_memory=$max_memory
  fi
  total_peak_cpu_usage=$(echo "$total_peak_cpu_usage + $peak_cpu_usage" | bc)
}

# Initialize total values
total_execution_time=0
total_cpu_time=0
total_max_memory=0
total_peak_cpu_usage=0

# List of Python scripts to be executed
PYTHON_SCRIPTS=("accuracy_test.py" "delay_test.py")

# Execute each Python script in sequence and measure its resource usage
for script in "${PYTHON_SCRIPTS[@]}"; do
  measure_script $script
done

# Calculate the overall CPU usage increment factor
overall_cpu_usage_factor=$(echo "scale=2; $total_peak_cpu_usage / 2" | bc -l)

# Print the combined results
echo "-----------------------------"
echo "Total Execution Time: ${total_execution_time}ms"
echo "Overall Peak CPU Usage During Execution: ${overall_cpu_usage_factor}%"
echo "Overall CPU Usage Increment Factor: ${overall_cpu_usage_factor}"
echo "Total CPU Time: ${total_cpu_time}s"
echo "Maximum Memory Usage: ${total_max_memory}KB"
echo "-----------------------------"
