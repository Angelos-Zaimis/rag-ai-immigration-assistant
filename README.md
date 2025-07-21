# Greetli AI Backend

A professional FastAPI backend with JWT authentication, user management, OCR processing, AI integration, and translation services.

## Features

- 🔐 **JWT Authentication** - Secure user registration, login, and token refresh
- 👤 **User Management** - Complete user CRUD operations
- 📝 **OCR Processing** - Text extraction from images
- 🤖 **AI Integration** - LangChain and OpenAI integration
- 🌐 **Translation Services** - Google Translate integration
- 🗄️ **Database** - PostgreSQL with async SQLAlchemy
- 🚀 **Production Ready** - Proper error handling, validation, and security

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Virtual environment (recommended)

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository>
cd greetliAIBackend
python -m venv greetlAI
source greetlAI/bin/activate  # On Windows: greetlAI\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Environment configuration:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Database setup:**
```bash
# Run migrations
alembic upgrade head
```

5. **Start the server:**
```bash
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `JWT_SECRET_KEY` | JWT signing secret (use strong key in production) | Generated default | Yes |
| `ENVIRONMENT` | Environment type | `development` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | `15` | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | `7` | No |

## Architecture

This project follows a clean, layered architecture:

```
app/
├── config/          # Configuration and settings
├── controllers/     # Request/Response handling
├── middleware/      # Authentication middleware
├── models/          # Database models
├── routes/          # API route definitions
├── schemas/         # Pydantic schemas/DTOs
└── services/        # Business logic layer
    ├── auth/        # Authentication services
    ├── user/        # User management
    └── ...          # Other services
```

### Key Principles

- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Injection**: Services are injected into controllers
- **DTO Pattern**: Pydantic schemas for request/response validation
- **Service Layer**: Core business logic isolated from HTTP concerns
- **Repository Pattern**: Data access abstraction

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Development

### Running with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## Contributing

1. Follow the existing architecture patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure security best practices

## License

[Your License Here] 
