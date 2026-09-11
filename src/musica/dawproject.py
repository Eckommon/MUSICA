"""Bounded DAWproject 1.0 interchange bridge for MUSICA M5-R3.

DAWproject artifacts are projections and candidate carriers only. They never
outrank accepted MUSICA Blueprint revisions or canonical Music IR.
"""

from __future__ import annotations

import copy
import hashlib
import re
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any

from lxml import etree

from .compiler import PPQ, compile_blueprint
from .contracts import ContractError, clone_for_revision, validate_contract, validate_revision
from .diff import structured_diff
from .evidence import canonical_json_bytes
from .project import MusicaProject

FORMAT_VERSION = "1.0"
UPSTREAM_REPOSITORY = "bitwig/dawproject"
UPSTREAM_COMMIT = "ee4dcdde75940f30e14e55401a26955a58b8322b"
UPSTREAM_LICENSE = "MIT"
EXPORTER_ID = "musica-dawproject-exporter"
EXPORTER_VERSION = "0.1.0"
IMPORTER_ID = "musica-dawproject-importer"
IMPORTER_VERSION = "0.1.0"
NORMALIZATION_POLICY = "musica-dawproject-bounded-v0"
VELOCITY_POLICY = "midi-int-1-127_to_normalized-six-decimal_and_round-back-v0"
MAX_ARCHIVE_BYTES = 4 * 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 4 * 1024 * 1024
MAX_ENTRIES = 32
VENDOR_DIR = Path(__file__).resolve().parents[2] / "schemas" / "vendor" / "dawproject-1.0"
PROJECT_XSD = VENDOR_DIR / "Project.xsd"
METADATA_XSD = VENDOR_DIR / "MetaData.xsd"
LOSS_STATES = {"PRESERVED", "TRANSFORMED", "DROPPED", "UNSUPPORTED", "UNKNOWN"}
_MAPPING = re.compile(r"^MUSICA\|track_id=([^|]+)\|part_id=([^|]+)$")


class InterchangeError(ContractError):
    """Raised when bounded interchange cannot proceed safely."""


@dataclass(frozen=True)
class DawProjectExport:
    artifact: bytes
    project_xml: bytes
    metadata_xml: bytes
    loss_report: dict[str, Any]
    manifest: dict[str, Any]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value: Any) -> str:
    return _sha256(canonical_json_bytes(value))


def _decimal(value: float, digits: int = 6) -> str:
    text = f"{float(value):.{digits}f}"
    text = text.rstrip("0").rstrip(".")
    return text if text else "0"


@lru_cache(maxsize=2)
def _schema(path: str) -> etree.XMLSchema:
    try:
        document = etree.parse(path)
        return etree.XMLSchema(document)
    except (OSError, etree.XMLSchemaParseError, etree.XMLSyntaxError) as exc:
        raise InterchangeError(f"cannot load DAWproject schema: {path}") from exc


def _parse_xml(data: bytes, schema_path: Path, label: str) -> etree._Element:
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise InterchangeError(f"{label} contains forbidden DTD/entity declaration")
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        recover=False,
        huge_tree=False,
        remove_blank_text=False,
    )
    try:
        root = etree.fromstring(data, parser=parser)
    except etree.XMLSyntaxError as exc:
        raise InterchangeError(f"malformed {label}") from exc
    schema = _schema(str(schema_path))
    if not schema.validate(root):
        message = schema.error_log.last_error
        detail = message.message if message is not None else "schema validation failed"
        raise InterchangeError(f"{label} is not DAWproject 1.0 XSD-valid: {detail}")
    return root


def _xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(
        root,
        encoding="UTF-8",
        xml_declaration=True,
        standalone=True,
        pretty_print=False,
    )


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return stream.getvalue()


