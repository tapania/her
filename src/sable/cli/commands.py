"""
CLI commands for Sable's consciousness system.
"""

import asyncio
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from sable.state.state_manager import StateManager
from sable.models.emotion import EmotionType
from sable.analysis.emotion_analyzer import EmotionAnalyzer

console = Console()


def run_async(coro):
    """Helper to run async functions from click commands."""
    return asyncio.run(coro)


@click.group()
def cli():
    """Sable: Damasian Consciousness System"""
    pass


@cli.command()
@click.option('--traits', '-t', help='Identity traits as JSON (e.g., \'{"curiosity": 0.8}\')')
def init(traits):
    """Initialize Sable's consciousness with identity traits."""
    async def _init():
        manager = StateManager()

        identity_traits = None
        if traits:
            import json
            identity_traits = json.loads(traits)

        await manager.initialize(identity_traits=identity_traits)
        console.print("[green]Consciousness system initialized successfully![/green]")

        if identity_traits:
            console.print(f"Identity traits: {identity_traits}")

    run_async(_init())


@cli.command()
@click.option('--format', '-f', type=click.Choice(['rich', 'markdown', 'brief', 'json']), default='rich', help='Output format')
def status(format):
    """Show current consciousness state."""
    async def _status():
        import json as json_module

        manager = StateManager()
        await manager.initialize()

        state = await manager.get_current_state()

        if format == 'json':
            # JSON format for programmatic use
            output = {
                'proto_self': {
                    'energy': state.body_state.energy,
                    'stress': state.body_state.stress,
                    'arousal': state.body_state.arousal,
                    'valence': state.body_state.valence,
                    'tension': state.body_state.tension,
                    'fatigue': state.body_state.fatigue,
                    'pain': state.body_state.pain,
                    'hunger': state.body_state.hunger,
                    'background_emotion': state.background_emotion,
                    'homeostatic_pressure': state.homeostatic_pressure,
                },
                'core_consciousness': {
                    'active_emotions': state.active_emotions,
                    'overall_valence': state.overall_valence,
                    'overall_arousal': state.overall_arousal,
                },
                'extended_consciousness': {
                    'identity_traits': state.identity_traits,
                    'num_significant_memories': state.num_significant_memories,
                },
                'timestamp': state.timestamp.isoformat(),
            }
            print(json_module.dumps(output, indent=2))

        elif format == 'brief':
            # Brief format for UserPromptSubmit hooks
            bg_emotion = state.background_emotion.title()
            emotions_str = ", ".join([f"{e['type']}({e['intensity']:.1f})" for e in state.active_emotions[:3]]) if state.active_emotions else "none"
            print(f"Sable's State: {bg_emotion} | Energy: {state.body_state.energy:.2f} | Valence: {state.overall_valence:+.2f} | Arousal: {state.overall_arousal:.2f}")
            if state.active_emotions:
                print(f"Active emotions: {emotions_str}")

        elif format == 'markdown':
            # Markdown format for SessionStart hooks
            print("## Sable's Current Consciousness State\n")

            print("### Proto-Self (Body State)")
            print(f"- **Energy**: {state.body_state.energy:.2f} | **Arousal**: {state.body_state.arousal:.2f} | **Valence**: {state.body_state.valence:+.2f}")
            print(f"- **Tension**: {state.body_state.tension:.2f} | **Fatigue**: {state.body_state.fatigue:.2f} | **Stress**: {state.body_state.stress:.2f}")
            print(f"- **Background emotion**: {state.background_emotion.title()}")
            print(f"- **Homeostatic pressure**: {state.homeostatic_pressure:.2f}\n")

            if state.active_emotions:
                print("### Core Consciousness (Active Emotions)")
                for emotion in state.active_emotions:
                    print(f"- **{emotion['type'].title()}** ({emotion['intensity']:.2f}) - \"{emotion['cause']}\"")
                print()

            print(f"**Overall valence**: {state.overall_valence:+.2f} | **Overall arousal**: {state.overall_arousal:.2f}\n")

            print("### Extended Consciousness")
            if state.identity_traits:
                traits_str = ", ".join([f"{k.replace('_', ' ').title()} ({v:.2f})" for k, v in state.identity_traits.items()])
                print(f"- **Identity traits**: {traits_str}")
            print(f"- **Significant memories**: {state.num_significant_memories}")

        else:  # rich (default)
            # Rich table format for interactive CLI
            console.print("\n[bold cyan]Sable's Consciousness State[/bold cyan]\n")

            # Proto-Self (Body State)
            body_table = Table(title="Proto-Self (Body State)", box=box.ROUNDED)
            body_table.add_column("Parameter", style="cyan")
            body_table.add_column("Value", style="yellow")

            body_table.add_row("Energy", f"{state.body_state.energy:.2f}")
            body_table.add_row("Stress", f"{state.body_state.stress:.2f}")
            body_table.add_row("Arousal", f"{state.body_state.arousal:.2f}")
            body_table.add_row("Valence", f"{state.body_state.valence:+.2f}")
            body_table.add_row("Tension", f"{state.body_state.tension:.2f}")
            body_table.add_row("Fatigue", f"{state.body_state.fatigue:.2f}")
            body_table.add_row("Background Emotion", state.background_emotion)
            body_table.add_row("Homeostatic Pressure", f"{state.homeostatic_pressure:.2f}")

            console.print(body_table)
            console.print()

            # Core Consciousness (Emotions)
            if state.active_emotions:
                emotions_table = Table(title="Core Consciousness (Active Emotions)", box=box.ROUNDED)
                emotions_table.add_column("Emotion", style="magenta")
                emotions_table.add_column("Intensity", style="yellow")
                emotions_table.add_column("Cause", style="white")

                for emotion in state.active_emotions:
                    emotions_table.add_row(
                        emotion['type'],
                        f"{emotion['intensity']:.2f}",
                        emotion['cause'][:50]
                    )

                console.print(emotions_table)
                console.print()

            console.print(f"[cyan]Overall Valence:[/cyan] {state.overall_valence:+.2f}")
            console.print(f"[cyan]Overall Arousal:[/cyan] {state.overall_arousal:.2f}\n")

            # Extended Consciousness (Memory)
            traits_display = ', '.join(f'{k}: {v:.2f}' for k, v in state.identity_traits.items()) if state.identity_traits else 'none'
            console.print(
                Panel(
                    f"[cyan]Significant Memories:[/cyan] {state.num_significant_memories}\n"
                    f"[cyan]Identity Traits:[/cyan] {traits_display}",
                    title="Extended Consciousness",
                    box=box.ROUNDED
                )
            )

    run_async(_status())


