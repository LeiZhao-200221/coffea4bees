#!/usr/bin/env python3
"""
Memory debugging script for HH4b processor
"""

import psutil
import os
import sys
import time
import logging
from contextlib import contextmanager
import tracemalloc
import gc
import numpy as np
import awkward as ak

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryMonitor:
    """Monitor memory usage at different stages of processing"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.get_memory_usage()
        self.checkpoints = {}
        
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
        }
    
    def checkpoint(self, name):
        """Record memory usage at a checkpoint"""
        current_memory = self.get_memory_usage()
        memory_diff = {
            'rss': current_memory['rss'] - self.baseline_memory['rss'],
            'vms': current_memory['vms'] - self.baseline_memory['vms'],
        }
        
        self.checkpoints[name] = {
            'absolute': current_memory,
            'diff_from_baseline': memory_diff,
            'timestamp': time.time()
        }
        
        logger.info(f"MEMORY [{name}]: RSS={current_memory['rss']:.1f}MB (+{memory_diff['rss']:.1f}MB), "
                   f"VMS={current_memory['vms']:.1f}MB (+{memory_diff['vms']:.1f}MB)")
        
        # Force garbage collection and log if it helps
        collected = gc.collect()
        if collected > 0:
            after_gc = self.get_memory_usage()
            gc_savings = current_memory['rss'] - after_gc['rss']
            if gc_savings > 10:  # Only log if significant
                logger.info(f"GC collected {collected} objects, saved {gc_savings:.1f}MB")
    
    @contextmanager
    def trace_memory_block(self, block_name):
        """Context manager to trace memory usage in a code block"""
        self.checkpoint(f"{block_name}_start")
        yield
        self.checkpoint(f"{block_name}_end")
        
        start_mem = self.checkpoints[f"{block_name}_start"]['absolute']['rss']
        end_mem = self.checkpoints[f"{block_name}_end"]['absolute']['rss']
        block_usage = end_mem - start_mem
        
        if abs(block_usage) > 5:  # Only log significant changes
            logger.info(f"BLOCK [{block_name}]: Memory change = {block_usage:+.1f}MB")
    
    def get_largest_objects(self, limit=10):
        """Get the largest objects in memory"""
        try:
            import gc
            objects = gc.get_objects()
            
            # Calculate sizes
            object_sizes = []
            for obj in objects:
                try:
                    size = sys.getsizeof(obj)
                    if hasattr(obj, '__len__'):
                        try:
                            length = len(obj)
                            if isinstance(obj, (np.ndarray, ak.Array)):
                                if isinstance(obj, np.ndarray):
                                    size = obj.nbytes
                                elif isinstance(obj, ak.Array):
                                    size = ak.nbytes(obj)
                            object_sizes.append((type(obj).__name__, size, length))
                        except:
                            object_sizes.append((type(obj).__name__, size, 'N/A'))
                    else:
                        object_sizes.append((type(obj).__name__, size, 'N/A'))
                except:
                    continue
            
            # Sort by size and get top objects
            object_sizes.sort(key=lambda x: x[1], reverse=True)
            
            logger.info("Largest objects in memory:")
            for i, (obj_type, size, length) in enumerate(object_sizes[:limit]):
                size_mb = size / 1024 / 1024
                logger.info(f"  {i+1}. {obj_type}: {size_mb:.1f}MB (length: {length})")
                
        except Exception as e:
            logger.warning(f"Could not analyze objects: {e}")
    
    def summary(self):
        """Print summary of memory usage"""
        logger.info("\n" + "="*60)
        logger.info("MEMORY USAGE SUMMARY")
        logger.info("="*60)
        
        for name, data in self.checkpoints.items():
            logger.info(f"{name:25s}: {data['absolute']['rss']:8.1f}MB "
                       f"(+{data['diff_from_baseline']['rss']:+6.1f}MB)")
        
        logger.info("="*60)

def trace_memory_hotspots():
    """Use tracemalloc to find memory hotspots"""
    tracemalloc.start()
    
    # This should be called after your processing
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    logger.info("\nTop 10 memory allocations:")
    for index, stat in enumerate(top_stats[:10], 1):
        logger.info(f"{index}. {stat}")

def analyze_awkward_arrays(event):
    """Analyze awkward array sizes in the event"""
    logger.info("\nAnalyzing awkward arrays in event:")
    
    total_size = 0
    for field in event.fields:
        try:
            obj = event[field]
            if isinstance(obj, ak.Array):
                size = ak.nbytes(obj)
                size_mb = size / 1024 / 1024
                total_size += size
                if size_mb > 1:  # Only log arrays > 1MB
                    logger.info(f"  {field}: {size_mb:.1f}MB")
        except Exception as e:
            logger.warning(f"Could not analyze field {field}: {e}")
    
    total_mb = total_size / 1024 / 1024
    logger.info(f"Total awkward array size: {total_mb:.1f}MB")
    return total_mb

# Example usage in processor
def debug_processor_memory(processor_instance, event):
    """Debug memory usage in processor"""
    monitor = MemoryMonitor()
    
    try:
        # Monitor different processing stages
        monitor.checkpoint("start_processing")
        
        with monitor.trace_memory_block("event_selection"):
            # Your event selection code here
            pass
        
        with monitor.trace_memory_block("friend_trees"):
            # Friend tree loading
            pass
        
        with monitor.trace_memory_block("jet_corrections"):
            # Jet corrections
            pass
        
        with monitor.trace_memory_block("object_selection"):
            # Object selection
            pass
        
        with monitor.trace_memory_block("btag_weights"):
            # B-tag weight calculation
            pass
        
        with monitor.trace_memory_block("combinatorics"):
            # Jet combinatorics
            pass
        
        with monitor.trace_memory_block("histograms"):
            # Histogram filling
            pass
        
        monitor.checkpoint("end_processing")
        
        # Analyze large objects
        monitor.get_largest_objects()
        
        # Analyze awkward arrays
        if 'event' in locals():
            analyze_awkward_arrays(event)
        
        # Summary
        monitor.summary()
        
    except Exception as e:
        logger.error(f"Error during memory debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test the memory monitor
    monitor = MemoryMonitor()
    monitor.checkpoint("test")
    
    # Create some test arrays to see memory usage
    test_array = np.random.random((1000000, 10))
    monitor.checkpoint("after_numpy_array")
    
    del test_array
    monitor.checkpoint("after_deletion")
    
    monitor.summary()