def _safe_zip_members(data: bytes) -> tuple[dict[str, bytes], list[str]]:
    if len(data) > MAX_ARCHIVE_BYTES:
        raise InterchangeError("DAWproject archive exceeds bounded compressed-size policy")
    try:
        archive = zipfile.ZipFile(BytesIO(data), "r")
    except zipfile.BadZipFile as exc:
        raise InterchangeError("malformed DAWproject ZIP") from exc

    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_ENTRIES:
            raise InterchangeError("DAWproject archive exceeds bounded entry-count policy")
        seen: set[str] = set()
        seen_casefold: set[str] = set()
        total = 0
        files: dict[str, bytes] = {}
        extras: list[str] = []
        for info in infos:
            name = info.filename
            if "\\" in name:
                raise InterchangeError(f"unsafe DAWproject archive path: {name}")
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                raise InterchangeError(f"unsafe DAWproject archive path: {name}")
            if info.is_dir():
                continue
            normalized = pure.as_posix()
            folded = normalized.casefold()
            if normalized in seen or folded in seen_casefold:
                raise InterchangeError(f"duplicate/ambiguous DAWproject archive entry: {normalized}")
            seen.add(normalized)
            seen_casefold.add(folded)
            if info.file_size > MAX_MEMBER_BYTES:
                raise InterchangeError(f"DAWproject member exceeds bounded size policy: {normalized}")
            total += info.file_size
            if total > MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise InterchangeError("DAWproject archive exceeds bounded uncompressed-size policy")
            if info.file_size > 1024 * 1024 and info.file_size > max(1, info.compress_size) * 64:
                raise InterchangeError(f"DAWproject member exceeds bounded compression-ratio policy: {normalized}")
            payload = archive.read(info)
            if len(payload) != info.file_size:
                raise InterchangeError(f"DAWproject member size mismatch: {normalized}")
            files[normalized] = payload
            if normalized not in {"project.xml", "metadata.xml"}:
                extras.append(normalized)

    if "project.xml" not in files:
        raise InterchangeError("DAWproject archive is missing project.xml")
    return files, sorted(extras)


def _meter_parts(meter: str) -> tuple[int, int]:
    try:
        numerator_text, denominator_text = meter.split("/", 1)
        numerator = int(numerator_text)
        denominator = int(denominator_text)
    except (ValueError, AttributeError) as exc:
        raise InterchangeError(f"unsupported MUSICA meter: {meter!r}") from exc
    if numerator <= 0 or denominator not in {1, 2, 4, 8, 16, 32}:
        raise InterchangeError(f"unsupported MUSICA meter: {meter!r}")
    return numerator, denominator


def _source_notes(ir: dict[str, Any]) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []
    for track in ir["tracks"]:
        notes = [
            {
                "tick": int(event["tick"]),
                "duration": int(event["duration"]),
                "note": int(event["note"]),
                "velocity": int(event["velocity"]),
                "channel": int(track["channel"]),
            }
            for event in track["events"]
            if event["type"] == "note"
        ]
        notes.sort(key=lambda item: (item["tick"], item["note"], item["duration"], item["velocity"]))
        tracks.append(
            {
                "track_id": str(track["track_id"]),
                "part_id": str(track["part_id"]),
                "notes": notes,
            }
        )
    return tracks


def _classify(semantic: str, state: str, reason: str, conversion_policy: str | None = None) -> dict[str, Any]:
    if state not in LOSS_STATES:
        raise InterchangeError(f"invalid interchange loss state: {state}")
    item = {"semantic": semantic, "state": state, "reason": reason}
    if conversion_policy is not None:
        item["conversion_policy"] = conversion_policy
    return item


