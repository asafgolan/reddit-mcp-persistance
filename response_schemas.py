"""
Response schemas extracted from server.py docstrings.
Single source of truth for all Reddit MCP response structures.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PostMetadata(BaseModel):
    """Metadata for post responses."""
    fetched_at: float
    post_count: int


class PostItem(BaseModel):
    """Individual post structure from get_top_posts."""
    id: str = Field(description="Post ID")
    title: str = Field(description="Post title")
    author: str = Field(description="Author's username")
    score: int = Field(description="Post score (upvotes - downvotes)")
    upvote_ratio: float = Field(description="Ratio of upvotes to total votes")
    num_comments: int = Field(description="Number of comments")
    created_utc: float = Field(description="Post creation timestamp")
    url: Optional[str] = Field(default=None, description="URL to the post")
    permalink: Optional[str] = Field(default=None, description="Relative URL to the post")
    is_self: bool = Field(description="Whether it's a self (text) post")
    selftext: Optional[str] = Field(default="", description="Content of self post (if any)")
    link_url: Optional[str] = Field(default=None, description="URL for link posts (if any)")
    over_18: bool = Field(description="Whether marked as NSFW")
    spoiler: bool = Field(description="Whether marked as spoiler")
    stickied: Optional[bool] = Field(default=False, description="Whether stickied in the subreddit")
    locked: Optional[bool] = Field(default=False, description="Whether comments are locked")
    distinguished: Optional[str] = Field(default=None, description="Distinguishing type (e.g., 'moderator')")
    flair: Optional[Dict] = Field(default=None, description="Post flair information if any")


class GetTopPostsResponse(BaseModel):
    """Response structure for get_top_posts function."""
    subreddit: str = Field(description="Subreddit name")
    time_filter: str = Field(description="The time period used for filtering")
    posts: List[PostItem] = Field(description="List of posts")
    metadata: PostMetadata = Field(description="Response metadata")


class UserInfo(BaseModel):
    """User information structure."""
    username: str = Field(description="User's username")
    created_utc: float = Field(description="Account creation timestamp")
    comment_karma: int = Field(description="User's comment karma")
    link_karma: int = Field(description="User's post/link karma")
    has_verified_email: bool = Field(description="Whether email is verified")
    is_mod: bool = Field(description="Whether user is a moderator")
    is_gold: bool = Field(description="Whether user has Reddit premium")
    has_subscribed: bool = Field(description="Whether user has subscribed to premium")
    is_employee: bool = Field(description="Whether user is a Reddit employee")
    over_18: bool = Field(description="Whether user is marked as NSFW")
    is_suspended: bool = Field(description="Whether account is suspended")
    suspension_expiration_utc: Optional[float] = Field(description="When suspension ends if suspended")
    total_karma: int = Field(description="Total karma (comments + posts)")
    subreddit: Optional[Dict] = Field(description="User's profile subreddit info if exists")


class SubredditMetadata(BaseModel):
    """Metadata for subreddit responses."""
    fetched_at: float = Field(description="Timestamp when data was fetched")
    url: str = Field(description="Full URL to the subreddit")
    moderators_count: int = Field(description="Number of moderators")
    rules: List[Dict] = Field(description="Subreddit rules if available")
    features: Dict[str, bool] = Field(description="Enabled subreddit features")


class SubredditInfo(BaseModel):
    """Subreddit information structure."""
    id: str = Field(description="Subreddit ID (e.g., '2qgzt')")
    display_name: str = Field(description="Subreddit display name (without r/ prefix)")
    title: str = Field(description="Subreddit title")
    public_description: str = Field(description="Public description")
    description: str = Field(description="Full description (can include markdown)")
    subscribers: int = Field(description="Number of subscribers")
    active_user_count: Optional[int] = Field(description="Currently active users if available")
    created_utc: float = Field(description="Creation timestamp (UTC)")
    over18: bool = Field(description="Whether marked as NSFW")
    submission_type: str = Field(description="Allowed submission types (any, link, self)")
    allow_images: bool = Field(description="Whether image uploads are allowed")
    allow_videos: bool = Field(description="Whether video uploads are allowed")
    allow_polls: bool = Field(description="Whether polls are allowed")
    spoilers_enabled: bool = Field(description="Whether spoiler tags are enabled")
    wikienabled: bool = Field(description="Whether wiki is enabled")
    user_is_banned: bool = Field(description="Whether current user is banned")
    user_is_moderator: bool = Field(description="Whether current user is a moderator")
    user_is_subscriber: bool = Field(description="Whether current user is a subscriber")
    mod_permissions: List[str] = Field(description="Moderator permissions if applicable")
    metadata: SubredditMetadata = Field(description="Response metadata")


class SubmissionMetadata(BaseModel):
    """Metadata for submission responses."""
    fetched_at: float = Field(description="Timestamp when data was fetched")
    subreddit_id: str = Field(description="Subreddit full ID")
    author_id: str = Field(description="Author's full ID if available")
    is_original_content: bool = Field(description="Whether marked as OC")
    is_meta: bool = Field(description="Whether marked as meta")
    is_crosspostable: bool = Field(description="Whether can be crossposted")
    is_reddit_media_domain: bool = Field(description="Whether media is hosted on Reddit")
    is_robot_indexable: bool = Field(description="Whether search engines should index")
    is_created_from_ads_ui: bool = Field(description="Whether created via ads UI")
    is_video: bool = Field(description="Whether the post is a video")
    pinned: bool = Field(description="Whether the post is pinned in the subreddit")
    gilded: int = Field(description="Number of times gilded")
    total_awards_received: int = Field(description="Total number of awards received")
    view_count: Optional[int] = Field(description="View count if available")
    visited: bool = Field(description="Whether the current user has visited")


class SubmissionInfo(BaseModel):
    """Submission information structure."""
    id: str = Field(description="Submission ID (e.g., 'abc123')")
    title: str = Field(description="Submission title")
    author: str = Field(description="Author's username or '[deleted]' if deleted")
    subreddit: str = Field(description="Subreddit name")
    score: int = Field(description="Post score (upvotes - downvotes)")
    upvote_ratio: float = Field(description="Ratio of upvotes to total votes")
    num_comments: int = Field(description="Number of comments")
    created_utc: float = Field(description="Post creation timestamp (UTC)")
    url: str = Field(description="Full URL to the post")
    permalink: str = Field(description="Relative URL to the post")
    is_self: bool = Field(description="Whether it's a self (text) post")
    selftext: str = Field(description="Content of self post (if any)")
    selftext_html: Optional[str] = Field(description="HTML formatted content")
    link_url: str = Field(description="URL for link posts (if any)")
    domain: str = Field(description="Domain of the linked content")
    over_18: bool = Field(description="Whether marked as NSFW")
    spoiler: bool = Field(description="Whether marked as spoiler")
    stickied: bool = Field(description="Whether stickied in the subreddit")
    locked: bool = Field(description="Whether comments are locked")
    archived: bool = Field(description="Whether the post is archived")
    distinguished: Optional[str] = Field(description="Distinguishing type (e.g., 'moderator')")
    flair: Optional[Dict] = Field(description="Post flair information if any")
    media: Optional[Dict] = Field(description="Media information if any")
    preview: Optional[Dict] = Field(description="Preview information if available")
    awards: List[Dict] = Field(description="List of awards received")
    metadata: SubmissionMetadata = Field(description="Response metadata")


class WhoAmIMetadata(BaseModel):
    """Metadata for who_am_i responses."""
    fetched_at: float = Field(description="Timestamp when data was fetched")
    is_authenticated: bool = Field(description="Whether user is authenticated")
    is_moderator: bool = Field(description="Whether user is a moderator")
    has_verified_email: bool = Field(description="Whether email is verified")
    has_mail: bool = Field(description="Whether user has unread messages")
    has_mod_mail: bool = Field(description="Whether user has mod mail")
    has_subscribed: bool = Field(description="Whether user has subscribed to Premium")
    in_chat: bool = Field(description="Whether user is in chat")
    in_redesign_beta: bool = Field(description="Whether user is in redesign beta")
    new_modmail_exists: bool = Field(description="Whether user has new modmail")
    pref_no_profanity: bool = Field(description="Whether to filter profanity")
    suspension_expiration_utc: Optional[float] = Field(description="When suspension ends if suspended")


class WhoAmIInfo(BaseModel):
    """Who am I response structure."""
    id: str = Field(description="Full user ID (e.g., 't2_abc123')")
    name: str = Field(description="Username")
    created_utc: float = Field(description="Account creation timestamp")
    comment_karma: int = Field(description="Comment karma")
    link_karma: int = Field(description="Post/link karma")
    total_karma: int = Field(description="Total karma (comments + posts)")
    awardee_karma: int = Field(description="Karma from awards received")
    awarder_karma: int = Field(description="Karma from awards given")
    has_verified_email: bool = Field(description="Whether email is verified")
    is_employee: bool = Field(description="Whether user is a Reddit employee")
    is_friend: bool = Field(description="Whether user is a friend")
    is_gold: bool = Field(description="Whether user has Reddit Premium")
    is_mod: bool = Field(description="Whether user is a moderator")
    is_suspended: bool = Field(description="Whether account is suspended")
    verified: bool = Field(description="Whether account is verified")
    has_subscribed: bool = Field(description="Whether user has subscribed to Premium")
    snoovatar_img: str = Field(description="URL to snoovatar image")
    icon_img: str = Field(description="URL to user's icon")
    pref_show_snoovatar: bool = Field(description="Whether to show snoovatar")
    snoovatar_size: Optional[List[int]] = Field(description="Snoovatar dimensions")
    subreddit: Optional[Dict] = Field(description="User's profile subreddit info")
    metadata: WhoAmIMetadata = Field(description="Response metadata")


class TrendingSubredditItem(BaseModel):
    """Individual trending subreddit structure."""
    display_name: str = Field(description="Subreddit display name")
    title: str = Field(description="Subreddit title")
    subscribers: int = Field(description="Number of subscribers")
    trending_reason: Optional[str] = Field(description="Reason for trending")


class GetTrendingSubredditsResponse(BaseModel):
    """Response structure for get_trending_subreddits function."""
    subreddits: List[TrendingSubredditItem] = Field(description="List of trending subreddits")
    metadata: Dict[str, Any] = Field(description="Response metadata")


# Schema mapping for easy lookup
FUNCTION_SCHEMAS = {
    "get_user_info": UserInfo,
    "who_am_i": WhoAmIInfo,
    "get_top_posts": GetTopPostsResponse,
    "get_subreddit_info": SubredditInfo,
    "get_subreddit_stats": SubredditInfo,  # Same schema as get_subreddit_info
    "get_trending_subreddits": GetTrendingSubredditsResponse,
    "get_submission_by_url": SubmissionInfo,
    "get_submission_by_id": SubmissionInfo,
    # Note: create_post and reply_to_post have different response structures
    # that would need separate schemas
}


def get_schema_for_function(function_name: str) -> Optional[BaseModel]:
    """Get the appropriate schema for a function."""
    return FUNCTION_SCHEMAS.get(function_name)


def extract_entities_from_response(data: Dict[str, Any], function_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract entities from response data using the appropriate schema."""
    schema = get_schema_for_function(function_name)
    if not schema:
        return {"unknown": [data]}
    
    # Validate the response against the schema
    try:
        validated_response = schema(**data)
        return _extract_entities_from_validated_response(validated_response, function_name)
    except Exception as e:
        # Fall back to raw data if validation fails
        return {"validation_error": [{"error": str(e), "data": data}]}


