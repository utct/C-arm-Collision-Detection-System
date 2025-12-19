#!/usr/bin/env python
"""
Simple results viewer - no external dependencies needed
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python view_results.py <results_file.json>")
    sys.exit(1)

results_file = Path(sys.argv[1])

with open(results_file, 'r') as f:
    result = json.load(f)

print("\n" + "="*80)
print("WORKSPACE ANALYSIS RESULTS")
print("="*80 + "\n")

print(f"Setup: {result.get('setup_name', 'N/A')}")
print(f"Intervention: {result.get('intervention_name', 'N/A')}")
print(f"DOF: {result.get('dof', 'N/A')}")
print(f"Samples: {result['num_samples']:,}")
print(f"Analysis Date: {result['timestamp']}\n")

stats = result['statistics']
print("="*80)
print("STATISTICS")
print("="*80)
print(f"  Total poses tested:     {stats['total']:>10,}")
print(f"  Collision-free poses:   {stats['collision_free']:>10,} ({stats['collision_free_percentage']:>6.2f}%)")
print(f"  Collision poses:        {stats['collision']:>10,} ({stats['collision_percentage']:>6.2f}%)\n")

breakdown = result['collision_breakdown']
print("="*80)
print("COLLISION BREAKDOWN")
print("="*80)
for component, count in breakdown.items():
    pct = 100 * count / stats['total'] if stats['total'] > 0 else 0
    print(f"  {component:20s}:   {count:>10,} ({pct:>6.2f}%)")

print("\n" + "="*80)
print("PERFORMANCE")
print("="*80)
print(f"  Analysis time:          {result['elapsed_time_seconds']:>10.1f} seconds")
print(f"  Processing rate:        {result['samples_per_second']:>10.1f} poses/second\n")

print("="*80 + "\n")

