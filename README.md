# 🐾 App para Entrenar a Perros

Una aplicación completa para gestionar el entrenamiento de perros con seguimiento de progreso, planes personalizados y sistema de logros.

---

## 🏗️ Arquitectura

```
App-para-entrenar-a-Perros/
├── backend/              ← API REST con FastAPI
│   ├── app/
│   │   ├── main.py       ← Entrada de la aplicación
│   │   ├── config.py     ← Configuración (ENV)
│   │   ├── database.py   ← Conexión async a BD
│   │   ├── models/       ← Modelos SQLAlchemy (ORM)
│   │   ├── schemas/      ← Validación Pydantic
│   │   ├── routers/      ← Endpoints de la API
│   │   ├── services/     ← Lógica de negocio
│   │   └── core/         ← Seguridad y dependencias
│   ├── tests/            ← Tests con pytest
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Inicio Rápido

### Con Docker
```bash
docker-compose up --build
```

### Sin Docker (desarrollo)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

La API estará en: **http://localhost:8000**
Documentación interactiva: **http://localhost:8000/docs**

---

## 📡 Endpoints de la API

### 🔐 Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Iniciar sesión (JWT) |

### 👤 Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Perfil propio |
| PATCH | `/api/v1/users/me` | Actualizar perfil |

### 🐕 Perros
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/dogs/` | Registrar perro |
| GET | `/api/v1/dogs/` | Listar mis perros |
| GET | `/api/v1/dogs/{id}` | Obtener perro |
| PATCH | `/api/v1/dogs/{id}` | Actualizar perro |
| DELETE | `/api/v1/dogs/{id}` | Eliminar perro |
| GET | `/api/v1/dogs/{id}/stats` | Estadísticas |

### 📚 Ejercicios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/exercises/` | Biblioteca de ejercicios |
| GET | `/api/v1/exercises/?category=básico` | Filtrar por categoría |
| POST | `/api/v1/exercises/` | Crear ejercicio |

### 📋 Planes de Entrenamiento
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/dogs/{id}/plans/` | Crear plan |
| GET | `/api/v1/dogs/{id}/plans/` | Listar planes |
| GET | `/api/v1/dogs/{id}/plans/{plan_id}` | Ver plan |
| PATCH | `/api/v1/dogs/{id}/plans/{plan_id}` | Actualizar plan |
| DELETE | `/api/v1/dogs/{id}/plans/{plan_id}` | Eliminar plan |

### 🎯 Sesiones de Entrenamiento
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/dogs/{id}/sessions/` | Iniciar sesión |
| GET | `/api/v1/dogs/{id}/sessions/` | Historial |
| POST | `/api/v1/dogs/{id}/sessions/{sid}/exercises` | Registrar ejercicio |
| POST | `/api/v1/dogs/{id}/sessions/{sid}/complete` | Completar sesión |

### 🏆 Logros
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/achievements` | Todos los logros |
| GET | `/api/v1/dogs/{id}/achievements` | Logros del perro |

---

## 🗄️ Modelos de Datos

```
User ──────┐
           │ (1:N)
           ▼
          Dog ─────── TrainingPlan ──── PlanExercise ──── Exercise
           │                │
           │ (1:N)          │ (1:N)
           ▼                ▼
    TrainingSession ─── SessionExerciseLog ──── Exercise
           │
           ▼
    DogAchievement ──── Achievement
```

### Niveles de Entrenamiento (XP)
- 🟢 **Principiante**: 0 - 299 XP
- 🟡 **Intermedio**: 300 - 999 XP  
- 🔴 **Avanzado**: 1000+ XP

### Categorías de Ejercicios
- 🐾 Básico (sit, down, stay, come)
- ✋ Obediencia (heel, stay extendido)
- 🌀 Trucos (spin, shake, roll over)
- ⬆️ Agilidad (saltos, slalom)
- 🌳 Socialización
- 🦷 Comportamiento

---

## 🧪 Tests

```bash
cd backend
python -m pytest tests/ -v
```

15 tests cubren: autenticación, CRUD de perros, ejercicios, planes y flujo completo de sesiones.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Framework | **FastAPI** |
| ORM | **SQLAlchemy 2.0** (async) |
| Base de datos | **SQLite** (dev) / PostgreSQL (prod) |
| Autenticación | **JWT** (python-jose) |
| Validación | **Pydantic v2** |
| Tests | **pytest + httpx** |
| Deploy | **Docker + docker-compose** |
