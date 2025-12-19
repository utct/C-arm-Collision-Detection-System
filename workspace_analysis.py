#!/usr/bin/env python
"""
Surgical Workspace Analysis Tool
=================================

Generates random C-arm and patient table poses, checks collisions,
and calculates reachability statistics following the methodology from:

F. Jaheen, V. Gutta, and P. Fallavollita, "C-arm and Patient Table 
Integrated Kinematics and Surgical Workspace Analysis," IEEE Access, 2024.

This script analyzes the collision-free workspace for different DOF configurations
and clinical interventional projections.
"""

import numpy as np
import json
from pathlib import Path
import time
from datetime import datetime
from collision_server import CollisionServer
import argparse

# Clinical interventional configurations from research paper (Table VII)
CLINICAL_INTERVENTIONS = {
    'PA': {  # Posterior-Anterior
        'name': 'Posterior-Anterior',
        'orbital': 0.0,  # LAO/RAO
        'tilt': 180.0    # CRAN/CAUD
    },
    'AP': {  # Anterior-Posterior
        'name': 'Anterior-Posterior',
        'orbital': 0.0,
        'tilt': 0.0
    },
    'V1': {  # Vascular 1
        'name': 'Vascular 1',
        'orbital': -30.0,
        'tilt': 180.0
    },
    'V2': {  # Vascular 2
        'name': 'Vascular 2',
        'orbital': 45.0,
        'tilt': 205.0  # 180 + 25 CAUD
    },
    'Ver': {  # Vertebroplasty
        'name': 'Vertebroplasty',
        'orbital': -35.0,
        'tilt': 180.0
    },
    'Lat': {  # Lateral
        'name': 'Lateral',
        'orbital': -90.0,
        'tilt': 180.0
    }
}

# DOF configurations from research paper (Table VIII)
DOF_SETUPS = {
    'setup1': {
        'name': 'C-arm 5DOF (no lateral)',
        'movable_joints': ['vertical', 'wigwag', 'horizontal', 'tilt', 'orbital'],
        'fixed_joints': {'lateral': 0.0},
        'dof': 5
    },
    'setup2': {
        'name': 'C-arm 6DOF (all joints)',
        'movable_joints': ['lateral', 'vertical', 'wigwag', 'horizontal', 'tilt', 'orbital'],
        'fixed_joints': {},
        'dof': 6
    },
    'setup3': {
        'name': 'C-arm 6DOF + Table Transverse',
        'movable_joints': ['lateral', 'vertical', 'wigwag', 'horizontal', 'tilt', 'orbital', 'table_transverse'],
        'fixed_joints': {},
        'dof': 7
    },
    'setup4': {
        'name': 'C-arm 6DOF + Table Transverse + Vertical',
        'movable_joints': ['lateral', 'vertical', 'wigwag', 'horizontal', 'tilt', 'orbital', 
                          'table_vertical', 'table_transverse'],
        'fixed_joints': {},
        'dof': 8
    },
    'setup5': {
        'name': 'C-arm 6DOF + Table All (Vertical, Longitudinal, Transverse)',
        'movable_joints': ['lateral', 'vertical', 'wigwag', 'horizontal', 'tilt', 'orbital',
                          'table_vertical', 'table_longitudinal', 'table_transverse'],
        'fixed_joints': {},
        'dof': 9
    },
    'setup6': {
        'name': 'Table All (no C-arm movement)',
        'movable_joints': ['table_vertical', 'table_longitudinal', 'table_transverse'],
        'fixed_joints': {
            'lateral': 0.0, 'vertical': 0.2, 'wigwag': 0.0,
            'horizontal': 0.1, 'tilt': 180.0, 'orbital': 0.0
        },
        'dof': 3
    }
}

