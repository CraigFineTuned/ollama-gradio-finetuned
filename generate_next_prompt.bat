@echo off
echo Running Project Assistant...
call .venv\Scripts\activate.bat
python dev_tools\project_assistant.py
echo.
echo Next prompt generated in dev_tools\next_session_prompt.md
echo.
pause
