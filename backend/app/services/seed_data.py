"""Datos iniciales para poblar la base de datos."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.exercise import Exercise, ExerciseCategory, DifficultyLevel
from app.models.achievement import Achievement


EXERCISES = [
    # Básicos
    {"name": "Sentarse (Sit)", "category": ExerciseCategory.BASICO, "difficulty": DifficultyLevel.FACIL,
     "description": "El perro aprende a sentarse ante la orden 'Siéntate'.",
     "instructions": "1. Sostén una golosina sobre la nariz del perro.\n2. Mueve la mano hacia atrás lentamente.\n3. Cuando se siente, di 'Siéntate' y recompénsalo.",
     "duration_seconds": 60, "xp_reward": 10, "icon": "🐕"},
    {"name": "Tumbarse (Down)", "category": ExerciseCategory.BASICO, "difficulty": DifficultyLevel.FACIL,
     "description": "El perro aprende a tumbarse.",
     "instructions": "1. Pide que se siente primero.\n2. Baja la golosina al suelo lentamente.\n3. Cuando se tumbe, di 'Échate' y premia.",
     "duration_seconds": 60, "xp_reward": 10, "icon": "🐾"},
    {"name": "Quedarse quieto (Stay)", "category": ExerciseCategory.OBEDIENCIA, "difficulty": DifficultyLevel.MEDIO,
     "description": "El perro permanece en su lugar hasta recibir la señal.",
     "instructions": "1. Ordena 'Siéntate'.\n2. Di 'Quieto' con la mano abierta.\n3. Retrocede unos pasos y vuelve.\n4. Premia si no se movió.",
     "duration_seconds": 90, "xp_reward": 20, "icon": "✋"},
    {"name": "Venir (Come)", "category": ExerciseCategory.OBEDIENCIA, "difficulty": DifficultyLevel.FACIL,
     "description": "El perro acude cuando lo llamas.",
     "instructions": "1. Aléjate unos metros.\n2. Llama a tu perro por nombre + 'Ven'.\n3. Premia con entusiasmo al llegar.",
     "duration_seconds": 60, "xp_reward": 15, "icon": "📣"},
    {"name": "Talón (Heel)", "category": ExerciseCategory.OBEDIENCIA, "difficulty": DifficultyLevel.DIFICIL,
     "description": "Caminar junto al dueño sin tirar de la correa.",
     "instructions": "1. Coloca al perro a tu izquierda.\n2. Camina y di 'Junto' o 'Aquí'.\n3. Premia cuando camine al nivel de tu pierna.",
     "duration_seconds": 120, "xp_reward": 30, "icon": "🚶"},
    {"name": "Dame la pata (Shake)", "category": ExerciseCategory.TRUCOS, "difficulty": DifficultyLevel.FACIL,
     "description": "El perro levanta una pata para saludar.",
     "instructions": "1. Pide que se siente.\n2. Toca suavemente su pata.\n3. Cuando la levante, di 'Dame la pata' y premia.",
     "duration_seconds": 60, "xp_reward": 10, "icon": "🤝"},
    {"name": "Gira (Spin)", "category": ExerciseCategory.TRUCOS, "difficulty": DifficultyLevel.MEDIO,
     "description": "El perro da una vuelta completa.",
     "instructions": "1. Sostén una golosina ante la nariz.\n2. Mueve la mano en círculo.\n3. Cuando complete la vuelta, di 'Gira' y premia.",
     "duration_seconds": 60, "xp_reward": 20, "icon": "🌀"},
    {"name": "Saltar obstáculo", "category": ExerciseCategory.AGILIDAD, "difficulty": DifficultyLevel.MEDIO,
     "description": "El perro salta sobre un obstáculo bajo.",
     "instructions": "1. Coloca un obstáculo bajo (20-30cm).\n2. Guía al perro con la correa hacia él.\n3. Anímalo con '¡Salta!' y premia al cruzar.",
     "duration_seconds": 90, "xp_reward": 25, "icon": "⬆️"},
    {"name": "Socialización en parque", "category": ExerciseCategory.SOCIALIZACION, "difficulty": DifficultyLevel.FACIL,
     "description": "Exposición controlada a otros perros y personas.",
     "instructions": "1. Ve al parque en horas de poco tráfico.\n2. Permite que explore a su ritmo.\n3. Recompensa comportamientos calmados.",
     "duration_seconds": 1800, "xp_reward": 30, "icon": "🌳"},
    {"name": "No morder (Bite inhibition)", "category": ExerciseCategory.COMPORTAMIENTO, "difficulty": DifficultyLevel.MEDIO,
     "description": "Enseñar al perro a controlar la presión de su mordida.",
     "instructions": "1. Si muerde al jugar, di '¡Ay!' y para el juego.\n2. Ignóralo 30 segundos.\n3. Retoma el juego. Repite consistentemente.",
     "duration_seconds": 300, "xp_reward": 20, "icon": "🦷"},
]

ACHIEVEMENTS = [
    {"name": "Primera Sesión 🐣", "description": "Completaste tu primera sesión de entrenamiento",
     "icon": "🐣", "xp_reward": 50, "condition_type": "sessions_completed", "condition_value": 1},
    {"name": "Entrena Duro 💪", "description": "Completaste 10 sesiones de entrenamiento",
     "icon": "💪", "xp_reward": 100, "condition_type": "sessions_completed", "condition_value": 10},
    {"name": "Maestro del Ring 🏆", "description": "Completaste 50 sesiones de entrenamiento",
     "icon": "🏆", "xp_reward": 500, "condition_type": "sessions_completed", "condition_value": 50},
    {"name": "Primeros Puntos ⭐", "description": "Tu perro acumuló 100 XP",
     "icon": "⭐", "xp_reward": 25, "condition_type": "total_xp", "condition_value": 100},
    {"name": "Perro Estrella 🌟", "description": "Tu perro acumuló 500 XP",
     "icon": "🌟", "xp_reward": 100, "condition_type": "total_xp", "condition_value": 500},
    {"name": "Campeón 🥇", "description": "Tu perro acumuló 1000 XP y llegó al nivel Avanzado",
     "icon": "🥇", "xp_reward": 250, "condition_type": "total_xp", "condition_value": 1000},
]


async def seed_database(db: AsyncSession) -> None:
    """Poblar la base de datos con datos iniciales."""
    # Seed exercises
    for ex_data in EXERCISES:
        result = await db.execute(select(Exercise).where(Exercise.name == ex_data["name"]))
        if not result.scalar_one_or_none():
            db.add(Exercise(**ex_data))

    # Seed achievements
    for ach_data in ACHIEVEMENTS:
        result = await db.execute(
            select(Achievement).where(Achievement.name == ach_data["name"])
        )
        if not result.scalar_one_or_none():
            db.add(Achievement(**ach_data))

    await db.commit()
