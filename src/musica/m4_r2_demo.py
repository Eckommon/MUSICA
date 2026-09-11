"""Generate canonical M4-R2 Browser Studio static/HTTP integration evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import threading
from importlib import resources
from pathlib import Path
from typing import Any
from urllib import request as urlrequest

from .evidence import artifact_record, write_canonical_json
from .studio import StudioService
from .studio_http import create_local_server


def _http_get(url: str) -> tuple[int, dict[str, str], bytes]:
    with urlrequest.urlopen(url, timeout=15) as response:
        return response.status, dict(response.headers.items()), response.read()


def _http_json(base: str, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = None if body is None else json.dumps(body).encode("utf-8")
    req = urlrequest.Request(
        base + path,
        data=raw,
        method=method,
        headers={
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if raw is not None else {}),
        },
    )
    with urlrequest.urlopen(req, timeout=30) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not value.get("ok", False):
        raise RuntimeError(f"M4-R2 canonical HTTP operation failed: {value}")
    return value["data"]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    workspace = root / "workspace"
    service = StudioService(workspace)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"

    try:
        index_status, index_headers, index_bytes = _http_get(base + "/")
        css_status, css_headers, css_bytes = _http_get(base + "/assets/app.css")
        js_status, js_headers, js_bytes = _http_get(base + "/assets/app.js")
        health_status, _, health_bytes = _http_get(base + "/v0/health")
        health = json.loads(health_bytes.decode("utf-8"))

        if not (index_status == css_status == js_status == health_status == 200):
            raise RuntimeError("M4-R2 static/health HTTP status proof failed")
        csp = index_headers.get("Content-Security-Policy", "")
        if not all(token in csp for token in ("default-src 'self'", "script-src 'self'", "connect-src 'self'", "frame-ancestors 'none'")):
            raise RuntimeError("M4-R2 strict CSP proof failed")

        index_text = index_bytes.decode("utf-8")
        css_text = css_bytes.decode("utf-8")
        js_text = js_bytes.decode("utf-8")
        for label in ("Direct", "Shape", "Inspect", "Code"):
            if label not in index_text:
                raise RuntimeError(f"M4-R2 progressive disclosure label missing: {label}")
        combined_text = "\n".join((index_text, css_text, js_text)).lower()
        if "https://" in combined_text or "http://" in combined_text:
            raise RuntimeError("M4-R2 canonical static UI contains a remote URL dependency")

        created = _http_json(
            base,
            "POST",
            "/v0/projects/create",
            {
                "project_slug": "browser-studio-proof",
                "session_id": "browser-studio-proof-session",
                "provider_mode": "fixture",
                "user_text": "Create a restrained dark electronic 8-second technology advertisement cue",
                "locale": "en-US",
                "duration_seconds": 8,
                "use_case": "advertisement",
                "style_profile": "dark_electronic",
                "seed": 4402,
                "preserve_on_edit": ["tempo", "melody_identity", "rhythm_identity"],
                "exclusions": ["vocals"],
            },
        )
        initial_session = created["session"]
        session_id = initial_session["session_id"]
        root_revision = initial_session["head_revision_id"]

        accepted_audio_status, accepted_audio_headers, accepted_audio = _http_get(
            base + f"/v0/sessions/{session_id}/media/audio.wav"
        )
        if accepted_audio_status != 200 or accepted_audio[:4] != b"RIFF":
            raise RuntimeError("M4-R2 initial accepted audio proof failed")

        preview = _http_json(
            base,
            "POST",
            f"/v0/sessions/{session_id}/preview/semantic",
            {
                "name": "tension",
                "operation": "set",
                "value": 0.82,
                "scope_kind": "final_section",
                "section_id": None,
            },
        )
        preview_session = preview["session"]
        if preview_session["head_revision_id"] != root_revision:
            raise RuntimeError("M4-R2 HTTP preview changed canonical revision before acceptance")
        if preview_session["pending_preview"] is None or not preview["diff"]:
            raise RuntimeError("M4-R2 preview/diff proof missing")

        preview_audio_status, preview_audio_headers, preview_audio = _http_get(
            base + f"/v0/sessions/{session_id}/media/audio.wav?preview=1"
        )
        if preview_audio_status != 200 or preview_audio[:4] != b"RIFF":
            raise RuntimeError("M4-R2 pending preview audio proof failed")

        accepted = _http_json(
            base,
            "POST",
            f"/v0/sessions/{session_id}/preview/accept",
            {},
        )
        accepted_session = accepted["session"]
        if accepted_session["head_revision_id"] == root_revision:
            raise RuntimeError("M4-R2 explicit acceptance did not advance revision")
        if accepted_session["pending_preview"] is not None:
            raise RuntimeError("M4-R2 accepted session still reports pending preview")

        branch = _http_json(
            base,
            "POST",
            f"/v0/sessions/{session_id}/branches",
            {"branch_name": "browser-variation", "checkout": True},
        )
        history = _http_json(base, "GET", f"/v0/sessions/{session_id}/history")
        exported = _http_json(base, "POST", f"/v0/sessions/{session_id}/export", {})
        final_session = _http_json(base, "GET", f"/v0/sessions/{session_id}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    static_dir = root / "browser-assets"
    static_dir.mkdir(parents=True, exist_ok=True)
    package = resources.files("musica.studio_web")
    copied_assets: list[Path] = []
    for name in ("index.html", "app.css", "app.js"):
        target = static_dir / name
        target.write_bytes(package.joinpath(name).read_bytes())
        copied_assets.append(target)

    accepted_audio_path = root / "accepted-before-edit.wav"
    accepted_audio_path.write_bytes(accepted_audio)
    preview_audio_path = root / "pending-preview.wav"
    preview_audio_path.write_bytes(preview_audio)

    ui_proof = {
        "browser_surface_status": "PASS",
        "static_status": {"index": index_status, "css": css_status, "js": js_status},
        "content_types": {
            "index": index_headers.get("Content-Type"),
            "css": css_headers.get("Content-Type"),
            "js": js_headers.get("Content-Type"),
        },
        "security_headers": {
            "content_security_policy": index_headers.get("Content-Security-Policy"),
            "referrer_policy": index_headers.get("Referrer-Policy"),
            "x_frame_options": index_headers.get("X-Frame-Options"),
            "x_content_type_options": index_headers.get("X-Content-Type-Options"),
        },
        "progressive_disclosure": ["Direct", "Shape", "Inspect", "Code"],
        "same_origin_assets": ["/assets/app.css", "/assets/app.js"],
        "remote_url_dependency_detected": False,
        "external_network_used": False,
        "live_openai_call_performed": False,
        "telemetry_enabled": False,
        "launcher": "musica-studio",
    }
    workflow_proof = {
        "health": health,
        "root_revision_id": root_revision,
        "preview_candidate_revision_id": preview["preview"]["candidate_revision_id"],
        "preview_ref_unchanged_before_accept": preview_session["head_revision_id"] == root_revision,
        "preview_diff_count": len(preview["diff"]),
        "preview_audio_wav": preview_audio[:4] == b"RIFF",
        "accepted_revision_id": accepted_session["head_revision_id"],
        "accept_advanced_revision": accepted_session["head_revision_id"] != root_revision,
        "accepted_pending_preview_cleared": accepted_session["pending_preview"] is None,
        "branch_created_and_checked_out": branch["session"]["current_branch"] == "browser-variation",
        "history_revision_count": len(history["revisions"]),
        "export_relpath": exported["export_relpath"],
        "export_sha256": exported["sha256"],
        "final_integrity_status": final_session["integrity_status"],
        "hard_lock_count": len(final_session["hard_locks"]),
        "six_semantic_axes_visible": sorted(final_session["semantic_state"].keys())
        == sorted(["energy", "tension", "density", "motion", "brightness", "warmth"]),
    }
    if not all(
        (
            workflow_proof["preview_ref_unchanged_before_accept"],
            workflow_proof["preview_audio_wav"],
            workflow_proof["accept_advanced_revision"],
            workflow_proof["accepted_pending_preview_cleared"],
            workflow_proof["branch_created_and_checked_out"],
            workflow_proof["final_integrity_status"] == "PASS",
            workflow_proof["six_semantic_axes_visible"],
        )
    ):
        raise RuntimeError("M4-R2 browser-visible workflow proof failed")

    summary_files = [
        write_canonical_json(root / "ui-proof.json", ui_proof),
        write_canonical_json(root / "http-workflow-proof.json", workflow_proof),
        write_canonical_json(root / "initial-session.json", initial_session),
        write_canonical_json(root / "preview-result.json", preview),
        write_canonical_json(root / "accepted-result.json", accepted),
        write_canonical_json(root / "branch-result.json", branch),
        write_canonical_json(root / "history.json", history),
        write_canonical_json(root / "export-result.json", exported),
        write_canonical_json(root / "final-session.json", final_session),
        accepted_audio_path,
        preview_audio_path,
        *copied_assets,
    ]
    workspace_files = sorted(path for path in workspace.rglob("*") if path.is_file())
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M4-R2-Browser-Studio-UI-v0",
        "proof": {
            "real_browser_deliverable_assets": True,
            "same_origin_http_integration": True,
            "progressive_disclosure": True,
            "preview_accept_authority_preserved": True,
            "exact_diff_returned_for_preview": len(preview["diff"]) > 0,
            "hard_locks_visible_in_session": len(final_session["hard_locks"]) > 0,
            "project_integrity_status": final_session["integrity_status"],
            "no_remote_asset_dependency": True,
            "no_external_network_used": True,
        },
        "asset_digests": {
            "index_html": _sha256_bytes(index_bytes),
            "app_css": _sha256_bytes(css_bytes),
            "app_js": _sha256_bytes(js_bytes),
        },
        "claim_boundary": [
            "M4-R2 validates a packaged browser-deliverable UI surface and same-origin HTTP integration.",
            "No browser automation or human usability study is claimed; those belong to M4-R3.",
            "The browser is non-authoritative; accepted state remains in the M2 Project Engine.",
            "No live OpenAI call, cloud service, telemetry, CDN, desktop installer, production mastering, or DAW interoperability is claimed.",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(
                {path.resolve(): path for path in summary_files + workspace_files}.values(),
                key=lambda item: item.relative_to(root).as_posix(),
            )
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M4-R2 Browser Studio evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
