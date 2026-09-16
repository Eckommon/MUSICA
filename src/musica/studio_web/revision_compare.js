(() => {
  "use strict";

  const host = window.MUSICA_AUTOMATION;
  if (!host || !host.state) return;

  const priorFetch = window.fetch.bind(window);
  const hostState = host.state;
  const compareState = {
    sessionId: null,
    history: [],
    view: null,
    userChoice: null,
    refreshSerial: 0,
    compareSerial: 0,
    refreshInFlight: false,
    refreshQueued: false,
  };

  const el = (id) => document.getElementById(id);
  const shortHash = (value) =>
    typeof value === "string" && value.length >= 12 ? `${value.slice(0, 12)}…` : "—";

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
    const panel = el("panel-inspect");
    if (!panel || el("revisionCompareCard")) return;
    const anchor = el("m7AutomationCard") || panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "revisionCompareCard";
    card.className = "card revision-compare-card";
    card.hidden = true;
    card.innerHTML = `
      <div class="card-heading revision-compare-heading">
        <div><span class="eyebrow">POST-M7 · COMPARE</span><h2>Accepted revision A/B / 승인 리비전 비교</h2></div>
        <span id="revisionCompareBadge" class="status-pill neutral">READ ONLY</span>
      </div>
      <p class="muted small">Compare two immutable accepted revisions. MUSICA shows exact structured changes and provenance-bound audition media, but never ranks a creative winner or accepts a revision implicitly.</p>
      <div id="revisionCompareStatus" class="revision-compare-status" role="status" aria-live="polite" hidden></div>
      <div class="revision-compare-toolbar">
        <label>Revision A<select id="revisionCompareA"></select></label>
        <span class="revision-compare-arrow" aria-hidden="true">→</span>
        <label>Revision B<select id="revisionCompareB"></select></label>
        <button id="revisionCompareRun" class="secondary" type="button">Compare A → B / 비교</button>
      </div>
      <div id="revisionCompareHead" class="mono muted small">—</div>
      <div id="revisionCompareResult" hidden>
        <div class="revision-compare-audio-grid">
          <section class="revision-compare-side" data-side="a">
            <div class="revision-compare-side-heading"><strong>A</strong><span id="revisionCompareALabel" class="mono">—</span></div>
            <audio id="revisionCompareAudioA" controls preload="metadata"></audio>
            <a id="revisionCompareMidiA" class="text-link" href="#">MIDI A</a>
            <div id="revisionCompareMetaA" class="mono muted small">—</div>
          </section>
          <section class="revision-compare-side" data-side="b">
            <div class="revision-compare-side-heading"><strong>B</strong><span id="revisionCompareBLabel" class="mono">—</span></div>
            <audio id="revisionCompareAudioB" controls preload="metadata"></audio>
            <a id="revisionCompareMidiB" class="text-link" href="#">MIDI B</a>
            <div id="revisionCompareMetaB" class="mono muted small">—</div>
          </section>
        </div>
        <div class="revision-compare-decision" aria-label="Local-only user revision choice">
          <div><strong>Your decision / 사용자 선택</strong><div class="muted small">This choice is Browser-local only. It does not Accept, checkout, move HEAD, or become MUSICA's creative verdict.</div></div>
          <div class="revision-compare-decision-actions">
            <button id="revisionCompareChooseA" class="secondary" type="button" aria-pressed="false">Choose A · local only</button>
            <button id="revisionCompareChooseB" class="secondary" type="button" aria-pressed="false">Choose B · local only</button>
          </div>
          <span id="revisionCompareChoice" class="status-pill neutral">NO USER CHOICE</span>
        </div>
        <div class="revision-compare-diff-heading">
          <strong>Structured Blueprint diff · A_TO_B</strong>
          <span id="revisionCompareDiffCount" class="status-pill neutral">0 changes</span>
        </div>
        <ol id="revisionCompareDiff" class="revision-compare-diff"></ol>
        <p class="muted small revision-compare-authority">Comparison, audition, media retrieval, and the local user choice are non-canonical. HEAD remains unchanged. Nothing here performs Accept or checkout.</p>
      </div>`;
    if (anchor) anchor.insertAdjacentElement("afterend", card);
    else panel.appendChild(card);

    el("revisionCompareRun").addEventListener("click", () => runCompare(false));
    el("revisionCompareChooseA").addEventListener("click", () => setUserChoice("A"));
    el("revisionCompareChooseB").addEventListener("click", () => setUserChoice("B"));
  }

  function status(message, kind = "info") {
    const target = el("revisionCompareStatus");
    if (!target) return;
    target.textContent = message;
    target.className = `revision-compare-status ${kind}`;
    target.hidden = !message;
  }

  function optionLabel(record) {
    const id = String(record.revision_id || "");
    const sequence = Number(record.logical_sequence || 0);
    return `#${sequence} · ${id}`;
  }

  function repopulateSelect(select, records, preferred) {
    const previous = preferred || select.value;
    select.textContent = "";
    records.forEach((record) => {
      const option = document.createElement("option");
      option.value = String(record.revision_id);
      option.textContent = optionLabel(record);
      select.appendChild(option);
    });
    if (records.some((record) => String(record.revision_id) === previous)) select.value = previous;
  }

  function chooseDefaults(history) {
    if (!history.length) return;
    const a = el("revisionCompareA");
    const b = el("revisionCompareB");
    if (!a || !b) return;
    const head = history[history.length - 1];
    const previous = history.length > 1 ? history[history.length - 2] : head;
    repopulateSelect(a, history, a.value || String(previous.revision_id));
    repopulateSelect(b, history, b.value || String(head.revision_id));
  }

  function renderHistory() {
    inject();
    const card = el("revisionCompareCard");
    if (!card) return;
    card.hidden = !compareState.sessionId || compareState.history.length === 0;
    if (card.hidden) return;
    chooseDefaults(compareState.history);
    if (!compareState.view) {
      const head = compareState.history[compareState.history.length - 1];
      el("revisionCompareHead").textContent = `history: ${compareState.history.length} accepted revision(s) · latest listed: ${head.revision_id}`;
    }
  }

  function renderDiff(diff) {
    const root = el("revisionCompareDiff");
    root.textContent = "";
    if (!diff.length) {
      const item = document.createElement("li");
      item.className = "revision-compare-empty";
      item.textContent = "No structured Blueprint differences. A and B are identical accepted state.";
      root.appendChild(item);
      return;
    }
    diff.forEach((change) => {
      const item = document.createElement("li");
      const operation = document.createElement("strong");
      operation.textContent = String(change.op).toUpperCase();
      const path = document.createElement("code");
      path.textContent = String(change.path);
      const values = document.createElement("span");
      values.className = "revision-compare-values";
      values.textContent = `${JSON.stringify(change.before)} → ${JSON.stringify(change.after)}`;
      item.append(operation, document.createTextNode(" "), path, values);
      root.appendChild(item);
    });
  }

  function artifactLabel(media) {
    if (media.source !== "bound_artifact") return "derived fallback · no artifact manifest";
    return `${media.artifact_name} · manifest ${shortHash(media.artifact_manifest_sha256)}`;
  }

  function setSide(sideKey, side) {
    const suffix = sideKey.toUpperCase();
    const revisionId = String(side.revision_id);
    const base = `/v0/sessions/${encodeURIComponent(compareState.sessionId)}/revisions/${encodeURIComponent(revisionId)}/media`;
    el(`revisionCompare${suffix}Label`).textContent = revisionId;
    const audio = el(`revisionCompareAudio${suffix}`);
    audio.src = `${base}/audio.wav`;
    const midi = el(`revisionCompareMidi${suffix}`);
    midi.href = `${base}/preview.mid`;
    midi.download = `${revisionId}.mid`;
    const wav = side.media.wav;
    const midiMeta = side.media.midi;
    el(`revisionCompareMeta${suffix}`).textContent = `Blueprint ${shortHash(side.blueprint_sha256)} · record ${shortHash(side.revision_record_sha256)} · WAV ${wav.source}:${shortHash(wav.sha256)} [${artifactLabel(wav)}] · MIDI ${midiMeta.source}:${shortHash(midiMeta.sha256)} [${artifactLabel(midiMeta)}]`;
  }

  function renderChoice() {
    const choice = compareState.userChoice;
    const target = el("revisionCompareChoice");
    const buttonA = el("revisionCompareChooseA");
    const buttonB = el("revisionCompareChooseB");
    if (!target || !buttonA || !buttonB) return;
    buttonA.setAttribute("aria-pressed", String(choice === "A"));
    buttonB.setAttribute("aria-pressed", String(choice === "B"));
    if (!choice || !compareState.view) {
      target.textContent = "NO USER CHOICE";
      target.className = "status-pill neutral";
      return;
    }
    const revision = choice === "A" ? compareState.view.revision_a.revision_id : compareState.view.revision_b.revision_id;
    target.textContent = `USER CHOICE · ${choice} · LOCAL ONLY · ${revision}`;
    target.className = "status-pill preview";
  }

  function setUserChoice(choice) {
    if (!compareState.view || !["A", "B"].includes(choice)) return;
    compareState.userChoice = choice;
    renderChoice();
    const revision = choice === "A" ? compareState.view.revision_a.revision_id : compareState.view.revision_b.revision_id;
    status(`User chose ${choice} (${revision}) locally. Canonical HEAD was not changed.`, "success");
  }

  function renderCompare() {
    const view = compareState.view;
    const root = el("revisionCompareResult");
    if (!root) return;
    root.hidden = !view;
    if (!view) {
      renderChoice();
      return;
    }

    setSide("a", view.revision_a);
    setSide("b", view.revision_b);
    renderDiff(view.diff || []);
    renderChoice();
    el("revisionCompareDiffCount").textContent = `${(view.diff || []).length} change${(view.diff || []).length === 1 ? "" : "s"}`;
    el("revisionCompareHead").textContent = `${view.current_branch} · HEAD ${view.current_head_revision_id} · head_unchanged=${String(view.head_unchanged)}`;
    const badge = el("revisionCompareBadge");
    badge.textContent = "READ ONLY · NO RANKING";
    badge.className = "status-pill accepted";
  }

  async function refreshHistory(quiet = false) {
    inject();
    const sessionId = hostState.sessionId;
    if (!sessionId) {
      compareState.sessionId = null;
      compareState.history = [];
      compareState.view = null;
      compareState.userChoice = null;
      renderHistory();
      renderCompare();
      return;
    }
    if (compareState.refreshInFlight) {
      compareState.refreshQueued = true;
      return;
    }
    compareState.refreshInFlight = true;
    const serial = ++compareState.refreshSerial;
    try {
      const data = await fetchJson(`/v0/sessions/${encodeURIComponent(sessionId)}/history`);
      if (serial !== compareState.refreshSerial || hostState.sessionId !== sessionId) return;
      const changedSession = compareState.sessionId !== sessionId;
      compareState.sessionId = sessionId;
      compareState.history = Array.isArray(data.revisions) ? data.revisions : [];
      if (changedSession) {
        compareState.view = null;
        compareState.userChoice = null;
      }
      renderHistory();
      renderCompare();
    } catch (error) {
      if (serial === compareState.refreshSerial) {
        compareState.history = [];
        compareState.view = null;
        compareState.userChoice = null;
        renderHistory();
        renderCompare();
      }
      if (!quiet && window.console) console.error("Accepted revision history refresh failed", error);
    } finally {
      compareState.refreshInFlight = false;
      if (compareState.refreshQueued) {
        compareState.refreshQueued = false;
        queueMicrotask(() => refreshHistory(true));
      }
    }
  }

  async function runCompare(quiet = false) {
    const sessionId = compareState.sessionId || hostState.sessionId;
    const a = el("revisionCompareA");
    const b = el("revisionCompareB");
    if (!sessionId || !a || !b || !a.value || !b.value) return;
    const serial = ++compareState.compareSerial;
    status("Comparing immutable accepted revisions…", "info");
    try {
      const path = `/v0/sessions/${encodeURIComponent(sessionId)}/compare/${encodeURIComponent(a.value)}/${encodeURIComponent(b.value)}`;
      const view = await fetchJson(path);
      if (serial !== compareState.compareSerial || hostState.sessionId !== sessionId) return;
      compareState.view = view;
      compareState.userChoice = null;
      renderCompare();
      status(`Compared ${view.revision_a.revision_id} → ${view.revision_b.revision_id} without moving HEAD.`, "success");
    } catch (error) {
      if (serial === compareState.compareSerial) {
        compareState.view = null;
        compareState.userChoice = null;
        renderCompare();
        status(error.message || String(error), "error");
      }
      if (!quiet && window.console) console.error("Accepted revision comparison failed", error);
    }
  }

  function queueRefresh() {
    if (!hostState.sessionId) return;
    compareState.refreshQueued = true;
    queueMicrotask(() => {
      if (!compareState.refreshInFlight && compareState.refreshQueued) {
        compareState.refreshQueued = false;
        refreshHistory(true);
      }
    });
  }

  window.fetch = async (...args) => {
    const response = await priorFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      const internalCompareRequest =
        url.includes("/history") || url.includes("/compare/") || url.includes("/revisions/");
      if (!internalCompareRequest) queueRefresh();
    } catch (_error) {
      // Read-only comparison must never interfere with the canonical Studio request path.
    }
    return response;
  };

  const priorRefresh = host.refresh;
  host.refresh = async (...args) => {
    const result = await priorRefresh(...args);
    await refreshHistory(true);
    return result;
  };
  host.refreshRevisionCompare = refreshHistory;
  host.revisionCompareState = compareState;

  inject();
  queueRefresh();
})();
