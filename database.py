import sqlite3
from pathlib import Path
from typing import Optional
from models import TestQuestion

DB_PATH = Path(__file__).parent / "questions.db"


def init_db() -> None:
    """Crea la base de datos y la tabla de preguntas si no existen."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic       TEXT    NOT NULL,
                question    TEXT    NOT NULL,
                option_a    TEXT    NOT NULL,
                option_b    TEXT    NOT NULL,
                option_c    TEXT    NOT NULL,
                option_d    TEXT    NOT NULL,
                correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
                explanation TEXT    NOT NULL,
                category    TEXT    NOT NULL,
                difficulty  TEXT    NOT NULL CHECK(difficulty IN ('Fácil','Media','Difícil')),
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_questions(questions: list[TestQuestion], topic: str) -> int:
    """Guarda una lista de preguntas en la base de datos. Devuelve el número guardadas."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            INSERT INTO questions
                (topic, question, option_a, option_b, option_c, option_d,
                 correct_answer, explanation, category, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    topic,
                    q.question,
                    q.option_a,
                    q.option_b,
                    q.option_c,
                    q.option_d,
                    q.correct_answer,
                    q.explanation,
                    q.category,
                    q.difficulty,
                )
                for q in questions
            ],
        )
        conn.commit()
    return len(questions)


def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    """Recupera preguntas de la base de datos con filtros opcionales."""
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
    if topic:
        query += " AND topic LIKE ?"
        params.append(f"%{topic}%")

    query += " ORDER BY created_at DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_categories() -> list[str]:
    """Devuelve las categorías únicas existentes en la BD."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM questions ORDER BY category"
        ).fetchall()
    return [row[0] for row in rows]


def get_stats() -> dict:
    """Devuelve estadísticas de la base de datos."""
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        by_difficulty = conn.execute(
            "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty"
        ).fetchall()
        by_category = conn.execute(
            "SELECT category, COUNT(*) FROM questions GROUP BY category ORDER BY COUNT(*) DESC"
        ).fetchall()
        by_topic = conn.execute(
            "SELECT topic, COUNT(*) FROM questions GROUP BY topic ORDER BY COUNT(*) DESC LIMIT 10"
        ).fetchall()

    return {
        "total": total,
        "by_difficulty": dict(by_difficulty),
        "by_category": dict(by_category),
        "by_topic": dict(by_topic),
    }


def delete_question(question_id: int) -> bool:
    """Elimina una pregunta por su ID. Devuelve True si se eliminó."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM questions WHERE id = ?", (question_id,)
        )
        conn.commit()
    return cursor.rowcount > 0


def get_random_questions(
    count: int,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> list[dict]:
    """Devuelve preguntas aleatorias para un examen."""
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(count)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]
