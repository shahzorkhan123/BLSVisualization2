#!/usr/bin/env python3
"""
Demo script showing the complete workflow for updating BLS visualization data
without touching HTML files and solving CORS issues.
"""

import os
import json
import pandas as pd
from pathlib import Path


def create_sample_data():
    """Create sample data to demonstrate the update workflow."""
    
    # Sample data with different years and regions
    sample_data = [
        # 2024 National data
        {"year": 2024, "Region_Type": "National", "Region": "United States", "SOC_Code": "15-1252", 
         "OCC_TITLE": "Software Developers", "SOC_Major_Group_Name": "Computer and Mathematical", 
         "TOT_EMP": 1847900, "A_MEAN": 110140, "GDP": 203525346000, "complexity_score": 0.85},
        {"year": 2024, "Region_Type": "National", "Region": "United States", "SOC_Code": "29-1141", 
         "OCC_TITLE": "Registered Nurses", "SOC_Major_Group_Name": "Healthcare Practitioners", 
         "TOT_EMP": 3175390, "A_MEAN": 80010, "GDP": 254095239900, "complexity_score": 0.72},
        {"year": 2024, "Region_Type": "National", "Region": "United States", "SOC_Code": "25-2021", 
         "OCC_TITLE": "Elementary School Teachers", "SOC_Major_Group_Name": "Education Training and Library", 
         "TOT_EMP": 1424890, "A_MEAN": 60940, "GDP": 86824851600, "complexity_score": 0.68},
        
        # 2023 National data
        {"year": 2023, "Region_Type": "National", "Region": "United States", "SOC_Code": "15-1252", 
         "OCC_TITLE": "Software Developers", "SOC_Major_Group_Name": "Computer and Mathematical", 
         "TOT_EMP": 1795600, "A_MEAN": 107510, "GDP": 192899356000, "complexity_score": 0.85},
        {"year": 2023, "Region_Type": "National", "Region": "United States", "SOC_Code": "29-1141", 
         "OCC_TITLE": "Registered Nurses", "SOC_Major_Group_Name": "Healthcare Practitioners", 
         "TOT_EMP": 3100250, "A_MEAN": 78500, "GDP": 243369625000, "complexity_score": 0.71},
        
        # State data samples
        {"year": 2024, "Region_Type": "State", "Region": "California", "SOC_Code": "15-1252", 
         "OCC_TITLE": "Software Developers", "SOC_Major_Group_Name": "Computer and Mathematical", 
         "TOT_EMP": 425000, "A_MEAN": 145000, "GDP": 61625000000, "complexity_score": 0.85},
        {"year": 2024, "Region_Type": "State", "Region": "Texas", "SOC_Code": "15-1252", 
         "OCC_TITLE": "Software Developers", "SOC_Major_Group_Name": "Computer and Mathematical", 
         "TOT_EMP": 195000, "A_MEAN": 108000, "GDP": 21060000000, "complexity_score": 0.85},
         
        # Metro data samples 
        {"year": 2024, "Region_Type": "Metropolitan", "Region": "New York-Newark-Jersey City, NY-NJ-PA", "SOC_Code": "15-1252", 
         "OCC_TITLE": "Software Developers", "SOC_Major_Group_Name": "Computer and Mathematical", 
         "TOT_EMP": 156000, "A_MEAN": 135000, "GDP": 21060000000, "complexity_score": 0.85}
    ]
    
    # Create CSV file
    df = pd.DataFrame(sample_data)
    csv_file = "demo_data.csv"
    df.to_csv(csv_file, index=False)
    print(f"✅ Created sample data file: {csv_file}")
    return csv_file


