#!/usr/bin/env python3
"""Main entry point for the back-to-back AI chat application."""

import argparse
import logging
import sys
from typing import Optional

import uvicorn

from . import __package_name__, __version__

# Configure logging
logger = logging.getLogger(__name__)


def setup_logging(verbosity: int) -> None:
    """Configure logging based on verbosity level."""
    log_levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    level = log_levels.get(min(verbosity, 2), logging.DEBUG)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog=__package_name__,
        description="Back-to-Back AI Chat API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{__package_name__} {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be repeated: -v, -vv, -vvv)",
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    return parser.parse_args(args)


def main(args: Optional[list[str]] = None) -> int:
    """Main entry point for the back-to-back command."""
    try:
        parsed_args = parse_args(args)
        setup_logging(parsed_args.verbose)

        logger.debug("Starting %s v%s", __package_name__, __version__)
        logger.info("Verbose mode enabled") if parsed_args.verbose else None

        # Start the FastAPI server
        logger.info("Starting Back-to-Back AI Chat API server...")
        logger.info("Server will be available at http://%s:%d", parsed_args.host, parsed_args.port)
        logger.info("API documentation at http://%s:%d/docs", parsed_args.host, parsed_args.port)

        uvicorn.run(
            "back_to_back.app:app",
            host=parsed_args.host,
            port=parsed_args.port,
            reload=parsed_args.reload,
            log_level="info" if parsed_args.verbose else "warning",
        )

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
