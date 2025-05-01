#!/usr/bin/env python3
"""
Setup Git Hooks for Ollama Gradio WebUI
Created by: CraigFineTuned

This script sets up git hooks to automatically run the project_assistant.py
script when changes are committed to the repository.
"""

import os
import sys
import stat
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
GIT_HOOKS_DIR = PROJECT_ROOT / '.git' / 'hooks'
POST_COMMIT_HOOK = GIT_HOOKS_DIR / 'post-commit'

def setup_post_commit_hook():
    """Set up the post-commit hook to run project_assistant.py."""
    if not GIT_HOOKS_DIR.exists():
        print(f"Git hooks directory not found: {GIT_HOOKS_DIR}")
        print("Make sure you are running this script from a git repository.")
        return False
    
    # Create the post-commit hook script
    hook_content = """#!/bin/sh
# Post-commit hook for Ollama Gradio WebUI
# Created by: CraigFineTuned

# Get the project root directory
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Run the project assistant script
python $PROJECT_ROOT/dev_tools/project_assistant.py

# Exit with success status
exit 0
"""
    
    with open(POST_COMMIT_HOOK, 'w') as f:
        f.write(hook_content)
    
    # Make the hook executable
    os.chmod(POST_COMMIT_HOOK, os.stat(POST_COMMIT_HOOK).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print(f"Post-commit hook installed: {POST_COMMIT_HOOK}")
    return True

def main():
    print("Setting up git hooks for Ollama Gradio WebUI...")
    
    if setup_post_commit_hook():
        print("\nGit hooks setup successfully!")
        print("\nNext steps:")
        print("1. Make changes to your project files")
        print("2. Commit your changes with 'git commit'")
        print("3. The project assistant will automatically run and generate the next prompt")
    else:
        print("\nFailed to set up git hooks.")
        print("You can still run the project assistant manually with:")
        print("  python dev_tools/project_assistant.py")

if __name__ == "__main__":
    main()
