#!/usr/bin/env python3
"""
Python memory monitor with auto-kill functionality
Monitors a process and kills it if memory usage exceeds threshold
"""

import os
import sys
import time
import psutil
import subprocess
import signal
import argparse
import logging
from datetime import datetime

def setup_logging(log_file):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_process_memory(pid):
    """Get total memory usage of process and all its children"""
    try:
        process = psutil.Process(pid)
        total_memory = 0
        
        # Get memory of main process
        total_memory += process.memory_info().rss
        
        # Get memory of all child processes
        for child in process.children(recursive=True):
            try:
                total_memory += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return total_memory / 1024 / 1024  # Convert to MB
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0

def kill_process_tree(pid):
    """Kill process and all its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Terminate children first
        for child in children:
            try:
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Terminate parent
        parent.terminate()
        
        # Wait a bit, then force kill if still alive
        time.sleep(3)
        
        for child in children:
            try:
                if child.is_running():
                    child.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if parent.is_running():
            parent.kill()
            
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def monitor_and_run(command, max_memory_mb=4000, check_interval=10, 
                   kill_threshold=0.9, log_file="memory_monitor.log"):
    """Run command with memory monitoring"""
    
    setup_logging(log_file)
    
    kill_threshold_mb = max_memory_mb * kill_threshold
    
    logging.info(f"Starting memory-monitored execution")
    logging.info(f"Command: {' '.join(command)}")
    logging.info(f"Max memory: {max_memory_mb}MB")
    logging.info(f"Kill threshold: {kill_threshold_mb:.1f}MB")
    logging.info(f"Check interval: {check_interval}s")
    
    # Start the process
    try:
        process = subprocess.Popen(command)
        pid = process.pid
        logging.info(f"Started process with PID: {pid}")
        
        # Monitor memory usage
        while process.poll() is None:  # While process is still running
            try:
                current_memory = get_process_memory(pid)
                logging.info(f"Memory usage: {current_memory:.1f}MB / {max_memory_mb}MB")
                
                if current_memory > kill_threshold_mb:
                    logging.error(f"MEMORY THRESHOLD EXCEEDED!")
                    logging.error(f"Current: {current_memory:.1f}MB, Threshold: {kill_threshold_mb:.1f}MB")
                    logging.error(f"Killing process tree...")
                    
                    if kill_process_tree(pid):
                        logging.error("Process killed due to excessive memory usage")
                    else:
                        logging.error("Failed to kill process")
                    
                    return 1  # Return error code
                
                time.sleep(check_interval)
                
            except Exception as e:
                logging.warning(f"Error monitoring process: {e}")
                time.sleep(check_interval)
        
        # Process completed normally
        exit_code = process.returncode
        logging.info(f"Process completed with exit code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logging.error(f"Error starting process: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='Run command with memory monitoring')
    parser.add_argument('--max-memory', type=int, default=4000,
                       help='Maximum memory in MB (default: 4000)')
    parser.add_argument('--check-interval', type=int, default=10,
                       help='Check interval in seconds (default: 10)')
    parser.add_argument('--kill-threshold', type=float, default=0.9,
                       help='Kill threshold as fraction of max memory (default: 0.9)')
    parser.add_argument('--log-file', default='memory_monitor.log',
                       help='Log file name (default: memory_monitor.log)')
    parser.add_argument('command', nargs='+',
                       help='Command to execute')
    
    args = parser.parse_args()
    
    exit_code = monitor_and_run(
        command=args.command,
        max_memory_mb=args.max_memory,
        check_interval=args.check_interval,
        kill_threshold=args.kill_threshold,
        log_file=args.log_file
    )
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