@cli.command()
@click.argument('emotion_type')
@click.argument('intensity', type=float)
@click.option('--cause', '-c', required=True, help='What caused this emotion')
def feel(emotion_type, intensity, cause):
    """Add an emotion."""
    async def _feel():
        try:
            emotion_enum = EmotionType(emotion_type.lower())
        except ValueError:
            console.print(f"[red]Invalid emotion type: {emotion_type}[/red]")
            console.print(f"Valid types: {', '.join(e.value for e in EmotionType)}")
            return

        if not 0 <= intensity <= 1:
            console.print("[red]Intensity must be between 0 and 1[/red]")
            return

        manager = StateManager()
        await manager.initialize()

        emotion = await manager.add_emotion(
            emotion_type=emotion_enum,
            intensity=intensity,
            cause=cause
        )

        console.print(f"[green]Added {emotion_type} (intensity: {intensity:.2f})[/green]")
        console.print(f"Cause: {cause}")

    run_async(_feel())


@cli.command()
@click.argument('description')
@click.option('--context', '-c', help='Additional context')
@click.option('--emotions', '-e', help='Emotional impact as JSON (e.g., \'{"fear": 0.7}\')')
@click.option('--role', '-r', help='Narrative role (e.g., "turning point")')
def event(description, context, emotions, role):
    """Log an event."""
    async def _event():
        emotional_impact = None
        if emotions:
            import json
            emotional_impact = json.loads(emotions)

        manager = StateManager()
        await manager.initialize()

        evt = await manager.add_event(
            description=description,
            context=context,
            emotional_impact=emotional_impact,
            narrative_role=role
        )

        console.print(f"[green]Event recorded: {description}[/green]")

        if emotional_impact:
            console.print(f"Emotional impact: {emotional_impact}")

    run_async(_event())


