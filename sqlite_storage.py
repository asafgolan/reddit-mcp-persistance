"""
SQLite-based storage for Reddit MCP entities.
Uses Pydantic models to define database schemas and ensure data integrity.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

# Import response schemas as single source of truth
from response_schemas import (
    UserInfo, WhoAmIInfo, PostItem, SubredditInfo, 
    SubmissionInfo, extract_entities_from_response
)


class SQLiteStorage:
    """SQLite-based storage for Reddit data using Pydantic schemas."""
    
    def __init__(self, db_path: str = "reddit_data.db"):
        """Initialize SQLite storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and create tables."""
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
    
    def _create_tables(self):
        """Create tables based on Pydantic models."""
        cursor = self.connection.cursor()
        
        # Batches table for tracking batch operations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                batch_id TEXT PRIMARY KEY,
                function_name TEXT NOT NULL,
                status TEXT NOT NULL,  -- 'processing', 'completed', 'failed'
                total_entities INTEGER DEFAULT 0,
                entities_stored INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                function_metadata TEXT,  -- JSON field
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            )
        """)
        
        # Users table based on UserInfo/WhoAmIInfo models
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                username TEXT NOT NULL,
                created_utc REAL,
                comment_karma INTEGER,
                link_karma INTEGER,
                total_karma INTEGER,
                has_verified_email BOOLEAN,
                is_employee BOOLEAN,
                is_mod BOOLEAN,
                is_gold BOOLEAN,
                over_18 BOOLEAN,
                is_suspended BOOLEAN,
                suspension_expiration_utc REAL,
                subreddit_info TEXT,  -- JSON field
                
                -- Extraction metadata
                source_function TEXT,
                extracted_at TEXT,
                function_metadata TEXT,  -- JSON field
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        """)
        
        # Posts table based on PostItem model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                post_id TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                score INTEGER,
                upvote_ratio REAL,
                num_comments INTEGER,
                created_utc REAL,
                url TEXT,
                permalink TEXT,
                is_self BOOLEAN,
                selftext TEXT,
                link_url TEXT,
                over_18 BOOLEAN,
                spoiler BOOLEAN,
                stickied BOOLEAN,
                locked BOOLEAN,
                distinguished TEXT,
                flair TEXT,  -- JSON field
                
                -- Extraction metadata
                source_function TEXT,
                extracted_at TEXT,
                function_metadata TEXT,  -- JSON field
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        """)
        
        # Comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                comment_id TEXT NOT NULL,
                author TEXT,
                body TEXT,
                parent_id TEXT,
                post_id TEXT,
                created_utc REAL,
                score INTEGER,
                
                -- Extraction metadata
                source_function TEXT,
                extracted_at TEXT,
                function_metadata TEXT,  -- JSON field
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        """)
        
        # Subreddits table based on SubredditInfo model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subreddits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                subreddit_id TEXT,
                display_name TEXT NOT NULL,
                title TEXT,
                public_description TEXT,
                description TEXT,
                subscribers INTEGER,
                active_user_count INTEGER,
                created_utc REAL,
                over18 BOOLEAN,
                submission_type TEXT,
                allow_images BOOLEAN,
                allow_videos BOOLEAN,
                allow_polls BOOLEAN,
                spoilers_enabled BOOLEAN,
                
                -- Extraction metadata
                source_function TEXT,
                extracted_at TEXT,
                function_metadata TEXT,  -- JSON field
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        """)
        
        # Submissions table based on SubmissionInfo model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                submission_id TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                subreddit TEXT,
                score INTEGER,
                upvote_ratio REAL,
                num_comments INTEGER,
                created_utc REAL,
                url TEXT,
                permalink TEXT,
                is_self BOOLEAN,
                selftext TEXT,
                selftext_html TEXT,
                link_url TEXT,
                domain TEXT,
                over_18 BOOLEAN,
                spoiler BOOLEAN,
                stickied BOOLEAN,
                locked BOOLEAN,
                archived BOOLEAN,
                distinguished TEXT,
                flair TEXT,  -- JSON field
                media TEXT,  -- JSON field
                preview TEXT,  -- JSON field
                awards TEXT,  -- JSON field
                
                -- Extraction metadata
                source_function TEXT,
                extracted_at TEXT,
                function_metadata TEXT,  -- JSON field
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batches_function_name ON batches(function_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batches_status ON batches(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_batch_id ON users(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_batch_id ON posts(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_post_id ON posts(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_batch_id ON comments(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_comment_id ON comments(comment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subreddits_batch_id ON subreddits(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subreddits_display_name ON subreddits(display_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_batch_id ON submissions(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_submission_id ON submissions(submission_id)")
        
        self.connection.commit()
    
    def create_batch(self, function_name: str, function_metadata: Dict[str, Any] = None) -> str:
        """Create a new batch and return its ID.
        
        Args:
            function_name: Name of the function that will generate the data
            function_metadata: Optional metadata about the function call
            
        Returns:
            Batch ID as string
        """
        batch_id = str(uuid.uuid4())
        cursor = self.connection.cursor()
        
        function_metadata_json = json.dumps(function_metadata) if function_metadata else None
        
        cursor.execute("""
            INSERT INTO batches (batch_id, function_name, status, function_metadata)
            VALUES (?, ?, ?, ?)
        """, (batch_id, function_name, "processing", function_metadata_json))
        
        self.connection.commit()
        return batch_id
    
    def update_batch_status(self, batch_id: str, status: str, entities_stored: int = 0, errors: int = 0, error_message: str = None):
        """Update batch status and statistics.
        
        Args:
            batch_id: Batch ID to update
            status: New status ('processing', 'completed', 'failed')
            entities_stored: Number of entities successfully stored
            errors: Number of errors encountered
            error_message: Error message if status is 'failed'
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            UPDATE batches 
            SET status = ?, entities_stored = ?, errors = ?, error_message = ?, 
                completed_at = CURRENT_TIMESTAMP
            WHERE batch_id = ?
        """, (status, entities_stored, errors, error_message, batch_id))
        
        self.connection.commit()
    
    def get_batch_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch information by batch ID.
        
        Args:
            batch_id: Batch ID to retrieve
            
        Returns:
            Dictionary with batch information or None if not found
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT batch_id, function_name, status, total_entities, entities_stored, 
                   errors, function_metadata, started_at, completed_at, error_message
            FROM batches WHERE batch_id = ?
        """, (batch_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "batch_id": row[0],
            "function_name": row[1],
            "status": row[2],
            "total_entities": row[3],
            "entities_stored": row[4],
            "errors": row[5],
            "function_metadata": json.loads(row[6]) if row[6] else None,
            "started_at": row[7],
            "completed_at": row[8],
            "error_message": row[9]
        }
    
    def get_batch_results(self, batch_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all entities for a given batch ID.
        
        Args:
            batch_id: Batch ID to retrieve results for
            
        Returns:
            Dictionary with entities organized by type
        """
        cursor = self.connection.cursor()
        
        results = {
            "users": [],
            "posts": [],
            "comments": [],
            "subreddits": [],
            "submissions": []
        }
        
        # Get users
        cursor.execute("""
            SELECT * FROM users WHERE batch_id = ? ORDER BY created_at
        """, (batch_id,))
        
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            user_data = dict(zip(columns, row))
            # Parse JSON fields
            if user_data.get('subreddit_info'):
                user_data['subreddit_info'] = json.loads(user_data['subreddit_info'])
            if user_data.get('function_metadata'):
                user_data['function_metadata'] = json.loads(user_data['function_metadata'])
            results["users"].append(user_data)
        
        # Get posts
        cursor.execute("""
            SELECT * FROM posts WHERE batch_id = ? ORDER BY created_at
        """, (batch_id,))
        
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            post_data = dict(zip(columns, row))
            # Parse JSON fields
            if post_data.get('flair'):
                post_data['flair'] = json.loads(post_data['flair'])
            if post_data.get('function_metadata'):
                post_data['function_metadata'] = json.loads(post_data['function_metadata'])
            results["posts"].append(post_data)
        
        # Get comments
        cursor.execute("""
            SELECT * FROM comments WHERE batch_id = ? ORDER BY created_at
        """, (batch_id,))
        
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            comment_data = dict(zip(columns, row))
            if comment_data.get('function_metadata'):
                comment_data['function_metadata'] = json.loads(comment_data['function_metadata'])
            results["comments"].append(comment_data)
        
        # Get subreddits
        cursor.execute("""
            SELECT * FROM subreddits WHERE batch_id = ? ORDER BY created_at
        """, (batch_id,))
        
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            subreddit_data = dict(zip(columns, row))
            if subreddit_data.get('function_metadata'):
                subreddit_data['function_metadata'] = json.loads(subreddit_data['function_metadata'])
            results["subreddits"].append(subreddit_data)
        
        # Get submissions
        cursor.execute("""
            SELECT * FROM submissions WHERE batch_id = ? ORDER BY created_at
        """, (batch_id,))
        
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            submission_data = dict(zip(columns, row))
            # Parse JSON fields
            for field in ['flair', 'media', 'preview', 'awards', 'function_metadata']:
                if submission_data.get(field):
                    submission_data[field] = json.loads(submission_data[field])
            results["submissions"].append(submission_data)
        
        return results
    
    def store_user(self, user_data: Dict[str, Any], batch_id: str, source_function: str = None, function_metadata: Dict[str, Any] = None) -> int:
        """Store user entity in database.
        
        Args:
            user_data: User data dictionary
            batch_id: Batch ID for this storage operation
            source_function: Function that generated this data
            function_metadata: Additional metadata about the function call
            
        Returns:
            Row ID of inserted user
        """
        cursor = self.connection.cursor()
        
        # Convert complex fields to JSON
        subreddit_info = json.dumps(user_data.get("subreddit")) if user_data.get("subreddit") else None
        function_metadata_json = json.dumps(function_metadata) if function_metadata else None
        
        cursor.execute("""
            INSERT INTO users (
                batch_id, username, created_utc, comment_karma, link_karma, total_karma,
                has_verified_email, is_employee, is_mod, is_gold, over_18,
                is_suspended, suspension_expiration_utc, subreddit_info,
                source_function, extracted_at, function_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            user_data.get("username"),
            user_data.get("created_utc"),
            user_data.get("comment_karma"),
            user_data.get("link_karma"),
            user_data.get("total_karma"),
            user_data.get("has_verified_email"),
            user_data.get("is_employee"),
            user_data.get("is_mod"),
            user_data.get("is_gold"),
            user_data.get("over_18"),
            user_data.get("is_suspended"),
            user_data.get("suspension_expiration_utc"),
            subreddit_info,
            source_function,
            datetime.now().isoformat(),
            function_metadata_json
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def store_post(self, post_data: Dict[str, Any], batch_id: str, source_function: str = None, function_metadata: Dict[str, Any] = None) -> int:
        """Store post entity in database.
        
        Args:
            post_data: Post data dictionary
            batch_id: Batch ID for this storage operation
            source_function: Function that generated this data
            function_metadata: Additional metadata about the function call
            
        Returns:
            Row ID of inserted post
        """
        cursor = self.connection.cursor()
        
        # Convert complex fields to JSON
        flair_json = json.dumps(post_data.get("flair")) if post_data.get("flair") else None
        function_metadata_json = json.dumps(function_metadata) if function_metadata else None
        
        cursor.execute("""
            INSERT INTO posts (
                batch_id, post_id, title, author, score, upvote_ratio, num_comments,
                created_utc, url, permalink, is_self, selftext, link_url,
                over_18, spoiler, stickied, locked, distinguished, flair,
                source_function, extracted_at, function_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            post_data.get("id"),
            post_data.get("title"),
            post_data.get("author"),
            post_data.get("score"),
            post_data.get("upvote_ratio"),
            post_data.get("num_comments"),
            post_data.get("created_utc"),
            post_data.get("url"),
            post_data.get("permalink"),
            post_data.get("is_self"),
            post_data.get("selftext"),
            post_data.get("link_url"),
            post_data.get("over_18"),
            post_data.get("spoiler"),
            post_data.get("stickied"),
            post_data.get("locked"),
            post_data.get("distinguished"),
            flair_json,
            source_function,
            datetime.now().isoformat(),
            function_metadata_json
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def store_subreddit(self, subreddit_data: Dict[str, Any], batch_id: str, source_function: str = None, function_metadata: Dict[str, Any] = None) -> int:
        """Store subreddit entity in database.
        
        Args:
            subreddit_data: Subreddit data dictionary
            batch_id: Batch ID for this storage operation
            source_function: Function that generated this data
            function_metadata: Additional metadata about the function call
            
        Returns:
            Row ID of inserted subreddit
        """
        cursor = self.connection.cursor()
        
        function_metadata_json = json.dumps(function_metadata) if function_metadata else None
        
        cursor.execute("""
            INSERT INTO subreddits (
                batch_id, subreddit_id, display_name, title, public_description, description,
                subscribers, active_user_count, created_utc, over18, submission_type,
                allow_images, allow_videos, allow_polls, spoilers_enabled,
                source_function, extracted_at, function_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            subreddit_data.get("id"),
            subreddit_data.get("display_name", subreddit_data.get("name")),
            subreddit_data.get("title"),
            subreddit_data.get("public_description"),
            subreddit_data.get("description"),
            subreddit_data.get("subscribers"),
            subreddit_data.get("active_user_count"),
            subreddit_data.get("created_utc"),
            subreddit_data.get("over18"),
            subreddit_data.get("submission_type"),
            subreddit_data.get("allow_images"),
            subreddit_data.get("allow_videos"),
            subreddit_data.get("allow_polls"),
            subreddit_data.get("spoilers_enabled"),
            source_function,
            datetime.now().isoformat(),
            function_metadata_json
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def store_submission(self, submission_data: Dict[str, Any], batch_id: str, source_function: str = None, function_metadata: Dict[str, Any] = None) -> int:
        """Store submission entity in database.
        
        Args:
            submission_data: Submission data dictionary
            batch_id: Batch ID for this storage operation
            source_function: Function that generated this data
            function_metadata: Additional metadata about the function call
            
        Returns:
            Row ID of inserted submission
        """
        cursor = self.connection.cursor()
        
        # Convert complex fields to JSON
        flair_json = json.dumps(submission_data.get("flair")) if submission_data.get("flair") else None
        media_json = json.dumps(submission_data.get("media")) if submission_data.get("media") else None
        preview_json = json.dumps(submission_data.get("preview")) if submission_data.get("preview") else None
        awards_json = json.dumps(submission_data.get("awards")) if submission_data.get("awards") else None
        function_metadata_json = json.dumps(function_metadata) if function_metadata else None
        
        cursor.execute("""
            INSERT INTO submissions (
                batch_id, submission_id, title, author, subreddit, score, upvote_ratio,
                num_comments, created_utc, url, permalink, is_self, selftext,
                selftext_html, link_url, domain, over_18, spoiler, stickied,
                locked, archived, distinguished, flair, media, preview, awards,
                source_function, extracted_at, function_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            submission_data.get("id"),
            submission_data.get("title"),
            submission_data.get("author"),
            submission_data.get("subreddit"),
            submission_data.get("score"),
            submission_data.get("upvote_ratio"),
            submission_data.get("num_comments"),
            submission_data.get("created_utc"),
            submission_data.get("url"),
            submission_data.get("permalink"),
            submission_data.get("is_self"),
            submission_data.get("selftext"),
            submission_data.get("selftext_html"),
            submission_data.get("link_url"),
            submission_data.get("domain"),
            submission_data.get("over_18"),
            submission_data.get("spoiler"),
            submission_data.get("stickied"),
            submission_data.get("locked"),
            submission_data.get("archived"),
            submission_data.get("distinguished"),
            flair_json,
            media_json,
            preview_json,
            awards_json,
            source_function,
            datetime.now().isoformat(),
            function_metadata_json
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def store_comment(self, comment_data: Dict[str, Any], batch_id: str, source_function: str = None, function_metadata: Dict[str, Any] = None) -> int:
        """Store comment entity in database.
        
        Args:
            comment_data: Comment data dictionary
            batch_id: Batch ID for this storage operation
            source_function: Function that generated this data
            function_metadata: Additional metadata about the function call
            
        Returns:
            Row ID of inserted comment
        """
        cursor = self.connection.cursor()
        
        function_metadata_json = json.dumps(function_metadata) if function_metadata else None
        
        cursor.execute("""
            INSERT INTO comments (
                batch_id, comment_id, author, body, parent_id, post_id, created_utc, score,
                source_function, extracted_at, function_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            comment_data.get("id"),
            comment_data.get("author"),
            comment_data.get("body"),
            comment_data.get("parent_id"),
            comment_data.get("post_id"),
            comment_data.get("created_utc"),
            comment_data.get("score"),
            source_function,
            datetime.now().isoformat(),
            function_metadata_json
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def parse_to_units(self, data: Dict[str, Any], function_name: str, function_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse response data to extract individual entities using schema-based extraction.
        
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
    
    def process_and_store_entities(self, raw_data: Dict[str, Any], function_name: str, function_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main processing function: extract entities and store in SQLite database with batch tracking.
        
        Args:
            raw_data: Raw response data from Reddit MCP function
            function_name: Name of the function that generated the response
            function_metadata: Optional metadata about the function call
            
        Returns:
            Dictionary with batch_id and statistics about stored entities
        """
        # Create a new batch
        batch_id = self.create_batch(function_name, function_metadata)
        
        # Extract entities using schema-based parsing
        extracted_units = self.parse_to_units(raw_data, function_name, function_metadata)
        
        stored_counts = {
            "users": 0,
            "posts": 0,
            "comments": 0,
            "subreddits": 0,
            "submissions": 0,
            "errors": 0
        }
        
        error_messages = []
        
        # Store each entity type with batch_id
        for user in extracted_units.get("users", []):
            try:
                self.store_user(user, batch_id, function_name, function_metadata)
                stored_counts["users"] += 1
            except Exception as e:
                error_msg = f"Error storing user {user.get('username', 'unknown')}: {e}"
                print(error_msg)
                error_messages.append(error_msg)
                stored_counts["errors"] += 1
        
        for post in extracted_units.get("posts", []):
            try:
                self.store_post(post, batch_id, function_name, function_metadata)
                stored_counts["posts"] += 1
            except Exception as e:
                error_msg = f"Error storing post {post.get('id', 'unknown')}: {e}"
                print(error_msg)
                error_messages.append(error_msg)
                stored_counts["errors"] += 1
        
        for comment in extracted_units.get("comments", []):
            try:
                self.store_comment(comment, batch_id, function_name, function_metadata)
                stored_counts["comments"] += 1
            except Exception as e:
                error_msg = f"Error storing comment {comment.get('id', 'unknown')}: {e}"
                print(error_msg)
                error_messages.append(error_msg)
                stored_counts["errors"] += 1
        
        for subreddit in extracted_units.get("subreddits", []):
            try:
                self.store_subreddit(subreddit, batch_id, function_name, function_metadata)
                stored_counts["subreddits"] += 1
            except Exception as e:
                error_msg = f"Error storing subreddit {subreddit.get('name', 'unknown')}: {e}"
                print(error_msg)
                error_messages.append(error_msg)
                stored_counts["errors"] += 1
        
        for submission in extracted_units.get("submissions", []):
            try:
                self.store_submission(submission, batch_id, function_name, function_metadata)
                stored_counts["submissions"] += 1
            except Exception as e:
                error_msg = f"Error storing submission {submission.get('id', 'unknown')}: {e}"
                print(error_msg)
                error_messages.append(error_msg)
                stored_counts["errors"] += 1
        
        # Calculate totals
        total_entities = sum(stored_counts[key] for key in stored_counts if key != "errors")
        
        # Update batch status
        batch_status = "completed" if stored_counts["errors"] == 0 else "failed"
        error_message = "; ".join(error_messages) if error_messages else None
        
        self.update_batch_status(
            batch_id, 
            batch_status, 
            total_entities, 
            stored_counts["errors"], 
            error_message
        )
        
        return {
            "batch_id": batch_id,
            "status": batch_status,
            "total_entities": total_entities,
            "entities_stored": stored_counts,
            "errors": stored_counts["errors"],
            "error_message": error_message
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        cursor = self.connection.cursor()
        
        stats = {}
        
        # Count records in each table
        for table in ["users", "posts", "comments", "subreddits", "submissions"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]
        
        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        stats["database_size_bytes"] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup on object deletion."""
        self.close()


# Global storage instance
_storage = None

def get_storage() -> SQLiteStorage:
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        _storage = SQLiteStorage()
    return _storage


def store_result(data: Dict[str, Any], function_name: str, function_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    """Helper function to store result data in SQLite.
    
    Args:
        data: Data to store
        function_name: Name of the function that generated the response
        function_metadata: Optional metadata about the function call
        
    Returns:
        Dictionary with count of stored entities per type
    """
    storage = get_storage()
    return storage.process_and_store_entities(data, function_name, function_metadata)
