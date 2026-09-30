"""REC-R1 trusted captured-asset finalize and recording Preview/Accept authority."""

from __future__ import annotations

import copy
import hashlib
import io
import wave
from dataclasses import dataclass
from typing import Any

from .automation_edit import automation_material_sha256
from .audio_assets import import_audio_asset_bytes, list_audio_assets, read_audio_asset
from .audio_contracts import (
    audio_material_from_blueprint,
    validate_audio_material,
    validate_project_blueprint_audio,
)
from .audio_edit import audio_material_sha256, blueprint_sha256
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes
from .recording_capture import (
    SimulatedCaptureRun,
    validate_recording_capture_plan,
    validate_recording_capture_report,
)
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256

MECHANISM_PREFIX = "recording_finalize_candidate:"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _routing_hash(blueprint: dict[str, Any]) -> str:
    material = routing_material_from_blueprint(blueprint)
    assert material is not None
    return routing_material_sha256(material)


def canonical_capture_wav_bytes(run: SimulatedCaptureRun) -> bytes:
    """Wrap exact REC-R0 PCM16 bytes in one deterministic RIFF/WAVE container."""

    _validate_capture_run(run)
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(int(run.plan["input_channels"]))
        writer.setsampwidth(2)
        writer.setframerate(int(run.plan["sample_rate_hz"]))
        writer.writeframes(run.captured_payload)
    return stream.getvalue()


def _validate_capture_run(run: SimulatedCaptureRun) -> None:
    validate_recording_capture_plan(run.plan)
    validate_recording_capture_report(run.report)

    plan = run.plan
    report = run.report
    payload = bytes(run.captured_payload)
    payload_info = report["payload"]
    metrics = report["metrics"]

    if str(report["source"]["revision_id"]) != str(plan["source"]["revision_id"]):
        raise ContractError("recording finalize capture report revision mismatch")
    if str(report["source"]["recording_capture_plan_sha256"]) != str(
        plan["recording_capture_plan_sha256"]
    ):
        raise ContractError("recording finalize capture plan/report hash mismatch")
    if str(payload_info["payload_sha256"]) != _sha(payload):
        raise ContractError("recording finalize captured payload SHA-256 mismatch")
    if int(payload_info["payload_size_bytes"]) != len(payload):
        raise ContractError("recording finalize captured payload size mismatch")
    if int(payload_info["sample_rate_hz"]) != int(plan["sample_rate_hz"]):
        raise ContractError("recording finalize capture sample rate mismatch")
    if int(payload_info["channels"]) != int(plan["input_channels"]):
        raise ContractError("recording finalize capture channel mismatch")
    expected_bytes = int(payload_info["captured_frames"]) * int(payload_info["channels"]) * 2
    if len(payload) != expected_bytes:
        raise ContractError("recording finalize PCM16 frame/byte count mismatch")

    # R1 intentionally finalizes only complete, clean deterministic captures.
    if int(metrics["frames_requested"]) != int(plan["capture_frames"]):
        raise ContractError("recording finalize capture requested frame count mismatch")
    if int(metrics["frames_captured"]) != int(plan["capture_frames"]):
        raise ContractError("recording finalize requires complete captured frame count")
    if int(payload_info["captured_frames"]) != int(plan["capture_frames"]):
        raise ContractError("recording finalize report payload frame count mismatch")
    if any(
        int(metrics[key]) != 0
        for key in ("error_count", "short_fill_count", "late_count", "dropout_equivalent_count")
    ):
        raise ContractError("recording finalize requires a capture with no injected failures")
    expected_lifecycle = [
        "CLOSED",
        "OPEN",
        "READY",
        "CAPTURING",
        "STOPPED",
        "FINALIZED",
        "CLOSED",
    ]
    if list(report["lifecycle"]) != expected_lifecycle:
        raise ContractError("recording finalize requires completed REC-R0 lifecycle")
    if report["accepted_head_unchanged"] is not True:
        raise ContractError("recording finalize capture did not preserve accepted HEAD")


