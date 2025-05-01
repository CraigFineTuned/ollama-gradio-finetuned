#!/usr/bin/env python3
"""
Project Assistant for Ollama Gradio WebUI
Created by: CraigFineTuned

This script helps track changes to the project and generates prompts for the next
development session. It can be run manually or integrated with git hooks.
"""

import os
import sys
import datetime
import hashlib
import json
import argparse
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TRACKED_EXTENSIONS = ['.py', '.json', '.md', '.bat', '.svg']
HASH_FILE = PROJECT_ROOT / 'dev_tools' / 'file_hashes.json'
CHANGE_LOG = PROJECT_ROOT / 'dev_tools' / 'change_log.md'
NEXT_PROMPT = PROJECT_ROOT / 'dev_tools' / 'next_session_prompt.md'

# Improvement areas to cycle through
IMPROVEMENT_AREAS = [
    "Model Performance Optimization",
    "Advanced Agent Capabilities",
    "Enhanced Vision Processing",
    "User Experience Refinements",
    "API Expansion",
    "Error Handling and Robustness",
    "Documentation Improvements",
    "Code Structure and Maintainability",
    "Testing and Quality Assurance"
]

def calculate_file_hash(filepath):
    """Calculate the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as file:
        # Read the file in chunks to handle large files
        for chunk in iter(lambda: file.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

def get_all_tracked_files():
    """Get all files that should be tracked for changes."""
    tracked_files = []
    for root, _, files in os.walk(PROJECT_ROOT):
        # Skip .venv directory and dev_tools
        if '.venv' in root or 'dev_tools' in root:
            continue
        
        for file in files:
            filepath = Path(root) / file
            if any(filepath.suffix == ext for ext in TRACKED_EXTENSIONS):
                tracked_files.append(filepath)
    return tracked_files

def load_previous_hashes():
    """Load the previous file hashes."""
    if HASH_FILE.exists():
        with open(HASH_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_current_hashes(hashes):
    """Save the current file hashes."""
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f, indent=2)

def update_change_log(changes):
    """Update the change log with the detected changes."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not CHANGE_LOG.parent.exists():
        CHANGE_LOG.parent.mkdir(parents=True)
    
    # Create the file if it doesn't exist
    if not CHANGE_LOG.exists():
        with open(CHANGE_LOG, 'w') as f:
            f.write("# Ollama Gradio WebUI Change Log\n\n")
    
    # Append the changes
    with open(CHANGE_LOG, 'a') as f:
        f.write(f"\n## Changes Detected - {timestamp}\n\n")
        if changes:
            for file, status in changes:
                f.write(f"- {status}: {file}\n")
        else:
            f.write("- No changes detected\n")

def generate_next_prompt(changes):
    """Generate a prompt for the next development session."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Select the next improvement area (cycling through the list)
    if NEXT_PROMPT.exists():
        with open(NEXT_PROMPT, 'r') as f:
            content = f.read()
            current_area_index = -1
            for i, area in enumerate(IMPROVEMENT_AREAS):
                if area in content.split("\n")[0]:
                    current_area_index = i
                    break
            
            next_area_index = (current_area_index + 1) % len(IMPROVEMENT_AREAS)
    else:
        next_area_index = 0
    
    next_area = IMPROVEMENT_AREAS[next_area_index]
    
    # Generate the prompt
    prompt = f"""# Next Development Focus: {next_area} - {timestamp}

I'm continuing development on the Ollama Gradio WebUI project. This is a Python-based web interface for interacting with Ollama's LLM models using Gradio (version 3.50.2).

The project has three core components:
1. A standard chat interface
2. An agent system using specialized prompts
3. A vision assistant for image analysis

## Recent Changes
"""

    if changes:
        for file, status in changes:
            prompt += f"- {status}: {file}\n"
    else:
        prompt += "- No recent changes\n"

    prompt += f"""
## Goal for Next Session

My goal for this session is to improve the project's {next_area.lower()}. 

Specific areas to focus on:
"""

    # Add specific suggestions based on the improvement area
    if next_area == "Model Performance Optimization":
        prompt += """- Implement context window management to handle longer conversations
