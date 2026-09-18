# Setup Guide: Supply Chain Control Tower

## Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher (with npm)

## 1. Backend Setup

```bash
cd src/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the backend API server
python run.py
```
Backend will start on `http://localhost:8000`. Database tables and 50+ seed shipments are automatically initialized on startup.

## 2. Frontend Setup

```bash
cd src/frontend

# Install frontend dependencies
npm install --legacy-peer-deps

# Run development server
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

## 3. Environment Variables (Optional)
In `src/backend/.env`:
```env
DATABASE_URL=sqlite:///./supply_chain.db
OPENAI_API_KEY=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
APP_ENV=development
```
*Note: Bob AI Assistant runs seamlessly in offline operational mode without any API keys.*
