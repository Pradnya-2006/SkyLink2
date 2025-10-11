"""
SkyLink System Demo - Complete Feature Showcase

This script demonstrates all the capabilities of the SkyLink collision detection system.
"""

import pandas as pd
from datetime import datetime
import os


def show_system_capabilities():
    """
    Display all available system capabilities and run a comprehensive demo.
    """
    print("🚁✈️ SkyLink Collision Detection System - Complete Demo")
    print("="*70)
    
    # System info
    print("📊 SYSTEM OVERVIEW:")
    print("   • Real-time collision detection between drones and aircraft")
    print("   • Interactive map visualization with Folium")
    print("   • Multiple output formats (JSON, CSV, HTML maps)")
    print("   • Configurable distance thresholds")
    print("   • Geographic and altitude filtering")
    print("   • Performance optimization for large datasets")
    print()
    
    # Check data availability
    print("📁 DATA STATUS:")
    plane_file = "plane_data/opensky_live_states.csv"
    drone_file = "drone_data/dummy_drone_dataset_30.csv"
    
    if os.path.exists(plane_file):
        planes_df = pd.read_csv(plane_file)
        print(f"   ✅ Plane data: {len(planes_df):,} records loaded")
    else:
        print("   ❌ Plane data file not found")
        
    if os.path.exists(drone_file):
        drones_df = pd.read_csv(drone_file)
        print(f"   ✅ Drone data: {len(drones_df):,} records loaded")
    else:
        print("   ❌ Drone data file not found")
    print()
    
    # Available scripts
    print("🛠️ AVAILABLE ANALYSIS TOOLS:")
    print("   1. main.py                - Full system analysis (use for small datasets)")
    print("   2. fast_main.py          - Optimized for large datasets")
    print("   3. regional_analysis.py  - Regional focused analysis")
    print("   4. demo.py               - Custom threshold demonstrations")
    print("   5. config.py             - System configuration settings")
    print()
    
    # Usage examples
    print("💡 USAGE EXAMPLES:")
    print("   Basic analysis:")
    print("   > python main.py")
    print()
    print("   Fast analysis for large datasets:")
    print("   > python fast_main.py")
    print()
    print("   Regional analysis:")
    print("   > python regional_analysis.py")
    print()
    print("   Custom demonstrations:")
    print("   > python demo.py")
    print()
    
    # Output files info
    print("📄 OUTPUT FILES GENERATED:")
    if os.path.exists("outputs"):
        output_files = os.listdir("outputs")
        if output_files:
            print(f"   Found {len(output_files)} output files:")
            for file in sorted(output_files)[-5:]:  # Show last 5 files
                print(f"   • {file}")
            if len(output_files) > 5:
                print(f"   ... and {len(output_files) - 5} more files")
        else:
            print("   No output files found - run analysis to generate results")
    print()
    
    # Performance stats
    print("⚡ PERFORMANCE OPTIMIZATION FEATURES:")
    print("   • Geographic bounds filtering")
    print("   • Altitude range filtering") 
    print("   • Data sampling for large datasets")
    print("   • Efficient distance calculations")
    print("   • Batch processing capabilities")
    print()
    
    # Visualization features
    print("🗺️ VISUALIZATION FEATURES:")
    print("   • Interactive Folium maps")
    print("   • Color-coded aircraft markers")
    print("   • Collision alert highlighting")
    print("   • Multiple map tile layers")
    print("   • Detailed popup information")
    print("   • Connection lines between conflicting aircraft")
    print()
    
    return True


def run_quick_demo():
    """
    Run a quick demonstration of the system.
    """
    print("🚀 RUNNING QUICK DEMO...")
    print("-" * 40)
    
    try:
        # Import and run fast analysis
        from regional_analysis import analyze_region
        
        print("Running optimized collision detection...")
        results = analyze_region(
            region_key='new_york',
            altitude_limit=500,
            h_threshold=0.3,
            v_threshold=75,
            max_samples=50
        )
        
        print("\n✅ Demo completed successfully!")
        print(f"Generated files in outputs/ directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def main():
    """
    Main demo function.
    """
    show_system_capabilities()
    
    print("🎯 QUICK DEMO:")
    print("Running a quick demonstration with sample data...")
    print()
    
    success = run_quick_demo()
    
    if success:
        print("\n" + "="*70)
        print("🎉 SKYLINK SYSTEM DEMO COMPLETED!")
        print("="*70)
        print("The system is ready for production use.")
        print("Check the outputs/ directory for generated maps and data files.")
        print()
        print("For more advanced usage:")
        print("• Modify thresholds in config.py")
        print("• Use different analysis scripts for various scenarios")
        print("• Integrate with real-time data feeds")
        print("• Scale up with cloud computing resources")
    else:
        print("\n❌ Demo encountered issues. Please check your data files.")


if __name__ == "__main__":
    main()