"""Command-line launcher for the local-first MUSICA Browser Studio / 로컬 Studio 실행기."""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from .studio import StudioService
from .studio_http import DEFAULT_HOST, create_local_server

DEFAULT_PORT = 8765
DEFAULT_WORKSPACE = Path.home() / "MUSICA-Workspace"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="musica-studio",
        description="Run the local-first MUSICA Browser Studio / 로컬 MUSICA Browser Studio 실행",
    )
    parser.add_argument(
        "--workspace",
        default=str(DEFAULT_WORKSPACE),
        help="Studio workspace directory / Studio 작업공간 디렉터리",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Loopback host / loopback 호스트")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local HTTP port / 로컬 HTTP 포트")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the default browser automatically / 브라우저 자동 열기 비활성화",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace = Path(args.workspace).expanduser()
    service = StudioService(workspace)
    server = create_local_server(service, host=args.host, port=args.port)
    actual_host, actual_port = server.server_address[:2]
    browser_host = "127.0.0.1" if actual_host in {"0.0.0.0", "::"} else str(actual_host)
    url = f"http://{browser_host}:{actual_port}/"

    print("MUSICA Studio / MUSICA 스튜디오")
    print(f"Workspace / 작업공간: {service.workspace}")
    print(f"Local URL / 로컬 주소: {url}")
    print("Press Ctrl+C to stop / 종료하려면 Ctrl+C")

    if not args.no_browser:
        timer = threading.Timer(0.35, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()

    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping MUSICA Studio / MUSICA Studio 종료")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
