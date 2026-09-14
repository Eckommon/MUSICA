(() => {
  "use strict";

  const originalFetch = window.fetch.bind(window);
  const automation = {
    sessionId: null,
    view: null,
    selectedKey: null,
    requestCounter: 0,
    root: null,
    lastSubmittedCandidate: null,
    lastAuthorityResult: null,
  };

  const el = (id) => document.getElementById(id);
  const pointKey = (laneId, pointId) => `${laneId}::${pointId}`;

  function status(message, kind = "info") {
    const target = el("m7AutomationStatus");
    if (!target) return;
    target.textContent = message;
    target.className = `m7-automation-status ${kind}`;
    target.hidden = false;
  }

  function clearStatus() {
    const target = el("m7AutomationStatus");
    if (!target) return;
    target.hidden = true;
    target.textContent = "";
  }

  async function automationFetch(path, options = {}) {
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
    const changed = automation.sessionId !== session.session_id;
    automation.sessionId = session.session_id;
    if (changed || session.head_revision_id) queueMicrotask(() => refreshAutomationView(true));
  }

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/automation")) {
        const clone = response.clone();
        const contentType = clone.headers.get("content-type") || "";
        if (contentType.includes("application/json")) observeSessionPayload(await clone.json());
      }
    } catch (_error) {
      // Browser observation is non-authoritative and must not break the core request.
    }
    return response;
  };

  function injectSurface() {
    const panel = el("panel-inspect");
    if (!panel || el("m7AutomationCard")) return;
    const anchor = el("m6PrecisionCard") || panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "m7AutomationCard";
    card.className = "card m7-automation-card";
    card.innerHTML = `
      <div class="card-heading m7-heading">
        <div><span class="eyebrow">M7 · AUTOMATION</span><h2>Canonical automation / 공식 자동화</h2></div>
        <span id="m7AutomationAvailability" class="status-pill neutral">NO PROJECT</span>
      </div>
      <p class="muted small m7-authority-copy">Lane geometry is presentation only. Every edit is bound to stable lane_id / point_id and remains PREVIEW until explicit Accept. Audible automation is not validated in M7-R2.</p>
      <div id="m7AutomationStatus" class="m7-automation-status" role="status" aria-live="polite" hidden></div>
      <div id="m7AutomationUnavailable" class="m7-unavailable">Open an automation-capable project to edit canonical automation.</div>
      <div id="m7AutomationWorkspace" hidden>
        <div class="m7-toolbar">
          <span id="m7AutomationSource" class="mono muted">—</span>
          <span id="m7AutomationPreviewBadge" class="status-pill accepted">ACCEPTED AUTOMATION</span>
        </div>
        <div id="m7AutomationLanes" class="m7-lanes" aria-label="Canonical automation lanes"></div>
        <div class="m7-editor-grid">
          <fieldset id="m7SelectedFieldset" class="m7-editor" disabled>
            <legend>Selected point / 선택 포인트</legend>
            <div class="m7-selected-line"><strong id="m7SelectedPoint">—</strong><span id="m7SelectedLocks" class="m7-lock-badges"></span></div>
            <div id="m7SelectedParameter" class="mono muted small">—</div>
            <div class="m7-fields">
              <label>Beat<input id="m7PointBeat" type="number" min="0" step="0.01"></label>
              <label>Value<input id="m7PointValue" type="number" step="0.01"></label>
              <label>Interpolation<select id="m7PointInterpolation"><option value="linear">linear</option><option value="hold">hold</option></select></label>
            </div>
            <div class="m7-actions">
              <button id="m7PreviewPointChanges" class="primary" type="button">Preview changes / 변경 미리보기</button>
              <button id="m7DeletePoint" class="danger" type="button">Delete point / 포인트 삭제</button>
            </div>
          </fieldset>
          <fieldset id="m7InsertFieldset" class="m7-editor">
            <legend>Insert point / 포인트 추가</legend>
            <div class="m7-fields">
              <label>Lane<select id="m7InsertLane"></select></label>
              <label>Point ID<input id="m7InsertPointId" value="AP-UI-NEW"></label>
              <label>Beat<input id="m7InsertBeat" type="number" min="0" step="0.01" value="0"></label>
              <label>Value<input id="m7InsertValue" type="number" step="0.01" value="0"></label>
              <label>Interpolation<select id="m7InsertInterpolation"><option value="linear">linear</option><option value="hold">hold</option></select></label>
            </div>
            <button id="m7InsertPoint" class="secondary" type="button">Preview insert / 추가 미리보기</button>
          </fieldset>
        </div>
      </div>`;
    if (anchor && anchor.id === "m6PrecisionCard") anchor.insertAdjacentElement("afterend", card);
    else anchor.insertAdjacentElement("afterend", card);
    automation.root = card;
    el("m7PreviewPointChanges").addEventListener("click", previewSelectedChanges);
    el("m7DeletePoint").addEventListener("click", previewDelete);
    el("m7InsertPoint").addEventListener("click", previewInsert);
  }

  function displayLanes() {
    if (!automation.view) return [];
    return automation.view.preview ? automation.view.preview.lanes : automation.view.lanes;
  }

  function acceptedLanes() {
    return automation.view ? automation.view.lanes || [] : [];
  }

  function findLane(lanes, laneId) {
    return (lanes || []).find((lane) => lane.lane_id === laneId) || null;
  }

  function findPoint(lanes, key) {
    if (!key) return null;
    const [laneId, pointId] = key.split("::");
    const lane = findLane(lanes, laneId);
    if (!lane) return null;
    const point = (lane.points || []).find((item) => item.point_id === pointId) || null;
    return point ? { lane, point } : null;
  }

  function selectedDisplay() {
    return findPoint(displayLanes(), automation.selectedKey);
  }

  function selectedAccepted() {
    return findPoint(acceptedLanes(), automation.selectedKey);
  }

  function locksFor(laneId, pointId) {
    if (!automation.view) return [];
    return (automation.view.automation_locks || []).filter((lock) => {
      const selector = lock.selector || {};
      if (selector.lane_id !== laneId) return false;
      if (selector.point_id !== undefined && selector.point_id !== null && selector.point_id !== pointId) return false;
      return true;
    });
  }

  function renderSelected() {
    const selected = selectedDisplay();
    const fieldset = el("m7SelectedFieldset");
    const pending = Boolean(automation.view && automation.view.preview);
    if (!selected) {
      fieldset.disabled = true;
      el("m7SelectedPoint").textContent = "—";
      el("m7SelectedParameter").textContent = "—";
      el("m7SelectedLocks").textContent = "";
      return;
    }
    const { lane, point } = selected;
    fieldset.disabled = pending;
    el("m7SelectedPoint").textContent = `${point.point_id} · ${lane.lane_id}`;
    el("m7SelectedParameter").textContent = `${lane.target.parameter_id} · ${lane.target.scope}${lane.target.owner_id ? `:${lane.target.owner_id}` : ""} · ${lane.target.unit} [${lane.target.minimum}, ${lane.target.maximum}]`;
    el("m7PointBeat").value = String(point.beat);
    el("m7PointValue").value = String(point.value);
    el("m7PointValue").min = String(lane.target.minimum);
    el("m7PointValue").max = String(lane.target.maximum);
    el("m7PointInterpolation").value = point.interpolation;
    const lockRoot = el("m7SelectedLocks");
    lockRoot.textContent = "";
    locksFor(lane.lane_id, point.point_id).forEach((lock) => {
      const badge = document.createElement("span");
      badge.className = `m7-lock-badge ${String(lock.strength).toLowerCase()}`;
      badge.textContent = `${lock.strength === "HARD" ? "🔒" : "◇"} ${lock.selector.property}`;
      badge.dataset.lockId = lock.lock_id;
      badge.dataset.lockProperty = lock.selector.property;
      badge.title = `${lock.lock_id}: ${lock.reason}`;
      lockRoot.appendChild(badge);
    });
  }

  function lanePointButton(lane, point, pending) {
    const total = Math.max(Number(automation.view.timing.total_beats), 1);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `m7-point ${pending ? "preview" : "accepted"}${pointKey(lane.lane_id, point.point_id) === automation.selectedKey ? " selected" : ""}`;
    button.dataset.laneId = lane.lane_id;
    button.dataset.pointId = point.point_id;
    button.dataset.parameterId = lane.target.parameter_id;
    button.dataset.beat = String(point.beat);
    button.dataset.value = String(point.value);
    button.style.left = `${Math.max(0, Math.min(100, (Number(point.beat) / total) * 100))}%`;
    const span = Number(lane.target.maximum) - Number(lane.target.minimum);
    const normalized = span > 0 ? (Number(point.value) - Number(lane.target.minimum)) / span : 0.5;
    button.style.bottom = `${Math.max(0, Math.min(100, normalized * 100))}%`;
    button.title = `${point.point_id} | beat ${point.beat} | value ${point.value} ${lane.target.unit} | ${point.interpolation}`;
    button.setAttribute("aria-label", button.title);
    button.addEventListener("click", () => {
      automation.selectedKey = pointKey(lane.lane_id, point.point_id);
      render();
    });
    return button;
  }

  function render() {
    const view = automation.view;
    const available = Boolean(view && view.automation_editing_available);
    el("m7AutomationWorkspace").hidden = !available;
    el("m7AutomationUnavailable").hidden = available;
    const availability = el("m7AutomationAvailability");
    if (!view) {
      availability.textContent = "NO PROJECT";
      availability.className = "status-pill neutral";
      return;
    }
    if (!available) {
      availability.textContent = "NO CANONICAL AUTOMATION";
      availability.className = "status-pill neutral";
      el("m7AutomationUnavailable").textContent = "This accepted revision has no canonical materials.automation. MUSICA will not reverse-infer lanes from semantics, Music IR, renderer or DAW state.";
      return;
    }

    availability.textContent = "AUTOMATION · READY";
    availability.className = "status-pill accepted";
    el("m7AutomationSource").textContent = `${view.project_id} · ${view.branch}@${view.revision_id} · blueprint:${view.blueprint_sha256.slice(0, 10)}… · automation:${view.automation_material_sha256.slice(0, 10)}…`;
    const pending = Boolean(view.preview);
    const badge = el("m7AutomationPreviewBadge");
    badge.textContent = pending ? "PREVIEW AUTOMATION · NOT ACCEPTED" : "ACCEPTED AUTOMATION";
    badge.className = pending ? "status-pill preview" : "status-pill accepted";
    el("m7InsertFieldset").disabled = pending;

    const laneSelect = el("m7InsertLane");
    const previousLane = laneSelect.value;
    laneSelect.textContent = "";
    acceptedLanes().forEach((lane) => {
      const option = document.createElement("option");
      option.value = lane.lane_id;
      option.textContent = `${lane.lane_id} · ${lane.target.parameter_id}`;
      laneSelect.appendChild(option);
    });
    if ([...laneSelect.options].some((option) => option.value === previousLane)) laneSelect.value = previousLane;

    const root = el("m7AutomationLanes");
    root.textContent = "";
    displayLanes().forEach((lane) => {
      const section = document.createElement("section");
      section.className = "m7-lane";
      section.dataset.laneId = lane.lane_id;
      section.dataset.parameterId = lane.target.parameter_id;
      const heading = document.createElement("div");
      heading.className = "m7-lane-heading";
      heading.innerHTML = `<strong></strong><span class="mono muted"></span>`;
      heading.querySelector("strong").textContent = lane.lane_id;
      heading.querySelector("span").textContent = `${lane.target.parameter_id} · ${lane.target.scope}${lane.target.owner_id ? `:${lane.target.owner_id}` : ""} · ${lane.target.unit}`;
      const plot = document.createElement("div");
      plot.className = "m7-lane-plot";
      plot.dataset.laneId = lane.lane_id;
      (lane.points || []).forEach((point) => plot.appendChild(lanePointButton(lane, point, pending)));
      const table = document.createElement("table");
      table.className = "m7-point-table";
      table.innerHTML = "<thead><tr><th>point_id</th><th>beat</th><th>value</th><th>curve</th></tr></thead><tbody></tbody>";
      const tbody = table.querySelector("tbody");
      (lane.points || []).forEach((point) => {
        const row = document.createElement("tr");
        row.dataset.laneId = lane.lane_id;
        row.dataset.pointId = point.point_id;
        row.tabIndex = 0;
        [point.point_id, point.beat, point.value, point.interpolation].forEach((value) => {
          const cell = document.createElement("td");
          cell.textContent = String(value);
          row.appendChild(cell);
        });
        const select = () => {
          automation.selectedKey = pointKey(lane.lane_id, point.point_id);
          render();
        };
        row.addEventListener("click", select);
        row.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            select();
          }
        });
        tbody.appendChild(row);
      });
      section.append(heading, plot, table);
      root.appendChild(section);
    });
    renderSelected();
  }

  function candidateFor(operations, reason) {
    const view = automation.view;
    automation.requestCounter += 1;
    return {
      candidate_version: "0",
      candidate_id: `AEC-UI-${Date.now()}-${automation.requestCounter}`,
      authority_target: "blueprint_automation_material",
      source: {
        project_id: view.project_id,
        revision_id: view.revision_id,
        blueprint_sha256: view.blueprint_sha256,
        automation_material_sha256: view.automation_material_sha256,
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
      item.lane_id ? `lane ${item.lane_id}` : null,
      item.point_id ? `point ${item.point_id}` : null,
      item.rule_id ? `rule ${item.rule_id}` : null,
    ].filter(Boolean).join(" · ");
    return `${context}: ${item.reason}`;
  }

  async function sendPreview(operations, reason) {
    if (!automation.sessionId || !automation.view) return;
    clearStatus();
    try {
      const candidate = candidateFor(operations, reason);
      automation.lastSubmittedCandidate = candidate;
      const data = await automationFetch(`/v0/sessions/${encodeURIComponent(automation.sessionId)}/preview/automation`, {
        method: "POST",
        body: { candidate },
      });
      automation.lastAuthorityResult = data.authority_result || null;
      automation.view = data.automation_view;
      if (!data.preview_installed) {
        const conflicts = (data.authority_result && data.authority_result.conflicts) || [];
        status(conflicts.map(conflictText).join(" | ") || "Automation edit blocked by trusted authority.", "error");
      } else {
        status("Automation Preview ready. Accepted revision is unchanged. Audible automation is not validated in M7-R2.", "success");
        const refresh = el("refreshButton");
        if (refresh) refresh.click();
      }
      render();
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  function previewSelectedChanges() {
    const original = selectedAccepted();
    if (!original) return status("Select an accepted automation point first.", "error");
    const target = { lane_id: original.lane.lane_id, point_id: original.point.point_id };
    const operations = [];
    const beat = Number(el("m7PointBeat").value);
    const value = Number(el("m7PointValue").value);
    const interpolation = el("m7PointInterpolation").value;
    if (beat !== Number(original.point.beat)) operations.push({ operation_id: "UI-AUTO-MOVE", op: "MOVE_POINT", target, beat });
    if (value !== Number(original.point.value)) operations.push({ operation_id: "UI-AUTO-VALUE", op: "SET_VALUE", target, value });
    if (interpolation !== original.point.interpolation) operations.push({ operation_id: "UI-AUTO-INTERP", op: "SET_INTERPOLATION", target, interpolation });
    if (!operations.length) return status("No automation properties changed.", "info");
    sendPreview(operations, `Browser Studio automation edit for ${original.point.point_id}.`);
  }

  function previewDelete() {
    const original = selectedAccepted();
    if (!original) return status("Select an accepted automation point first.", "error");
    sendPreview(
      [{ operation_id: "UI-AUTO-DELETE", op: "DELETE_POINT", target: { lane_id: original.lane.lane_id, point_id: original.point.point_id } }],
      `Browser Studio delete automation point ${original.point.point_id}.`,
    );
  }

  function previewInsert() {
    if (!automation.view || !automation.view.automation_editing_available) return;
    const laneId = el("m7InsertLane").value;
    const pointId = el("m7InsertPointId").value.trim();
    if (!laneId || !pointId) return status("Lane and Point ID are required.", "error");
    const point = {
      point_id: pointId,
      beat: Number(el("m7InsertBeat").value),
      value: Number(el("m7InsertValue").value),
      interpolation: el("m7InsertInterpolation").value,
    };
    sendPreview(
      [{ operation_id: "UI-AUTO-INSERT", op: "INSERT_POINT", target: { lane_id: laneId }, point }],
      `Browser Studio insert automation point ${pointId}.`,
    );
  }

  async function refreshAutomationView(quiet = false) {
    if (!automation.sessionId || !automation.root) return;
    try {
      automation.view = await automationFetch(`/v0/sessions/${encodeURIComponent(automation.sessionId)}/automation`);
      if (automation.selectedKey && !findPoint(displayLanes(), automation.selectedKey)) automation.selectedKey = null;
      render();
      if (!quiet) status("Automation view refreshed.", "success");
    } catch (error) {
      automation.view = null;
      render();
      if (!quiet) status(error.message || String(error), "error");
    }
  }

  injectSurface();
  window.MUSICA_AUTOMATION = {
    refresh: refreshAutomationView,
    state: automation,
  };
})();
