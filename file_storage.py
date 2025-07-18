"""
Minimal file-based storage for Reddit MCP results.
Stores results as JSON files with no schema constraints.
Perfect for later NER extraction and analysis.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class FileStorage:
    """Simple file-based storage for Reddit data."""
    
    def __init__(self, base_dir: str = "reddit_data"):
        """Initialize file storage.
        
        Args:
            base_dir: Base directory for storing files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.base_dir / "posts").mkdir(exist_ok=True)
        (self.base_dir / "users").mkdir(exist_ok=True)
        (self.base_dir / "subreddits").mkdir(exist_ok=True)
        (self.base_dir / "submissions").mkdir(exist_ok=True)
    
    def _generate_filename(self, data_type: str, identifier: str) -> str:
        """Generate filename for storing data.
        
        Args:
            data_type: Type of data (post, user, subreddit, etc.)
            identifier: Unique identifier for the data
            
        Returns:
            Filename string
        """
        # Clean identifier for filename
        clean_id = "".join(c for c in identifier if c.isalnum() or c in '-_')
        timestamp = int(time.time())
        return f"{clean_id}_{timestamp}.json"
    
    def store_post_data(self, data: Dict[str, Any], post_id: Optional[str] = None) -> str:
        """Store post data to file.
        
        Args:
            data: Post data dictionary
            post_id: Optional post ID, will extract from data if not provided
            
        Returns:
            Path to stored file
        """
        # Extract post ID if not provided
        if not post_id:
            if 'posts' in data and len(data['posts']) > 0:
                post_id = data['posts'][0].get('id', 'unknown')
            else:
                post_id = data.get('id', 'unknown')
        
        filename = self._generate_filename("post", post_id)
        file_path = self.base_dir / "posts" / filename
        
        # Add metadata
        storage_data = {
            "stored_at": datetime.now().isoformat(),
            "data_type": "post",
            "identifier": post_id,
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
        
        return str(file_path)
    
    def store_user_data(self, data: Dict[str, Any], username: Optional[str] = None) -> str:
        """Store user data to file.
        
        Args:
            data: User data dictionary
            username: Optional username, will extract from data if not provided
            
        Returns:
            Path to stored file
        """
        # Extract username if not provided
        if not username:
            username = data.get('username', 'unknown')
        
        filename = self._generate_filename("user", username)
        file_path = self.base_dir / "users" / filename
        
        # Add metadata
        storage_data = {
            "stored_at": datetime.now().isoformat(),
            "data_type": "user",
            "identifier": username,
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
        
        return str(file_path)
    
    def store_subreddit_data(self, data: Dict[str, Any], subreddit: Optional[str] = None) -> str:
        """Store subreddit data to file.
        
        Args:
            data: Subreddit data dictionary
            subreddit: Optional subreddit name, will extract from data if not provided
            
        Returns:
            Path to stored file
        """
        # Extract subreddit name if not provided
        if not subreddit:
            subreddit = data.get('display_name', data.get('subreddit', 'unknown'))
        
        filename = self._generate_filename("subreddit", subreddit)
        file_path = self.base_dir / "subreddits" / filename
        
        # Add metadata
        storage_data = {
            "stored_at": datetime.now().isoformat(),
            "data_type": "subreddit",
            "identifier": subreddit,
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
        
        return str(file_path)
    
    def store_submission_data(self, data: Dict[str, Any], submission_id: Optional[str] = None) -> str:
        """Store submission data to file.
        
        Args:
            data: Submission data dictionary
            submission_id: Optional submission ID, will extract from data if not provided
            
        Returns:
            Path to stored file
        """
        # Extract submission ID if not provided
        if not submission_id:
            submission_id = data.get('id', 'unknown')
        
        filename = self._generate_filename("submission", submission_id)
        file_path = self.base_dir / "submissions" / filename
        
        # Add metadata
        storage_data = {
            "stored_at": datetime.now().isoformat(),
            "data_type": "submission",
            "identifier": submission_id,
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
        
        return str(file_path)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            "base_directory": str(self.base_dir),
            "total_files": 0,
            "by_type": {}
        }
        
        for subdir in ["posts", "users", "subreddits", "submissions"]:
            path = self.base_dir / subdir
            if path.exists():
                file_count = len(list(path.glob("*.json")))
                stats["by_type"][subdir] = file_count
                stats["total_files"] += file_count
        
        return stats


# Global storage instance
_storage = None

def get_storage() -> FileStorage:
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        _storage = FileStorage()
    return _storage


def store_result(data: Dict[str, Any], data_type: str, identifier: Optional[str] = None) -> Optional[str]:
    """Helper function to store result data.
    
    Args:
        data: Data to store
        data_type: Type of data (post, user, subreddit, submission)
        identifier: Optional identifier
        
    Returns:
        Path to stored file or None if error
    """
    try:
        storage = get_storage()
        
        if data_type == "post":
            return storage.store_post_data(data, identifier)
        elif data_type == "user":
            return storage.store_user_data(data, identifier)
        elif data_type == "subreddit":
            return storage.store_subreddit_data(data, identifier)
        elif data_type == "submission":
            return storage.store_submission_data(data, identifier)
        else:
            # Generic storage
            filename = storage._generate_filename(data_type, identifier or "unknown")
            file_path = storage.base_dir / f"{data_type}s" / filename
            file_path.parent.mkdir(exist_ok=True)
            
            storage_data = {
                "stored_at": datetime.now().isoformat(),
                "data_type": data_type,
                "identifier": identifier,
                "data": data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
            
            return str(file_path)
    
    except Exception as e:
        print(f"Error storing {data_type} data: {e}")
        return None
