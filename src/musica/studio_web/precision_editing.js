(() => {
  "use strict";

  const originalFetch = window.fetch.bind(window);
  const precision = {
    sessionId: null,
    view: null,
    selectedKey: null,
    requestCounter: 0,
    root: null,
  };

  const el = (id) => document.getElementById(id);
  const noteKey = (note) => `${note.part_id}::${note.note_id}`;

  function status(message, kind = "info") {
    const target = el("m6NoteStatus");
    if (!target) return;
    target.textContent = message;
    target.className = `m6-note-status ${kind}`;
    target.hidden = false;
  }

  function clearStatus() {
    const target = el("m6NoteStatus");
    if (!target) return;
    target.hidden = true;
    target.textContent = "";
  }

  async function precisionFetch(path, options = {}) {
    const init = { method: options.method || "GET", headers: { Accept: "application/json" } };
    if (options.body !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(options.body);
    }
    const response = await originalFetch(path, init);
    const payload = await response.json();
    if (!response.ok || !payload || payload.ok === false) {
      const detail = payload && payload.error ? payload.error : { message: `HTTP ${response.status}` };
      const error = new Error(detail.message || `HTTP ${response.status}`);
      error.code = detail.code || "http_error";
      throw error;
    }
    return payload.data;
  }

  function observeSessionPayload(payload) {
    if (!payload || typeof payload !== "object") return;
    const data = payload.data && typeof payload.data === "object" ? payload.data : payload;
    const session = data.session && typeof data.session === "object" ? data.session : null;
    if (!session || !session.session_id) return;
    const changed = precision.sessionId !== session.session_id;
    precision.sessionId = session.session_id;
    if (changed || session.head_revision_id) queueMicrotask(() => refreshNoteView(true));
  }

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/notes")) {
        const clone = response.clone();
        const contentType = clone.headers.get("content-type") || "";
        if (contentType.includes("application/json")) observeSessionPayload(await clone.json());
      }
    } catch (_error) {
      // Observation is non-authoritative and must never break the core Studio request.
    }
    return response;
  };

  function injectSurface() {
    const panel = el("panel-inspect");
    if (!panel || el("m6PrecisionCard")) return;
    const heading = panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "m6PrecisionCard";
    card.className = "card m6-precision-card";
    card.innerHTML = `
      <div class="card-heading m6-heading">
        <div><span class="eyebrow">M6 · PRECISION</span><h2>Exact-note piano roll / 정밀 노트 편집</h2></div>
        <span id="m6Availability" class="status-pill neutral">NO PROJECT</span>
      </div>
      <p class="muted small m6-authority-copy">Browser coordinates are interaction data only. Every change becomes a source-bound NoteEditCandidate and remains PREVIEW until explicit Accept.</p>
      <div id="m6NoteStatus" class="m6-note-status" role="status" aria-live="polite" hidden></div>
      <div id="m6Unavailable" class="m6-unavailable">Open an exact-note project to use precision editing / exact-note 프로젝트를 열어 정밀 편집을 사용하세요.</div>
      <div id="m6Workspace" hidden>
        <div class="m6-roll-toolbar">
          <span id="m6SourceBinding" class="mono muted">—</span>
          <span id="m6PreviewBadge" class="status-pill accepted">ACCEPTED NOTES</span>
        </div>
        <div id="m6PianoScroll" class="m6-piano-scroll" tabindex="0" aria-label="Exact-note piano roll / exact-note 피아노 롤">
          <div id="m6PianoRoll" class="m6-piano-roll"></div>
        </div>
        <div class="m6-editor-grid">
          <fieldset id="m6SelectedFieldset" class="m6-note-editor" disabled>
            <legend>Selected note / 선택 노트</legend>
            <div class="m6-selected-id"><strong id="m6SelectedId">—</strong><span id="m6SelectedLocks" class="m6-lock-badges"></span></div>
            <div class="m6-fields">
              <label>Start beat<input id="m6Start" type="number" min="0" step="0.01"></label>
              <label>Duration<input id="m6Duration" type="number" min="0.01" step="0.01"></label>
              <label>Pitch<input id="m6Pitch" type="number" min="0" max="127" step="1"></label>
              <label>Velocity<input id="m6Velocity" type="number" min="1" max="127" step="1"></label>
            </div>
            <div class="m6-actions">
              <button id="m6PreviewChanges" class="primary" type="button">Preview changes / 변경 미리듣기</button>
              <button id="m6DeleteNote" class="danger" type="button">Delete note / 노트 삭제</button>
            </div>
          </fieldset>
          <fieldset id="m6InsertFieldset" class="m6-note-editor">
            <legend>Insert note / 노트 추가</legend>
            <div class="m6-fields">
              <label>Note ID<input id="m6InsertId" value="N-UI-NEW"></label>
              <label>Start beat<input id="m6InsertStart" type="number" min="0" step="0.01" value="0"></label>
              <label>Duration<input id="m6InsertDuration" type="number" min="0.01" step="0.01" value="0.5"></label>
              <label>Pitch<input id="m6InsertPitch" type="number" min="0" max="127" step="1" value="60"></label>
              <label>Velocity<input id="m6InsertVelocity" type="number" min="1" max="127" step="1" value="80"></label>
            </div>
            <button id="m6InsertNote" class="secondary" type="button">Preview insert / 추가 미리듣기</button>
          </fieldset>
        </div>
      </div>`;
    heading.insertAdjacentElement("afterend", card);
    precision.root = card;
    el("m6PreviewChanges").addEventListener("click", previewSelectedChanges);
    el("m6DeleteNote").addEventListener("click", previewDelete);
    el("m6InsertNote").addEventListener("click", previewInsert);
  }

  function currentNotes() {
    if (!precision.view) return [];
    return precision.view.preview ? precision.view.preview.notes : precision.view.notes;
  }

  function findSelected() {
    return currentNotes().find((note) => noteKey(note) === precision.selectedKey) || null;
  }

  function acceptedSelected() {
    if (!precision.view) return null;
    return precision.view.notes.find((note) => noteKey(note) === precision.selectedKey) || null;
  }

  function locksFor(note) {
    if (!precision.view || !note) return [];
    return (precision.view.note_locks || []).filter(
      (lock) => lock.selector.part_id === note.part_id && lock.selector.note_id === note.note_id,
    );
  }

  function renderSelected() {
    const note = findSelected();
    const fieldset = el("m6SelectedFieldset");
    const pending = Boolean(precision.view && precision.view.preview);
    if (!note) {
      fieldset.disabled = true;
      el("m6SelectedId").textContent = "—";
      el("m6SelectedLocks").textContent = "";
      return;
    }
    fieldset.disabled = pending;
    el("m6SelectedId").textContent = `${note.note_id} · ${note.part_id}`;
    el("m6Start").value = String(note.start_beat);
    el("m6Duration").value = String(note.duration_beats);
    el("m6Pitch").value = String(note.pitch);
    el("m6Velocity").value = String(note.velocity);
    const lockRoot = el("m6SelectedLocks");
    lockRoot.textContent = "";
    const locks = locksFor(note);
    locks.forEach((lock) => {
      const badge = document.createElement("span");
      badge.className = "m6-lock-badge";
      badge.textContent = `🔒 ${lock.selector.property}`;
      badge.title = `${lock.lock_id}: ${lock.reason}`;
      lockRoot.appendChild(badge);
    });
    ["start_beat", "duration_beats", "pitch", "velocity"].forEach((property) => {
      const id = { start_beat: "m6Start", duration_beats: "m6Duration", pitch: "m6Pitch", velocity: "m6Velocity" }[property];
      el(id).disabled = pending || locks.some((lock) => lock.selector.property === property);
    });
  }

  function renderRoll() {
    const view = precision.view;
    const available = Boolean(view && view.exact_note_editing_available);
    el("m6Workspace").hidden = !available;
    el("m6Unavailable").hidden = available;
    const availability = el("m6Availability");
    if (!view) {
      availability.textContent = "NO PROJECT";
      availability.className = "status-pill neutral";
      return;
    }
    if (!available) {
      availability.textContent = "LEGACY · READ ONLY";
      availability.className = "status-pill neutral";
      el("m6Unavailable").textContent = "This accepted revision has no canonical exact_timeline. MUSICA will not fabricate editable notes from Music IR. / 공식 exact_timeline이 없어 Music IR에서 편집 노트를 역생성하지 않습니다.";
      return;
    }
    availability.textContent = "EXACT · READY";
    availability.className = "status-pill accepted";
    el("m6SourceBinding").textContent = `${view.project_id} · ${view.branch}@${view.revision_id} · sha256:${view.blueprint_sha256.slice(0, 12)}…`;
    const pending = Boolean(view.preview);
    const badge = el("m6PreviewBadge");
    badge.textContent = pending ? "PREVIEW NOTES · NOT ACCEPTED" : "ACCEPTED NOTES";
    badge.className = pending ? "status-pill preview" : "status-pill accepted";
    el("m6InsertFieldset").disabled = pending;

    const roll = el("m6PianoRoll");
    roll.textContent = "";
    const accepted = view.notes || [];
    const display = currentNotes();
    const allPitches = [...accepted, ...display].map((note) => Number(note.pitch));
    const minPitch = Math.max(0, Math.min(...allPitches, 60) - 2);
    const maxPitch = Math.min(127, Math.max(...allPitches, 72) + 2);
    const rows = maxPitch - minPitch + 1;
    roll.style.setProperty("--m6-rows", String(rows));
    roll.style.setProperty("--m6-total-beats", String(Math.max(Number(view.timing.total_beats), 1)));

    for (let pitch = maxPitch; pitch >= minPitch; pitch -= 1) {
      const row = document.createElement("div");
      row.className = `m6-pitch-row ${pitch % 12 === 0 ? "root" : ""}`;
      row.style.gridRow = String(maxPitch - pitch + 1);
      const label = document.createElement("span");
      label.className = "m6-pitch-label";
      label.textContent = String(pitch);
      row.appendChild(label);
      roll.appendChild(row);
    }

    (view.sections || []).forEach((section) => {
      const marker = document.createElement("div");
      marker.className = "m6-section-marker";
      marker.style.left = `${(Number(section.start_beat) / Number(view.timing.total_beats)) * 100}%`;
      marker.title = `${section.section_id} · ${section.name}`;
      roll.appendChild(marker);
    });

    if (pending) {
      accepted.forEach((note) => addNoteButton(roll, note, maxPitch, minPitch, "accepted ghost"));
    }
    display.forEach((note) => addNoteButton(roll, note, maxPitch, minPitch, pending ? "preview" : "accepted"));
    renderSelected();
  }

  function addNoteButton(roll, note, maxPitch, minPitch, kind) {
    const total = Math.max(Number(precision.view.timing.total_beats), 1);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `m6-note ${kind}${noteKey(note) === precision.selectedKey ? " selected" : ""}`;
    button.style.left = `${(Number(note.start_beat) / total) * 100}%`;
    button.style.width = `${Math.max((Number(note.duration_beats) / total) * 100, 0.8)}%`;
    button.style.top = `${((maxPitch - Number(note.pitch)) / (maxPitch - minPitch + 1)) * 100}%`;
    button.style.height = `${100 / (maxPitch - minPitch + 1)}%`;
    button.textContent = `${note.note_id} · ${note.pitch}`;
    button.title = `${note.note_id} | beat ${note.start_beat} | dur ${note.duration_beats} | vel ${note.velocity}`;
    button.dataset.noteKey = noteKey(note);
    button.disabled = kind.includes("ghost");
    button.addEventListener("click", () => {
      precision.selectedKey = noteKey(note);
      renderRoll();
    });
    roll.appendChild(button);
  }

  function sectionForBeat(beat) {
    if (!precision.view) return null;
    const found = (precision.view.sections || []).find(
      (section) => Number(section.start_beat) <= beat && beat < Number(section.end_beat),
    );
    return found ? found.section_id : null;
  }

  function candidateFor(operations, reason) {
    const view = precision.view;
    precision.requestCounter += 1;
    return {
      candidate_version: "0",
      candidate_id: `NEC-UI-${Date.now()}-${precision.requestCounter}`,
      authority_target: "blueprint_exact_note_material",
      source: {
        project_id: view.project_id,
        revision_id: view.revision_id,
        blueprint_sha256: view.blueprint_sha256,
      },
      actor: { kind: "user", actor_id: "browser-studio" },
      reason,
      operations,
      preview_only: true,
    };
  }

  async function sendPreview(operations, reason) {
    if (!precision.sessionId || !precision.view) return;
    clearStatus();
    try {
      const data = await precisionFetch(`/v0/sessions/${encodeURIComponent(precision.sessionId)}/preview/notes`, {
        method: "POST",
        body: { candidate: candidateFor(operations, reason) },
      });
      precision.view = data.note_view;
      if (!data.preview_installed) {
        const conflicts = (data.authority_result && data.authority_result.conflicts) || [];
        const text = conflicts.map((item) => `${item.code}${item.note_id ? ` · ${item.note_id}` : ""}: ${item.reason}`).join(" | ");
        status(text || "Edit blocked by trusted authority / trusted authority에 의해 편집이 차단되었습니다.", "error");
      } else {
        status("Exact-note Preview ready. Accepted revision is unchanged / exact-note Preview가 준비되었고 승인 리비전은 변경되지 않았습니다.", "success");
        const refresh = el("refreshButton");
        if (refresh) refresh.click();
      }
      renderRoll();
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  function previewSelectedChanges() {
    const original = acceptedSelected();
    if (!original) return status("Select an accepted note first / 승인 노트를 먼저 선택하세요.", "error");
    const operations = [];
    const target = { note_id: original.note_id, part_id: original.part_id };
    const start = Number(el("m6Start").value);
    const duration = Number(el("m6Duration").value);
    const pitch = Number(el("m6Pitch").value);
    const velocity = Number(el("m6Velocity").value);
    if (start !== Number(original.start_beat)) operations.push({ operation_id: "UI-MOVE", op: "MOVE", target, start_beat: start });
    if (duration !== Number(original.duration_beats)) operations.push({ operation_id: "UI-RESIZE", op: "RESIZE", target, duration_beats: duration });
    if (pitch !== Number(original.pitch)) operations.push({ operation_id: "UI-REPITCH", op: "REPITCH", target, pitch });
    if (velocity !== Number(original.velocity)) operations.push({ operation_id: "UI-VELOCITY", op: "SET_VELOCITY", target, velocity });
    if (!operations.length) return status("No exact-note properties changed / 변경된 exact-note 속성이 없습니다.", "info");
    sendPreview(operations, `Browser Studio precision edit for ${original.note_id}.`);
  }

  function previewDelete() {
    const original = acceptedSelected();
    if (!original) return status("Select an accepted note first / 승인 노트를 먼저 선택하세요.", "error");
    sendPreview(
      [{ operation_id: "UI-DELETE", op: "DELETE", target: { note_id: original.note_id, part_id: original.part_id } }],
      `Browser Studio delete ${original.note_id}.`,
    );
  }

  function previewInsert() {
    if (!precision.view || !precision.view.editable_part) return;
    const start = Number(el("m6InsertStart").value);
    const note = {
      note_id: el("m6InsertId").value.trim(),
      part_id: precision.view.editable_part.part_id,
      section_id: sectionForBeat(start),
      start_beat: start,
      duration_beats: Number(el("m6InsertDuration").value),
      pitch: Number(el("m6InsertPitch").value),
      velocity: Number(el("m6InsertVelocity").value),
    };
    if (!note.note_id) return status("Note ID is required / Note ID가 필요합니다.", "error");
    if (!note.section_id) return status("Insert start must fall inside a known section / 삽입 시작점은 알려진 구간 안이어야 합니다.", "error");
    sendPreview([{ operation_id: "UI-INSERT", op: "INSERT", note }], `Browser Studio insert ${note.note_id}.`);
  }

  async function refreshNoteView(quiet = false) {
    if (!precision.sessionId || !precision.root) return;
    try {
      precision.view = await precisionFetch(`/v0/sessions/${encodeURIComponent(precision.sessionId)}/notes`);
      if (precision.selectedKey && !currentNotes().some((note) => noteKey(note) === precision.selectedKey)) precision.selectedKey = null;
      renderRoll();
      if (!quiet) status("Exact-note view refreshed / exact-note view를 새로고침했습니다.", "success");
    } catch (error) {
      precision.view = null;
      renderRoll();
      if (!quiet) status(error.message || String(error), "error");
    }
  }

  injectSurface();
  window.MUSICA_PRECISION = {
    refresh: refreshNoteView,
    state: precision,
  };
})();
