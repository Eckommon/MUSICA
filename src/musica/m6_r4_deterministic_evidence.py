"""Byte-reproducible canonical M6-R4 evidence entrypoint.

The underlying evidence scenarios intentionally rewrite DAWproject fixtures.  This
entrypoint pins ZIP metadata for those rewritten fixtures so repeated evidence
runs from the same source head are byte-identical rather than inheriting wall-clock
ZIP timestamps.
"""

from __future__ import annotations

import os
import zipfile
from io import BytesIO
from typing import Callable

from lxml import etree

from . import m6_r4_evidence as base


def _deterministic_rewrite(
    artifact: bytes,
    mutate: Callable[[etree._Element, list[etree._Element]], None],
) -> bytes:
    with zipfile.ZipFile(BytesIO(artifact), "r") as source:
        files = {name: source.read(name) for name in source.namelist()}

    root = etree.fromstring(files["project.xml"])
    motif = next(
        track
        for track in root.find("Structure").findall("Track")
        if "track_id=T-MOTIF" in (track.get("comment") or "")
    )
    lane = next(
        lane
        for lane in root.xpath(".//Lanes[@track]")
        if lane.get("track") == motif.get("id")
    )
    notes = lane.xpath("./Clips/Clip/Notes/Note")
    mutate(root, notes)
    files["project.xml"] = etree.tostring(
        root,
        encoding="UTF-8",
        xml_declaration=True,
        standalone=True,
        pretty_print=False,
    )

    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as output:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            output.writestr(info, files[name])
    return stream.getvalue()


def generate(output_dir: str) -> dict:
    original = base._rewrite
    try:
        base._rewrite = _deterministic_rewrite
        return base.generate_m6_r4_evidence(output_dir)
    finally:
        base._rewrite = original


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_M6_R4_EVIDENCE_OUT",
        "artifacts/m6-r4-interchange-note-reconciliation",
    )
    generate(destination)
