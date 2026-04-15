from pydantic import BaseModel, Field
from typing import Literal, List


class TestQuestion(BaseModel):
    question: str = Field(description="El texto completo de la pregunta tipo test")
    option_a: str = Field(description="Opción de respuesta A")
    option_b: str = Field(description="Opción de respuesta B")
    option_c: str = Field(description="Opción de respuesta C")
    option_d: str = Field(description="Opción de respuesta D")
    correct_answer: Literal["A", "B", "C", "D"] = Field(
        description="La letra de la respuesta correcta (A, B, C o D)"
    )
    explanation: str = Field(
        description="Explicación detallada de por qué la respuesta es correcta"
    )
    category: str = Field(
        description=(
            "Categoría temática de la pregunta, por ejemplo: "
            "Matemáticas, Historia, Ciencias, Programación, Literatura, Geografía, etc."
        )
    )
    difficulty: Literal["Fácil", "Media", "Difícil"] = Field(
        description="Nivel de dificultad de la pregunta"
    )


class QuestionBank(BaseModel):
    questions: List[TestQuestion] = Field(
        description="Lista de preguntas tipo test generadas"
    )
