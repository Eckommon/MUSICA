(() => {
  "use strict";

  const originalFetch = window.fetch.bind(window);
  const routing = {
    sessionId: null,
    view: null,
    root: null,
    requestCounter: 0,
    lastSubmittedCandidate: null,
    lastAuthorityResult: null,
  };

  const el = (id) => document.getElementById(id);

  async function routingFetch(path, options = {}) {
    const init = { method: options.method || "GET", headers: { Accept: "application/json" } };
    if (options.body !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(options.body);
    }
    const response = await originalFetch(path, init);
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : null;
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
    const changed = routing.sessionId !== session.session_id;
    routing.sessionId = session.session_id;
    if (changed || session.head_revision_id) queueMicrotask(() => refreshRoutingView(true));
  }

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/mixer-routing")) {
        const clone = response.clone();
        const contentType = clone.headers.get("content-type") || "";
        if (contentType.includes("application/json")) observeSessionPayload(await clone.json());
      }
    } catch (_error) {
      // Derived Browser observation must never break the core request.
    }
    return response;
  };

  function status(message, kind = "info") {
    const target = el("mramRoutingStatus");
    if (!target) return;
    target.textContent = message;
    target.className = `mram-routing-status ${kind}`;
    target.hidden = false;
  }

  function clearStatus() {
    const target = el("mramRoutingStatus");
    if (!target) return;
    target.hidden = true;
    target.textContent = "";
  }

  function injectSurface() {
    const panel = el("panel-inspect");
    if (!panel || el("mramRoutingCard")) return;
    const anchor = el("m7AutomationCard") || panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "mramRoutingCard";
    card.className = "card mram-routing-card";
    card.innerHTML = `
      <div class="card-heading">
        <div><span class="eyebrow">MRAM · ROUTING</span><h2>Routing & native mixer automation / 라우팅·네이티브 자동화</h2></div>
        <span id="mramRoutingBadge" class="status-pill neutral">NO PROJECT</span>
      </div>
      <p class="muted small">Stable IDs and accepted source hashes are authoritative. Browser state is derived; every routing change remains PREVIEW until explicit Accept.</p>
      <div id="mramRoutingStatus" class="mram-routing-status" role="status" aria-live="polite" hidden></div>
      <div id="mramRoutingWorkspace" hidden>
        <div class="mram-source mono muted" id="mramRoutingSource">—</div>
        <audio id="mramRoutingAudio" controls preload="metadata"></audio>
        <div class="mram-routing-grid">
          <section><h3>Track outputs</h3><div id="mramTrackOutputs"></div></section>
          <section><h3>Nodes</h3><div id="mramNodes"></div></section>
          <section><h3>Post-fader sends</h3><div id="mramSends"></div></section>
          <section><h3>Native gain/pan automation</h3><div id="mramNativeAutomation"></div></section>
        </div>
        <div class="mram-edit-grid">
          <fieldset>
            <legend>Track output Preview</legend>
            <label>Track<select id="mramTrackSelect"></select></label>
            <label>Target node<select id="mramTrackTarget"></select></label>
            <button id="mramPreviewTrackOutput" class="secondary" type="button">Preview output</button>
          </fieldset>
          <fieldset>
            <legend>Send gain Preview</legend>
            <label>Send<select id="mramSendSelect"></select></label>
            <label>Gain dB<input id="mramSendGain" type="number" min="-60" max="12" step="0.1"></label>
            <button id="mramPreviewSendGain" class="secondary" type="button">Preview send gain</button>
          </fieldset>
          <fieldset>
            <legend>Node mixer Preview</legend>
            <label>Node<select id="mramNodeSelect"></select></label>
            <label>Gain dB<input id="mramNodeGain" type="number" min="-60" max="12" step="0.1"></label>
            <label>Pan<input id="mramNodePan" type="number" min="-1" max="1" step="0.05"></label>
            <label class="mram-check"><input id="mramNodeMute" type="checkbox"> Mute</label>
            <button id="mramPreviewNodeMixer" class="secondary" type="button">Preview node mixer</button>
          </fieldset>
        </div>
      </div>`;
    anchor.insertAdjacentElement("afterend", card);
    routing.root = card;

    el("mramPreviewTrackOutput").addEventListener("click", previewTrackOutput);
    el("mramPreviewSendGain").addEventListener("click", previewSendGain);
    el("mramPreviewNodeMixer").addEventListener("click", previewNodeMixer);
    el("mramSendSelect").addEventListener("change", syncSend);
    el("mramNodeSelect").addEventListener("change", syncNode);
  }

  function activeRouting() {
    if (!routing.view) return { track_outputs: [], nodes: [], sends: [] };
    return routing.view.preview || routing.view;
  }

  function fillSelect(select, items, valueKey, labelFn) {
    const previous = select.value;
    select.textContent = "";
    (items || []).forEach((item) => {
      const option = document.createElement("option");
      option.value = String(item[valueKey]);
      option.textContent = labelFn(item);
      select.appendChild(option);
    });
    if ([...select.options].some((option) => option.value === previous)) select.value = previous;
  }

  function itemRow(type, id, text) {
    const row = document.createElement("div");
    row.className = "mram-row";
    row.dataset.mramType = type;
    row.dataset.mramId = id;
    const code = document.createElement("code");
    code.textContent = id;
    const span = document.createElement("span");
    span.textContent = text;
    row.append(code, span);
    return row;
  }

  function renderRows(containerId, items, builder) {
    const root = el(containerId);
    root.textContent = "";
    if (!items.length) {
      const p = document.createElement("p");
      p.className = "muted";
      p.textContent = "None";
      root.appendChild(p);
      return;
    }
    items.forEach((item) => root.appendChild(builder(item)));
  }

  function syncSend() {
    const value = activeRouting();
    const send = (value.sends || []).find((item) => item.send_id === el("mramSendSelect").value);
    if (send) el("mramSendGain").value = String(send.gain_db);
  }

  function syncNode() {
    const value = activeRouting();
    const node = (value.nodes || []).find((item) => item.node_id === el("mramNodeSelect").value);
    if (!node) return;
    el("mramNodeGain").value = String(node.mixer.gain_db);
    el("mramNodePan").value = String(node.mixer.pan);
    el("mramNodeMute").checked = Boolean(node.mixer.mute);
  }

  function render() {
    const workspace = el("mramRoutingWorkspace");
    const badge = el("mramRoutingBadge");
    if (!routing.view) {
      workspace.hidden = true;
      badge.textContent = "NO PROJECT";
      badge.className = "status-pill neutral";
      return;
    }

    workspace.hidden = false;
    const preview = routing.view.preview;
    badge.textContent = preview ? "PREVIEW · NOT ACCEPTED" : "ACCEPTED ROUTING";
    badge.className = `status-pill ${preview ? "preview" : "accepted"}`;
    el("mramRoutingSource").textContent =
      `${routing.view.project_id} · ${routing.view.revision_id} · blueprint ${routing.view.blueprint_sha256.slice(0, 12)} · routing ${routing.view.routing_material_sha256.slice(0, 12)} · automation ${routing.view.automation_material_sha256.slice(0, 12)}`;

    const value = activeRouting();
    renderRows("mramTrackOutputs", value.track_outputs || [], (item) =>
      itemRow("track-output", item.track_id, `→ ${item.target_node_id}`)
    );
    renderRows("mramNodes", value.nodes || [], (item) =>
      itemRow("node", item.node_id, `${item.node_type} · out ${item.output_node_id || "MASTER"} · gain ${item.mixer.gain_db} dB · pan ${item.mixer.pan}${item.mixer.mute ? " · MUTED" : ""}`)
    );
    renderRows("mramSends", value.sends || [], (item) =>
      itemRow("send", item.send_id, `${item.source.kind}:${item.source.source_id} → ${item.target_node_id} · ${item.gain_db} dB · ${item.tap}`)
    );
    renderRows("mramNativeAutomation", routing.view.native_automation_lanes || [], (lane) =>
      itemRow("automation-lane", lane.lane_id, `${lane.target.scope}:${lane.target.owner_id} · ${lane.target.parameter_id} · ${lane.points.length} point(s)`)
    );

    fillSelect(el("mramTrackSelect"), value.track_outputs || [], "track_id", (item) => item.track_id);
    fillSelect(el("mramTrackTarget"), value.nodes || [], "node_id", (item) => `${item.node_id} · ${item.node_type}`);
    fillSelect(el("mramSendSelect"), value.sends || [], "send_id", (item) => item.send_id);
    fillSelect(el("mramNodeSelect"), value.nodes || [], "node_id", (item) => `${item.node_id} · ${item.node_type}`);
    syncSend();
    syncNode();

    const audio = el("mramRoutingAudio");
    const audition = preview ? preview.audition : routing.view.accepted_audition;
    if (audition && audition.available) {
      const source = preview ? "preview" : "accepted";
      audio.src = `/v0/sessions/${encodeURIComponent(routing.sessionId)}/mixer-routing/media/${source}.wav?v=${Date.now()}`;
      audio.hidden = false;
    } else {
      audio.removeAttribute("src");
      audio.load();
      audio.hidden = true;
    }
  }

  function candidateFor(operations, reason) {
    const view = routing.view;
    routing.requestCounter += 1;
    return {
      candidate_version: "0",
      candidate_id: `RTE-UI-${Date.now()}-${routing.requestCounter}`,
      authority_target: "blueprint_routing_material",
      source: {
        project_id: view.project_id,
        revision_id: view.revision_id,
        blueprint_sha256: view.blueprint_sha256,
        audio_material_sha256: view.audio_material_sha256,
        routing_material_sha256: view.routing_material_sha256,
      },
      actor: { kind: "user", actor_id: "browser-studio" },
      reason,
      operations,
      preview_only: true,
    };
  }

  function conflictText(item) {
    const context = [
      item.code,
      item.track_id ? `track ${item.track_id}` : null,
      item.node_id ? `node ${item.node_id}` : null,
      item.send_id ? `send ${item.send_id}` : null,
    ].filter(Boolean).join(" · ");
    return `${context}: ${item.reason}`;
  }

  async function sendPreview(operations, reason) {
    if (!routing.sessionId || !routing.view || routing.view.preview) return;
    clearStatus();
    try {
      const candidate = candidateFor(operations, reason);
      routing.lastSubmittedCandidate = candidate;
      const data = await routingFetch(
        `/v0/sessions/${encodeURIComponent(routing.sessionId)}/preview/routing`,
        { method: "POST", body: { candidate } },
      );
      routing.lastAuthorityResult = data.authority_result || null;
      routing.view = data.routing_view;
      if (!data.preview_installed) {
        const conflicts = (data.authority_result && data.authority_result.conflicts) || [];
        status(conflicts.map(conflictText).join(" | ") || "Routing edit blocked by trusted authority.", "error");
      } else {
        status("Routing Preview ready. Accepted HEAD is unchanged; audition is the exact routed candidate.", "success");
        const refresh = el("refreshButton");
        if (refresh) refresh.click();
      }
      render();
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  function previewTrackOutput() {
    const trackId = el("mramTrackSelect").value;
    const targetNodeId = el("mramTrackTarget").value;
    if (!trackId || !targetNodeId) return status("Track and target node are required.", "error");
    sendPreview(
      [{ operation_id: "UI-ROUTE-TRACK", op: "SET_TRACK_OUTPUT", track_id: trackId, target_node_id: targetNodeId }],
      `Browser Studio route ${trackId} to ${targetNodeId}.`,
    );
  }

  function previewSendGain() {
    const sendId = el("mramSendSelect").value;
    const gain = Number(el("mramSendGain").value);
    if (!sendId || !Number.isFinite(gain)) return status("Send and finite gain are required.", "error");
    sendPreview(
      [{ operation_id: "UI-ROUTE-SEND", op: "SET_SEND_GAIN", send_id: sendId, gain_db: gain }],
      `Browser Studio set send ${sendId} gain to ${gain} dB.`,
    );
  }

  function previewNodeMixer() {
    const nodeId = el("mramNodeSelect").value;
    const gain = Number(el("mramNodeGain").value);
    const pan = Number(el("mramNodePan").value);
    if (!nodeId || !Number.isFinite(gain) || !Number.isFinite(pan)) return status("Node, gain and pan are required.", "error");
    sendPreview(
      [{
        operation_id: "UI-ROUTE-NODE",
        op: "SET_NODE_MIXER",
        node_id: nodeId,
        mixer: { gain_db: gain, pan, mute: Boolean(el("mramNodeMute").checked) },
      }],
      `Browser Studio edit node mixer ${nodeId}.`,
    );
  }

  async function refreshRoutingView(quiet = false) {
    if (!routing.sessionId || !routing.root) return;
    try {
      routing.view = await routingFetch(
        `/v0/sessions/${encodeURIComponent(routing.sessionId)}/mixer-routing`,
      );
      render();
      if (!quiet) status("Routing view refreshed.", "success");
    } catch (error) {
      routing.view = null;
      render();
      if (!quiet) status(error.message || String(error), "error");
    }
  }

  injectSurface();
  window.MUSICA_ROUTING = { refresh: refreshRoutingView, state: routing };
})();