# Joint limits (from your implementation and research paper)
JOINT_LIMITS = {
    # C-arm joints
    'lateral': (-0.15, 0.15),      # meters
    'vertical': (0.0, 0.46),       # meters
    'wigwag': (-10.0, 10.0),       # degrees
    'horizontal': (0.0, 0.15),     # meters
    'tilt': (-90.0, 270.0),        # degrees (CRAN/CAUD)
    'orbital': (-100.0, 100.0),    # degrees (LAO/RAO)
    
    # Table joints
    'table_vertical': (0.0, 0.36),      # meters
    'table_longitudinal': (0.0, 0.7),   # meters
    'table_transverse': (-0.13, 0.13)   # meters
}


class WorkspaceAnalyzer:
    def __init__(self):
        print("="*80)
        print("SURGICAL WORKSPACE ANALYSIS TOOL")
        print("="*80)
        print("\nInitializing collision detection system...")
        self.collision_server = CollisionServer()
        print("\n[OK] Workspace analyzer ready\n")
        
    def generate_random_pose(self, movable_joints, fixed_joints, intervention_config=None):
        """
        Generate random joint configuration within limits.
        
        Args:
            movable_joints: List of joints that can vary
            fixed_joints: Dict of joints fixed to specific values
            intervention_config: Optional dict with 'orbital' and 'tilt' for clinical interventions
            
        Returns:
            Dict of joint values
        """
        pose = {}
        
        # Set fixed joints
        for joint, value in fixed_joints.items():
            pose[joint] = value
        
        # Set intervention-specific joints (orbital and tilt) if provided
        if intervention_config:
            pose['orbital'] = intervention_config['orbital']
            pose['tilt'] = intervention_config['tilt']
            # Remove from movable if they're fixed by intervention
            movable_joints = [j for j in movable_joints if j not in ['orbital', 'tilt']]
        
        # Generate random values for movable joints
        for joint in movable_joints:
            if joint in JOINT_LIMITS:
                min_val, max_val = JOINT_LIMITS[joint]
                pose[joint] = np.random.uniform(min_val, max_val)
        
        # Ensure all joints have values (default to 0 if not set)
        for joint in ['lateral', 'vertical', 'wigwag', 'horizontal', 'tilt', 'orbital',
                     'table_vertical', 'table_longitudinal', 'table_transverse']:
            if joint not in pose:
                pose[joint] = 0.0
        
        return pose
    
    def check_pose_collision(self, pose):
        """Check if a pose results in collision."""
        result = self.collision_server.check_collision(
            lao_rao_deg=pose['orbital'],
            cran_caud_deg=pose['tilt'],
            wigwag_deg=pose['wigwag'],
            lateral_m=pose['lateral'],
            vertical_m=pose['vertical'],
            horizontal_m=pose['horizontal'],
            table_vertical_m=pose['table_vertical'],
            table_longitudinal_m=pose['table_longitudinal'],
            table_transverse_m=pose['table_transverse']
        )
        return result['collision'], result['collision_points']
    
    def analyze_workspace(self, setup_name, intervention_name, num_samples=10000, verbose=True):
        """
        Analyze workspace for specific DOF setup and clinical intervention.
        
        Args:
            setup_name: Key from DOF_SETUPS
            intervention_name: Key from CLINICAL_INTERVENTIONS
            num_samples: Number of random poses to test
            verbose: Print progress
            
        Returns:
            Dict with analysis results
        """
        setup = DOF_SETUPS[setup_name]
        intervention = CLINICAL_INTERVENTIONS[intervention_name]
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"Analyzing: {setup['name']} ({setup['dof']} DOF)")
            print(f"Intervention: {intervention['name']}")
            print(f"Samples: {num_samples:,}")
            print(f"{'='*80}\n")
        
        # Statistics
        collision_free_count = 0
        collision_count = 0
        mixed_collision_count = 0  # Has some collision but not all components
        
        collision_free_poses = []
        collision_poses = []
        
        collision_details = {
            'table_top': 0,
            'table_body': 0,
            'table_base': 0,
            'patient': 0
        }
        
        start_time = time.time()
        
        # Generate and test random poses
        for i in range(num_samples):
            if verbose and (i % 1000 == 0 or i == num_samples - 1):
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta = (num_samples - i - 1) / rate if rate > 0 else 0
                print(f"  Progress: {i+1:,}/{num_samples:,} ({100*(i+1)/num_samples:.1f}%) | "
                      f"Rate: {rate:.1f} poses/s | ETA: {eta:.0f}s", end='\r')
            
            # Generate random pose
            pose = self.generate_random_pose(
                setup['movable_joints'],
                setup['fixed_joints'],
                intervention_config=intervention
            )
            
            # Check collision
            has_collision, points = self.check_pose_collision(pose)
            
            if has_collision:
                collision_count += 1
                collision_poses.append(pose)
                
                # Track which components are colliding
                for component in collision_details:
                    if points[component] > 0:
                        collision_details[component] += 1
            else:
                collision_free_count += 1
                collision_free_poses.append(pose)
        
        elapsed_time = time.time() - start_time
        
        if verbose:
            print()  # New line after progress
        
        # Calculate statistics
        total = collision_free_count + collision_count
        collision_free_percentage = 100 * collision_free_count / total if total > 0 else 0
        collision_percentage = 100 * collision_count / total if total > 0 else 0
        
        results = {
            'setup': setup_name,
            'setup_name': setup['name'],
            'dof': setup['dof'],
            'intervention': intervention_name,
            'intervention_name': intervention['name'],
            'intervention_config': intervention,
            'num_samples': num_samples,
            'elapsed_time_seconds': elapsed_time,
            'samples_per_second': num_samples / elapsed_time if elapsed_time > 0 else 0,
            'statistics': {
                'collision_free': collision_free_count,
                'collision': collision_count,
                'total': total,
                'collision_free_percentage': collision_free_percentage,
                'collision_percentage': collision_percentage
            },
            'collision_breakdown': {
                'table_top': collision_details['table_top'],
                'table_body': collision_details['table_body'],
                'table_base': collision_details['table_base'],
                'patient': collision_details['patient']
            },
            'timestamp': datetime.now().isoformat()
        }
        
        if verbose:
            self._print_results(results)
        
        return results, collision_free_poses, collision_poses
    
    def _print_results(self, results):
        """Print formatted analysis results."""
        print(f"\n{'='*80}")
        print(f"RESULTS: {results['setup_name']}")
        print(f"Intervention: {results['intervention_name']}")
        print(f"{'='*80}")
        
        stats = results['statistics']
        print(f"\n  Total poses tested:     {stats['total']:,}")
        print(f"  Collision-free:         {stats['collision_free']:,} ({stats['collision_free_percentage']:.2f}%)")
        print(f"  Collision:              {stats['collision']:,} ({stats['collision_percentage']:.2f}%)")
        
        print(f"\n  Collision breakdown:")
        breakdown = results['collision_breakdown']
        for component, count in breakdown.items():
            pct = 100 * count / stats['total'] if stats['total'] > 0 else 0
            print(f"    {component:20s}: {count:,} ({pct:.2f}%)")
        
        print(f"\n  Analysis time:          {results['elapsed_time_seconds']:.1f}s")
        print(f"  Processing rate:        {results['samples_per_second']:.1f} poses/second")
        print(f"{'='*80}\n")
    
    def compare_setups(self, intervention_name, num_samples=10000, setups=None):
        """
        Compare multiple DOF setups for a specific intervention.
        
        Args:
            intervention_name: Clinical intervention to analyze
            num_samples: Number of samples per setup
            setups: List of setup names (default: all setups)
            
        Returns:
            Dict with comparison results
        """
        if setups is None:
            setups = list(DOF_SETUPS.keys())
        
        print(f"\n{'='*80}")
        print(f"COMPARATIVE ANALYSIS")
        print(f"Intervention: {CLINICAL_INTERVENTIONS[intervention_name]['name']}")
        print(f"Setups: {len(setups)}")
        print(f"Samples per setup: {num_samples:,}")
        print(f"Total samples: {len(setups) * num_samples:,}")
        print(f"{'='*80}\n")
        
        comparison_results = []
        
        for setup_name in setups:
            results, _, _ = self.analyze_workspace(setup_name, intervention_name, num_samples)
            comparison_results.append(results)
        
        # Print comparison table
        self._print_comparison_table(comparison_results)
        
        return comparison_results
    
    def _print_comparison_table(self, results_list):
        """Print formatted comparison table."""
        print(f"\n{'='*80}")
        print("WORKSPACE COMPARISON")
        print(f"{'='*80}\n")
        
        # Header
        print(f"{'Setup':<50} {'DOF':>5} {'Collision-Free %':>18}")
        print(f"{'-'*50} {'-'*5} {'-'*18}")
        
        # Rows
        for result in results_list:
            setup_name = result['setup_name'][:48]
            dof = result['dof']
            pct = result['statistics']['collision_free_percentage']
            print(f"{setup_name:<50} {dof:>5} {pct:>17.2f}%")
        
        print(f"{'='*80}\n")
    
    def analyze_all_interventions(self, setup_name='setup5', num_samples=10000):
        """
        Analyze all clinical interventions for a specific setup.
        
        Args:
            setup_name: DOF setup to use
            num_samples: Number of samples per intervention
            
        Returns:
            List of results for each intervention
        """
        results = []
        
        for intervention_name in CLINICAL_INTERVENTIONS.keys():
            result, _, _ = self.analyze_workspace(setup_name, intervention_name, num_samples)
            results.append(result)
        
        # Print summary
        self._print_intervention_summary(results)
        
        return results
    
    def _print_intervention_summary(self, results_list):
        """Print summary of all interventions."""
        print(f"\n{'='*80}")
        print("INTERVENTION SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"{'Intervention':<30} {'Collision-Free %':>18} {'Sample Count':>15}")
        print(f"{'-'*30} {'-'*18} {'-'*15}")
        
        for result in results_list:
            name = result['intervention_name'][:28]
            pct = result['statistics']['collision_free_percentage']
            count = result['statistics']['collision_free']
            print(f"{name:<30} {pct:>17.2f}% {count:>15,}")
        
        print(f"{'='*80}\n")
    
    def save_results(self, results, filename='workspace_analysis_results.json'):
        """Save analysis results to JSON file."""
        output_dir = Path('workspace_analysis_output')
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n[SAVED] Results saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Surgical Workspace Analysis')
    parser.add_argument('--samples', type=int, default=10000,
                       help='Number of random poses to generate (default: 10000)')
    parser.add_argument('--setup', type=str, default='setup5',
                       choices=list(DOF_SETUPS.keys()),
                       help='DOF setup configuration (default: setup5 - 9 DOF)')
    parser.add_argument('--intervention', type=str, default='PA',
                       choices=list(CLINICAL_INTERVENTIONS.keys()),
                       help='Clinical intervention projection (default: PA)')
    parser.add_argument('--compare-setups', action='store_true',
                       help='Compare all DOF setups for selected intervention')
    parser.add_argument('--all-interventions', action='store_true',
                       help='Analyze all interventions for selected setup')
    parser.add_argument('--quick', action='store_true',
                       help='Quick test with 1000 samples')
    
    args = parser.parse_args()
    
    if args.quick:
        args.samples = 1000
        print("\n[QUICK MODE] Using 1000 samples for rapid testing\n")
    
    # Initialize analyzer
    analyzer = WorkspaceAnalyzer()
    
    # Run analysis based on mode
    if args.compare_setups:
        # Compare all setups for one intervention
        results = analyzer.compare_setups(args.intervention, args.samples)
        analyzer.save_results(results, f'comparison_{args.intervention}_{args.samples}_samples.json')
        
    elif args.all_interventions:
        # Analyze all interventions for one setup
        results = analyzer.analyze_all_interventions(args.setup, args.samples)
        analyzer.save_results(results, f'interventions_{args.setup}_{args.samples}_samples.json')
        
    else:
        # Single analysis
        results, collision_free_poses, collision_poses = analyzer.analyze_workspace(
            args.setup, args.intervention, args.samples
        )
        analyzer.save_results(results, f'{args.setup}_{args.intervention}_{args.samples}_samples.json')
    
    print("\n[COMPLETE] Workspace analysis finished!")


if __name__ == '__main__':
    main()