def _base_loss_report(
    blueprint: dict[str, Any],
    ir: dict[str, Any],
    *,
    artifact_sha256: str,
    classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    report = {
        "report_version": "0",
        "source_revision_id": blueprint["project"]["revision_id"],
        "source_blueprint_sha256": _canonical_hash(blueprint),
        "source_music_ir_sha256": _canonical_hash(ir),
        "source_artifact_sha256": artifact_sha256,
        "normalization_policy": NORMALIZATION_POLICY,
        "classifications": classifications,
    }
    validate_contract(report, "interchange-loss-report-v0.schema.json")
    return report


def export_dawproject(blueprint: dict[str, Any], ir: dict[str, Any] | None = None) -> DawProjectExport:
    """Project one accepted Blueprint/Music-IR state into bounded DAWproject 1.0."""

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    compiled = copy.deepcopy(ir) if ir is not None else compile_blueprint(blueprint)
    validate_contract(compiled, "music-ir-v0.schema.json")
    if compiled["source_blueprint_revision"] != blueprint["project"]["revision_id"]:
        raise InterchangeError("Music IR is not bound to the supplied Blueprint revision")
    if int(compiled["timing"]["ppq"]) != PPQ:
        raise InterchangeError(f"M5-R3 v0 supports only PPQ={PPQ}")
    if len(compiled["tempo_events"]) != 1 or int(compiled["tempo_events"][0]["tick"]) != 0:
        raise InterchangeError("M5-R3 v0 supports one fixed tempo event at tick 0")

    bpm = float(compiled["tempo_events"][0]["bpm"])
    numerator, denominator = _meter_parts(blueprint["musical_context"]["meter"])
    project = etree.Element("Project", version=FORMAT_VERSION)
    etree.SubElement(project, "Application", name="MUSICA", version=EXPORTER_VERSION)
    transport = etree.SubElement(project, "Transport")
    etree.SubElement(
        transport,
        "Tempo",
        unit="bpm",
        value=_decimal(bpm),
        id="musica-tempo",
        name="Tempo",
    )
    etree.SubElement(
        transport,
        "TimeSignature",
        denominator=str(denominator),
        numerator=str(numerator),
        id="musica-meter",
        name="Meter",
    )

    structure = etree.SubElement(project, "Structure")
    track_xml_ids: dict[str, str] = {}
    for index, track in enumerate(compiled["tracks"]):
        xml_id = f"musica-track-{index:03d}"
        track_xml_ids[str(track["track_id"])] = xml_id
        etree.SubElement(
            structure,
            "Track",
            contentType="notes",
            loaded="true",
            id=xml_id,
            name=str(track["track_id"]),
            comment=f"MUSICA|track_id={track['track_id']}|part_id={track['part_id']}",
        )

    arrangement = etree.SubElement(project, "Arrangement", id="musica-arrangement")
    root_lanes = etree.SubElement(arrangement, "Lanes", timeUnit="beats", id="musica-lanes")
    for index, track in enumerate(compiled["tracks"]):
        track_id = str(track["track_id"])
        lane = etree.SubElement(
            root_lanes,
            "Lanes",
            track=track_xml_ids[track_id],
            id=f"musica-lane-{index:03d}",
        )
        clips = etree.SubElement(lane, "Clips", id=f"musica-clips-{index:03d}")
        note_events = [event for event in track["events"] if event["type"] == "note"]
        end_tick = max((int(event["tick"]) + int(event["duration"]) for event in note_events), default=0)
        clip = etree.SubElement(
            clips,
            "Clip",
            time="0",
            duration=_decimal(end_tick / PPQ, 9),
            playStart="0",
        )
        notes = etree.SubElement(
            clip,
            "Notes",
            timeUnit="beats",
            id=f"musica-notes-{index:03d}",
        )
        for event in sorted(
            note_events,
            key=lambda item: (int(item["tick"]), int(item["note"]), int(item["duration"]), int(item["velocity"])),
        ):
            etree.SubElement(
                notes,
                "Note",
                time=_decimal(int(event["tick"]) / PPQ, 9),
                duration=_decimal(int(event["duration"]) / PPQ, 9),
                channel=str(int(track["channel"])),
                key=str(int(event["note"])),
                vel=f"{int(event['velocity']) / 127.0:.6f}",
            )
    etree.SubElement(project, "Scenes")

    metadata = etree.Element("MetaData")
    etree.SubElement(metadata, "Title").text = str(blueprint["project"]["title"])
    etree.SubElement(metadata, "Producer").text = "MUSICA"
    etree.SubElement(metadata, "Comment").text = (
        f"Source revision {blueprint['project']['revision_id']}; "
        f"normalization {NORMALIZATION_POLICY}"
    )

    project_xml = _xml_bytes(project)
    metadata_xml = _xml_bytes(metadata)
    _parse_xml(project_xml, PROJECT_XSD, "project.xml")
    _parse_xml(metadata_xml, METADATA_XSD, "metadata.xml")
    artifact = _zip_bytes({"metadata.xml": metadata_xml, "project.xml": project_xml})
    artifact_sha = _sha256(artifact)

    control_count = sum(
        1
        for track in compiled["tracks"]
        for event in track["events"]
        if event["type"] == "control"
    )
    classifications = [
        _classify("tempo", "PRESERVED", "Fixed tick-zero BPM is represented by Transport/Tempo."),
        _classify("meter", "PRESERVED", "Blueprint fixed meter is represented by Transport/TimeSignature."),
        _classify("track_order", "PRESERVED", "Structure and arrangement lanes are emitted in canonical IR track order."),
        _classify("note_pitch", "PRESERVED", "MIDI key integers are copied exactly."),
        _classify("note_start", "TRANSFORMED", "Ticks are converted to beat decimals.", f"tick/{PPQ}"),
        _classify("note_duration", "TRANSFORMED", "Tick durations are converted to beat decimals.", f"duration/{PPQ}"),
        _classify("note_velocity", "TRANSFORMED", "Integer velocity is normalized for DAWproject Note.vel.", VELOCITY_POLICY),
        _classify("track_part_mapping", "PRESERVED", "MUSICA track_id and part_id are carried in Track.comment."),
        _classify("midi_control_events", "UNSUPPORTED" if control_count else "PRESERVED",
                  f"M5-R3 v0 does not project {control_count} Music-IR control events." if control_count else "No control events present."),
        _classify("program_timbre_hints", "UNSUPPORTED", "M5-R3 v0 does not claim DAW instrument/device fidelity."),
        _classify("blueprint_semantics", "UNSUPPORTED", "Semantic vectors remain authoritative only in MUSICA Blueprint."),
        _classify("locks_constraints", "UNSUPPORTED", "Locks/constraints are not serialized as DAWproject authority data."),
    ]
    loss_report = _base_loss_report(
        blueprint,
        compiled,
        artifact_sha256=artifact_sha,
        classifications=classifications,
    )
    manifest = {
        "format": "DAWproject",
        "format_version": FORMAT_VERSION,
        "upstream_repository": UPSTREAM_REPOSITORY,
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_license": UPSTREAM_LICENSE,
        "exporter_id": EXPORTER_ID,
        "exporter_version": EXPORTER_VERSION,
        "normalization_policy": NORMALIZATION_POLICY,
        "source_revision_id": blueprint["project"]["revision_id"],
        "source_blueprint_sha256": _canonical_hash(blueprint),
        "source_music_ir_sha256": _canonical_hash(compiled),
        "project_xml_sha256": _sha256(project_xml),
        "metadata_xml_sha256": _sha256(metadata_xml),
        "artifact_sha256": artifact_sha,
        "loss_report_sha256": _canonical_hash(loss_report),
    }
    return DawProjectExport(artifact, project_xml, metadata_xml, loss_report, manifest)


def _track_mapping(track: etree._Element) -> tuple[str | None, str | None]:
    comment = track.get("comment") or ""
    match = _MAPPING.fullmatch(comment)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def _import_normalized(project_root: etree._Element) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if project_root.tag != "Project" or project_root.get("version") != FORMAT_VERSION:
        raise InterchangeError(f"unsupported DAWproject format version: {project_root.get('version')!r}")

    application = project_root.find("Application")
    transport = project_root.find("Transport")
    if application is None or transport is None:
        raise InterchangeError("bounded DAWproject requires Application and Transport")
    tempo = transport.find("Tempo")
    meter = transport.find("TimeSignature")
    if tempo is None or meter is None or tempo.get("value") is None:
        raise InterchangeError("bounded DAWproject requires fixed tempo and time signature")
    try:
        bpm = float(tempo.get("value"))
        numerator = int(meter.get("numerator"))
        denominator = int(meter.get("denominator"))
    except (TypeError, ValueError) as exc:
        raise InterchangeError("invalid bounded DAWproject transport values") from exc
    _meter_parts(f"{numerator}/{denominator}")
    if not 20 <= bpm <= 300:
        raise InterchangeError("bounded DAWproject tempo is outside MUSICA v0 range")

    structure = project_root.find("Structure")
    arrangement = project_root.find("Arrangement")
    if structure is None or arrangement is None:
        raise InterchangeError("bounded DAWproject requires Structure and Arrangement")

    ordered: list[tuple[str, str | None, str | None]] = []
    for track in structure.findall("Track"):
        xml_id = track.get("id")
        if not xml_id:
            raise InterchangeError("bounded DAWproject Track lacks id")
        source_track, source_part = _track_mapping(track)
        ordered.append((xml_id, source_track, source_part))
    if not ordered:
        raise InterchangeError("bounded DAWproject contains no tracks")

    lanes_by_track: dict[str, etree._Element] = {}
    for lane in arrangement.xpath(".//Lanes[@track]"):
        track_ref = lane.get("track")
        if track_ref in lanes_by_track:
            raise InterchangeError(f"ambiguous multiple arrangement lanes for track {track_ref}")
        lanes_by_track[str(track_ref)] = lane

    normalized_tracks: list[dict[str, Any]] = []
    mapping_issues: list[dict[str, Any]] = []
    for xml_id, source_track, source_part in ordered:
        lane = lanes_by_track.get(xml_id)
        if lane is None:
            raise InterchangeError(f"bounded DAWproject lacks arrangement lane for track {xml_id}")
        note_nodes = lane.xpath("./Clips/Clip/Notes/Note")
        clips = lane.xpath("./Clips/Clip")
        if len(clips) != 1:
            raise InterchangeError(f"bounded DAWproject requires exactly one direct note Clip for track {xml_id}")
        clip = clips[0]
        try:
            clip_offset_beats = float(clip.get("time", "0"))
        except ValueError as exc:
            raise InterchangeError(f"invalid clip time for track {xml_id}") from exc

        notes: list[dict[str, int]] = []
        for note in note_nodes:
            try:
                tick = round((clip_offset_beats + float(note.get("time"))) * PPQ)
                duration = round(float(note.get("duration")) * PPQ)
                key = int(note.get("key"))
                velocity = round(float(note.get("vel", "1")) * 127.0)
                channel = int(note.get("channel"))
            except (TypeError, ValueError) as exc:
                raise InterchangeError(f"invalid note value for track {xml_id}") from exc
            if tick < 0 or duration <= 0 or not 0 <= key <= 127 or not 0 <= channel <= 15:
                raise InterchangeError(f"note outside bounded MUSICA range for track {xml_id}")
            velocity = max(1, min(127, velocity))
            notes.append(
                {
                    "tick": tick,
                    "duration": duration,
                    "note": key,
                    "velocity": velocity,
                    "channel": channel,
                }
            )
        notes.sort(key=lambda item: (item["tick"], item["note"], item["duration"], item["velocity"]))
        if source_track is None or source_part is None:
            mapping_issues.append(
                _classify("track_part_mapping", "UNKNOWN", f"Track {xml_id} lacks MUSICA trace mapping.")
            )
        normalized_tracks.append(
            {
                "xml_track_id": xml_id,
                "track_id": source_track,
                "part_id": source_part,
                "notes": notes,
            }
        )

    normalized = {
        "format_version": FORMAT_VERSION,
        "source_application": {
            "name": application.get("name"),
            "version": application.get("version"),
        },
        "transport": {
            "bpm": bpm,
            "meter": f"{numerator}/{denominator}",
        },
        "tracks": normalized_tracks,
    }
    return normalized, mapping_issues


def import_dawproject_candidate(
    project: MusicaProject,
    artifact: bytes,
    *,
    branch: str | None = None,
    expected_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    """Import DAWproject bytes as a non-canonical candidate without mutating M2 state."""

    observed_artifact_sha256 = _sha256(artifact)
    if expected_artifact_sha256 is not None and observed_artifact_sha256 != expected_artifact_sha256:
        raise InterchangeError(
            f"DAWproject artifact hash mismatch: expected {expected_artifact_sha256}, got {observed_artifact_sha256}"
        )
    source_branch = branch or project.current_branch()
    source_revision_id = project.head_revision_id(source_branch)
    source_blueprint = project.read_revision(source_revision_id)
    source_ir = compile_blueprint(source_blueprint)
    before_head = project.head_revision_id(source_branch)
    before_blueprint_hash = _canonical_hash(source_blueprint)

    files, extras = _safe_zip_members(artifact)
    project_root = _parse_xml(files["project.xml"], PROJECT_XSD, "project.xml")
    if "metadata.xml" in files:
        _parse_xml(files["metadata.xml"], METADATA_XSD, "metadata.xml")
    normalized, mapping_issues = _import_normalized(project_root)

    if project.head_revision_id(source_branch) != before_head:
        raise InterchangeError("import unexpectedly mutated accepted branch state")
    if _canonical_hash(project.read_revision(source_revision_id)) != before_blueprint_hash:
        raise InterchangeError("import unexpectedly mutated accepted Blueprint")

    expected_tracks = _source_notes(source_ir)
    imported_tracks = normalized["tracks"]
    mapping_complete = all(item["track_id"] and item["part_id"] for item in imported_tracks)
    imported_comparable = [
        {
            "track_id": item["track_id"],
            "part_id": item["part_id"],
            "notes": item["notes"],
        }
        for item in imported_tracks
    ]
    note_equal = imported_comparable == expected_tracks
    expected_order = [item["track_id"] for item in expected_tracks]
    imported_order = [item["track_id"] for item in imported_tracks]
    track_order_equal = mapping_complete and expected_order == imported_order

    source_bpm = float(source_blueprint["musical_context"]["tempo"]["bpm"])
    source_meter = str(source_blueprint["musical_context"]["meter"])
    imported_bpm = float(normalized["transport"]["bpm"])
    imported_meter = str(normalized["transport"]["meter"])
    artifact_sha = observed_artifact_sha256

    classifications = [
        _classify("tempo", "PRESERVED" if imported_bpm == source_bpm else "TRANSFORMED",
                  "Imported BPM equals accepted Blueprint." if imported_bpm == source_bpm else f"External BPM proposes {source_bpm} -> {imported_bpm}."),
        _classify("meter", "PRESERVED" if imported_meter == source_meter else "TRANSFORMED",
                  "Imported meter equals accepted Blueprint." if imported_meter == source_meter else f"External meter proposes {source_meter} -> {imported_meter}."),
        _classify("track_order", "PRESERVED" if track_order_equal else "UNKNOWN",
                  "Traceable track order is identical." if track_order_equal else "Track order cannot be proven identical."),
        _classify("note_pitch", "PRESERVED" if note_equal else "UNSUPPORTED",
                  "All normalized notes are identical." if note_equal else "External note edits cannot be reverse-mapped into Blueprint v0 safely."),
        _classify("note_start", "PRESERVED" if note_equal else "UNSUPPORTED",
                  "All normalized note starts are identical." if note_equal else "External note edits cannot be reverse-mapped into Blueprint v0 safely."),
        _classify("note_duration", "PRESERVED" if note_equal else "UNSUPPORTED",
                  "All normalized note durations are identical." if note_equal else "External note edits cannot be reverse-mapped into Blueprint v0 safely."),
        _classify("note_velocity", "PRESERVED" if note_equal else "UNSUPPORTED",
                  "Velocity normalization round-trips to the exact source integers." if note_equal else "External note edits cannot be reverse-mapped into Blueprint v0 safely.",
                  VELOCITY_POLICY),
        _classify("track_part_mapping", "PRESERVED" if mapping_complete else "UNKNOWN",
                  "All tracks carry MUSICA source IDs." if mapping_complete else "One or more tracks lack MUSICA source IDs."),
        _classify("extra_archive_members", "UNSUPPORTED" if extras else "PRESERVED",
                  f"Ignored non-authoritative archive members: {extras}" if extras else "No extra archive members."),
        _classify("blueprint_semantics", "UNSUPPORTED", "DAWproject does not become authority for MUSICA semantic vectors."),
        _classify("locks_constraints", "UNSUPPORTED", "DAWproject does not become authority for MUSICA locks or constraints."),
    ] + mapping_issues
    loss_report = _base_loss_report(
        source_blueprint,
        source_ir,
        artifact_sha256=artifact_sha,
        classifications=classifications,
    )

    proposed = clone_for_revision(source_blueprint, f"import-{artifact_sha[:16]}")
    proposed_changes: list[dict[str, Any]] = []
    if imported_bpm != source_bpm:
        proposed["musical_context"]["tempo"]["bpm"] = imported_bpm
        proposed_changes.append({"path": "/musical_context/tempo/bpm", "before": source_bpm, "after": imported_bpm})
    if imported_meter != source_meter:
        proposed["musical_context"]["meter"] = imported_meter
        proposed_changes.append({"path": "/musical_context/meter", "before": source_meter, "after": imported_meter})
    proposed["provenance"] = {
        "created_from_intent_id": source_blueprint["provenance"]["created_from_intent_id"],
        "actor": "import",
        "change_reason": f"Import bounded DAWproject candidate {artifact_sha}.",
        "source_revision": source_revision_id,
        "selected_mechanisms": ["dawproject_import"],
        "rejected_mechanisms": [],
    }

    conflicts: list[dict[str, Any]] = []
    if not note_equal:
        conflicts.append(
            {
                "conflict_id": "C-INTERCHANGE-NOTES-001",
                "rule_type": "interchange",
                "rule_id": "blueprint-v0-note-reverse-mapping",
                "target": "/materials",
                "status": "BLOCKED",
                "reason": "External note edit is UNSUPPORTED because Blueprint v0 stores generative musical material rather than canonical note timeline.",
            }
        )
    if not mapping_complete or not track_order_equal:
        conflicts.append(
            {
                "conflict_id": "C-INTERCHANGE-MAPPING-001",
                "rule_type": "interchange",
                "rule_id": "traceable-track-part-mapping",
                "target": "/roles/instruments_or_parts",
                "status": "BLOCKED",
                "reason": "Imported track/part identity or order is not safely traceable.",
            }
        )

    try:
        revision_conflicts = validate_revision(source_blueprint, proposed)
        conflicts.extend(item.as_dict() for item in revision_conflicts)
    except ContractError as exc:
        conflicts.append(
            {
                "conflict_id": "C-INTERCHANGE-CONTRACT-001",
                "rule_type": "contract",
                "rule_id": "music-blueprint-v0",
                "target": "/",
                "status": "BLOCKED",
                "reason": str(exc),
            }
        )
    validation_status = "BLOCKED" if any(item["status"] == "BLOCKED" for item in conflicts) else "PASS"
    candidate_seed = {
        "source_revision_id": source_revision_id,
        "source_artifact_sha256": artifact_sha,
        "normalized": normalized,
    }
    candidate_id = f"CAND-{_canonical_hash(candidate_seed)[:16]}"
    candidate = {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "status": "PENDING",
        "validation_status": validation_status,
        "source_branch": source_branch,
        "source_revision_id": source_revision_id,
        "source_artifact_sha256": artifact_sha,
        "source_application": normalized["source_application"],
        "transport": normalized["transport"],
        "tracks": normalized["tracks"],
        "proposed_changes": proposed_changes,
        "proposed_blueprint": proposed,
        "conflicts": conflicts,
        "loss_report_sha256": _canonical_hash(loss_report),
        "loss_report": loss_report,
        "normalized_candidate_sha256": _canonical_hash(normalized),
        "project_xml_sha256": _sha256(files["project.xml"]),
        "metadata_xml_sha256": _sha256(files["metadata.xml"]) if "metadata.xml" in files else None,
        "importer": {
            "id": IMPORTER_ID,
            "version": IMPORTER_VERSION,
            "normalization_policy": NORMALIZATION_POLICY,
            "upstream_commit": UPSTREAM_COMMIT,
        },
    }
    candidate["diff"] = structured_diff(source_blueprint, proposed)
    candidate["diff_sha256"] = _canonical_hash(candidate["diff"])
    validate_contract(candidate, "interchange-candidate-v0.schema.json")
    return candidate


def accept_dawproject_candidate(project: MusicaProject, candidate: dict[str, Any]) -> dict[str, Any]:
    """Explicitly accept a validated pending candidate through M2 only."""

    validate_contract(candidate, "interchange-candidate-v0.schema.json")
    if candidate["status"] != "PENDING" or candidate["validation_status"] != "PASS":
        raise InterchangeError("only a PENDING candidate with validation PASS may be accepted")
    branch = str(candidate["source_branch"])
    expected_revision = str(candidate["source_revision_id"])
    if project.head_revision_id(branch) != expected_revision:
        raise InterchangeError("stale import candidate: branch head moved after import")
    proposed = copy.deepcopy(candidate["proposed_blueprint"])
    conflicts = validate_revision(project.read_revision(expected_revision), proposed)
    blocking = [item for item in conflicts if item.status == "BLOCKED"]
    if blocking:
        raise InterchangeError("candidate no longer satisfies HARD locks/constraints")
    record = project.commit_revision(
        proposed,
        branch=branch,
        actor="import",
        reason=f"Explicitly accept DAWproject candidate {candidate['candidate_id']} from {candidate['source_artifact_sha256']}.",
    )
    return {
        "candidate_id": candidate["candidate_id"],
        "accepted_revision_id": record["revision_id"],
        "revision_record": record,
        "source_artifact_sha256": candidate["source_artifact_sha256"],
    }


def inspect_dawproject(artifact: bytes) -> dict[str, Any]:
    """Safely inspect and XSD-validate a bounded DAWproject artifact."""

    files, extras = _safe_zip_members(artifact)
    project_root = _parse_xml(files["project.xml"], PROJECT_XSD, "project.xml")
    if "metadata.xml" in files:
        _parse_xml(files["metadata.xml"], METADATA_XSD, "metadata.xml")
    normalized, mapping_issues = _import_normalized(project_root)
    return {
        "artifact_sha256": _sha256(artifact),
        "project_xml_sha256": _sha256(files["project.xml"]),
        "metadata_xml_sha256": _sha256(files["metadata.xml"]) if "metadata.xml" in files else None,
        "extras": extras,
        "normalized": normalized,
        "mapping_issues": mapping_issues,
    }
