# Development Tools for Ollama Gradio WebUI

Created by: **CraigFineTuned**

This directory contains tools to help with the ongoing development of the Ollama Gradio WebUI project.

## Tools Included

### 1. Project Assistant (`project_assistant.py`)

This script helps track changes to the project and generates prompts for the next development session. It can be run manually or integrated with git hooks.

Features:
- Detects changes in tracked files (Python, JSON, Markdown, Batch, SVG)
- Logs changes in a change log file
- Generates structured prompts for the next development session
- Cycles through different improvement areas

Usage:
```bash
python dev_tools/project_assistant.py
```

To force generation of a new prompt even if no changes are detected:
```bash
python dev_tools/project_assistant.py --force
```

### 2. Git Hooks Setup (`setup_git_hooks.py`)

This script sets up git hooks to automatically run the project assistant when changes are committed to the repository.

Usage:
```bash
python dev_tools/setup_git_hooks.py
```

## Automated Workflow

Once the git hooks are set up, the workflow is:

1. Make changes to your project files
2. Commit your changes with `git commit`
3. The project assistant automatically runs and generates:
   - An updated change log (`dev_tools/change_log.md`)
   - A new prompt for the next development session (`dev_tools/next_session_prompt.md`)

## Manual Workflow

If you prefer not to use git hooks, you can run the project assistant manually:

1. Make changes to your project files
2. Run `python dev_tools/project_assistant.py`
3. Use the generated prompt in `dev_tools/next_session_prompt.md` for your next AI development session

## Improvement Areas

The project assistant cycles through these improvement areas:

1. Model Performance Optimization
2. Advanced Agent Capabilities  
3. Enhanced Vision Processing
4. User Experience Refinements
5. API Expansion
6. Error Handling and Robustness
7. Documentation Improvements
8. Code Structure and Maintainability
9. Testing and Quality Assurance

Each time you run the project assistant, it generates a prompt focused on the next area in the cycle.