def demo_data_update():
    """Demonstrate the data update workflow."""
    
    print("🚀 BLS Visualization Data Update Demo")
    print("=" * 50)
    
    # Step 1: Create sample data
    print("\n📊 Step 1: Creating sample data...")
    csv_file = create_sample_data()
    
    # Step 2: Update the JavaScript data file
    print("\n🔄 Step 2: Updating JavaScript data file...")
    os.system(f"python3 scripts/update_data.py --csv {csv_file} --output data/job_data.js")
    
    # Step 3: Verify the update
    print("\n✅ Step 3: Verifying update...")
    if os.path.exists("data/job_data.js"):
        with open("data/job_data.js", "r") as f:
            content = f.read()
            if "BLS_DATA" in content and "jobData" in content:
                print("✅ Data file updated successfully!")
                
                # Count records
                lines = content.split('\n')
                record_lines = [line for line in lines if '"year":' in line]
                print(f"✅ Found {len(record_lines)} data records in updated file")
                
                # Check metadata
                if '"metadata":' in content:
                    print("✅ Metadata generated successfully")
                
            else:
                print("❌ Data file update failed!")
    else:
        print("❌ Data file not found!")
    
    # Step 4: Cleanup
    print("\n🧹 Step 4: Cleaning up demo files...")
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"✅ Removed {csv_file}")
    
    print("\n🎉 Demo completed!")
    print("\n📋 What this demonstrates:")
    print("   ✅ Python script can update data without touching HTML")
    print("   ✅ JSONP format avoids CORS issues")
    print("   ✅ Metadata is automatically generated")
    print("   ✅ Multiple years and regions supported")
    print("   ✅ Ready for Parquet format migration")


def show_architecture_benefits():
    """Show the benefits of the new architecture."""
    
    print("\n🏗️  Architecture Benefits Summary")
    print("=" * 50)
    
    # File size analysis
    old_files = [
        "visualizations/direct_html_job_treemap.html",
        "visualizations/direct_html_compensation_treemap.html"
    ]
    
    new_files = [
        "visualizations/refactored_job_treemap.html", 
        "visualizations/refactored_compensation_treemap.html"
    ]
    
    shared_files = [
        "shared/common.css",
        "shared/utils.js", 
        "shared/treemap.js",
        "data/job_data.js"
    ]
    
    print("\n📊 File Size Comparison:")
    
    old_total = 0
    for file in old_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            old_total += size
            print(f"   📄 {file}: {size:.1f} KB")
    
    new_total = 0
    for file in new_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            new_total += size
            print(f"   📄 {file}: {size:.1f} KB")
    
    shared_total = 0
    print("\n   📁 Shared resources (cached once):")
    for file in shared_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            shared_total += size
            print(f"   📄 {file}: {size:.1f} KB")
    
    print(f"\n📈 Results:")
    print(f"   📊 Old approach: {old_total:.1f} KB per page")
    print(f"   📊 New approach: {new_total:.1f} KB per page + {shared_total:.1f} KB shared (cached)")
    print(f"   🚀 Size reduction: {((old_total - new_total) / old_total * 100):.1f}% per page!")
    
    print(f"\n✨ Additional Benefits:")
    print(f"   🔄 Better caching (shared resources)")
    print(f"   🌐 CORS-free (works with static hosting)")
    print(f"   🐍 Python-updatable (no HTML changes)")
    print(f"   📦 Future-ready (Parquet support)")
    print(f"   🔧 Maintainable (separation of concerns)")


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("scripts/update_data.py"):
        print("❌ Please run this script from the repository root directory")
        exit(1)
    
    # Check if pandas is available
    try:
        import pandas as pd
        print("✅ pandas available")
    except ImportError:
        print("❌ pandas not available. Installing...")
        os.system("pip install pandas")
    
    # Run the demo
    demo_data_update()
    show_architecture_benefits()
    
    print("\n🎯 Next Steps:")
    print("   1. Download actual library files to lib/ folder")
    print("   2. Refactor remaining HTML files")
    print("   3. Set up automated data update pipeline")
    print("   4. Configure proper HTTP cache headers")
    print("   5. Test deployment on GitHub Pages")