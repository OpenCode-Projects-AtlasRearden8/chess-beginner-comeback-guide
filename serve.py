#!/usr/bin/env python3
"""Serve the built guide locally: python3 serve.py [--port 8765] [--dir site].

Standard-library only. Opens your browser unless you pass --no-browser.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socket
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def free_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, default=ROOT / "site",
                    help="directory to serve (default: ./site)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    if not (args.dir / "index.html").exists():
        raise SystemExit(
            f"{args.dir} has no index.html — run 'python3 build.py' first."
        )

    port = free_port(args.port)
    url = f"http://127.0.0.1:{port}/"

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):  # keep the terminal calm
            pass

    handler = functools.partial(Quiet, directory=str(args.dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Serving {args.dir} at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Bye.")


if __name__ == "__main__":
    main()
