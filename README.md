# Ollama Workshop Platform

A collaborative platform for workshops centered around Ollama, a local LLM runner. This platform provides a structured interface for working with Ollama models, prompts, tools, documents, and RAG systems.

## Features

- **Model Management**: List, create, edit, and test Ollama models
- **Prompt Creation**: Organize and test prompts with different models
- **Tool Integration**: Create Python functions to extend LLM capabilities
- **Document Management**: Upload and process documents for RAG
- **Vector Database Configuration**: Set up and manage vector databases
- **Embedding Creation**: Create and manage embeddings for semantic search
- **RAG Systems**: Build complete retrieval-augmented generation pipelines

## Technology Stack

- **Backend**: Python FastAPI with SQLAlchemy
- **Frontend**: Svelte with TypeScript
- **Database**: SQLite (default), PostgreSQL (optional)
- **Containerization**: Docker and Docker Compose

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Ollama](https://ollama.ai/download) installed locally

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ollama-workshop-platform.git
   cd ollama-workshop-platform
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:8080
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Setup

#### Backend (FastAPI)

1. Create a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the development server:
   ```bash
   python run.py
   ```

#### Frontend (Svelte)

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Project Structure

### Backend Structure

```
backend/
├── alembic/              # Database migration scripts
├── app/
│   ├── api/              # API endpoints
│   │   ├── dependencies/ # API dependencies
│   │   └── v1/           # API v1 routes
│   ├── core/             # Core functionality
│   ├── db/               # Database setup
│   ├── middleware/       # Middleware components
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

### Frontend Structure

```
frontend/
├── public/               # Static files
└── src/
    ├── components/       # Reusable components
    ├── lib/              # Utilities and API client
    └── pages/            # Application pages
```

## Database Setup

The application uses SQLite by default, but you can configure PostgreSQL:

1. Update the `DATABASE_URL` in the `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   ```

2. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

## Default Users

After setup, the following default users are available:

- **Admin User**:
  - Email: admin@example.com
  - Password: admin

- **Regular User**:
  - Email: user@example.com
  - Password: password

## API Documentation

When the application is running, you can access the Swagger documentation at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Health Checks

The application provides health check endpoints:

- Basic health check: http://localhost:8000/api/health
- Detailed health check: http://localhost:8000/api/health/detailed
- Public health check (no auth): http://localhost:8000/api/public/health

## Production Deployment

For production deployment, please ensure:

1. Set a secure `SECRET_KEY` in the `.env` file
2. Configure proper database credentials
3. Use HTTPS for all traffic
4. Adjust CORS settings for production domains
5. Set up appropriate resource limits in Docker Compose

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
