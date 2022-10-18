import click
from .server import PluginServer


@click.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8484, help="Port to bind to")
@click.option("--debug", default=False, is_flag=True, help="Enable debug mode")
def main(host, port, debug):
    server = PluginServer()
    server.run(host=host, port=port, debug=debug)
