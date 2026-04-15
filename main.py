#!/usr/bin/env python3
"""
Generador de preguntas tipo test con IA
Usa Claude (Anthropic) para generar, clasificar y almacenar preguntas.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box

import database as db
from generator import generate_questions

console = Console()

DIFFICULTY_COLORS = {
    "Fácil": "green",
    "Media": "yellow",
    "Difícil": "red",
}

ANSWER_LABELS = {"A": "🅐", "B": "🅑", "C": "🅒", "D": "🅓"}


# ─────────────────────────── helpers ────────────────────────────────────────

def print_header() -> None:
    console.print(Panel.fit(
        "[bold cyan]🤖 Generador de Preguntas Tipo Test con IA[/bold cyan]\n"
        "[dim]Powered by Claude (Anthropic)[/dim]",
        border_style="cyan",
    ))


def print_question_table(questions: list[dict], show_answers: bool = False) -> None:
    """Muestra preguntas en una tabla Rich."""
    if not questions:
        console.print("[yellow]No se encontraron preguntas.[/yellow]")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("ID", style="dim", width=4, justify="right")
    table.add_column("Pregunta", min_width=30)
    table.add_column("Categoría", style="cyan", width=18)
    table.add_column("Dificultad", width=10, justify="center")
    table.add_column("Tema", style="dim", width=16)

    for q in questions:
        diff = q["difficulty"]
        color = DIFFICULTY_COLORS.get(diff, "white")
        table.add_row(
            str(q["id"]),
            q["question"][:80] + ("…" if len(q["question"]) > 80 else ""),
            q["category"],
            f"[{color}]{diff}[/{color}]",
            q["topic"][:16],
        )

    console.print(table)
    console.print(f"[dim]Total: {len(questions)} pregunta(s)[/dim]")


def print_question_detail(q: dict) -> None:
    """Muestra el detalle completo de una pregunta."""
    diff = q["difficulty"]
    color = DIFFICULTY_COLORS.get(diff, "white")

    console.print(Panel(
        f"[bold]{q['question']}[/bold]",
        title=f"[cyan]{q['category']}[/cyan]  [{color}]{diff}[/{color}]  [dim]Tema: {q['topic']}[/dim]",
        border_style="blue",
    ))

    options = {
        "A": q["option_a"],
        "B": q["option_b"],
        "C": q["option_c"],
        "D": q["option_d"],
    }
    correct = q["correct_answer"]

    for letter, text in options.items():
        if letter == correct:
            console.print(f"  [bold green]✓ {letter})[/bold green] [green]{text}[/green]")
        else:
            console.print(f"    {letter}) {text}")

    console.print(f"\n[dim]💡 {q['explanation']}[/dim]")


# ─────────────────────────── menú acciones ──────────────────────────────────

def action_generate() -> None:
    """Genera nuevas preguntas con IA y las guarda en la BD."""
    console.print("\n[bold cyan]── Generar nuevas preguntas ──[/bold cyan]")

    topic = Prompt.ask("[bold]Tema de las preguntas[/bold]")
    if not topic.strip():
        console.print("[red]El tema no puede estar vacío.[/red]")
        return

    count = IntPrompt.ask(
        "[bold]¿Cuántas preguntas?[/bold]",
        default=5,
        show_default=True,
    )
    if count < 1 or count > 30:
        console.print("[red]Elige entre 1 y 30 preguntas.[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(
            f"[cyan]Generando {count} pregunta(s) sobre '{topic}' con Claude…[/cyan]",
            total=None,
        )
        try:
            questions = generate_questions(topic, count)
        except EnvironmentError as e:
            console.print(f"\n[bold red]Error de configuración:[/bold red] {e}")
            return
        except Exception as e:
            console.print(f"\n[bold red]Error al generar preguntas:[/bold red] {e}")
            return

    saved = db.save_questions(questions, topic)
    console.print(f"\n[bold green]✅ {saved} pregunta(s) generadas y guardadas.[/bold green]")

    # Vista previa
    console.print("\n[bold]Vista previa:[/bold]")
    for i, q in enumerate(questions, 1):
        diff = q.difficulty
        color = DIFFICULTY_COLORS.get(diff, "white")
        console.print(
            f"  {i}. [{color}]{diff}[/{color}] [cyan]{q.category}[/cyan] — {q.question[:70]}…"
        )


def action_list() -> None:
    """Lista preguntas con filtros opcionales."""
    console.print("\n[bold cyan]── Listar preguntas ──[/bold cyan]")

    categories = db.get_categories()
    category_filter = None
    difficulty_filter = None

    if categories:
        console.print("[dim]Categorías disponibles:[/dim] " + ", ".join(categories))
        cat_input = Prompt.ask(
            "Filtrar por categoría [dim](Enter para todas)[/dim]",
            default="",
        )
        if cat_input.strip():
            category_filter = cat_input.strip()

    diff_input = Prompt.ask(
        "Filtrar por dificultad [dim](Fácil/Media/Difícil, Enter para todas)[/dim]",
        default="",
    )
    if diff_input.strip() in ("Fácil", "Media", "Difícil"):
        difficulty_filter = diff_input.strip()

    questions = db.get_questions(category=category_filter, difficulty=difficulty_filter)
    console.print()
    print_question_table(questions)

    if questions:
        see_detail = Confirm.ask("\n¿Ver detalle de alguna pregunta?", default=False)
        if see_detail:
            qid = IntPrompt.ask("ID de la pregunta")
            matches = [q for q in questions if q["id"] == qid]
            if matches:
                print_question_detail(matches[0])
            else:
                console.print("[yellow]ID no encontrado.[/yellow]")


def action_quiz() -> None:
    """Modo examen: responde preguntas aleatorias y puntúa."""
    console.print("\n[bold cyan]── Modo Examen ──[/bold cyan]")

    stats = db.get_stats()
    if stats["total"] == 0:
        console.print("[yellow]No hay preguntas en la base de datos. Genera algunas primero.[/yellow]")
        return

    count = IntPrompt.ask("¿Cuántas preguntas quieres responder?", default=5)

    categories = db.get_categories()
    category_filter = None
    if categories:
        console.print("[dim]Categorías:[/dim] " + ", ".join(categories))
        cat_input = Prompt.ask("Categoría [dim](Enter para todas)[/dim]", default="")
        if cat_input.strip() in categories:
            category_filter = cat_input.strip()

    diff_input = Prompt.ask(
        "Dificultad [dim](Fácil/Media/Difícil, Enter para todas)[/dim]",
        default="",
    )
    difficulty_filter = diff_input.strip() if diff_input.strip() in ("Fácil", "Media", "Difícil") else None

    questions = db.get_random_questions(count, category=category_filter, difficulty=difficulty_filter)

    if not questions:
        console.print("[yellow]No hay preguntas con esos filtros.[/yellow]")
        return

    score = 0
    total = len(questions)

    console.print(f"\n[bold]Comenzando examen: {total} pregunta(s)[/bold]\n")

    for i, q in enumerate(questions, 1):
        diff = q["difficulty"]
        color = DIFFICULTY_COLORS.get(diff, "white")

        console.print(Panel(
            f"[bold]{q['question']}[/bold]",
            title=f"[dim]Pregunta {i}/{total}[/dim]  [{color}]{diff}[/{color}]  [cyan]{q['category']}[/cyan]",
            border_style="blue",
        ))
        console.print(f"  A) {q['option_a']}")
        console.print(f"  B) {q['option_b']}")
        console.print(f"  C) {q['option_c']}")
        console.print(f"  D) {q['option_d']}")

        answer = ""
        while answer not in ("A", "B", "C", "D"):
            answer = Prompt.ask("\n[bold]Tu respuesta[/bold] (A/B/C/D)").strip().upper()

        if answer == q["correct_answer"]:
            score += 1
            console.print("[bold green]✅ ¡Correcto![/bold green]")
        else:
            console.print(
                f"[bold red]❌ Incorrecto.[/bold red] "
                f"La respuesta era [bold green]{q['correct_answer']})[/bold green]"
            )

        console.print(f"[dim]💡 {q['explanation']}[/dim]\n")

    pct = (score / total) * 100
    result_color = "green" if pct >= 70 else "yellow" if pct >= 40 else "red"
    console.print(Panel(
        f"[bold {result_color}]Resultado: {score}/{total} ({pct:.0f}%)[/bold {result_color}]",
        title="🏆 Fin del Examen",
        border_style=result_color,
    ))


def action_stats() -> None:
    """Muestra estadísticas de la base de datos."""
    console.print("\n[bold cyan]── Estadísticas ──[/bold cyan]")

    stats = db.get_stats()

    if stats["total"] == 0:
        console.print("[yellow]La base de datos está vacía. Genera preguntas primero.[/yellow]")
        return

    console.print(f"\n[bold]Total de preguntas:[/bold] [cyan]{stats['total']}[/cyan]\n")

    # Por dificultad
    diff_table = Table(title="Por Dificultad", box=box.SIMPLE)
    diff_table.add_column("Dificultad", style="bold")
    diff_table.add_column("Preguntas", justify="right")
    for diff, count in stats["by_difficulty"].items():
        color = DIFFICULTY_COLORS.get(diff, "white")
        diff_table.add_row(f"[{color}]{diff}[/{color}]", str(count))
    console.print(diff_table)

    # Por categoría
    cat_table = Table(title="Por Categoría", box=box.SIMPLE)
    cat_table.add_column("Categoría", style="cyan")
    cat_table.add_column("Preguntas", justify="right")
    for cat, count in stats["by_category"].items():
        cat_table.add_row(cat, str(count))
    console.print(cat_table)

    # Por tema
    topic_table = Table(title="Por Tema (top 10)", box=box.SIMPLE)
    topic_table.add_column("Tema", style="dim")
    topic_table.add_column("Preguntas", justify="right")
    for topic, count in stats["by_topic"].items():
        topic_table.add_row(topic, str(count))
    console.print(topic_table)


def action_delete() -> None:
    """Elimina una pregunta por su ID."""
    console.print("\n[bold cyan]── Eliminar pregunta ──[/bold cyan]")

    questions = db.get_questions(limit=20)
    if not questions:
        console.print("[yellow]No hay preguntas en la base de datos.[/yellow]")
        return

    print_question_table(questions)

    qid = IntPrompt.ask("\nID de la pregunta a eliminar (0 para cancelar)", default=0)
    if qid == 0:
        return

    if Confirm.ask(f"[red]¿Eliminar pregunta #{qid}?[/red]", default=False):
        if db.delete_question(qid):
            console.print(f"[green]Pregunta #{qid} eliminada.[/green]")
        else:
            console.print(f"[yellow]No se encontró la pregunta #{qid}.[/yellow]")


# ─────────────────────────── menú principal ─────────────────────────────────

MENU_OPTIONS = {
    "1": ("🧠  Generar preguntas con IA", action_generate),
    "2": ("📋  Listar preguntas",         action_list),
    "3": ("📝  Modo examen",              action_quiz),
    "4": ("📊  Estadísticas",            action_stats),
    "5": ("🗑️   Eliminar pregunta",       action_delete),
    "0": ("🚪  Salir",                   None),
}


def main() -> None:
    db.init_db()
    print_header()

    while True:
        console.print("\n[bold]Menú principal:[/bold]")
        for key, (label, _) in MENU_OPTIONS.items():
            console.print(f"  [cyan]{key}[/cyan]  {label}")

        choice = Prompt.ask("\n[bold]Elige una opción[/bold]", default="0")

        if choice not in MENU_OPTIONS:
            console.print("[red]Opción no válida.[/red]")
            continue

        label, action = MENU_OPTIONS[choice]

        if action is None:
            console.print("\n[dim]¡Hasta pronto![/dim]")
            sys.exit(0)

        action()


if __name__ == "__main__":
    main()
