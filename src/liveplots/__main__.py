"""CLI entry point for liveplots."""

from __future__ import annotations

import argparse
import logging
import time

from liveplots.server import rpc_plot

logger = logging.getLogger(__name__)


def main() -> None:
    """Start a liveplot server monitoring a file or directory."""
    parser = argparse.ArgumentParser(
        prog="liveplots",
        description="Start a liveplot daemon for monitoring files.",
    )
    parser.add_argument(
        "path",
        nargs="+",
        help="File or directory to monitor.",
    )
    parser.add_argument(
        "-e",
        "--event",
        nargs="+",
        choices=["create", "delete", "close_write", "close_nowrite", "access", "attrib", "modify"],
        default=["modify"],
        help="Events to monitor.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    port = rpc_plot(persist=0)
    logger.info("Liveplot server running on port %s. Press Ctrl+C to stop.", port)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    main()
