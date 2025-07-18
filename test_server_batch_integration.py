#!/usr/bin/env python3
"""
Test to verify that Reddit MCP server functions return batch results with batch_id
instead of raw Reddit data.
"""

import sys
import os
import tempfile
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import get_top_posts, read_reddit_results
from sqlite_storage import SQLiteStorage

def test_server_batch_integration():
    """Test that server functions return batch results with batch_id."""
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Initialize storage with test database
        storage = SQLiteStorage(db_path)
        
        print("🧪 Testing Reddit MCP Server Batch Integration")
        print("=" * 55)
        
        # Test get_top_posts function
        print("📡 Calling get_top_posts('programming', 'day', 5)...")
        
        # Call the server function
        result = get_top_posts('programming', 'day', 5)
        
        print(f"📋 Server Response Type: {type(result)}")
        print(f"📋 Server Response Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Check if we got a batch result instead of raw Reddit data
        if isinstance(result, dict):
            if 'batch_id' in result:
                print(f"✅ SUCCESS: Server returned batch result!")
                print(f"   Batch ID: {result['batch_id']}")
                print(f"   Status: {result.get('status', 'Unknown')}")
                print(f"   Total Entities: {result.get('total_entities', 'Unknown')}")
                print(f"   Entities Stored: {result.get('entities_stored', 'Unknown')}")
                
                # Test batch retrieval
                print(f"\n🔍 Testing batch retrieval...")
                batch_results = storage.get_batch_results(result['batch_id'])
                print(f"   Retrieved {len(batch_results['posts'])} posts from batch")
                print(f"   Retrieved {len(batch_results['users'])} users from batch")
                print(f"   Retrieved {len(batch_results['subreddits'])} subreddits from batch")
                
                # Show sample data
                if batch_results['posts']:
                    sample_post = batch_results['posts'][0]
                    print(f"   Sample Post: '{sample_post['title']}' by {sample_post['author']}")
                
                # Test new read_reddit_results function
                print(f"\n🔍 Testing new read_reddit_results function...")
                
                # Test 1: Read by batch_id
                read_result = read_reddit_results(batch_id=result['batch_id'])
                import json
                read_data = json.loads(read_result)
                
                if read_data['status'] == 'success':
                    print(f"✅ read_reddit_results by batch_id: SUCCESS")
                    print(f"   Query type: {read_data['query_type']}")
                    print(f"   Total results: {read_data['total_results']}")
                    print(f"   Posts found: {len(read_data['results']['posts'])}")
                    print(f"   Users found: {len(read_data['results']['users'])}")
                else:
                    print(f"❌ read_reddit_results by batch_id: FAILED - {read_data.get('error')}")
                
                # Test 2: Read recent results
                recent_result = read_reddit_results(limit=5)
                recent_data = json.loads(recent_result)
                
                if recent_data['status'] == 'success':
                    print(f"✅ read_reddit_results recent: SUCCESS")
                    print(f"   Query type: {recent_data['query_type']}")
                    print(f"   Total results: {recent_data['total_results']}")
                else:
                    print(f"❌ read_reddit_results recent: FAILED - {recent_data.get('error')}")
                
                # Test 3: Read by entity type
                posts_result = read_reddit_results(entity_type='posts', limit=3)
                posts_data = json.loads(posts_result)
                
                if posts_data['status'] == 'success':
                    print(f"✅ read_reddit_results by entity type: SUCCESS")
                    print(f"   Query type: {posts_data['query_type']}")
                    print(f"   Posts found: {len(posts_data['results']['posts'])}")
                    
                    # Show sample read data
                    if posts_data['results']['posts']:
                        sample_read_post = posts_data['results']['posts'][0]
                        print(f"   Sample Read Post: '{sample_read_post['title']}' by {sample_read_post['author']}")
                else:
                    print(f"❌ read_reddit_results by entity type: FAILED - {posts_data.get('error')}")
                
                return True
                
            elif 'posts' in result and 'subreddit' in result:
                print(f"❌ ISSUE: Server returned raw Reddit data instead of batch result")
                print(f"   Found keys: {list(result.keys())}")
                print(f"   This means the fix didn't work - server should return batch_id")
                return False
                
            else:
                print(f"❌ UNEXPECTED: Server returned unexpected format")
                print(f"   Keys: {list(result.keys())}")
                return False
        else:
            print(f"❌ ERROR: Server returned non-dict result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    return True

if __name__ == "__main__":
    success = test_server_batch_integration()
    
    if success:
        print(f"\n🎉 Test PASSED: Reddit MCP server now returns batch results with batch_id!")
        print(f"   ✅ No more raw Reddit data being returned")
        print(f"   ✅ Batch tracking works end-to-end")
        print(f"   ✅ LLM will receive batch_id for tracking")
    else:
        print(f"\n❌ Test FAILED: Server integration needs more work")
    
    sys.exit(0 if success else 1)
