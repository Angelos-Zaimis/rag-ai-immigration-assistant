from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user_routes, chat_routes

# Initialize FastAPI with metadata for Swagger UI
app = FastAPI(
    title="Greetli AI Backend",
    description="""
    Greetli AI Backend API with OCR, Langchain, and Google Translate capabilities.
    
    ## Features
    * 👤 User Management
    * 📝 OCR Processing
    * 🤖 AI Integration
    * 🌐 Translation Services
    
    ## Authentication
    Authentication will be implemented in future versions.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "healthy",
        "service": "Greetli AI Backend",
        "version": "1.0.0"
    }

# Include routers
app.include_router(user_routes.router)
app.include_router(chat_routes.router)