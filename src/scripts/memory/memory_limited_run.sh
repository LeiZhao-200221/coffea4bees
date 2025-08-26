#!/bin/bash
#
# Memory-limited job wrapper for HH4b analysis
# Monitors memory usage and kills the job if it exceeds threshold
#

# Default settings
MAX_MEMORY_MB=2000  # Much lower default - 2GB 
CHECK_INTERVAL=2    # Check every 2 seconds (much faster)
KILL_THRESHOLD=0.8  # Kill at 80% of max memory (much more aggressive)
LOG_FILE="memory_monitor.log"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --max-memory)
            MAX_MEMORY_MB="$2"
            shift 2
            ;;
        --check-interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        --kill-threshold)
            KILL_THRESHOLD="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            break
            ;;
    esac
done

# The actual command to run
COMMAND="$@"

if [ -z "$COMMAND" ]; then
    echo "Usage: $0 [--max-memory MB] [--check-interval SEC] [--log-file FILE] [--kill-threshold RATIO] -- COMMAND"
    echo "Example: $0 --max-memory 4000 -- python your_script.py"
    exit 1
fi

echo "Starting memory-limited execution" | tee -a "$LOG_FILE"
echo "Max memory: ${MAX_MEMORY_MB}MB" | tee -a "$LOG_FILE"
echo "Kill threshold: $(echo "$KILL_THRESHOLD * $MAX_MEMORY_MB" | bc)MB" | tee -a "$LOG_FILE"
echo "Command: $COMMAND" | tee -a "$LOG_FILE"
echo "Started at: $(date)" | tee -a "$LOG_FILE"

# Start the command in background
$COMMAND &
MAIN_PID=$!

# Function to get memory usage of process and its children
get_memory_usage() {
    local pid=$1
    local total_memory=0
    
    # Get all child processes
    local pids=$(pstree -p $pid 2>/dev/null | grep -o '([0-9]\+)' | grep -o '[0-9]\+' | sort -u)
    
    for p in $pids; do
        if [ -d "/proc/$p" ]; then
            # Get RSS (Resident Set Size) in KB
            local mem=$(cat /proc/$p/status 2>/dev/null | grep VmRSS | awk '{print $2}')
            if [ ! -z "$mem" ]; then
                total_memory=$((total_memory + mem))
            fi
        fi
    done
    
    # Convert KB to MB
    echo $((total_memory / 1024))
}

# Monitor memory usage
monitor_memory() {
    local kill_threshold_mb=$(echo "$KILL_THRESHOLD * $MAX_MEMORY_MB" | bc | cut -d. -f1)
    
    while kill -0 $MAIN_PID 2>/dev/null; do
        local current_memory=$(get_memory_usage $MAIN_PID)
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

        # Only log to file, not to stdout to avoid mixing with process output
        echo "$timestamp: Memory usage: ${current_memory}MB / ${MAX_MEMORY_MB}MB" >> "$LOG_FILE"

        if [ $current_memory -gt $kill_threshold_mb ]; then
            echo "" # Add newline to separate from process output
            echo "========================================" | tee -a "$LOG_FILE"
            echo "$timestamp: MEMORY THRESHOLD EXCEEDED!" | tee -a "$LOG_FILE"
            echo "$timestamp: Current: ${current_memory}MB, Threshold: ${kill_threshold_mb}MB" | tee -a "$LOG_FILE"
            echo "========================================" | tee -a "$LOG_FILE"
            
            # Kill the entire process tree
            pkill -TERM -P $MAIN_PID
            sleep 5
            pkill -KILL -P $MAIN_PID
            kill -KILL $MAIN_PID 2>/dev/null
            
            echo "$timestamp: Process killed due to excessive memory usage" | tee -a "$LOG_FILE"
            exit 1
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# Start monitoring in background
monitor_memory &
MONITOR_PID=$!

# Wait for the main command to complete
wait $MAIN_PID
EXIT_CODE=$?

# Kill the monitor
kill $MONITOR_PID 2>/dev/null

echo "Finished at: $(date)" | tee -a "$LOG_FILE"
echo "Exit code: $EXIT_CODE" | tee -a "$LOG_FILE"

exit $EXIT_CODE
