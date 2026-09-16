(() => {
  "use strict";

  const priorFetch = window.fetch.bind(window);
  const host = window.MUSICA_AUTOMATION;
  if (!host || !host.state) return;

  const state = host.state;
  state.auditionView = null;
  let requestSerial = 0;
  let refreshQueued = false;
  let refreshInFlight = false;

  const el = (id) => document.getElementById(id);
  const shortHash = (value) => (typeof value === "string" && value.length >= 12 ? `${value.slice(0, 12)}…` : "—");

  async function fetchJson(path) {
    const response = await priorFetch(path, { headers: { Accept: "application/json" } });
    const payload = await response.json();
    if (!response.ok || !payload || payload.ok === false) {
      const detail = payload && payload.error ? payload.error : { message: `HTTP ${response.status}` };
      const error = new Error(detail.message || `HTTP ${response.status}`);
      error.code = detail.code || "http_error";
      throw error;
    }
    return payload.data;
  }

  function inject() {
    const card = el("m7AutomationCard");
    if (!card || el("m7AuditionInspector")) return;
    const authorityCopy = card.querySelector(".m7-authority-copy");
    const inspector = document.createElement("section");
    inspector.id = "m7AuditionInspector";
    inspector.className = "m7-audition-inspector";
    inspector.hidden = true;
    inspector.innerHTML = `
      <div class="m7-audition-heading">
        <div><span class="eyebrow">M7-R6 · AUDITION INSPECTION</span><strong>Audible automation truth / 가청 자동화 사실</strong></div>
        <span id="m7AuditionBadge" class="status-pill neutral">NO SESSION</span>
      </div>
      <p class="muted small">Historical R2 automation view remains unchanged. This read-only panel reports only the bounded R5 audition and exact accepted-media identity; Browser/audio state is not canonical.</p>
      <dl class="m7-audition-grid">
        <div><dt>Renderer policy</dt><dd id="m7AuditionPolicy" class="mono">—</dd></div>
        <div><dt>Accepted mapping</dt><dd id="m7AuditionMapping" class="mono">—</dd></div>
        <div><dt>Pending audition</dt><dd id="m7AuditionPending" class="mono">—</dd></div>
        <div><dt>Accepted media</dt><dd id="m7AuditionAcceptedMedia" class="mono">—</dd></div>
      </dl>`;
    if (authorityCopy) authorityCopy.insertAdjacentElement("afterend", inspector);
    else card.prepend(inspector);
  }

  function render() {
    inject();
    const root = el("m7AuditionInspector");
    if (!root) return;
    const view = state.auditionView;
    root.hidden = !view;
    if (!view) return;

    const policy = view.renderer_policy;
    const mapping = view.accepted_mapping;
    const pending = view.pending_audition;
    const media = view.accepted_media;
    const badge = el("m7AuditionBadge");

    if (pending) {
      badge.textContent = pending.automation_applied
        ? "AUDIBLE PREVIEW · NOT ACCEPTED"
        : "PREVIEW · UNMAPPED / BASELINE";
      badge.className = "status-pill preview";
    } else {
      badge.textContent = "ACCEPTED MEDIA";
      badge.className = "status-pill accepted";
    }

    el("m7AuditionPolicy").textContent = `${policy.renderer_id} · ${policy.policy_id}`;
    const mapped = (mapping.mapped_lane_ids || []).join(", ") || "none";
    const unmapped = (mapping.unmapped_lane_ids || []).join(", ") || "none";
    el("m7AuditionMapping").textContent = `mapped: ${mapped} · unmapped: ${unmapped}`;

    if (pending) {
      el("m7AuditionPending").textContent = `${pending.candidate_revision_id} · mapped: ${(pending.mapped_lane_ids || []).join(", ") || "none"} · unmapped: ${(pending.unmapped_lane_ids || []).join(", ") || "none"} · wav:${shortHash(pending.preview_wav_sha256)} · plan:${shortHash(pending.render_plan_sha256)}`;
    } else {
      el("m7AuditionPending").textContent = "none · accepted state only";
    }

    el("m7AuditionAcceptedMedia").textContent = `${media.revision_id} · WAV ${media.wav.source}:${shortHash(media.wav.sha256)} · MIDI ${media.midi.source}:${shortHash(media.midi.sha256)}`;
  }

  async function refresh(quiet = false) {
    if (refreshInFlight) {
      refreshQueued = true;
      return;
    }
    const sessionId = state.sessionId;
    if (!sessionId) {
      state.auditionView = null;
      render();
      return;
    }
    refreshInFlight = true;
    const serial = ++requestSerial;
    try {
      const value = await fetchJson(`/v0/sessions/${encodeURIComponent(sessionId)}/automation/audition`);
      if (serial === requestSerial && state.sessionId === sessionId) state.auditionView = value;
    } catch (error) {
      if (serial === requestSerial) state.auditionView = null;
      if (!quiet && window.console) console.error("M7-R6 audition inspection failed", error);
    } finally {
      refreshInFlight = false;
      render();
      if (refreshQueued) {
        refreshQueued = false;
        queueMicrotask(() => refresh(true));
      }
    }
  }

  function queueRefresh() {
    if (!state.sessionId) return;
    refreshQueued = true;
    queueMicrotask(() => {
      if (!refreshInFlight && refreshQueued) {
        refreshQueued = false;
        refresh(true);
      }
    });
  }

  window.fetch = async (...args) => {
    const response = await priorFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/automation/audition")) queueRefresh();
    } catch (_error) {
      // This inspection overlay is non-authoritative and must not break Studio requests.
    }
    return response;
  };

  const priorRefresh = host.refresh;
  host.refresh = async (...args) => {
    const result = await priorRefresh(...args);
    await refresh(true);
    return result;
  };
  host.refreshAudition = refresh;

  inject();
  queueRefresh();
})();
