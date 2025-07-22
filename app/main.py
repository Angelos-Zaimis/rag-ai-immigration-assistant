from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user_routes, chat_routes, documents_routes, auth_routes
from app.services.cron_jobs.immi_web_scrape_cron_job import ImmigrationWebScrapeCronJob

scheduler = AsyncIOScheduler()

# Initialize FastAPI with metadata for Swagger UI
app = FastAPI(
    title="Greetli AI Backend",
    description="""
    Greetli AI Backend API with OCR, Langchain, Google Translate, and JWT Authentication capabilities.
    
    ## Features
    * 🔐 JWT Authentication (Register, Login, Refresh)
    * 👤 User Management
    * 📝 OCR Processing
    * 🤖 AI Integration
    * 🌐 Translation Services
    
    ## Authentication
    
    This API uses JWT (JSON Web Tokens) for authentication:
    
    1. **Register** or **Login** to get access and refresh tokens
    2. **Access Token**: Short-lived (15 minutes) - use for API requests
    3. **Refresh Token**: Long-lived (7 days) - use to get new access tokens
    4. **Protected Endpoints**: Include `Authorization: Bearer <access_token>` header
    
    ### Example Usage:
    
    1. Register: `POST /auth/register` with email and password
    2. Get tokens in response
    3. Use access token: `Authorization: Bearer eyJ0eXAiOiJKV1Q...`
    4. Refresh when needed: `POST /auth/refresh` with refresh token
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
        "version": "1.0.0",
        "features": ["JWT Authentication", "User Management", "OCR", "AI Integration", "Translation"]
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    immigration_cron_job = ImmigrationWebScrapeCronJob()

    scheduler.add_job(
        immigration_cron_job.scrape_immigration_info_weekly,
        trigger=CronTrigger(day_of_week="wed", hour=9, minute=0),
        id="immigration_weekly_scrape_job",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started...")

    yield

    scheduler.shutdown()
    print("Scheduler stopped.")

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(chat_routes.router)
app.include_router(documents_routes.router)