"""
Test script to verify file-based storage integration works correctly.
"""

import os
import json
from file_storage import get_storage, store_result

def test_file_storage():
    """Test the file storage functionality."""
    
    print("🧪 Testing file-based storage...")
    
    # Test storing different types of data
    test_cases = [
        {
            "data": {"username": "testuser", "karma": 1000, "created_utc": 1234567890},
            "data_type": "user",
            "identifier": "testuser"
        },
        {
            "data": {"subreddit": "python", "posts": [{"title": "Test Post", "score": 100}]},
            "data_type": "post",
            "identifier": "python_week"
        },
        {
            "data": {"display_name": "MachineLearning", "subscribers": 50000},
            "data_type": "subreddit",
            "identifier": "MachineLearning"
        }
    ]
    
    stored_files = []
    
    for test_case in test_cases:
        print(f"  📁 Testing {test_case['data_type']} storage...")
        
        # Store the data
        file_path = store_result(
            test_case["data"], 
            test_case["data_type"], 
            test_case["identifier"]
        )
        
        if file_path:
            stored_files.append(file_path)
            print(f"    ✅ Stored to: {file_path}")
            
            # Verify the file exists and contains correct data
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    stored_data = json.load(f)
                    
                # Check structure
                assert "stored_at" in stored_data
                assert "data_type" in stored_data
                assert "identifier" in stored_data
                assert "data" in stored_data
                
                # Check data integrity
                assert stored_data["data_type"] == test_case["data_type"]
                assert stored_data["identifier"] == test_case["identifier"]
                assert stored_data["data"] == test_case["data"]
                
                print(f"    ✅ Data integrity verified")
            else:
                print(f"    ❌ File not found: {file_path}")
        else:
            print(f"    ❌ Failed to store {test_case['data_type']} data")
    
    # Test storage statistics
    print("\n📊 Testing storage statistics...")
    storage = get_storage()
    stats = storage.get_stats()
    
    print(f"  Base directory: {stats['base_directory']}")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Files by type: {stats['by_type']}")
    
    # Cleanup test files
    print("\n🧹 Cleaning up test files...")
    for file_path in stored_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  🗑️  Removed: {file_path}")
    
    print("\n🎉 All tests passed! File storage is working correctly.")

if __name__ == "__main__":
    test_file_storage()