def _authority_result(
    candidate_id: str, conflicts: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    blocked = bool(conflicts)
    value = {
        "result_version": "0",
        "candidate_id": candidate_id,
        "status": "BLOCKED" if blocked else "READY_FOR_PREVIEW",
        "conflicts": conflicts or [],
        "preview_generation_allowed": not blocked,
        "explicit_accept_required": True,
        "asset_mutation_authorized": False,
        "project_mutation_authorized": False,
    }
    validate_contract(value, "recording-finalize-authority-result-v0.schema.json")
    return value


def _conflict(
    ordinal: int,
    code: str,
    reason: str,
    *,
    track_id: str | None = None,
    clip_id: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "conflict_id": f"REC-R1-C-{ordinal:03d}",
        "code": code,
        "reason": reason,
    }
    if track_id is not None:
        value["track_id"] = track_id
    if clip_id is not None:
        value["clip_id"] = clip_id
    return value


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = _sha(canonical_json_bytes(candidate))[:16]
    return f"{parent['project']['revision_id']}-recording-{digest}"


def _capture_binding(run: SimulatedCaptureRun) -> dict[str, Any]:
    return {
        "recording_capture_plan_sha256": str(run.plan["recording_capture_plan_sha256"]),
        "recording_capture_run_report_sha256": str(
            run.report["recording_capture_run_report_sha256"]
        ),
        "payload_sha256": str(run.report["payload"]["payload_sha256"]),
        "payload_size_bytes": int(run.report["payload"]["payload_size_bytes"]),
        "sample_rate_hz": int(run.report["payload"]["sample_rate_hz"]),
        "channels": int(run.report["payload"]["channels"]),
        "captured_frames": int(run.report["payload"]["captured_frames"]),
        "sample_format": str(run.report["payload"]["format"]),
    }


def _source_binding(blueprint: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": str(blueprint["project"]["project_id"]),
        "revision_id": str(blueprint["project"]["revision_id"]),
        "blueprint_sha256": blueprint_sha256(blueprint),
        "audio_material_sha256": audio_material_sha256(blueprint),
        "routing_material_sha256": _routing_hash(blueprint),
        "automation_material_sha256": automation_material_sha256(blueprint),
    }


def _find_track(material: dict[str, Any], track_id: str) -> dict[str, Any] | None:
    for track in material["tracks"]:
        if str(track["track_id"]) == str(track_id):
            return track
    return None


def _clip_ids(material: dict[str, Any]) -> set[str]:
    return {
        str(clip["clip_id"])
        for track in material["tracks"]
        for clip in track["clips"]
    }


@dataclass(frozen=True)
class RecordingFinalizePreview:
    authority_result: dict[str, Any]
    blueprint: dict[str, Any] | None
    source_revision_id: str
    source_blueprint_sha256: str
    source_audio_material_sha256: str
    source_routing_material_sha256: str
    source_automation_material_sha256: str
    recording_capture_plan_sha256: str
    recording_capture_run_report_sha256: str
    captured_payload_sha256: str
    candidate_blueprint_sha256: str | None
    candidate_audio_material_sha256: str | None
    prospective_wav_sha256: str | None
    prospective_asset_id: str | None
    destination_track_id: str
    destination_clip_id: str

    @property
    def ready(self) -> bool:
        return self.authority_result["status"] == "READY_FOR_PREVIEW"

    def as_dict(self) -> dict[str, Any]:
        return {
            "authority_result": copy.deepcopy(self.authority_result),
            "source_revision_id": self.source_revision_id,
            "source_blueprint_sha256": self.source_blueprint_sha256,
            "source_audio_material_sha256": self.source_audio_material_sha256,
            "source_routing_material_sha256": self.source_routing_material_sha256,
            "source_automation_material_sha256": self.source_automation_material_sha256,
            "recording_capture_plan_sha256": self.recording_capture_plan_sha256,
            "recording_capture_run_report_sha256": self.recording_capture_run_report_sha256,
            "captured_payload_sha256": self.captured_payload_sha256,
            "candidate_blueprint_sha256": self.candidate_blueprint_sha256,
            "candidate_audio_material_sha256": self.candidate_audio_material_sha256,
            "prospective_wav_sha256": self.prospective_wav_sha256,
            "prospective_asset_id": self.prospective_asset_id,
            "destination_track_id": self.destination_track_id,
            "destination_clip_id": self.destination_clip_id,
        }


def _blocked_preview(
    parent: dict[str, Any],
    candidate: dict[str, Any],
    run: SimulatedCaptureRun,
    conflicts: list[dict[str, Any]],
) -> RecordingFinalizePreview:
    source = _source_binding(parent)
    capture = _capture_binding(run)
    dest = candidate["destination"]
    return RecordingFinalizePreview(
        authority_result=_authority_result(str(candidate["candidate_id"]), conflicts),
        blueprint=None,
        source_revision_id=source["revision_id"],
        source_blueprint_sha256=source["blueprint_sha256"],
        source_audio_material_sha256=source["audio_material_sha256"],
        source_routing_material_sha256=source["routing_material_sha256"],
        source_automation_material_sha256=source["automation_material_sha256"],
        recording_capture_plan_sha256=capture["recording_capture_plan_sha256"],
        recording_capture_run_report_sha256=capture["recording_capture_run_report_sha256"],
        captured_payload_sha256=capture["payload_sha256"],
        candidate_blueprint_sha256=None,
        candidate_audio_material_sha256=None,
        prospective_wav_sha256=None,
        prospective_asset_id=None,
        destination_track_id=str(dest["track_id"]),
        destination_clip_id=str(dest["clip_id"]),
    )


def build_recording_finalize_preview(
    project: Any,
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    capture_run: SimulatedCaptureRun,
    *,
    branch: str | None = None,
    revision_id: str | None = None,
) -> RecordingFinalizePreview:
    """Build a non-canonical recording Preview without writing project assets."""

    validate_contract(
        parent_blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_contract(candidate, "recording-finalize-candidate-v0.schema.json")
    validate_project_blueprint_audio(project, parent_blueprint)

    selected_branch = branch or project.current_branch()
    source = _source_binding(parent_blueprint)
    stale: list[str] = []
    for key, value in source.items():
        if candidate["source"][key] != value:
            stale.append(f"{key} mismatch")
    if project.head_revision_id(selected_branch) != source["revision_id"]:
        stale.append("project branch HEAD no longer equals source revision")
    persisted = project.read_revision(source["revision_id"])
    if _source_binding(persisted) != source:
        stale.append("persisted accepted source hash mismatch")
    try:
        _validate_capture_run(capture_run)
    except ContractError as exc:
        stale.append(str(exc))
    if str(capture_run.plan["source"]["revision_id"]) != source["revision_id"]:
        stale.append("capture plan accepted revision mismatch")
    for key in (
        "project_id",
        "blueprint_sha256",
        "audio_material_sha256",
        "routing_material_sha256",
        "automation_material_sha256",
    ):
        if capture_run.plan["source"][key] != source[key]:
            stale.append(f"capture plan source {key} mismatch")
    if candidate["capture"] != _capture_binding(capture_run):
        stale.append("candidate capture binding mismatch")
    if stale:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [_conflict(1, "STALE_OR_INVALID_CAPTURE", "; ".join(stale))],
        )

    material = copy.deepcopy(audio_material_from_blueprint(parent_blueprint))
    assert material is not None
    track_id = str(candidate["destination"]["track_id"])
    clip_id = str(candidate["destination"]["clip_id"])
    track = _find_track(material, track_id)
    if track is None:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [_conflict(1, "UNKNOWN_TRACK", f"unknown destination audio track: {track_id}", track_id=track_id)],
        )
    if clip_id in _clip_ids(material):
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [_conflict(1, "DUPLICATE_CLIP", f"audio clip_id already exists: {clip_id}", track_id=track_id, clip_id=clip_id)],
        )

    capture_rate = int(capture_run.plan["sample_rate_hz"])
    existing_rates = {
        int(read_audio_asset(project, str(clip["asset_id"]))["format"]["sample_rate_hz"])
        for clip in track["clips"]
    }
    if existing_rates and existing_rates != {capture_rate}:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [
                _conflict(
                    1,
                    "SAMPLE_RATE_MISMATCH",
                    f"recording capture sample rate {capture_rate} does not match destination track source rates {sorted(existing_rates)} under no-resampling policy",
                    track_id=track_id,
                    clip_id=clip_id,
                )
            ],
        )

    wav_bytes = canonical_capture_wav_bytes(capture_run)
    wav_sha = _sha(wav_bytes)
    asset_id = f"sha256:{wav_sha}"
    duration = int(capture_run.plan["capture_frames"]) / int(capture_run.plan["sample_rate_hz"])
    track["clips"].append(
        {
            "clip_id": clip_id,
            "asset_id": asset_id,
            "timeline_start_seconds": candidate["destination"]["timeline_start_seconds"],
            "source_in_seconds": 0.0,
            "source_out_seconds": duration,
            "gain_db": candidate["destination"]["gain_db"],
        }
    )
    track["clips"].sort(
        key=lambda clip: (float(clip["timeline_start_seconds"]), str(clip["clip_id"]))
    )
    try:
        validate_audio_material(
            material,
            project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]),
        )
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [_conflict(1, "INVALID_DESTINATION", str(exc), track_id=track_id, clip_id=clip_id)],
        )

    working = copy.deepcopy(parent_blueprint)
    working["materials"]["audio"] = material
    working["project"]["parent_revision_id"] = source["revision_id"]
    working["project"]["revision_id"] = revision_id or _revision_id(parent_blueprint, candidate)
    provenance = working["provenance"]
    provenance["actor"] = "deterministic_transform" if candidate["actor"]["kind"] == "system" else candidate["actor"]["kind"]
    provenance["change_reason"] = candidate["reason"]
    provenance["source_revision"] = source["revision_id"]
    selected = list(provenance.get("selected_mechanisms", []))
    selected.append(f"{MECHANISM_PREFIX}{candidate['candidate_id']}")
    selected.append(f"recording_capture_plan:{capture_run.plan['recording_capture_plan_sha256']}")
    selected.append(f"recording_capture_report:{capture_run.report['recording_capture_run_report_sha256']}")
    provenance["selected_mechanisms"] = selected

    try:
        validate_contract(
            working,
            "music-blueprint-v0.schema.json",
            allow_nonempty_routing=True,
        )
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [_conflict(1, "UNREPRESENTABLE_RECORDING", str(exc), track_id=track_id, clip_id=clip_id)],
        )
    conflicts = validate_revision(parent_blueprint, working, allow_nonempty_routing=True)
    blocking = [item for item in conflicts if item.status == "BLOCKED"]
    if blocking:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            capture_run,
            [
                _conflict(index, "REVISION_CONFLICT", item.reason, track_id=track_id, clip_id=clip_id)
                for index, item in enumerate(blocking, start=1)
            ],
        )

    return RecordingFinalizePreview(
        authority_result=_authority_result(str(candidate["candidate_id"])),
        blueprint=working,
        source_revision_id=source["revision_id"],
        source_blueprint_sha256=source["blueprint_sha256"],
        source_audio_material_sha256=source["audio_material_sha256"],
        source_routing_material_sha256=source["routing_material_sha256"],
        source_automation_material_sha256=source["automation_material_sha256"],
        recording_capture_plan_sha256=str(capture_run.plan["recording_capture_plan_sha256"]),
        recording_capture_run_report_sha256=str(
            capture_run.report["recording_capture_run_report_sha256"]
        ),
        captured_payload_sha256=str(capture_run.report["payload"]["payload_sha256"]),
        candidate_blueprint_sha256=blueprint_sha256(working),
        candidate_audio_material_sha256=audio_material_sha256(working),
        prospective_wav_sha256=wav_sha,
        prospective_asset_id=asset_id,
        destination_track_id=track_id,
        destination_clip_id=clip_id,
    )


