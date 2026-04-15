import os
import anthropic
from models import TestQuestion, QuestionBank

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """Eres un experto pedagogo y generador de contenido educativo.
Tu tarea es crear preguntas tipo test de alta calidad sobre el tema solicitado.

Para cada pregunta debes:
1. Redactar una pregunta clara, precisa y sin ambigüedad.
2. Crear cuatro opciones de respuesta plausibles (A, B, C, D), donde solo una es correcta.
3. Identificar la respuesta correcta.
4. Proporcionar una explicación didáctica de por qué es correcta.
5. Clasificar la pregunta en una categoría temática adecuada.
6. Asignar un nivel de dificultad:
   - Fácil: conocimiento básico, hechos directos.
   - Media: comprensión y aplicación de conceptos.
   - Difícil: análisis, síntesis o conocimiento especializado.

Genera preguntas variadas en dificultad y asegúrate de que los distractores
(respuestas incorrectas) sean creíbles pero claramente erróneos para quien conoce el tema."""


def generate_questions(topic: str, count: int) -> list[TestQuestion]:
    """
    Genera 'count' preguntas tipo test sobre 'topic' usando Claude.
    Devuelve una lista de objetos TestQuestion validados.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Falta la variable de entorno ANTHROPIC_API_KEY. "
            "Configúrala antes de ejecutar la aplicación."
        )

    client = anthropic.Anthropic(api_key=api_key)

    user_prompt = (
        f"Genera exactamente {count} preguntas tipo test sobre el siguiente tema: "
        f'"{topic}".\n\n'
        f"Asegúrate de incluir preguntas de distintos niveles de dificultad "
        f"(Fácil, Media, Difícil) y asigna la categoría temática más adecuada a cada una."
    )

    response = client.messages.parse(
        model=MODEL,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        output_format=QuestionBank,
    )

    bank: QuestionBank = response.parsed_output
    if bank is None:
        raise ValueError("La IA no devolvió preguntas válidas. Inténtalo de nuevo.")

    return bank.questions
