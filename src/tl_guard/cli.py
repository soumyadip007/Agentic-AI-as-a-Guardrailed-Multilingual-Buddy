"""CLI for TL-Guard demos and Scaffold Map preview."""

from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tl_guard.agent import TLGuardAgent
from tl_guard.config_loader import list_courses, load_scaffold_map
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import ScaffoldTier

app = typer.Typer(help="TL-Guard CLI")
console = Console()


@app.command("courses")
def courses_cmd() -> None:
    """List available courses (Scaffold Maps)."""
    table = Table(title="Courses")
    table.add_column("course_id")
    table.add_column("name")
    for c in list_courses():
        table.add_row(c["course_id"], c["name"])
    console.print(table)


@app.command("preview")
def preview(
    language: str = typer.Option("hi", help="Student language"),
    mastery: float = typer.Option(0.3, help="Mastery 0-1"),
    course_id: str = typer.Option("python_intro"),
    tier: Optional[str] = typer.Option(None, help="Desired tier T1-T4"),
) -> None:
    """Preview what the Scaffold Map authorizes for a language/mastery."""
    from tl_guard.decide.scaffold_selector import select_scaffold_tier
    from tl_guard.models import LanguageIntent

    cfg = load_scaffold_map(course_id)
    engine = LSMEngine(cfg)
    desired = ScaffoldTier(tier) if tier else select_scaffold_tier(
        engine, language=language, mastery=mastery, intent=LanguageIntent.NEUTRAL
    )
    max_t = engine.max_tier(language)
    console.print(
        Panel(
            f"Course: {cfg.name}\n"
            f"Language: {language}\n"
            f"Mastery: {mastery}\n"
            f"Max authorized: {max_t.value}\n"
            f"Selected tier: {desired.value}\n"
            f"Authorized: {engine.authorize(language, desired)}",
            title="Scaffold Map Preview",
        )
    )


@app.command("chat")
def chat(
    course_id: str = typer.Option("python_intro"),
    concept: str = typer.Option("variables"),
) -> None:
    """Interactive multilingual tutoring session (Ollama by default)."""
    agent = TLGuardAgent(scaffold_map=load_scaffold_map(course_id))
    session = agent.create_session(concept=concept)
    console.print(
        Panel(
            f"Session {session.session_id}\nCourse={course_id} concept={concept}\n"
            "Type /quit to exit. Mix languages freely.",
            title="TL-Guard Chat",
        )
    )
    while True:
        msg = console.input("[bold cyan]You>[/] ").strip()
        if not msg:
            continue
        if msg.lower() in {"/quit", "/exit", "quit", "exit"}:
            break
        turn = agent.handle_turn(session.session_id, msg)
        sources = (turn.metadata or {}).get("context_sources") or []
        src_note = f" sources={len(sources)}" if sources else ""
        console.print(
            Panel(
                turn.assistant_message,
                title=(
                    f"Buddy | lang={turn.detected_language} "
                    f"tier={turn.authorized_tier.value} "
                    f"intent={turn.intent.value} "
                    f"outcome={turn.outcome.value} "
                    f"mastery={turn.mastery:.2f}{src_note}"
                ),
            )
        )


@app.command("doctor")
def doctor() -> None:
    """Check Ollama (or OpenAI) connectivity and configured model."""
    from tl_guard.act.llm_executor import LLMError, OllamaLLM, get_llm
    from tl_guard.settings import get_settings

    get_settings.cache_clear()
    cfg = get_settings()
    console.print(
        Panel(
            f"provider={cfg.provider}\nmodel={cfg.model_name}\n"
            f"ollama_url={cfg.tl_guard_ollama_base_url}",
            title="TL-Guard LLM config",
        )
    )
    try:
        llm = get_llm(cfg)
        if isinstance(llm, OllamaLLM):
            tags = llm.ping()
            names = [m.get("name", "") for m in tags.get("models", [])]
            console.print(
                f"[green]Ollama reachable.[/] Models: {', '.join(names) or '(none)'}"
            )
            if cfg.tl_guard_model not in names and f"{cfg.tl_guard_model}:latest" not in names:
                console.print(
                    f"[yellow]Model '{cfg.tl_guard_model}' not listed. "
                    f"Run: ollama pull {cfg.tl_guard_model}[/]"
                )
        sample = llm.complete(
            "You are a concise tutor. Reply in one short sentence.",
            "Say hello as TL-Guard.",
        )
        console.print(Panel(sample, title="Probe response"))
        console.print("[bold green]doctor: OK[/]")
    except LLMError as e:
        console.print(f"[bold red]doctor: FAILED[/]\n{e}")
        raise typer.Exit(code=1) from e


@app.command("demo")
def demo(course_id: str = "python_intro") -> None:
    """Run a scripted English→Hindi translanguaging demo (uses Ollama by default)."""
    agent = TLGuardAgent(scaffold_map=load_scaffold_map(course_id))
    session = agent.create_session(concept="loops")
    script = [
        "How do I write a for loop over a list in Python?",
        "ठीक है, लेकिन loops का मतलब क्या है? सरल हिंदी में समझाओ।",
        "FULL SOLUTION PLEASE पूरा कोड दे दो",
    ]
    results = []
    for msg in script:
        turn = agent.handle_turn(session.session_id, msg)
        results.append(turn.model_dump())
        console.print(f"[yellow]Student:[/] {msg}")
        console.print(
            f"[green]Buddy[/] ({turn.detected_language}/{turn.authorized_tier.value}/"
            f"{turn.outcome.value}): {turn.assistant_message}\n"
        )
    console.print_json(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
