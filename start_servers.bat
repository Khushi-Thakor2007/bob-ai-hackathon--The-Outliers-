@echo off
echo Starting Supply Chain Control Tower...
start cmd /k "cd src\backend && venv\Scripts\python.exe run.py"
timeout /t 2 /nobreak >nul
start cmd /k "cd src\frontend && npm run dev"
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