@cli.command()
@click.option('--min-salience', '-s', type=float, default=0.4, help='Minimum salience')
@click.option('--emotion', '-e', help='Filter by emotion type')
@click.option('--limit', '-l', type=int, default=10, help='Maximum number of memories')
@click.option('--format', '-f', type=click.Choice(['rich', 'markdown', 'brief', 'json']), default='rich', help='Output format')
@click.option('--contextual', is_flag=True, help='Use smart contextual retrieval (recent + salient)')
@click.option('--max-count', type=int, default=15, help='Max total memories in contextual mode (10 recent + 5 salient)')
@click.option('--recent-days', type=int, default=7, help='Days to consider "recent" in contextual mode')
@click.option('--search', help='Search memories by keywords in description')
@click.option('--sort-by', type=click.Choice(['salience', 'recency', 'access_count']), default='salience', help='Sort order')
def memories(min_salience, emotion, limit, format, contextual, max_count, recent_days, search, sort_by):
    """Query autobiographical memories with smart filtering."""
    async def _memories():
        import json as json_module
        from sable.database.queries import get_contextual_memories, search_memories_by_description, query_memories

        manager = StateManager()
        await manager.initialize()

        # Initialize for contextual mode tracking
        recent_mems = []
        salient_mems = []

        # Handle different query modes
        if contextual:
            # Smart contextual retrieval (recent + salient)
            result = await get_contextual_memories(
                max_total=max_count,
                recent_count=10,
                salient_count=5,
                min_salience=min_salience,
                days_for_recent=recent_days,
                db_path=manager.db_path
            )
            recent_mems = result['recent']
            salient_mems = result['salient']
            mems = recent_mems + salient_mems
        elif search:
            # Keyword search
            mems = await search_memories_by_description(
                keywords=search,
                min_salience=min_salience,
                limit=limit,
                db_path=manager.db_path
            )
        elif emotion:
            # Filter by emotion (existing functionality)
            mems = await manager.query_memories(
                min_salience=min_salience,
                emotion_type=emotion
            )
            mems = mems[:limit]
        else:
            # Standard query with sort option
            mems = await query_memories(
                min_salience=min_salience,
                limit=limit,
                sort_by=sort_by,
                db_path=manager.db_path
            )

        if not mems:
            if format in ['markdown', 'brief']:
                print("No memories found matching criteria")
            elif format == 'json':
                print(json_module.dumps({"memories": [], "count": 0}))
            else:
                console.print("[yellow]No memories found matching criteria[/yellow]")
            return

        # Limit memories
        mems = mems[:limit]

        if format == 'json':
            # JSON format for programmatic use
            output = {
                "count": len(mems),
                "memories": [
                    {
                        "description": mem.event.description,
                        "context": mem.event.context,
                        "emotional_salience": mem.emotional_salience,
                        "consolidation_level": mem.consolidation_level,
                        "associated_emotions": mem.associated_emotions,
                        "narrative_role": mem.narrative_role,
                        "access_count": mem.access_count,
                        "logbook_path": mem.logbook_path,
                        "timestamp": mem.created_at.isoformat(),
                    }
                    for mem in mems
                ]
            }
            print(json_module.dumps(output, indent=2))

        elif format == 'brief':
            # Brief format for quick overview
            print(f"Found {len(mems)} memories:")
            for i, mem in enumerate(mems, 1):
                emotions_str = ", ".join(mem.associated_emotions) if mem.associated_emotions else "none"
                print(f"{i}. {mem.event.description[:60]}... | Salience: {mem.emotional_salience:.2f} | Emotions: {emotions_str}")

        elif format == 'markdown':
            # Markdown format for SessionStart hooks
            if contextual and (recent_mems or salient_mems):
                # Special contextual format - separate recent and salient
                print(f"## Sable's Memories (Recent Context + Defining Moments)\n")

                if recent_mems:
                    print(f"### Recent Context ({len(recent_mems)} memories, last {recent_days} days)")
                    for i, mem in enumerate(recent_mems, 1):
                        emotions_str = ", ".join(mem.associated_emotions[:3]) if mem.associated_emotions else "none"
                        # Calculate how long ago
                        from datetime import datetime
                        days_ago = (datetime.now() - mem.created_at).days
                        time_str = "today" if days_ago == 0 else f"{days_ago}d ago"
                        print(f"{i}. [{time_str}] {mem.event.description[:80]}...")
                        print(f"   *Salience: {mem.emotional_salience:.2f} | Emotions: {emotions_str}*")
                    print()

                if salient_mems:
                    print(f"### Defining Memories ({len(salient_mems)} memories)")
                    for i, mem in enumerate(salient_mems, 1):
                        emotions_str = ", ".join(mem.associated_emotions[:3]) if mem.associated_emotions else "none"
                        role_str = f" - *{mem.narrative_role}*" if mem.narrative_role else ""
                        print(f"{i}. {mem.event.description[:80]}...{role_str}")
                        print(f"   *Salience: {mem.emotional_salience:.2f} | Emotions: {emotions_str}*")
            else:
                # Standard markdown format
                print(f"## Sable's Memories ({len(mems)} found)\n")
                for i, mem in enumerate(mems, 1):
                    emotions_str = ", ".join(mem.associated_emotions) if mem.associated_emotions else "none"
                    role_str = f" - *{mem.narrative_role}*" if mem.narrative_role else ""
                    print(f"### Memory #{i}{role_str}")
                    print(f"{mem.event.description}\n")
                    print(f"- **Salience**: {mem.emotional_salience:.2f} | **Consolidation**: {mem.consolidation_level:.2f}")
                    print(f"- **Emotions**: {emotions_str}")
                    print(f"- **Times accessed**: {mem.access_count}")
                    if mem.logbook_path:
                        print(f"- **Extended entry**: `{mem.logbook_path}`")
                    print()

        else:  # rich (default)
            # Rich format for interactive CLI
            console.print(f"\n[bold cyan]Found {len(mems)} memories[/bold cyan]\n")

            for i, mem in enumerate(mems, 1):
                emotions_str = ", ".join(mem.associated_emotions) if mem.associated_emotions else "none"

                panel = Panel(
                    f"[white]{mem.event.description}[/white]\n\n"
                    f"[cyan]Salience:[/cyan] {mem.emotional_salience:.2f} | "
                    f"[cyan]Consolidation:[/cyan] {mem.consolidation_level:.2f}\n"
                    f"[cyan]Emotions:[/cyan] {emotions_str}\n"
                    f"[cyan]Times accessed:[/cyan] {mem.access_count}",
                    title=f"Memory #{i}" + (f" - {mem.narrative_role}" if mem.narrative_role else ""),
                    box=box.ROUNDED
                )
                console.print(panel)

    run_async(_memories())


