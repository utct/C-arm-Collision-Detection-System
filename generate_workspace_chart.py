"""
Generate publication-quality bar chart for workspace analysis results
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def load_all_results():
    """Load all workspace analysis results from output directory"""
    results_dir = Path("workspace_analysis_output")
    results = []
    
    if not results_dir.exists():
        print(f"Error: {results_dir} not found")
        return results
    
    # Load all JSON files
    for json_file in sorted(results_dir.glob("*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                # Handle both single result and array of results
                if isinstance(data, list):
                    results.extend(data)
                    print(f"Loaded: {json_file.name} ({len(data)} interventions)")
                else:
                    results.append(data)
                    print(f"Loaded: {json_file.name}")
        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")
    
    return results

def create_workspace_chart(results, output_file="workspace_analysis_chart.png"):
    """Create bar chart of collision-free percentages by intervention"""
    
    if not results:
        print("No data to plot!")
        return
    
    # Extract data
    interventions = []
    percentages = []
    colors = []
    
    # Color scheme: green for safe zones, yellow-orange gradient for increasing collision risk
    color_map = {
        'PA': '#2ecc71',  # Green
        'AP': '#3498db',  # Blue
        'V1': '#9b59b6',  # Purple
        'V2': '#e67e22',  # Orange
        'Ver': '#e74c3c', # Red
        'Lat': '#f39c12'  # Yellow-orange
    }
    
    for result in results:
        intervention = result['intervention']
        intervention_name = result['intervention_name']
        pct = result['statistics']['collision_free_percentage']
        
        # Use shorter labels if we have multiple interventions
        if len(results) > 3:
            interventions.append(intervention)
        else:
            interventions.append(f"{intervention}\n({intervention_name})")
        percentages.append(pct)
        colors.append(color_map.get(intervention, '#95a5a6'))
    
    # Create figure with professional styling
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bars with appropriate width
    x = np.arange(len(interventions))
    bar_width = 0.6 if len(interventions) > 1 else 0.3
    bars = ax.bar(x, percentages, width=bar_width, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Customize axes
    ax.set_xlabel('Intervention Type', fontsize=13, fontweight='bold')
    ax.set_ylabel('Collision-Free Workspace (%)', fontsize=13, fontweight='bold')
    ax.set_title('C-arm Workspace Analysis: Collision-Free Percentage by Intervention',
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x)
    ax.set_xticklabels(interventions, fontsize=10)
    ax.set_ylim(0, 100)
    
    # Add grid for readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, linewidth=0.8)
    ax.set_axisbelow(True)
    
    # Add percentage labels on top of bars
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                f'{pct:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add reference line at 50%
    if len(interventions) > 0:
        ax.axhline(y=50, color='red', linestyle=':', linewidth=1.5, alpha=0.5, 
                   label='50% threshold')
        ax.legend(loc='upper right', fontsize=10)
    
    # Add sample size annotation
    num_samples = results[0]['num_samples']
    ax.text(0.02, 0.98, f'Sample size: {num_samples:,} random poses per intervention',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # Tight layout
    plt.tight_layout()
    
    # Save with high DPI for publication quality
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved to: {output_file}")
    print(f"  Resolution: 300 DPI (publication quality)")
    print(f"  Format: PNG")
    
    # Also show the plot
    plt.show()

def print_summary(results):
    """Print summary statistics"""
    if not results:
        return
    
    print("\n" + "="*70)
    print("WORKSPACE ANALYSIS SUMMARY")
    print("="*70)
    
    for result in results:
        intervention = result['intervention_name']
        pct = result['statistics']['collision_free_percentage']
        collision_free = result['statistics']['collision_free']
        total = result['statistics']['total']
        
        print(f"{intervention:25s}: {pct:5.1f}% collision-free ({collision_free}/{total})")
    
    print("="*70)

def main():
    print("="*70)
    print("WORKSPACE ANALYSIS CHART GENERATOR")
    print("="*70)
    
    # Load all results
    results = load_all_results()
    
    if not results:
        print("\nNo results found. Run workspace analysis first:")
        print("  python workspace_analysis.py --all-interventions")
        return
    
    print(f"\nFound {len(results)} intervention(s)")
    
    # Print summary
    print_summary(results)
    
    # Create chart
    print("\nGenerating chart...")
    create_workspace_chart(results)

if __name__ == "__main__":
    main()

