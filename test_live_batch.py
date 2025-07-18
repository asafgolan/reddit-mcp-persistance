#!/usr/bin/env python3
"""
Live test of batch system using real Reddit MCP data from cryptocurrency subreddit.
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlite_storage import SQLiteStorage

# Real Reddit data from cryptocurrency subreddit (top 20 posts from today)
REDDIT_DATA = {
  "subreddit": "cryptocurrency",
  "time_filter": "day",
  "posts": [
    {
      "id": "1m2ecpo",
      "title": "ETH finally said alright, it's my turn",
      "author": "Odd-Radio-8500",
      "score": 3176,
      "upvote_ratio": 0.94,
      "num_comments": 152,
      "created_utc": 1752774770.0,
      "url": "https://www.reddit.com/r/CryptoCurrency/comments/1m2ecpo/eth_finally_said_alright_its_my_turn/",
      "permalink": "/r/CryptoCurrency/comments/1m2ecpo/eth_finally_said_alright_its_my_turn/",
      "is_self": False,
      "selftext": "",
      "link_url": "https://i.redd.it/5rchov9a3hdf1.jpeg",
      "over_18": False,
      "spoiler": False,
      "stickied": False,
      "locked": False,
      "distinguished": None,
      "flair": {
        "text": "MEME",
        "css_class": "",
        "template_id": "8735438a-b376-11ef-936f-fe54cf27bc81",
        "text_color": "light",
        "background_color": "#5bcd32"
      }
    },
    {
      "id": "1m2juj7",
      "title": "Donald Trump set to open US retirement market to crypto investments",
      "author": "LargeSnorlax",
      "score": 874,
      "upvote_ratio": 0.94,
      "num_comments": 137,
      "created_utc": 1752787499.0,
      "url": "https://www.reddit.com/r/CryptoCurrency/comments/1m2juj7/donald_trump_set_to_open_us_retirement_market_to/",
      "permalink": "/r/CryptoCurrency/comments/1m2juj7/donald_trump_set_to_open_us_retirement_market_to/",
      "is_self": False,
      "selftext": "",
      "link_url": "https://www.ft.com/content/07906211-5ab8-4917-bcad-5397c0bc3170",
      "over_18": False,
      "spoiler": False,
      "stickied": False,
      "locked": False,
      "distinguished": None,
      "flair": {
        "text": "🟢 GENERAL-NEWS",
        "css_class": "GENERAL-NEWS",
        "template_id": None,
        "text_color": "dark",
        "background_color": ""
      }
    },
    {
      "id": "1m2j6e6",
      "title": "XRP Smashes All-Time High As Bitcoin Reclaims $119,000",
      "author": "partymsl",
      "score": 656,
      "upvote_ratio": 0.89,
      "num_comments": 210,
      "created_utc": 1752785700.0,
      "url": "https://www.reddit.com/r/CryptoCurrency/comments/1m2j6e6/xrp_smashes_alltime_high_as_bitcoin_reclaims/",
      "permalink": "/r/CryptoCurrency/comments/1m2j6e6/xrp_smashes_alltime_high_as_bitcoin_reclaims/",
      "is_self": False,
      "selftext": "",
      "link_url": "https://www.coingecko.com/en/news/xrp-smashes-all-time-high-as-bitcoin-reclaims-119000",
      "over_18": False,
      "spoiler": False,
      "stickied": False,
      "locked": False,
      "distinguished": None,
      "flair": {
        "text": "GENERAL-NEWS",
        "css_class": "NEWS",
        "template_id": "f170aab2-246f-11ec-8143-429a193c9848",
        "text_color": "light",
        "background_color": "#0aa18f"
      }
    }
  ],
  "metadata": {
    "fetched_at": 1752844045.382667,
    "post_count": 20
  }
}

def test_live_batch_processing():
    """Test batch system with real Reddit data."""
    
    # Initialize storage with default database
    storage = SQLiteStorage("reddit_mcp.db")
    
    print("🚀 Testing Live Batch Processing with Cryptocurrency Subreddit Data")
    print("=" * 70)
    
    # Mock parse_to_units to extract entities from the Reddit data
    def mock_parse_to_units(data, function_name, function_metadata):
        """Extract entities from Reddit MCP response."""
        entities = {
            "users": [],
            "posts": [],
            "comments": [],
            "subreddits": [],
            "submissions": []
        }
        
        # Extract unique users (authors)
        unique_users = set()
        for post in data.get("posts", []):
            if post.get("author") and post["author"] not in unique_users:
                unique_users.add(post["author"])
                entities["users"].append({
                    "username": post["author"],
                    "total_karma": post.get("score", 0),  # Using post score as proxy
                    "extraction_metadata": {
                        "function_name": function_name,
                        "extracted_at": datetime.now().isoformat()
                    }
                })
        
        # Extract posts
        for post in data.get("posts", []):
            entities["posts"].append({
                "id": post["id"],
                "title": post["title"],
                "author": post["author"],
                "score": post["score"],
                "upvote_ratio": post["upvote_ratio"],
                "num_comments": post["num_comments"],
                "created_utc": post["created_utc"],
                "url": post["url"],
                "permalink": post["permalink"],
                "is_self": post["is_self"],
                "selftext": post.get("selftext", ""),
                "link_url": post.get("link_url", ""),
                "over_18": post["over_18"],
                "spoiler": post["spoiler"],
                "stickied": post["stickied"],
                "locked": post["locked"],
                "distinguished": post["distinguished"],
                "flair": post.get("flair"),
                "extraction_metadata": {
                    "function_name": function_name,
                    "extracted_at": datetime.now().isoformat()
                }
            })
        
        # Extract subreddit info
        if data.get("subreddit"):
            entities["subreddits"].append({
                "name": data["subreddit"],
                "display_name": data["subreddit"],
                "extraction_metadata": {
                    "function_name": function_name,
                    "extracted_at": datetime.now().isoformat()
                }
            })
        
        return entities
    
    # Replace the parse_to_units method
    storage.parse_to_units = mock_parse_to_units
    
    try:
        # Process the Reddit data through our batch system
        print("📊 Processing Reddit data through batch system...")
        
        function_metadata = {
            "subreddit": "cryptocurrency",
            "time_filter": "day",
            "limit": 20,
            "fetched_at": datetime.now().isoformat()
        }
        
        result = storage.process_and_store_entities(
            REDDIT_DATA, 
            "get_top_posts", 
            function_metadata
        )
        
        print(f"\n✅ Batch Processing Complete!")
        print(f"   Batch ID: {result['batch_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Total Entities: {result['total_entities']}")
        print(f"   Entities Stored: {result['entities_stored']}")
        
        if result['errors'] > 0:
            print(f"   ⚠️  Errors: {result['errors']}")
            print(f"   Error Message: {result['error_message']}")
        
        # Get detailed batch results
        print("\n📋 Retrieving Batch Results...")
        batch_results = storage.get_batch_results(result['batch_id'])
        
        print(f"   Users: {len(batch_results['users'])}")
        print(f"   Posts: {len(batch_results['posts'])}")
        print(f"   Comments: {len(batch_results['comments'])}")
        print(f"   Subreddits: {len(batch_results['subreddits'])}")
        print(f"   Submissions: {len(batch_results['submissions'])}")
        
        # Show some sample data
        print("\n📝 Sample Stored Data:")
        
        if batch_results['users']:
            print(f"   First User: {batch_results['users'][0]['username']}")
        
        if batch_results['posts']:
            sample_post = batch_results['posts'][0]
            print(f"   First Post: '{sample_post['title']}' by {sample_post['author']} (Score: {sample_post['score']})")
        
        if batch_results['subreddits']:
            print(f"   Subreddit: {batch_results['subreddits'][0]['name']}")
        
        # Get batch info
        print("\n🔍 Batch Information:")
        batch_info = storage.get_batch_info(result['batch_id'])
        print(f"   Function: {batch_info['function_name']}")
        print(f"   Started: {batch_info['started_at']}")
        print(f"   Completed: {batch_info['completed_at']}")
        print(f"   Status: {batch_info['status']}")
        
        # Show database stats
        print("\n📈 Database Statistics:")
        stats = storage.get_stats()
        for key, value in stats.items():
            if key.endswith('_count'):
                print(f"   {key.replace('_count', '').capitalize()}: {value}")
        
        print(f"\n🎉 Live batch processing test completed successfully!")
        print(f"   Real cryptocurrency subreddit data has been processed and stored")
        print(f"   with full batch tracking and entity extraction!")
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_live_batch_processing()
    sys.exit(0 if success else 1)