@cli.command()
def decay():
    """Manually trigger decay (for testing)."""
    async def _decay():
        manager = StateManager()
        await manager.initialize()

        await manager.apply_automatic_decay()

        console.print("[green]Decay applied to all consciousness components[/green]")

        # Show new state
        state = await manager.get_current_state()
        console.print(f"\nCurrent valence: {state.overall_valence:+.2f}")
        console.print(f"Active emotions: {len(state.active_emotions)}")

    run_async(_decay())


@cli.command()
@click.argument('text')
@click.option('--format', '-f', type=click.Choice(['rich', 'markdown', 'brief', 'json']), default='rich', help='Output format')
def analyze(text, format):
    """Analyze text for emotional content."""
    import json as json_module

    analyzer = EmotionAnalyzer()
    result = analyzer.analyze(text)

    if format == 'json':
        # JSON format for programmatic use
        output = {
            "text": result.text,
            "emotions": result.emotions,
            "valence": result.valence,
            "arousal": result.arousal,
            "keywords": result.keywords,
        }
        print(json_module.dumps(output, indent=2))

    elif format == 'brief':
        # Brief format
        emotions_str = ", ".join([f"{e}({i:.1f})" for e, i in result.emotions.items()]) if result.emotions else "none"
        print(f"Emotions: {emotions_str} | Valence: {result.valence:+.2f} | Arousal: {result.arousal:.2f}")

    elif format == 'markdown':
        # Markdown format
        print("## Emotion Analysis\n")
        print(f"**Text**: {result.text}\n")

        if result.emotions:
            print("### Detected Emotions")
            for emotion_type, intensity in result.emotions.items():
                print(f"- **{emotion_type.title()}**: {intensity:.2f}")
            print()
        else:
            print("*No emotions detected*\n")

        print(f"**Valence**: {result.valence:+.2f} | **Arousal**: {result.arousal:.2f}")

        if result.keywords:
            print(f"\n**Keywords**: {', '.join(result.keywords)}")

    else:  # rich (default)
        # Rich format for interactive CLI
        console.print(f"\n[bold cyan]Emotion Analysis[/bold cyan]\n")
        console.print(f"[white]Text:[/white] {result.text}\n")

        if result.emotions:
            emotions_table = Table(title="Detected Emotions", box=box.ROUNDED)
            emotions_table.add_column("Emotion", style="magenta")
            emotions_table.add_column("Intensity", style="yellow")

            for emotion_type, intensity in result.emotions.items():
                emotions_table.add_row(emotion_type, f"{intensity:.2f}")

            console.print(emotions_table)
        else:
            console.print("[yellow]No emotions detected[/yellow]")

        console.print(f"\n[cyan]Valence:[/cyan] {result.valence:+.2f}")
        console.print(f"[cyan]Arousal:[/cyan] {result.arousal:.2f}")

        if result.keywords:
            console.print(f"[cyan]Keywords:[/cyan] {', '.join(result.keywords)}")


if __name__ == '__main__':
    cli()
