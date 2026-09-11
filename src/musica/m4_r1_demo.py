"""Generate canonical M4-R1 Studio application-service evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import threading
from pathlib import Path
from typing import Any
from urllib import request as urlrequest

from .evidence import artifact_record, write_canonical_json
from .studio import StudioApplication, StudioService, StudioServiceError
from .studio_http import create_local_server


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _http_get_json(url: str) -> tuple[int, str, dict[str, Any]]:
    with urlrequest.urlopen(url, timeout=10) as response:
        return (
            response.status,
            response.headers.get_content_type(),
            json.loads(response.read().decode("utf-8")),
        )


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    workspace = root / "workspace"

    service = StudioService(workspace)
    created = service.create_project_session(
        project_slug="canonical-studio",
        session_id="canonical-session",
        provider_mode="fixture",
        user_text="Create a restrained dark electronic 8-second technology advertisement cue",
        locale="en-US",
        duration_seconds=8,
        use_case="advertisement",
        style_profile="dark_electronic",
        seed=4401,
        preserve_on_edit=["tempo", "melody_identity", "rhythm_identity"],
        exclusions=["vocals"],
    )
    initial_session = created["session"]
    root_revision = initial_session["head_revision_id"]

    initial_audio = service.media_path("canonical-session", "audio")
    initial_midi = service.media_path("canonical-session", "midi")
    copied_initial_audio = root / "initial-accepted.wav"
    copied_initial_midi = root / "initial-accepted.mid"
    shutil.copyfile(initial_audio, copied_initial_audio)
    shutil.copyfile(initial_midi, copied_initial_midi)

    preview = service.preview_semantic_edit(
        "canonical-session",
        name="tension",
        operation="increase",
        value=0.18,
        scope_kind="final_section",
    )
    preview_session = service.inspect_session("canonical-session")
    if preview_session["head_revision_id"] != root_revision:
        raise RuntimeError("M4-R1 preview mutated canonical branch head")
    preview_audio = service.media_path("canonical-session", "audio")
    preview_midi = service.media_path("canonical-session", "midi")
    copied_preview_audio = root / "pending-preview.wav"
    copied_preview_midi = root / "pending-preview.mid"
    shutil.copyfile(preview_audio, copied_preview_audio)
    shutil.copyfile(preview_midi, copied_preview_midi)

    accepted = service.accept_preview("canonical-session")
    accepted_revision = accepted["session"]["head_revision_id"]
    if accepted_revision != preview["preview"]["candidate_revision_id"]:
        raise RuntimeError("M4-R1 accepted revision does not match preview candidate")

    branch = service.create_branch(
        "canonical-session",
        branch_name="variation-a",
        checkout=True,
    )
    variation_base = branch["session"]["head_revision_id"]
    discard_preview = service.preview_semantic_edit(
        "canonical-session",
        name="brightness",
        operation="increase",
        value=0.15,
        scope_kind="whole_project",
    )
    if service.inspect_session("canonical-session")["head_revision_id"] != variation_base:
        raise RuntimeError("M4-R1 second preview changed branch head before discard")
    discarded = service.discard_preview("canonical-session")
    if discarded["head_revision_id"] != variation_base:
        raise RuntimeError("M4-R1 discard changed branch head")

    history = service.revision_history("canonical-session")
    first_export = service.export_project("canonical-session")
    first_export_path = workspace / first_export["export_relpath"]
    first_export_bytes = first_export_path.read_bytes()
    second_export = service.export_project("canonical-session")
    export_reproducible = first_export_bytes == first_export_path.read_bytes()
    if not export_reproducible or first_export["sha256"] != second_export["sha256"]:
        raise RuntimeError("M4-R1 deterministic project export proof failed")

    service.close_session("canonical-session")
    reopened_service = StudioService(workspace)
    reopened = reopened_service.open_project_session(
        project_slug="canonical-studio",
        session_id="canonical-reopen",
        provider_mode="fixture",
    )
    if reopened["session"]["head_revision_id"] != variation_base:
        raise RuntimeError("M4-R1 reopened session did not preserve branch head")

    app = StudioApplication(reopened_service)
    dispatch_proof = app.dispatch("GET", "/v0/sessions/canonical-reopen")

    # Real loopback HTTP proof for the bridge M4-R2 will consume.
    server = create_local_server(reopened_service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        health_status, health_type, health_body = _http_get_json(base + "/v0/health")
        inspect_status, inspect_type, inspect_body = _http_get_json(base + "/v0/sessions/canonical-reopen")
        with urlrequest.urlopen(
            base + "/v0/sessions/canonical-reopen/media/audio.wav",
            timeout=10,
        ) as response:
            http_audio = response.read()
            audio_status = response.status
            audio_type = response.headers.get_content_type()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    http_proof = {
        "health_status": health_status,
        "health_content_type": health_type,
        "health_body": health_body,
        "inspect_status": inspect_status,
        "inspect_content_type": inspect_type,
        "inspect_head_revision_id": inspect_body["data"]["head_revision_id"],
        "audio_status": audio_status,
        "audio_content_type": audio_type,
        "audio_size_bytes": len(http_audio),
        "audio_sha256": hashlib.sha256(http_audio).hexdigest(),
        "loopback_only": True,
    }
    if not (
        health_status == 200
        and inspect_status == 200
        and audio_status == 200
        and audio_type == "audio/wav"
        and http_audio[:4] == b"RIFF"
    ):
        raise RuntimeError("M4-R1 loopback HTTP proof failed")

    negative_cases: list[dict[str, Any]] = []
    try:
        reopened_service.open_project_session(
            project_slug="../outside",
            session_id="escape-attempt",
        )
    except StudioServiceError as exc:
        negative_cases.append(
            {
                "case": "project_path_traversal",
                "status": "BLOCKED_AS_EXPECTED",
                "code": exc.code,
            }
        )
    else:
        raise RuntimeError("M4-R1 path traversal was not blocked")

    try:
        create_local_server(reopened_service, host="0.0.0.0", port=0)
    except StudioServiceError as exc:
        negative_cases.append(
            {
                "case": "non_loopback_http_bind",
                "status": "BLOCKED_AS_EXPECTED",
                "code": exc.code,
            }
        )
    else:
        raise RuntimeError("M4-R1 non-loopback binding was not blocked")

    project_verification = reopened_service._get_session("canonical-reopen").project.verify_integrity()

    summary_files = [
        write_canonical_json(root / "initial-session.json", initial_session),
        write_canonical_json(root / "create-director-trace.json", created["director_trace"]),
        write_canonical_json(root / "create-intent.json", created["intent"]),
        write_canonical_json(root / "preview-result.json", preview),
        write_canonical_json(root / "preview-session.json", preview_session),
        write_canonical_json(root / "accepted-result.json", accepted),
        write_canonical_json(root / "branch-result.json", branch),
        write_canonical_json(root / "discard-preview-result.json", discard_preview),
        write_canonical_json(root / "discarded-result.json", discarded),
        write_canonical_json(root / "history.json", history),
        write_canonical_json(root / "export-proof.json", {
            "first": first_export,
            "second": second_export,
            "byte_identical": export_reproducible,
        }),
        write_canonical_json(root / "reopened-session.json", reopened["session"]),
        write_canonical_json(root / "dispatch-proof.json", dispatch_proof),
        write_canonical_json(root / "http-proof.json", http_proof),
        write_canonical_json(root / "negative-cases.json", negative_cases),
        write_canonical_json(root / "project-verification.json", project_verification),
        copied_initial_audio,
        copied_initial_midi,
        copied_preview_audio,
        copied_preview_midi,
    ]

    workspace_files = sorted(path for path in workspace.rglob("*") if path.is_file())
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M4-R1-Studio-Application-Service-v0",
        "service": {"id": "musica-studio-service", "version": "0.1.0"},
        "proof": {
            "root_revision_id": root_revision,
            "accepted_revision_id": accepted_revision,
            "preview_ref_unchanged_before_accept": preview_session["head_revision_id"] == root_revision,
            "accept_advanced_to_preview_candidate": accepted_revision == preview["preview"]["candidate_revision_id"],
            "discard_ref_unchanged": discarded["head_revision_id"] == variation_base,
            "branch_created_and_checked_out": branch["session"]["current_branch"] == "variation-a",
            "history_revision_count": len(history["revisions"]),
            "deterministic_export_byte_identical": export_reproducible,
            "reopen_preserved_head": reopened["session"]["head_revision_id"] == variation_base,
            "project_integrity_status": project_verification["status"],
            "loopback_http_status": "PASS",
            "negative_cases_blocked": all(case["status"] == "BLOCKED_AS_EXPECTED" for case in negative_cases),
        },
        "network_policy": {
            "provider_mode": "fixture",
            "external_network_used": False,
            "loopback_http_used": True,
            "live_openai_call_performed": False,
        },
        "claim_boundary": [
            "M4-R1 validates the local application/session service, not a polished end-user UI.",
            "Loopback HTTP is validated; remote network serving is explicitly blocked in R1.",
            "Fixture Director mode is used; no live OpenAI provider evidence is claimed.",
            "Production renderer quality, cloud collaboration, desktop packaging, and DAW interoperability are not claimed.",
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
    parser = argparse.ArgumentParser(description="Generate MUSICA M4-R1 Studio service evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
