# Ollama Workshop Platform - Enhanced Edition

The Ollama Workshop Platform has been completely redesigned with a modern, responsive UI and enhanced user experience. This update introduces a variety of improvements to make the platform more intuitive, visually appealing, and functional.

## New Features & Improvements

### UI/UX Enhancements
- Modern design system with consistent colors, spacing, and typography
- Responsive layout that works on mobile devices
- Dark mode optimized interface
- Enhanced cards and components
- Improved loading states and empty states
- Toast notification system

### Feature Enhancements
- Modernized chat interface with markdown and code highlighting
- Enhanced dashboard with better statistics and organization
- Improved model browsing and management
- Chat history export functionality
- Responsive sidebar with mobile support

### Technical Improvements
- Consistent CSS variables for theming
- Component-based architecture
- Improved error handling
- Better organization of code
- Enhanced form components

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.9+
- Ollama installed and running locally

### Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The enhanced frontend will be available at http://localhost:5173

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

## Testing the Platform

For testing purposes, you can use the following credentials:

- Regular user:
  - Email: user@example.com
  - Password: password

- Admin user:
  - Email: admin@example.com
  - Password: admin

## Key Components

### Core Improvements
1. **Theme System** - A comprehensive CSS variable-based theme system that provides consistent colors, spacing, and typography
2. **Component Library** - Reusable UI components like Cards, Toast notifications, and form elements
3. **Responsive Design** - Mobile-first approach ensuring the platform works well on all device sizes

### Enhanced Pages
1. **Dashboard** - Redesigned with better statistics, quick actions, and activity tracking
2. **Chat Interface** - Modernized with markdown support, code highlighting, and improved UX
3. **Login Screen** - More attractive and user-friendly authentication page
4. **Models Display** - Better visualization and management of Ollama models

## Future Improvements

Here are some areas for future enhancement:

1. **Community Features** - Implement the planned community section for sharing models and prompts
2. **RAG Visualization** - Add visual tools for understanding and optimizing RAG processes
3. **User Management** - Enhance the admin interface for managing workshop attendees
4. **Analytics Dashboard** - Add usage tracking and performance metrics
5. **Model Comparison Tools** - Create interfaces for comparing different models' performance

## Troubleshooting

- If you encounter any issues with the UI, check the browser console for errors
- Make sure Ollama is running locally for the model functionality to work
- If styles aren't loading correctly, try clearing your browser cache

## License

MIT
