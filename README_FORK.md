# Reddit MCP Server Extended - Fork Setup

**Enhanced fork with SQLite persistence and sequential processing capabilities.**

## 🚀 What's New in This Fork

- **✅ Enhanced .env Support**: Proper environment variable loading with python-dotenv
- **💾 SQLite Persistence**: Local Reddit data storage for persistence (planned)
- **🔄 Native MCP Usage**: Focus on standard MCP protocol implementation
- **📊 Data Storage & Retrieval**: Store and retrieve Reddit posts and comments locally

## 📋 Quick Setup

### 1. Clone and Install
```bash
git clone https://github.com/YOUR_USERNAME/reddit-mcp-extended.git
cd reddit-mcp-extended
```

### 2. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Reddit API credentials
# Get credentials from: https://www.reddit.com/prefs/apps

# OPTIONAL: upstream on forked main branch
# Check if dependencies changed after pulling upstream
git pull upstream main


#run setup script
uv run python scripts/setup.py
```

When to Run the Setup Script:
1. Initial Setup (One-time)
After cloning/forking the repository
When setting up the project for the first time
This is the primary use case
2. After Upstream Updates
When you pull new upstream changes that include:
New dependencies in 
pyproject.toml
Updated Python version requirements
Changes to the development environment
3. Environment Refresh
When you want a clean, fresh virtual environment
If your current environment becomes corrupted or has issues
When switching between different Python versions
4. After Major Changes
When the project structure changes significantly
If there are new development tools or configurations
When NOT to Run It:
Regular daily development - Once set up, you just use uv run commands
Minor code changes - No need to re-run for regular development
Bug fixes or small updates - The existing environment should work fine
Best Practice:
bash
# Check if dependencies changed after pulling upstream
git pull upstream main
# If pyproject.toml was modified, consider running:
uv run python scripts/setup.py
The setup script is designed to be safe to run multiple times - it will clean up the old environment and create a fresh one, so you can run it whenever you're unsure about your environment state.


### 3. Run with MCP Inspector
```bash
# Start MCP Inspector for testing
npx @modelcontextprotocol/inspector uv --directory $(pwd) run server.py
```

### 4. Connect to MCP Client (Claude/Cursor)

**For Claude Desktop** - Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "reddit": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/asafgolan/ultron/mcp-servers/reddit-mcp",
        "run",
        "server.py"
      ],
      "env": {
        "REDDIT_CLIENT_ID": "your_client_id",
        "REDDIT_CLIENT_SECRET": "your_client_secret",
        "REDDIT_USER_AGENT": "RedditMCPServer/1.0",
        "REDDIT_USERNAME": "your_username",
        "REDDIT_PASSWORD": "your_password"
      }
    }
  }
}
```

**For Cursor** - Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "reddit": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/asafgolan/ultron/mcp-servers/reddit-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 🔧 Maintenance & Upstream Sync

### Current Remote Configuration
```bash
# Check remotes
git remote -v
# Should show:
# upstream    https://github.com/Arindam200/reddit-mcp.git (fetch)
# upstream    https://github.com/Arindam200/reddit-mcp.git (push)
# origin      https://github.com/YOUR_USERNAME/reddit-mcp-extended.git (fetch)
# origin      https://github.com/YOUR_USERNAME/reddit-mcp-extended.git (push)
```

### Sync with Upstream
```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream changes (if needed)
git merge upstream/main

# Push to your fork
git push origin main
```

### Development Workflow
```bash
# Create feature branch
git checkout -b feature/sqlite-persistence

# Make your changes
# ...

# Commit and push
git add .
git commit -m "Add SQLite persistence layer"
git push origin feature/sqlite-persistence

# Create pull request on GitHub
```

## 🛠️ Available Tools

### Read-Only Tools (minimal credentials)
- `get_user_info(username)` - User analysis with engagement insights
- `get_top_posts(subreddit, time_filter, limit)` - Top posts with AI insights
- `get_subreddit_stats(subreddit)` - Comprehensive subreddit analysis
- `get_trending_subreddits(limit)` - Trending subreddits
- `get_submission_by_url(url)` - Get post by URL
- `get_submission_by_id(submission_id)` - Get post by ID

### Authenticated Tools (full credentials)
- `who_am_i()` - Current user info
- `create_post()` - Create new posts
- `reply_to_post()` - Reply to posts

## 📊 Roadmap

### ✅ Completed
- Enhanced .env support with python-dotenv
- Improved MCP configuration
- Fork maintenance documentation

### 🔄 In Progress
- SQLite persistence layer
- Data storage and retrieval tools

### 📋 Planned
- Reddit post and comment storage
- Local data querying capabilities
- Enhanced error handling
- Performance optimizations

## 🆘 Troubleshooting

### Common Issues

**Connection Error in MCP Inspector:**
```bash
# Check if server starts correctly
uv run server.py

# Verify .env file is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); from os import getenv; print(f'Client ID: {getenv(\"REDDIT_CLIENT_ID\")[:5]}...')"
```

**Import Errors:**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**Reddit API Errors:**
- Verify credentials at https://www.reddit.com/prefs/apps
- Check rate limits (60 requests per minute)
- Ensure proper user agent string

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Original implementation by [Arindam200](https://github.com/Arindam200/reddit-mcp)
- Model Context Protocol by [Anthropic](https://github.com/modelcontextprotocol)
- PRAW by [praw-dev](https://github.com/praw-dev/praw)
