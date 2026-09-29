(() => {
  "use strict";

  const priorFetch = window.fetch.bind(window);
  const rtio = {
    sessionId: null,
    runtimeId: null,
    view: null,
    root: null,
    lastErrorCode: null,
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
    if (rtio.sessionId !== session.session_id) {
      rtio.sessionId = session.session_id;
      rtio.runtimeId = null;
      rtio.view = null;
      rtio.lastErrorCode = null;
      queueMicrotask(render);
    }
  }

  window.fetch = async (...args) => {
    const response = await priorFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/realtime/")) {
        const clone = response.clone();
        if ((clone.headers.get("content-type") || "").includes("application/json")) {
          observeSessionPayload(await clone.json());
        }
      }
    } catch (_error) {
      // Runtime observation is derived and must never break the core Studio request.
    }
    return response;
  };

  function status(message, kind = "info") {
    const target = el("rtioRuntimeStatus");
    if (!target) return;
    target.hidden = false;
    target.textContent = message;
    target.className = `rtio-runtime-status ${kind}`;
  }

  function clearStatus() {
    const target = el("rtioRuntimeStatus");
    if (!target) return;
    target.hidden = true;
    target.textContent = "";
  }

  function inject() {
    const panel = el("panel-inspect");
    if (!panel || el("rtioRuntimeCard")) return;
    const routingCard = el("mramRoutingCard");
    const anchor = routingCard || el("m7AutomationCard") || panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "rtioRuntimeCard";
    card.className = "card rtio-runtime-card";
    card.innerHTML = `
      <div class="card-heading">
        <div><span class="eyebrow">RTIO · RUNTIME</span><h2>Realtime runtime inspection / 실시간 런타임 검사</h2></div>
        <span id="rtioRuntimeBadge" class="status-pill neutral">CLOSED</span>
      </div>
      <p class="muted small">Runtime state is derived and non-canonical. Position authority is the exact frame cursor, never wall-clock time. Commands cannot mutate accepted project state.</p>
      <div id="rtioRuntimeStatus" class="rtio-runtime-status" role="status" aria-live="polite" hidden></div>
      <div class="rtio-runtime-controls">
        <label>Sample rate
          <select id="rtioSampleRate"><option value="8000">8000</option><option value="44100">44100</option><option value="48000">48000</option></select>
        </label>
        <label>Block frames
          <select id="rtioBlockSize"><option>64</option><option>128</option><option selected>256</option><option>512</option><option>1024</option></select>
        </label>
        <button id="rtioOpen" class="secondary" type="button">Open runtime</button>
        <button id="rtioRefresh" class="ghost" type="button">Refresh</button>
      </div>
      <div id="rtioRuntimeWorkspace" hidden>
        <div id="rtioRuntimeSource" class="mono muted rtio-runtime-source">—</div>
        <div class="rtio-runtime-grid">
          <section><h3>Transport</h3><dl id="rtioTransportFacts"></dl></section>
          <section><h3>Configuration</h3><dl id="rtioConfigFacts"></dl></section>
          <section><h3>Latency provenance</h3><dl id="rtioLatencyFacts"></dl></section>
          <section><h3>Dropout metrics</h3><dl id="rtioMetricFacts"></dl></section>
        </div>
        <div class="rtio-command-row">
          <button id="rtioPlay" type="button">Play</button>
          <button id="rtioStep" type="button">Step callback</button>
          <button id="rtioStop" type="button">Stop</button>
          <label>Seek frame<input id="rtioSeekFrame" type="number" min="0" step="1" value="0"></label>
          <button id="rtioSeek" type="button">Seek</button>
          <button id="rtioClose" class="danger" type="button">Close runtime</button>
        </div>
        <p class="muted small" id="rtioAuthorityText">Accepted project state is canonical. Runtime and Browser state are not canonical.</p>
      </div>`;
    anchor.insertAdjacentElement("afterend", card);
    rtio.root = card;

    el("rtioOpen").addEventListener("click", openRuntime);
    el("rtioRefresh").addEventListener("click", () => refreshRuntime(false));
    el("rtioPlay").addEventListener("click", () => command("play"));
    el("rtioStep").addEventListener("click", () => command("callback"));
    el("rtioStop").addEventListener("click", () => command("stop"));
    el("rtioSeek").addEventListener("click", seekRuntime);
    el("rtioClose").addEventListener("click", closeRuntime);
    render();
  }

  function facts(rootId, pairs) {
    const root = el(rootId);
    root.textContent = "";
    pairs.forEach(([name, value]) => {
      const wrapper = document.createElement("div");
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = name;
      dd.textContent = String(value);
      wrapper.append(dt, dd);
      root.appendChild(wrapper);
    });
  }

  function render() {
    if (!rtio.root) return;
    const badge = el("rtioRuntimeBadge");
    const workspace = el("rtioRuntimeWorkspace");
    if (!rtio.view) {
      badge.textContent = "CLOSED";
      badge.className = "status-pill neutral";
      workspace.hidden = true;
      return;
    }

    const view = rtio.view;
    const state = view.transport.state;
    badge.textContent = state;
    badge.className = `status-pill ${state === "PLAYING" ? "preview" : "accepted"}`;
    workspace.hidden = false;
    el("rtioRuntimeSource").textContent =
      `${view.runtime_id} · revision ${view.revision_id} · plan ${view.realtime_execution_plan_sha256.slice(0, 16)} · routed ${view.source.routed_wav_sha256.slice(0, 16)}`;

    facts("rtioTransportFacts", [
      ["State", state],
      ["Playhead frame", view.transport.playhead_frame],
      ["Duration frames", view.configuration.duration_frames],
      ["Callback index", view.transport.callback_index === null ? "—" : view.transport.callback_index],
    ]);
    facts("rtioConfigFacts", [
      ["Sample rate Hz", view.configuration.sample_rate_hz],
      ["Channels", view.configuration.output_channels],
      ["Block frames", view.configuration.block_size_frames],
      ["Backend", view.backend.backend_id],
    ]);
    facts("rtioLatencyFacts", [
      ["Nominal frames", view.latency.nominal_output_latency_frames],
      ["Source", view.latency.nominal_source],
      ["Host observed", view.latency.host_observed_latency_available],
      ["Wall-clock guarantee", view.latency.wall_clock_guarantee_claimed],
    ]);
    facts("rtioMetricFacts", [
      ["Callbacks", view.metrics.callbacks_requested],
      ["Requested frames", view.metrics.frames_requested],
      ["Delivered frames", view.metrics.frames_delivered],
      ["ERROR", view.metrics.error_count],
      ["SHORT_FILL", view.metrics.short_fill_count],
      ["LATE", view.metrics.late_count],
      ["Xrun/dropout eq.", view.metrics.xrun_dropout_equivalent_count],
      ["Seeks", view.metrics.seek_count],
    ]);

    el("rtioSeekFrame").max = String(view.configuration.duration_frames);
    el("rtioPlay").disabled = state !== "STOPPED";
    el("rtioStep").disabled = state !== "PLAYING";
    el("rtioStop").disabled = state !== "PLAYING";
    el("rtioSeek").disabled = state === "PLAYING";
    el("rtioClose").disabled = state === "PLAYING";
    el("rtioOpen").disabled = true;
  }

  async function openRuntime() {
    if (!rtio.sessionId || rtio.runtimeId) return;
    clearStatus();
    try {
      const data = await api(
        `/v0/sessions/${encodeURIComponent(rtio.sessionId)}/realtime/open`,
        {
          method: "POST",
          body: {
            sample_rate_hz: Number(el("rtioSampleRate").value),
            output_channels: 2,
            block_size_frames: Number(el("rtioBlockSize").value),
          },
        },
      );
      rtio.runtimeId = data.runtime_id;
      rtio.view = data;
      rtio.lastErrorCode = null;
      status("Runtime opened from exact accepted revision. Project HEAD is unchanged.", "success");
      render();
    } catch (error) {
      rtio.lastErrorCode = error.code || "error";
      status(error.message || String(error), "error");
    }
  }

  async function refreshRuntime(quiet = true) {
    if (!rtio.sessionId || !rtio.runtimeId) return;
    try {
      rtio.view = await api(
        `/v0/sessions/${encodeURIComponent(rtio.sessionId)}/realtime/${encodeURIComponent(rtio.runtimeId)}`,
      );
      rtio.lastErrorCode = null;
      render();
      if (!quiet) status("Runtime inspection refreshed.", "success");
    } catch (error) {
      rtio.lastErrorCode = error.code || "error";
      status(error.message || String(error), "error");
    }
  }

  async function command(name, body = {}) {
    if (!rtio.sessionId || !rtio.runtimeId) return;
    clearStatus();
    try {
      const data = await api(
        `/v0/sessions/${encodeURIComponent(rtio.sessionId)}/realtime/${encodeURIComponent(rtio.runtimeId)}/${name}`,
        { method: "POST", body },
      );
      rtio.view = data.runtime;
      rtio.lastErrorCode = null;
      status(`${name.toUpperCase()} applied to derived runtime only. Accepted HEAD unchanged.`, "success");
      render();
    } catch (error) {
      rtio.lastErrorCode = error.code || "error";
      status(error.message || String(error), "error");
    }
  }

  function seekRuntime() {
    const target = Number(el("rtioSeekFrame").value);
    if (!Number.isInteger(target) || target < 0) {
      status("Seek frame must be a non-negative integer.", "error");
      return;
    }
    command("seek", { target_frame: target });
  }

  async function closeRuntime() {
    if (!rtio.sessionId || !rtio.runtimeId) return;
    clearStatus();
    try {
      await api(
        `/v0/sessions/${encodeURIComponent(rtio.sessionId)}/realtime/${encodeURIComponent(rtio.runtimeId)}/close`,
        { method: "POST", body: {} },
      );
      rtio.runtimeId = null;
      rtio.view = null;
      rtio.lastErrorCode = null;
      el("rtioOpen").disabled = false;
      status("Derived runtime closed. No runtime playhead was persisted into project state.", "success");
      render();
    } catch (error) {
      rtio.lastErrorCode = error.code || "error";
      status(error.message || String(error), "error");
    }
  }

  inject();
  window.MUSICA_REALTIME = {
    state: rtio,
    open: openRuntime,
    refresh: refreshRuntime,
    command,
  };
})();