def _extract_entities_from_validated_response(response: BaseModel, function_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract entities from a validated response object."""
    entities = {
        "users": [],
        "posts": [],
        "comments": [],
        "subreddits": [],
        "submissions": []
    }
    
    if function_name in ["get_user_info", "who_am_i"]:
        entities["users"].append(response.dict())
        
    elif function_name == "get_top_posts":
        # Extract subreddit info
        entities["subreddits"].append({
            "name": response.subreddit,
            "time_filter": response.time_filter,
            "post_count": len(response.posts)
        })
        
        # Extract individual posts and their authors
        for post in response.posts:
            entities["posts"].append(post.dict())
            if post.author != "[deleted]":
                entities["users"].append({
                    "username": post.author,
                    "post_activity": True
                })
                
    elif function_name in ["get_subreddit_info", "get_subreddit_stats"]:
        entities["subreddits"].append(response.dict())
        
    elif function_name == "get_trending_subreddits":
        for subreddit in response.subreddits:
            entities["subreddits"].append({
                **subreddit.dict(),
                "is_trending": True
            })
            
    elif function_name in ["get_submission_by_url", "get_submission_by_id"]:
        entities["submissions"].append(response.dict())
        if response.author != "[deleted]":
            entities["users"].append({
                "username": response.author,
                "submission_activity": True
            })
        entities["subreddits"].append({
            "name": response.subreddit,
            "submission_activity": True
        })
    
    return entities
