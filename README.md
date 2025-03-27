# AI Workshop Platform

A collaborative platform for workshop attendees to create, save, and share prompts, tools, and model files.

## Features

- User authentication and invitation system
- Model management (view, create, test)
- Prompt management (create, save, share)
- Tool integration (Python functions)
- RAG system with document management
- Community features for sharing and collaboration

## Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Ollama installed and running locally

## Quick Start

### Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

### Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at http://localhost:8000 with Swagger documentation at http://localhost:8000/docs

## Development

### Default Credentials

For testing purposes, you can use the following credentials:

examples
- Regular user:
  - Email: user@example.com
  - Password: password

- Admin user:
  - Email: admin@example.com
  - Password: admin

### Project Structure

```
ollama-workshop-platform/
├── frontend/                 # Svelte + Vite frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   └── ...
│   └── ...
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality
│   │   ├── models/           # Data models
│   │   └── ...
│   └── ...
└── ...
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test your changes
4. Submit a pull request

## License

MIT