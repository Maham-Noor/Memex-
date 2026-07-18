# Memex-

Semantic Browser Recall is a privacy-first browser memory system that captures browsing sessions and enables semantic retrieval of previously visited pages.

## Milestone 0: Planning & Repository Setup

This repository has an initial scaffold for:

- Backend API (`backend/`)
- Frontend application (`frontend/`)
- Chrome extension scaffold (`extension/`)
- Documentation directory (`docs/`)

## Getting Started

### Backend

```powershell
cd backend
"C:/Users/Maham Noor/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pip install --upgrade pip
"C:/Users/Maham Noor/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Extension

Load the `extension/` folder as an unpacked extension in Chrome/Edge.

## Notes

The project is currently in Milestone 0, focused on initializing the repository, setting up scaffolds, and preparing the local development environment.
