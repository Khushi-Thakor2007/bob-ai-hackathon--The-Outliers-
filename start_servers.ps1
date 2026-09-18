# Start Backend and Frontend Servers for Supply Chain Control Tower

Write-Host "Starting Backend FastAPI Server on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src/backend; .\venv\Scripts\python.exe run.py"

Start-Sleep -Seconds 2

Write-Host "Starting Frontend Vite Server on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd src/frontend; npm run dev"

Write-Host "`nControl Tower is launching!" -ForegroundColor Yellow
Write-Host "Backend API:  http://localhost:8000 (Swagger: http://localhost:8000/docs)"
Write-Host "Frontend App: http://localhost:5173"
