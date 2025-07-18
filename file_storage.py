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

# Import response schemas as single source of truth
from response_schemas import extract_entities_from_response, get_schema_for_function


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
        (self.base_dir / "comments").mkdir(exist_ok=True)
    
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
            "total_files": 0,
            "posts": 0,
            "users": 0,
            "subreddits": 0,
            "submissions": 0
        }
        
        for subdir in ["posts", "users", "subreddits", "submissions"]:
            path = self.base_dir / subdir
            if path.exists():
                files = list(path.glob("*.json"))
                stats[subdir] = len(files)
                stats["total_files"] += len(files)
        
        return stats
    
    def parse_to_units(self, data: Dict[str, Any], function_name: str, function_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse response data to extract individual entities based on function type.
        
        Uses response_schemas.py as single source of truth for response structures.
        
        Args:
            data: Response data from the MCP function
            function_name: Name of the function that generated the response
            function_metadata: Optional metadata about the function call
            
        Returns:
            Dictionary with extracted entities organized by type
        """
        # Use schema-based extraction as single source of truth
        try:
            extracted_units = extract_entities_from_response(data, function_name)
            
            # Add function metadata to all extracted units
            if function_metadata:
                for entity_type in extracted_units:
                    for entity in extracted_units[entity_type]:
                        if isinstance(entity, dict):
                            entity["extraction_metadata"] = {
                                "function_name": function_name,
                                "extracted_at": datetime.now().isoformat(),
                                "function_metadata": function_metadata
                            }
            
            return extracted_units
            
        except Exception as e:
            # Fallback to basic extraction if schema processing fails
            return {
                "users": [],
                "posts": [],
                "comments": [],
                "subreddits": [],
                "submissions": [],
                "extraction_errors": [{
                    "error": str(e),
                    "function_name": function_name,
                    "raw_data": data
                }]
            }
    
    def store_extracted_units(self, extracted_units: Dict[str, Any], function_name: str, function_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
        """Store each extracted entity as its own file.
        
        Args:
            extracted_units: Dictionary of extracted entities organized by type
            function_name: Name of the function that generated the response
            function_metadata: Optional metadata about the function call
            
        Returns:
            Dictionary with count of stored files per entity type
        """
        stored_counts = {
            "users": 0,
            "posts": 0,
            "comments": 0,
            "subreddits": 0,
            "submissions": 0,
            "errors": 0
        }
        
        # Store users
        for user in extracted_units.get("users", []):
            try:
                username = user.get("username", "unknown")
                filename = self._generate_filename("user", username)
                file_path = self.base_dir / "users" / filename
                
                # Add storage metadata
                storage_data = {
                    "stored_at": datetime.now().isoformat(),
                    "entity_type": "user",
                    "identifier": username,
                    "source_function": function_name,
                    "function_metadata": function_metadata,
                    "data": user
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
                
                stored_counts["users"] += 1
            except Exception as e:
                print(f"Error storing user {user.get('username', 'unknown')}: {e}")
                stored_counts["errors"] += 1
        
        # Store posts
        for post in extracted_units.get("posts", []):
            try:
                post_id = post.get("id", "unknown")
                filename = self._generate_filename("post", post_id)
                file_path = self.base_dir / "posts" / filename
                
                # Add storage metadata
                storage_data = {
                    "stored_at": datetime.now().isoformat(),
                    "entity_type": "post",
                    "identifier": post_id,
                    "source_function": function_name,
                    "function_metadata": function_metadata,
                    "data": post
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
                
                stored_counts["posts"] += 1
            except Exception as e:
                print(f"Error storing post {post.get('id', 'unknown')}: {e}")
                stored_counts["errors"] += 1
        
        # Store comments
        for comment in extracted_units.get("comments", []):
            try:
                comment_id = comment.get("id", "unknown")
                filename = self._generate_filename("comment", comment_id)
                file_path = self.base_dir / "comments" / filename
                
                # Add storage metadata
                storage_data = {
                    "stored_at": datetime.now().isoformat(),
                    "entity_type": "comment",
                    "identifier": comment_id,
                    "source_function": function_name,
                    "function_metadata": function_metadata,
                    "data": comment
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
                
                stored_counts["comments"] += 1
            except Exception as e:
                print(f"Error storing comment {comment.get('id', 'unknown')}: {e}")
                stored_counts["errors"] += 1
        
        # Store subreddits
        for subreddit in extracted_units.get("subreddits", []):
            try:
                subreddit_name = subreddit.get("name", "unknown")
                filename = self._generate_filename("subreddit", subreddit_name)
                file_path = self.base_dir / "subreddits" / filename
                
                # Add storage metadata
                storage_data = {
                    "stored_at": datetime.now().isoformat(),
                    "entity_type": "subreddit",
                    "identifier": subreddit_name,
                    "source_function": function_name,
                    "function_metadata": function_metadata,
                    "data": subreddit
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
                
                stored_counts["subreddits"] += 1
            except Exception as e:
                print(f"Error storing subreddit {subreddit.get('name', 'unknown')}: {e}")
                stored_counts["errors"] += 1
        
        # Store submissions
        for submission in extracted_units.get("submissions", []):
            try:
                submission_id = submission.get("id", "unknown")
                filename = self._generate_filename("submission", submission_id)
                file_path = self.base_dir / "submissions" / filename
                
                # Add storage metadata
                storage_data = {
                    "stored_at": datetime.now().isoformat(),
                    "entity_type": "submission",
                    "identifier": submission_id,
                    "source_function": function_name,
                    "function_metadata": function_metadata,
                    "data": submission
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(storage_data, f, indent=2, ensure_ascii=False, default=str)
                
                stored_counts["submissions"] += 1
            except Exception as e:
                print(f"Error storing submission {submission.get('id', 'unknown')}: {e}")
                stored_counts["errors"] += 1
        
        return stored_counts
    
    def process_and_store_entities(self, raw_data: Dict[str, Any], function_name: str, function_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
        """Main processing function: extract entities and store each as individual files.
        
        This replaces the old raw response storage with per-entity storage.
        
        Args:
            raw_data: Raw response data from Reddit MCP function
            function_name: Name of the function that generated the response
            function_metadata: Optional metadata about the function call
            
        Returns:
            Dictionary with count of stored files per entity type
        """
        # Extract entities using schema-based parsing
        extracted_units = self.parse_to_units(raw_data, function_name, function_metadata)
        
        # Store each entity as its own file
        stored_counts = self.store_extracted_units(extracted_units, function_name, function_metadata)
        
        return stored_counts


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
