/* PLUG-R3B: bounded, truthful Browser editor for accepted simulated bus-host.
   AI/browser state is never canonical. No native binary hosting/realtime claims. */
(() => {
  "use strict";
  const upstreamFetch = window.fetch.bind(window);
  const state = {
    sessionId: null,
    observedRevisionId: null,
    editor: null,
    accepted: null,
    preview: null,
    counter: 0,
    requestId: 0,
    root: null,
  };
  const byId = (id) => document.getElementById(id);
  const escapePath = (value) => encodeURIComponent(String(value));

  async function request(path, options = {}) {
    const init = {
      method: options.method || "GET",
      headers: {Accept: "application/json"},
      cache: "no-store",
    };
    if (options.body !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(options.body);
    }
    const response = await upstreamFetch(path, init);
    const payload = await response.json().catch(() => null);
    if (!response.ok || !payload || !payload.ok) {
      const issue = payload && payload.error;
      throw new Error(issue && issue.message ? issue.message : "HTTP " + response.status);
    }
    return payload.data;
  }
  function rootPath() {
    return "/v0/sessions/" + escapePath(state.sessionId);
  }
  function note(message, kind = "info") {
    const target = byId("plugBrowserStatus");
    if (!target) return;
    target.textContent = String(message);
    target.className = "plug-browser-message " + kind;
    target.hidden = false;
  }
  function clearPreviewPlayer() {
    const player = byId("plugBrowserPreviewAudio");
    if (player) {
      player.pause();
      player.removeAttribute("src");
      player.load();
    }
  }
  function fillSelect(select, options, prior) {
    if (!select) return;
    select.replaceChildren();
    for (const option of options) {
      const el = document.createElement("option");
      el.value = String(option.id);
      el.textContent = String(option.label);
      select.appendChild(el);
    }
    if (options.some((o) => String(o.id) === String(prior))) select.value = String(prior);
  }
  function text(id, value) {
    const target = byId(id);
    if (target) target.textContent = String(value);
  }
  function inject() {
    const panel = byId("panel-inspect");
    if (!panel || byId("plugBrowserCard")) return;
    const section = document.createElement("section");
    section.id = "plugBrowserCard";
    section.className = "card plug-browser-card";
    // All HTML is trusted static markup; project strings use textContent only.
    section.innerHTML = `
      <div class="card-heading">
        <div><span class="eyebrow">PLUG · SIMULATED BUS</span>
          <h2>Bus processors / 버스 이펙트</h2></div>
        <span id="plugBrowserBadge" class="status-pill neutral">NO PROJECT</span>
      </div>
      <p class="muted small">Two accepted buses only · Simulated algorithmic latency,
        not VST3/CLAP/AU or realtime PDC. Preview never edits the accepted project.
        / Preview는 승인 전 프로젝트를 변경하지 않습니다.</p>
      <div id="plugBrowserStatus" class="plug-browser-message" role="status"
           aria-live="polite" hidden></div>
      <div id="plugBrowserWorkspace" hidden>
        <div class="plug-browser-provenance">
          <span class="eyebrow">ACCEPTED SOURCE / 승인 상태</span>
          <code id="plugBrowserSource">—</code>
        </div>
        <div class="plug-browser-columns">
          <section class="plug-browser-pane" aria-labelledby="plugAcceptedTitle">
            <h3 id="plugAcceptedTitle">Accepted / 승인됨</h3>
            <div id="plugBrowserAcceptedList" class="plug-browser-instances"></div>
            <label class="plug-browser-audio-label" for="plugBrowserAcceptedAudio">Accepted offline mix</label>
            <audio id="plugBrowserAcceptedAudio" controls preload="none"></audio>
          </section>
          <section class="plug-browser-pane" aria-labelledby="plugEditTitle">
            <h3 id="plugEditTitle">Propose / 변경 제안</h3>
            <label>Owner bus / 대상 버스
              <select id="plugBrowserBus"></select></label>
            <label>Algorithmic latency · frames / 처리 지연
              <input id="plugBrowserLatency" type="number" min="0" max="4096" step="1" value="3"></label>
            <label>Creative delay · frames / 의도적 지연
              <input id="plugBrowserCreative" type="number" min="0" max="4096" step="1" value="0"></label>
            <label class="plug-browser-check"><input id="plugBrowserBypass" type="checkbox">
              Bypass processing / 처리 우회 (창작 지연은 보존)</label>
            <div class="plug-browser-actions">
              <button id="plugBrowserPropose" class="secondary" type="button">Preview add/update / 미리보기</button>
              <button id="plugBrowserRemove" class="ghost" type="button">Preview remove / 제거 제안</button>
            </div>
          </section>
        </div>
        <section class="plug-browser-preview" id="plugBrowserPending" hidden aria-labelledby="plugPendingTitle">
          <div class="card-heading">
            <h3 id="plugPendingTitle">PREVIEW ONLY / 미승인 변경</h3>
            <span class="status-pill preview">NOT ACCEPTED</span>
          </div>
          <p id="plugBrowserPendingDescription" class="muted"></p>
          <audio id="plugBrowserPreviewAudio" controls preload="none"></audio>
          <div class="plug-browser-actions">
            <button id="plugBrowserAccept" class="primary" type="button">Accept / 명시적 승인</button>
            <button id="plugBrowserDiscard" class="secondary" type="button">Discard / 폐기</button>
          </div>
        </section>
      </div>`;
    const anchor = byId("mramRoutingCard");
    if (anchor) anchor.insertAdjacentElement("afterend", section);
    else panel.appendChild(section);
    state.root = section;
    byId("plugBrowserBus").addEventListener("change", syncInputs);
    byId("plugBrowserPropose").addEventListener("click", () => preview(false));
    byId("plugBrowserRemove").addEventListener("click", () => preview(true));
    byId("plugBrowserAccept").addEventListener("click", () => finish(true));
    byId("plugBrowserDiscard").addEventListener("click", () => finish(false));
  }
  function acceptedInstances() {
    return state.editor?.accepted_material?.instances || [];
  }
  function syncInputs() {
    const bus = byId("plugBrowserBus")?.value;
    const instance = acceptedInstances().find((v) => v.owner_bus_id === bus);
    byId("plugBrowserLatency").value = instance ? instance.algorithmic_latency_frames : "3";
    byId("plugBrowserCreative").value = instance ? instance.creative_delay_frames : "0";
    byId("plugBrowserBypass").checked = Boolean(instance?.bypass);
  }
  function formatInstance(instance) {
    return instance.owner_bus_id + " · " +
      (instance.bypass ? "BYPASS" : "ACTIVE") + " · alg " +
      instance.algorithmic_latency_frames + "f / creative " +
      instance.creative_delay_frames + "f";
  }
  function showView() {
    if (!state.root) return;
    byId("plugBrowserWorkspace").hidden = !state.editor;
    const available = Boolean(state.editor?.eligible_for_bounded_preview);
    const pending = Boolean(state.preview) || Boolean(state.editor?.preview_pending);
    text("plugBrowserBadge", !state.editor ? "NO PROJECT" : pending ? "PREVIEW" : available ? "ACCEPTED" : "INSPECT ONLY");
    text("plugBrowserSource", state.editor ?
      state.editor.revision_id + " · sha256:" + state.editor.source.blueprint_sha256.slice(0, 16) + "…" : "—");
    const list = byId("plugBrowserAcceptedList");
    list?.replaceChildren();
    const instances = acceptedInstances();
    if (!instances.length && list) {
      const el = document.createElement("p");
      el.className = "muted";
      el.textContent = "No accepted bus processors / 승인된 버스 프로세서 없음";
      list.appendChild(el);
    }
    for (const instance of instances) {
      const el = document.createElement("p");
      el.className = "plug-browser-instance";
      el.textContent = formatInstance(instance);
      list?.appendChild(el);
    }
    const bus = byId("plugBrowserBus");
    const prior = bus?.value;
    fillSelect(bus, (state.editor?.supported_buses || []).map((path) => ({
      id: path.bus_node_id,
      label: path.bus_node_id + " ← " + path.track_id,
    })), prior);
    syncInputs();
    byId("plugBrowserPropose").disabled = !available || pending;
    byId("plugBrowserRemove").disabled = !available || pending;
    const audition = state.accepted?.offline_audition;
    const player = byId("plugBrowserAcceptedAudio");
    if (player) {
      if (audition?.available && audition.wav_sha256) {
        const src = rootPath() + "/bus-plugins/media/accepted.wav?sha=" +
          escapePath(audition.wav_sha256);
        if (player.getAttribute("src") !== src) player.setAttribute("src", src);
      } else {
        player.pause();
        player.removeAttribute("src");
        player.load();
      }
    }
    const ours = state.preview && state.preview.preview?.kind === "bus_host_edit";
    byId("plugBrowserPending").hidden = !ours;
    byId("plugBrowserAccept").disabled = !ours;
    byId("plugBrowserDiscard").disabled = !ours;
    if (ours) {
      text("plugBrowserPendingDescription",
        state.preview.preview.candidate_revision_id + " · derived offline WAV; not accepted");
      const p = byId("plugBrowserPreviewAudio");
      const src = rootPath() + "/bus-plugins/media/preview.wav?preview=" +
        escapePath(state.preview.preview.preview_id);
      if (p.getAttribute("src") !== src) p.setAttribute("src", src);
    } else {
      clearPreviewPlayer();
    }
    if (state.editor && !available && !pending) {
      note("Read-only: " + (state.editor.ineligible_reason || "unsupported routing"), "info");
    }
    if (state.editor?.preview_pending && !ours) {
      note("Another Studio Preview is pending. Accept or discard it before editing plugins.", "info");
    }
  }
  async function refresh(quiet = true) {
    if (!state.sessionId || !state.root) return;
    const index = ++state.requestId;
    try {
      const base = rootPath();
      // Do not eagerly render an offline accepted WAV for unrelated Studio
      // projects. It can be expensive and contend with Recording/RTIO startup.
      // First query the cheap exact-source/topology eligibility projection;
      // render accepted WAV only for the supported bounded two-bus editor.
      const editor = await request(base + "/bus-plugins/editor");
      if (index !== state.requestId) return;
      const accepted = editor.eligible_for_bounded_preview
        ? await request(base + "/bus-plugins")
        : {offline_audition: {available: false}};
      if (index !== state.requestId) return;
      state.editor = editor;
      state.accepted = accepted;
      if (!editor.preview_pending) state.preview = null;
      showView();
      if (!quiet) note("Accepted bus-host state refreshed.", "success");
    } catch (error) {
      if (index !== state.requestId) return;
      state.editor = null;
      state.accepted = null;
      showView();
      if (!quiet) note(error.message || String(error), "error");
    }
  }
  function boundedInt(id) {
    const input = byId(id);
    const raw = input?.value?.trim() || "";
    if (!/^\d+$/.test(raw)) throw new Error("Frame counts must be whole nonnegative integers.");
    const value = Number(raw);
    if (!Number.isSafeInteger(value) || value < 0 || value > 4096)
      throw new Error("Frame count must be an integer from 0 to 4096.");
    return value;
  }
  async function preview(remove) {
    if (!state.editor || !state.editor.eligible_for_bounded_preview) return;
    if (state.editor.preview_pending) return note("A Preview is already pending.", "error");
    const bus = byId("plugBrowserBus").value;
    if (!state.editor.supported_buses.some((v) => v.bus_node_id === bus))
      return note("Select an accepted bus before preview.", "error");
    try {
      const material = JSON.parse(JSON.stringify(state.editor.accepted_material));
      material.instances = material.instances.filter((item) => item.owner_bus_id !== bus);
      if (!remove) {
        const existing = acceptedInstances().find((item) => item.owner_bus_id === bus);
        material.instances.push({
          instance_id: existing?.instance_id || ("BPI-" + bus),
          owner_kind: "routing_node",
          owner_bus_id: bus,
          slot: 0,
          processor_id: "musica-simulated-bus-latency-v0",
          processor_version: "0",
          latency_provenance: "accepted_explicit_simulated_reference",
          algorithmic_latency_frames: boundedInt("plugBrowserLatency"),
          creative_delay_frames: boundedInt("plugBrowserCreative"),
          bypass: Boolean(byId("plugBrowserBypass").checked),
        });
      }
      material.instances.sort((a, b) => a.owner_bus_id.localeCompare(b.owner_bus_id));
      if (remove && material.instances.length === acceptedInstances().length) {
        return note("No accepted processor exists on that bus.", "error");
      }
      const candidate = {
        candidate_version: "0",
        candidate_id: "BROWSER-PLUG-R3B-" + String(++state.counter),
        authority_target: "blueprint_bus_plugin_material",
        source: structuredClone(state.editor.source),
        proposed_material: material,
        actor: {kind: "user", actor_id: "studio-browser-bus-host"},
        reason: remove ? "Browser remove simulated bus processor on " + bus :
          "Browser preview simulated bus processor on " + bus,
        preview_only: true,
      };
      note("Validating source and rendering noncanonical Preview...", "info");
      const data = await request(rootPath() + "/preview/bus-plugins", {
        method: "POST", body: {candidate},
      });
      if (!data.preview_installed) {
        return note("Preview blocked: " + data.reason, "error");
      }
      state.preview = data;
      await refresh(true);
      showView();
      note("Preview ready. Listen, then explicitly Accept or Discard.", "success");
    } catch (error) {
      note(error.message || String(error), "error");
      await refresh(true);
    }
  }
  async function finish(accept) {
    if (!state.preview || state.preview.preview?.kind !== "bus_host_edit") return;
    const name = accept ? "accept" : "discard";
    try {
      clearPreviewPlayer();
      note(accept ? "Rechecking source and accepting..." : "Discarding transient Preview...", "info");
      const data = await request(rootPath() + "/preview/" + name, {
        method: "POST", body: {},
      });
      state.preview = null;
      await refresh(true);
      const globalRefresh = byId("refreshButton");
      if (globalRefresh) globalRefresh.click();
      note(accept ? "Accepted a new Project revision; offline mix rebuilt." :
        "Preview discarded; accepted Project unchanged.", "success");
    } catch (error) {
      note(error.message || String(error), "error");
      await refresh(true);
    }
  }
  function observe(response) {
    try {
      const ct = response.headers.get("content-type") || "";
      if (!ct.includes("application/json")) return;
      response.clone().json().then((payload) => {
        const datum = payload?.data;
        const session = datum?.session;
        if (!session?.session_id) return;
        const changed = state.sessionId !== session.session_id
          || state.observedRevisionId !== session.head_revision_id;
        state.sessionId = session.session_id;
        state.observedRevisionId = session.head_revision_id;
        // Multiple overlays observe the same Studio session response. Refresh
        // only on a distinct accepted revision/session, not on every request;
        // otherwise redundant bus-host rendering can starve recording/RTIO UI.
        if (changed) queueMicrotask(() => refresh(true));
      }).catch(() => {});
    } catch (_) {}
  }
  window.fetch = async (...args) => {
    const response = await upstreamFetch(...args);
    const req = args[0];
    const url = typeof req === "string" ? req : req?.url || "";
    if (!url.includes("/bus-plugins")) observe(response);
    return response;
  };
  inject();
  window.MUSICA_BUS_HOST = {refresh, state};
})();
