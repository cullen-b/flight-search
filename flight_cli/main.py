"""CLI entry point."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import click
from dotenv import load_dotenv

# Load .env at startup
load_dotenv(Path(__file__).parent.parent / ".env")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--config", "-c", default=None, help="Path to config.yaml")
@click.option("--filter", "-f", "named_filter", default=None,
              help="Apply a named filter from config.yaml (e.g. 'nonstop_only')")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--mock", is_flag=True, help="Force mock provider (ignore API credentials)")
def main(config: str | None, named_filter: str | None, debug: bool, mock: bool) -> None:
    """✈  Flight Search — interactive terminal flight finder.\n
    \b
    Usage:
      flights                 Launch interactive TUI
      flights --mock          Demo mode (no API key needed)
      flights -f nonstop_only Pre-apply a named filter
      flights -c my.yaml      Use a custom config file

    \b
    Keyboard shortcuts in the results view:
      p  Sort by price       d  Sort by duration
      t  Sort by departure   a  Sort by arrival
      f  Focus filter panel  r  Refresh results
      ESC  Back to search    Ctrl+Q  Quit
    """
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
        )
    else:
        logging.basicConfig(level=logging.WARNING)

    if mock:
        # Clear credentials to force mock provider
        os.environ.pop("AMADEUS_CLIENT_ID", None)
        os.environ.pop("AMADEUS_CLIENT_SECRET", None)

    from flight_cli.config import load_config
    from flight_cli.cli.app import FlightSearchApp

    app_config = load_config(config)
    app = FlightSearchApp(config=app_config)
    app.run()


if __name__ == "__main__":
    main()