def accept_recording_finalize_preview(
    project: Any,
    preview: RecordingFinalizePreview,
    capture_run: SimulatedCaptureRun,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly finalize one validated capture into accepted audio material."""

    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW recording candidates may be accepted")
    selected_branch = branch or project.current_branch()
    if project.head_revision_id(selected_branch) != preview.source_revision_id:
        raise ContractError("recording Preview source is stale: project HEAD changed")

    current = project.read_revision(preview.source_revision_id)
    expected_source = {
        "revision_id": preview.source_revision_id,
        "blueprint_sha256": preview.source_blueprint_sha256,
        "audio_material_sha256": preview.source_audio_material_sha256,
        "routing_material_sha256": preview.source_routing_material_sha256,
        "automation_material_sha256": preview.source_automation_material_sha256,
    }
    current_source = _source_binding(current)
    for key, expected in expected_source.items():
        if current_source[key] != expected:
            raise ContractError(f"recording Preview source {key} is stale")

    _validate_capture_run(capture_run)
    if str(capture_run.plan["recording_capture_plan_sha256"]) != preview.recording_capture_plan_sha256:
        raise ContractError("recording Preview capture plan changed")
    if str(capture_run.report["recording_capture_run_report_sha256"]) != preview.recording_capture_run_report_sha256:
        raise ContractError("recording Preview capture report changed")
    if str(capture_run.report["payload"]["payload_sha256"]) != preview.captured_payload_sha256:
        raise ContractError("recording Preview captured payload changed")
    if str(capture_run.plan["source"]["revision_id"]) != preview.source_revision_id:
        raise ContractError("recording Preview capture source revision changed")

    wav_bytes = canonical_capture_wav_bytes(capture_run)
    wav_sha = _sha(wav_bytes)
    if wav_sha != preview.prospective_wav_sha256:
        raise ContractError("recording Preview prospective WAV changed")
    if f"sha256:{wav_sha}" != preview.prospective_asset_id:
        raise ContractError("recording Preview prospective asset identity changed")
    if blueprint_sha256(preview.blueprint) != preview.candidate_blueprint_sha256:
        raise ContractError("recording Preview candidate Blueprint changed")
    if audio_material_sha256(preview.blueprint) != preview.candidate_audio_material_sha256:
        raise ContractError("recording Preview candidate audio material changed")
    if preview.blueprint["project"].get("parent_revision_id") != preview.source_revision_id:
        raise ContractError("recording Preview candidate parent revision changed")

    # Asset write is deliberately delayed until every source/capture/candidate check above
    # succeeds. The immutable resource itself still is not creative authority.
    descriptor = import_audio_asset_bytes(project, wav_bytes)
    if str(descriptor["asset_id"]) != preview.prospective_asset_id:
        raise ContractError("recording finalized asset identity mismatch")

    validate_project_blueprint_audio(project, preview.blueprint)
    assets_after_import = {str(item["asset_id"]) for item in list_audio_assets(project)}
    if preview.prospective_asset_id not in assets_after_import:
        raise ContractError("recording finalized asset missing after import")

    provenance = preview.blueprint["provenance"]
    return project._commit_revision(
        preview.blueprint,
        branch=selected_branch,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
        allow_audio_material_change=True,
    )
