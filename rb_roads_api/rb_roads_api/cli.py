import click
from threading import Thread
from trogon import tui


@tui(command="ui", help="Launch the TUI.")
@click.group()
def cli():
    pass


@cli.command()
@click.option('--host', '-H', type=str, default='0.0.0.0', help='Host to run the uvicorn app on.')
@click.option("--port", "-p", type=int, default=5000, help="Port to run the uvicorn app on.")
@click.option("--bg", is_flag=True, help="Run the uvicorn app in the background.")
def runserver(host: str, port: int, bg: bool):
    """Launch the uvicorn app on port 5000."""
    import uvicorn
    if bg:
        def run_uvicorn():
            uvicorn.run("rb_roads_api.api:app", host=host, port=port)
        Thread(
            target=run_uvicorn,
            daemon=True
        ).start()
    else:
        uvicorn.run("rb_roads_api.api:app", host=host, port=port)
