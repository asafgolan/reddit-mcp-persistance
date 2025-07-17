#!/usr/bin/env python3
"""
Setup script for Reddit MCP Server
Based on the setup pattern from Jarvis and MLX Batch Generator projects
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    if isinstance(cmd, str):
        cmd = cmd.split()
    
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def main():
    """Main setup function"""
    print("🚀 Setting up Reddit MCP Server...")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"📁 Working in: {project_root}")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and fill in your Reddit credentials.")
        env_example = project_root / ".env.example"
        if env_example.exists():
            print("💡 You can run: cp .env.example .env")
        return
    
    print("✅ .env file found")
    
    # Remove existing virtual environment if it exists
    venv_path = project_root / ".venv"
    if venv_path.exists():
        print("🗑️  Removing existing virtual environment...")
        run_command(f"rm -rf {venv_path}")
    
    # Create fresh virtual environment using uv
    print("🐍 Creating fresh virtual environment...")
    run_command("uv venv")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    run_command("uv sync")
    
    # Install development dependencies if they exist
    try:
        result = run_command("uv add --dev jupyter ipykernel nbstripout pytest black ruff", check=False)
        if result.returncode == 0:
            print("✅ Development dependencies installed")
    except Exception as e:
        print(f"⚠️  Some development dependencies may not be available: {e}")
    
    # Create .python-version file
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_version_file = project_root / ".python-version"
    with open(python_version_file, "w") as f:
        f.write(python_version)
    print(f"📝 Created .python-version: {python_version}")
    
    # Register Jupyter kernel if available
    print("🔧 Registering Jupyter kernel...")
    result = subprocess.run([
        "uv", "run", "python", "-m", "ipykernel", "install", 
        "--user", "--name=reddit-mcp", "--display-name=Reddit MCP (uv)"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️  Warning: Failed to register Jupyter kernel: {result.stderr}")
    else:
        print("✅ Jupyter kernel registered successfully!")
    
    # Verify key packages
    print("\n🔍 Verifying key packages...")
    packages_to_check = ["mcp", "praw", "python-dotenv"]
    
    for package in packages_to_check:
        try:
            # Handle special import names
            if package == "python-dotenv":
                import_name = "dotenv"
            else:
                import_name = package.replace('-', '_')
            
            result = subprocess.run([
                "uv", "run", "python", "-c", 
                f"import {import_name}; print('{package}: OK')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package}: Available")
            else:
                print(f"❌ {package}: Not available - {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {package}: Not available - {e}")
    
    print("\n" + "="*50)
    print("🎉 Reddit MCP Server setup complete!")
    print("="*50)
    print("\n📋 Next steps:")
    print("1. Verify your .env file has valid Reddit credentials")
    print("2. Test the server: uv run python server.py")
    print("3. Test with MCP inspector: npx @modelcontextprotocol/inspector uv run python server.py")
    print("4. Start JupyterLab: uv run jupyter lab")
    print("\n💡 For notebook development, run: uv run nbstripout --install")

if __name__ == "__main__":
    main()
