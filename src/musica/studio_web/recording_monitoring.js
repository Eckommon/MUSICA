(() => {
  "use strict";

  const priorFetch = window.fetch.bind(window);
  const rec = {
    sessionId: null,
    view: null,
    runtimeId: null,
    root: null,
  };
  const el = (id) => document.getElementById(id);

  async function api(path, options = {}) {
    const init = { method: options.method || "GET", headers: { Accept: "application/json" } };
    if (options.body !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(options.body);
    }
    const response = await priorFetch(path, init);
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
    const changed = rec.sessionId !== session.session_id;
    rec.sessionId = session.session_id;
    if (changed) {
      rec.view = null;
      rec.runtimeId = null;
    }
    queueMicrotask(() => refresh(true));
  }

  window.fetch = async (...args) => {
    const response = await priorFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/recording")) {
        const clone = response.clone();
        if ((clone.headers.get("content-type") || "").includes("application/json")) {
          observeSessionPayload(await clone.json());
        }
      }
    } catch (_error) {
      // Derived recording observation must never break core Studio requests.
    }
    return response;
  };

  function status(message, kind = "info") {
    const target = el("recRuntimeStatus");
    if (!target) return;
    target.hidden = false;
    target.textContent = message;
    target.className = `rec-runtime-status ${kind}`;
  }

  function clearStatus() {
    const target = el("recRuntimeStatus");
    if (!target) return;
    target.hidden = true;
    target.textContent = "";
  }

  function facts(rootId, pairs) {
    const root = el(rootId);
    if (!root) return;
    root.textContent = "";
    pairs.forEach(([name, value]) => {
      const row = document.createElement("div");
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = name;
      dd.textContent = String(value);
      row.append(dt, dd);
      root.appendChild(row);
    });
  }

  function fillTracks() {
    const select = el("recTrack");
    if (!select || !rec.view) return;
    const previous = select.value;
    select.textContent = "";
    (rec.view.audio_tracks || []).forEach((track) => {
      const option = document.createElement("option");
      option.value = track.track_id;
      option.textContent = `${track.track_id} · ${track.name}`;
      select.appendChild(option);
    });
    if ([...select.options].some((option) => option.value === previous)) select.value = previous;
  }

  function render() {
    if (!rec.root) return;
    const badge = el("recRuntimeBadge");
    const workspace = el("recRuntimeWorkspace");
    if (!rec.view) {
      badge.textContent = "NO PROJECT";
      badge.className = "status-pill neutral";
      workspace.hidden = true;
      return;
    }

    workspace.hidden = false;
    const runtime = rec.view.runtime;
    rec.runtimeId = runtime ? runtime.runtime_id : null;
    badge.textContent = runtime ? (runtime.capture_clean ? "CLEAN CAPTURE" : "DIRTY CAPTURE") : "READY";
    badge.className = `status-pill ${runtime ? (runtime.capture_clean ? "preview" : "neutral") : "accepted"}`;
    el("recSource").textContent =
      `revision ${rec.view.revision_id} · blueprint ${rec.view.source.blueprint_sha256.slice(0, 16)} · audio ${rec.view.source.audio_material_sha256.slice(0, 16)}`;
    fillTracks();

    el("recStart").disabled = Boolean(runtime);
    el("recReset").disabled = !runtime;
    el("recPreview").disabled = !runtime;
    el("recAccept").disabled = !(runtime && runtime.finalize_preview && runtime.finalize_preview.authority_result.status === "READY_FOR_PREVIEW");
    el("recDiscard").disabled = !(runtime && runtime.finalize_preview);

    if (!runtime) {
      facts("recCaptureFacts", [["Runtime", "none"], ["Authority", "accepted project only"]]);
      facts("recMonitorFacts", [["Monitor", "not running"]]);
      el("recPreviewFacts").textContent = "No recording finalize Preview.";
      return;
    }

    facts("recCaptureFacts", [
      ["Runtime ID", runtime.runtime_id],
      ["Clean", runtime.capture_clean],
      ["Capture plan", runtime.recording_capture_plan_sha256.slice(0, 16)],
      ["Capture report", runtime.recording_capture_run_report_sha256.slice(0, 16)],
      ["Payload", runtime.capture_payload_sha256.slice(0, 16)],
      ["Frames", runtime.capture_metrics.frames_captured],
      ["Errors", runtime.capture_metrics.error_count],
      ["Short fills", runtime.capture_metrics.short_fill_count],
      ["Late", runtime.capture_metrics.late_count],
    ]);
    facts("recMonitorFacts", [
      ["Enabled", runtime.monitor_enabled],
      ["Monitor plan", runtime.recording_monitor_plan_sha256.slice(0, 16)],
      ["Monitor report", runtime.recording_monitor_run_report_sha256.slice(0, 16)],
      ["Frames written", runtime.monitor_metrics.frames_written],
      ["Output xruns", runtime.monitor_metrics.output_xrun_count],
    ]);
    const preview = runtime.finalize_preview;
    el("recPreviewFacts").textContent = preview
      ? `${preview.authority_result.status} · track ${preview.destination_track_id} · clip ${preview.destination_clip_id} · asset ${preview.prospective_asset_id || "blocked"}`
      : "No recording finalize Preview.";
  }

  function inject() {
    const panel = el("panel-inspect");
    if (!panel || el("recRuntimeCard")) return;
    const rtioCard = el("rtioRuntimeCard");
    const anchor = rtioCard || el("mramRoutingCard") || panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "recRuntimeCard";
    card.className = "card rec-runtime-card";
    card.innerHTML = `
      <div class="card-heading">
        <div><span class="eyebrow">REC · R3</span><h2>Recording & monitoring / 녹음·모니터링</h2></div>
        <span id="recRuntimeBadge" class="status-pill neutral">NO PROJECT</span>
      </div>
      <p class="muted small">Capture and monitor state are derived runtime only. A clean capture becomes creative state only through REC-R1 Preview → explicit Accept.</p>
      <div id="recRuntimeStatus" class="rec-runtime-status" role="status" aria-live="polite" hidden></div>
      <div id="recRuntimeWorkspace" hidden>
        <div id="recSource" class="mono muted rec-source">—</div>
        <div class="rec-controls">
          <label>Sample rate<select id="recRate"><option value="8000">8000</option></select></label>
          <label>Block frames<select id="recBlock"><option>64</option><option>128</option><option selected>256</option><option>512</option><option>1024</option></select></label>
          <label>Capture frames<input id="recFrames" type="number" min="1" step="1" value="800"></label>
          <label class="rec-check"><input id="recMonitorEnabled" type="checkbox" checked> Monitor enabled</label>
          <button id="recStart" class="secondary" type="button">Run capture</button>
          <button id="recRefresh" class="ghost" type="button">Refresh</button>
          <button id="recReset" class="danger" type="button">Reset runtime</button>
        </div>
        <div class="rec-grid">
          <section><h3>Capture</h3><dl id="recCaptureFacts"></dl></section>
          <section><h3>Monitor</h3><dl id="recMonitorFacts"></dl></section>
        </div>
        <fieldset class="rec-finalize">
          <legend>REC-R1 finalize authority</legend>
          <label>Destination track<select id="recTrack"></select></label>
          <label>Clip ID<input id="recClip" value="REC-STUDIO-001" pattern="[A-Za-z0-9][A-Za-z0-9._:-]*"></label>
          <label>Timeline start seconds<input id="recStartSeconds" type="number" min="0" step="0.01" value="0"></label>
          <div class="rec-actions">
            <button id="recPreview" class="secondary" type="button">Preview finalize</button>
            <button id="recDiscard" class="danger" type="button">Discard Preview</button>
            <button id="recAccept" class="primary" type="button">Accept recording</button>
          </div>
          <p id="recPreviewFacts" class="mono muted">No recording finalize Preview.</p>
        </fieldset>
      </div>`;
    anchor.insertAdjacentElement("afterend", card);
    rec.root = card;

    el("recStart").addEventListener("click", runCapture);
    el("recRefresh").addEventListener("click", () => refresh(false));
    el("recReset").addEventListener("click", resetRuntime);
    el("recPreview").addEventListener("click", previewFinalize);
    el("recDiscard").addEventListener("click", discardPreview);
    el("recAccept").addEventListener("click", acceptRecording);
    render();
  }

  async function refresh(quiet = true) {
    if (!rec.sessionId || !rec.root) return;
    try {
      rec.view = await api(`/v0/sessions/${encodeURIComponent(rec.sessionId)}/recording`);
      render();
      if (!quiet) status("Recording/monitoring inspection refreshed.", "success");
    } catch (error) {
      rec.view = null;
      render();
      if (!quiet) status(error.message || String(error), "error");
    }
  }

  async function runCapture() {
    if (!rec.sessionId || rec.runtimeId) return;
    clearStatus();
    try {
      rec.view = await api(
        `/v0/sessions/${encodeURIComponent(rec.sessionId)}/recording/run`,
        {
          method: "POST",
          body: {
            sample_rate_hz: Number(el("recRate").value),
            input_channels: 2,
            block_size_frames: Number(el("recBlock").value),
            capture_frames: Number(el("recFrames").value),
            monitor_enabled: Boolean(el("recMonitorEnabled").checked),
          },
        },
      );
      render();
      status("Derived capture/monitor run completed. Accepted HEAD and assets are unchanged.", "success");
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  async function previewFinalize() {
    if (!rec.sessionId || !rec.runtimeId) return;
    clearStatus();
    try {
      const data = await api(
        `/v0/sessions/${encodeURIComponent(rec.sessionId)}/recording/${encodeURIComponent(rec.runtimeId)}/preview`,
        {
          method: "POST",
          body: {
            track_id: el("recTrack").value,
            clip_id: el("recClip").value.trim(),
            timeline_start_seconds: Number(el("recStartSeconds").value),
            gain_db: 0,
          },
        },
      );
      rec.view = data.recording_view;
      render();
      const conflicts = (data.authority_result && data.authority_result.conflicts) || [];
      status(
        data.preview_installed
          ? "Recording finalize Preview ready. Project HEAD/assets remain unchanged."
          : conflicts.map((item) => item.reason).join(" | ") || "Finalize Preview blocked.",
        data.preview_installed ? "success" : "error",
      );
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  async function discardPreview() {
    if (!rec.sessionId || !rec.runtimeId) return;
    try {
      rec.view = await api(
        `/v0/sessions/${encodeURIComponent(rec.sessionId)}/recording/${encodeURIComponent(rec.runtimeId)}/discard`,
        { method: "POST", body: {} },
      );
      render();
      status("Finalize Preview discarded. Accepted state unchanged.", "success");
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  async function acceptRecording() {
    if (!rec.sessionId || !rec.runtimeId) return;
    try {
      const data = await api(
        `/v0/sessions/${encodeURIComponent(rec.sessionId)}/recording/${encodeURIComponent(rec.runtimeId)}/accept`,
        { method: "POST", body: {} },
      );
      rec.view = data.recording_view;
      rec.runtimeId = null;
      render();
      status(`Recording accepted as revision ${data.accepted_head_revision_id}. Transient runtime reset.`, "success");
      const refreshButton = el("refreshButton");
      if (refreshButton) refreshButton.click();
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  async function resetRuntime() {
    if (!rec.sessionId || !rec.runtimeId) return;
    try {
      rec.view = await api(
        `/v0/sessions/${encodeURIComponent(rec.sessionId)}/recording/${encodeURIComponent(rec.runtimeId)}/reset`,
        { method: "POST", body: {} },
      );
      rec.runtimeId = null;
      render();
      status("Transient recording runtime reset. Accepted state unchanged.", "success");
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  inject();
  window.MUSICA_RECORDING = {
    state: rec,
    refresh,
    runCapture,
    previewFinalize,
    acceptRecording,
  };
})();
