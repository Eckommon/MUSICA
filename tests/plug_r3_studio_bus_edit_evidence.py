"""PLUG-R3-A independent exact Studio Preview->Accept and WAV evidence."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import wave

from musica.bus_host_material import bus_host_material_from_blueprint
from musica.bus_host_runtime import render_accepted_simulated_bus_host
from musica.evidence import canonical_json_bytes
from musica.project import MusicaProject
from musica.studio_bus_plugin_edit import StudioBusHostEditSurface

from test_plug_r2b_k2_studio_bus_plugins import _service, _pair
from test_plug_r2b_k1b_accepted_bus_host import _candidate

ROOT=Path(__file__).resolve().parents[1]
FILES=[
    "schemas/studio-preview-v0.schema.json",
    "src/musica/studio.py",
    "src/musica/studio_http.py",
    "src/musica/studio_bus_plugin_edit.py",
    "src/musica/bus_host_edit.py",
    "tests/test_plug_r3_studio_bus_edit.py",
    "tests/plug_r3_studio_bus_edit_evidence.py",
    "docs/PLUG_R3_STUDIO_BUS_EDIT_CONTRACT.md",
    ".github/workflows/plug-r3-studio-bus-edit-evidence.yml",
]


def _sha(v: bytes) -> str:
    return hashlib.sha256(v).hexdigest()


def _json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value))


def _frames(w: bytes):
    with wave.open(io.BytesIO(w)) as r:
        assert r.getnchannels()==2 and r.getsampwidth()==2 and r.getframerate()==8000
        return list(struct.iter_unpack("<hh",r.readframes(r.getnframes())))


def generate(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="musica-plug-r3-") as value:
        service,sid,project,rid=_service(Path(value))
        parent=project.read_revision(rid)
        before=service.media_bytes(sid,"audio")
        surface=StudioBusHostEditSurface(service)
        view=surface.editor_view(sid)
        assert view["source"]["revision_id"]==rid
        candidate=_candidate(parent,_pair(),"R3-EVIDENCE")
        preview=surface.preview_edit(sid,candidate=candidate)
        assert preview["preview_installed"] is True
        assert project.head_revision_id("main")==rid
        preview_raw=surface.preview_wav(sid)
        assert _sha(preview_raw)==preview["detail"]["offline_preview"]["wav_sha256"]
        assert service.media_bytes(sid,"audio")==before

        accepted=service.accept_preview(sid)
        new_rid=accepted["revision_record"]["revision_id"]
        assert accepted["artifact_manifest"] is None
        assert project.head_revision_id("main")==new_rid
        assert service.media_bytes(sid,"audio")==before
        blueprint=project.read_revision(new_rid)
        assert bus_host_material_from_blueprint(blueprint)==_pair()
        post=render_accepted_simulated_bus_host(project,new_rid,sample_rate_hz=8000)
        assert post.wav_bytes==preview_raw
        assert service.inspect_session(sid)["pending_preview"] is None
        assert _frames(preview_raw)[9]==(24576,24576)

        archive=project.export_to(out/"accepted-project.musica.zip")
        reopened=MusicaProject.import_from(
            archive,Path(value)/"reopened.musica"
        )
        replay=render_accepted_simulated_bus_host(reopened,new_rid,sample_rate_hz=8000)
        assert replay.plan==post.plan and replay.wav_bytes==post.wav_bytes
        _json(out/"source-editor.json",view)
        _json(out/"preview.json",{
            "preview":preview["preview"],
            "offline_preview":preview["detail"]["offline_preview"],
            "changed_instance_ids":preview["detail"]["changed_instance_ids"],
        })
        _json(out/"accepted-material.json",bus_host_material_from_blueprint(blueprint))
        _json(out/"derived-plan.json",post.plan)
        (out/"preview.wav").write_bytes(preview_raw)
        (out/"accepted-replay.wav").write_bytes(post.wav_bytes)
        _json(out/"proof.json",{
            "version":"0",
            "classification":"STUDIO_EXPLICIT_BUS_HOST_PREVIEW_ACCEPT_OFFLINE_ONLY",
            "parent_revision_id":rid,
            "accepted_revision_id":new_rid,
            "preview_left_head_unchanged":True,
            "explicit_accept_advanced_exactly_one_revision":True,
            "accepted_material_is_from_exact_source_candidate":True,
            "preview_audio_matches_accepted_audio_byte_exact":True,
            "generic_studio_audio_unchanged":True,
            "export_reopen_exact_plan_and_wav":True,
            "first_aligned_sample_frame":9,
            "first_aligned_pcm":[24576,24576],
            "browser_graphical_editor_proven":False,
            "native_realtime_plugin_host_proven":False,
        })

    manifest={
        "version":"0",
        "classification":"PLUG_R3_STUDIO_BUS_HOST_AUTHORITY_EVIDENCE",
        "artifacts":[
            {"path":f.name,"bytes":len(f.read_bytes()),"sha256":_sha(f.read_bytes())}
            for f in sorted(out.iterdir())
        ],
        "contracts":[
            {"path":n,"bytes":len((ROOT/n).read_bytes()),"sha256":_sha((ROOT/n).read_bytes())}
            for n in FILES
        ],
    }
    _json(out/"manifest.json",manifest)


if __name__=="__main__":
    generate(Path(os.environ.get("MUSICA_PLUG_R3_OUT","artifacts/plug-r3")))
    print("PLUG-R3 Studio bus-host Preview/Accept authority evidence generated")
