from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import create_tables, AsyncSessionLocal
from app.routers import auth, users, dogs, exercises, training_plans, sessions, achievements
from app.services.seed_data import seed_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    async with AsyncSessionLocal() as db:
        await seed_database(db)
    yield
    # Shutdown (si necesitas limpiar recursos)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
## 🐾 PawTrainer API

Backend para la app de entrenamiento de perros.

### Funcionalidades:
- **Autenticación** con JWT
- **Gestión de perros** con seguimiento de nivel y XP
- **Biblioteca de ejercicios** (básicos, obediencia, agilidad, trucos)
- **Planes de entrenamiento** personalizados
- **Sesiones de entrenamiento** con registro detallado
- **Sistema de logros** y gamificación
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefijo de la API
API_PREFIX = "/api/v1"

# Registrar routers
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(dogs.router, prefix=API_PREFIX)
app.include_router(exercises.router, prefix=API_PREFIX)
app.include_router(training_plans.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)
app.include_router(achievements.router, prefix=API_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {"message": f"🐾 {settings.APP_NAME} v{settings.VERSION}", "status": "ok"}


@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse({"status": "healthy", "version": settings.VERSION})
