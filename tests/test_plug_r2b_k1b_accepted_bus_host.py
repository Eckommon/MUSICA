"""PLUG-R2B K1-B: authorized, persisted simulated bus plugin state."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from musica.bus_host_material import (
    accepted_bus_host_sha256, bus_host_material_from_blueprint,
    empty_bus_host_material, validate_bus_host_material,
)
from musica.bus_host_edit import (
    accept_bus_host_edit_preview,
    build_bus_host_edit_preview,
    source_for_bus_host_candidate,
)
from musica.contracts import ContractError
from musica.project import MusicaProject
from test_plug_r2b_k1_accepted_bridge import _accepted_two_buses


def _instance(
    bus: str = "BUS-001", *, instance_id: str = "BPI-001",
    latency: int = 3, creative: int = 0, bypass: bool = False,
):
    return {
        "instance_id": instance_id,
        "owner_kind": "routing_node",
        "owner_bus_id": bus,
        "slot": 0,
        "processor_id": "musica-simulated-bus-latency-v0",
        "processor_version": "0",
        "latency_provenance": "accepted_explicit_simulated_reference",
        "algorithmic_latency_frames": latency,
        "creative_delay_frames": creative,
        "bypass": bypass,
    }


def _material(instances: list[dict]) -> dict:
    return {
        "material_version": "0",
        "classification": "accepted_simulated_bus_host_material",
        "instances": sorted(instances, key=lambda x: x["owner_bus_id"]),
    }


def _candidate(parent: dict, material: dict, suffix: str = "A") -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": f"K1-B-{suffix}",
        "authority_target": "blueprint_bus_plugin_material",
        "source": source_for_bus_host_candidate(parent),
        "proposed_material": copy.deepcopy(material),
        "actor": {"kind": "user", "actor_id": "k1-b-test"},
        "reason": f"explicit accepted bus processor change {suffix}",
        "preview_only": True,
    }


def _accept(project, parent: dict, material: dict, suffix: str):
    candidate = _candidate(parent, material, suffix)
    preview = build_bus_host_edit_preview(project, parent, candidate)
    assert preview.ready, preview.reason
    assert preview.blueprint is not None
    head = project.head_revision_id("main")
    assert head == parent["project"]["revision_id"]
    assert project.head_revision_id("main") == head
    with pytest.raises(ContractError, match="trusted bus-host Preview/Accept"):
        project.commit_revision(preview.blueprint)
    assert project.head_revision_id("main") == head
    record = accept_bus_host_edit_preview(project, preview)
    with pytest.raises(ContractError, match="stale"):
        accept_bus_host_edit_preview(project, preview)
    assert project.head_revision_id("main") == record["revision_id"]
    return project.read_revision(record["revision_id"])


def test_bus_plugin_add_exact_preview_accept_and_reopen(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    source = project.read_revision(revision)
    assert bus_host_material_from_blueprint(source) == empty_bus_host_material()
    head = project.head_revision_id("main")
    material = _material([_instance(), _instance(
        "BUS-002", instance_id="BPI-002", latency=9)])
    candidate = _candidate(source, material)
    preview = build_bus_host_edit_preview(project, source, candidate)
    assert preview.ready and preview.blueprint is not None
    assert preview.changed_instance_ids == ("BPI-001", "BPI-002")
    assert project.head_revision_id("main") == head
    accepted = _accept(project, source, material, "ADD")
    assert bus_host_material_from_blueprint(accepted) == material
    assert accepted_bus_host_sha256(accepted) != accepted_bus_host_sha256(source)
    assert accepted["materials"]["plugins"] == source["materials"]["plugins"] if "plugins" in source["materials"] else True
    exported = project.export_to(tmp_path / "k1-b-project.musica.zip")
    reopened = MusicaProject.import_from(exported, tmp_path / "reopened.musica")
    assert bus_host_material_from_blueprint(
        reopened.read_revision(accepted["project"]["revision_id"])
    ) == material
    assert accepted_bus_host_sha256(
        reopened.read_revision(accepted["project"]["revision_id"])
    ) == accepted_bus_host_sha256(accepted)


def test_bus_plugin_parameter_bypass_and_remove_each_need_explicit_accept(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    source = project.read_revision(revision)
    a = _accept(project, source, _material([_instance()]), "ADD")
    state = _accept(project, a, _material([_instance(latency=8, creative=5)]), "STATE")
    assert bus_host_material_from_blueprint(state)["instances"][0]["creative_delay_frames"] == 5
    bypassed = _accept(project, state, _material([_instance(
        latency=8, creative=5, bypass=True
    )]), "BYPASS")
    assert bus_host_material_from_blueprint(bypassed)["instances"][0]["bypass"] is True
    removed = _accept(project, bypassed, empty_bus_host_material(), "REMOVE")
    assert bus_host_material_from_blueprint(removed)["instances"] == []
    assert project.head_revision_id("main") == removed["project"]["revision_id"]


def test_stale_source_forged_parent_tampered_preview_and_noop_fail_closed(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    parent = project.read_revision(revision)
    material = _material([_instance()])
    candidate = _candidate(parent, material)
    stale = copy.deepcopy(candidate)
    stale["source"]["blueprint_sha256"] = "f" * 64
    blocked = build_bus_host_edit_preview(project, parent, stale)
    assert not blocked.ready
    with pytest.raises(ContractError):
        accept_bus_host_edit_preview(project, blocked)
    forged = copy.deepcopy(parent)
    forged["project"]["title"] = str(forged["project"]["title"]) + " forged"
    assert not build_bus_host_edit_preview(
        project, forged, _candidate(forged, material, "FORGED")
    ).ready
    preview = build_bus_host_edit_preview(project, parent, candidate)
    assert preview.ready
    assert preview.blueprint is not None
    preview.blueprint["materials"]["bus_plugins"]["instances"][0]["algorithmic_latency_frames"] = 5
    with pytest.raises(ContractError, match="Blueprint was changed"):
        accept_bus_host_edit_preview(project, preview)
    assert project.head_revision_id("main") == revision
    assert not build_bus_host_edit_preview(
        project, parent, _candidate(parent, empty_bus_host_material(), "NOOP")
    ).ready


@pytest.mark.parametrize("case", [
    "wrong_bus", "duplicate_bus", "unknown_processor",
    "wrong_provenance", "negative_latency", "excessive_latency",
    "noninteger_latency", "duplicate_instance_id",
])
def test_reject_invalid_simulated_bus_plugin_proposal(tmp_path: Path, case: str):
    project, revision = _accepted_two_buses(tmp_path)
    parent = project.read_revision(revision)
    instances = [_instance()]
    first = instances[0]
    if case == "wrong_bus":
        first["owner_bus_id"] = "BUS-NOT-ACCEPTED"
    elif case == "duplicate_bus":
        instances.append(_instance("BUS-001", instance_id="BPI-002"))
    elif case == "duplicate_instance_id":
        instances.append(_instance("BUS-002", instance_id="BPI-001"))
    elif case == "unknown_processor":
        first["processor_id"] = "external-VST3"
    elif case == "wrong_provenance":
        first["latency_provenance"] = "measured_real_plugin"
    elif case == "negative_latency":
        first["algorithmic_latency_frames"] = -1
    elif case == "excessive_latency":
        first["algorithmic_latency_frames"] = 4097
    elif case == "noninteger_latency":
        first["algorithmic_latency_frames"] = 1.5
    preview = build_bus_host_edit_preview(
        project, parent, _candidate(parent, _material(instances), case)
    )
    assert not preview.ready
    assert project.head_revision_id("main") == revision


def test_non_neutral_master_cannot_accept_bus_processor_state(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    accepted = project.read_revision(revision)
    forged = copy.deepcopy(accepted)
    forged["materials"]["routing"]["nodes"][-1]["mixer"]["gain_db"] = -3.0
    with pytest.raises(ContractError, match="neutral unmuted master"):
        validate_bus_host_material(_material([_instance()]), blueprint=forged)