- Add parameter tuning options for temperature, top_p, etc.
- Improve streaming response handling for better user experience
- Optimize memory usage for large conversations"""
    
    elif next_area == "Advanced Agent Capabilities":
        prompt += """- Expand the agent system with more specialized prompts
- Implement a way for users to create and save custom agents
- Add agent chaining capabilities for complex tasks
- Create specialized agents for code generation, writing, etc."""
    
    elif next_area == "Enhanced Vision Processing":
        prompt += """- Improve image preprocessing for better analysis
- Add support for multiple image uploads
- Implement image annotation capabilities
- Support different image formats and sizes"""
    
    elif next_area == "User Experience Refinements":
        prompt += """- Add conversation saving/loading functionality
- Implement themes or dark mode support
- Improve responsive design for mobile devices
- Add keyboard shortcuts for common actions"""
    
    elif next_area == "API Expansion":
        prompt += """- Support newer Ollama API features
- Add support for model downloading and management
- Implement model comparison capabilities
- Add API authentication options"""
    
    elif next_area == "Error Handling and Robustness":
        prompt += """- Improve error messages for better user feedback
- Add graceful degradation for offline operation
- Implement request retries for intermittent failures
- Add comprehensive logging for troubleshooting"""
    
    elif next_area == "Documentation Improvements":
        prompt += """- Update and expand the README with more examples
- Add inline code documentation
- Create user guides for different features
- Document configuration options in detail"""
    
    elif next_area == "Code Structure and Maintainability":
        prompt += """- Refactor the codebase for better organization
- Break down complex functions into smaller ones
- Implement consistent naming conventions
- Add type hints for better code comprehension"""
    
    elif next_area == "Testing and Quality Assurance":
        prompt += """- Add unit tests for core functionality
- Implement integration tests for the UI
- Create a test suite for regression testing
- Add automated linting and code quality checks"""

    prompt += """

Please help me design and implement these improvements while maintaining compatibility with the existing architecture.

Here are the key technical constraints to keep in mind:
- Requires specific dependency versions (see requirements.txt)
- Streaming responses require Gradio queue functionality
- Error handling is critical for Ollama API communication

I'd like to start by exploring the most impactful changes we can make in this area.
"""

    # Save the prompt
    if not NEXT_PROMPT.parent.exists():
        NEXT_PROMPT.parent.mkdir(parents=True)
    
    with open(NEXT_PROMPT, 'w') as f:
        f.write(prompt)
    
    return prompt

def detect_changes():
    """Detect changes in the tracked files."""
    files = get_all_tracked_files()
    previous_hashes = load_previous_hashes()
    current_hashes = {}
    changes = []
    
    for filepath in files:
        rel_path = str(filepath.relative_to(PROJECT_ROOT))
        current_hash = calculate_file_hash(filepath)
        current_hashes[rel_path] = current_hash
        
        if rel_path not in previous_hashes:
            changes.append((rel_path, "Added"))
        elif previous_hashes[rel_path] != current_hash:
            changes.append((rel_path, "Modified"))
    
    # Check for deleted files
    for rel_path in previous_hashes:
        if rel_path not in current_hashes:
            changes.append((rel_path, "Deleted"))
    
    save_current_hashes(current_hashes)
    return changes

def main():
    parser = argparse.ArgumentParser(description="Track project changes and generate prompts")
    parser.add_argument("--force", action="store_true", help="Force creation of next prompt even if no changes")
    args = parser.parse_args()
    
    print(f"Checking for changes in {PROJECT_ROOT}...")
    changes = detect_changes()
    
    if changes or args.force:
        print(f"Detected {len(changes)} changes:")
        for file, status in changes:
            print(f"  {status}: {file}")
        
        update_change_log(changes)
        print(f"Change log updated: {CHANGE_LOG}")
        
        next_prompt = generate_next_prompt(changes)
        print(f"Next session prompt generated: {NEXT_PROMPT}")
        
        print("\nNext steps:")
        print("1. Review the change log to understand what has changed")
        print("2. Use the generated prompt for your next AI development session")
        print("3. Consider setting up a git hook to run this script automatically")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
