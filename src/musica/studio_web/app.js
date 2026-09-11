(() => {
  "use strict";

  const state = {
    sessionId: null,
    session: null,
    preview: null,
    activeAxis: "tension",
    activeTab: "direct",
  };

  const $ = (id) => document.getElementById(id);
  const tabs = [...document.querySelectorAll(".depth-tab")];
  const panels = [...document.querySelectorAll(".panel")];
  const sliders = [...document.querySelectorAll('input[type="range"][data-axis]')];

  function showNotice(message, kind = "info") {
    const notice = $("notice");
    notice.textContent = message;
    notice.className = `notice ${kind === "error" ? "error" : kind === "success" ? "success" : ""}`.trim();
    notice.hidden = false;
  }

  function clearNotice() {
    $("notice").hidden = true;
    $("notice").textContent = "";
  }

  function humanError(error) {
    if (error && typeof error === "object" && error.message) return error.message;
    return String(error || "Unknown Studio error");
  }

  async function api(path, options = {}) {
    const init = { method: options.method || "GET", headers: { Accept: "application/json" } };
    if (options.body !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(options.body);
    }
    const response = await fetch(path, init);
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : null;
    if (!response.ok || !payload || payload.ok === false) {
      const detail = payload && payload.error ? payload.error : { message: `HTTP ${response.status}` };
      const err = new Error(detail.message || `HTTP ${response.status}`);
      err.code = detail.code || "http_error";
      err.retryable = Boolean(detail.retryable);
      throw err;
    }
    return payload.data;
  }

  function setBusy(button, busy, busyLabel = "Working…") {
    if (!button) return;
    if (busy) {
      button.dataset.originalLabel = button.textContent;
      button.textContent = busyLabel;
      button.disabled = true;
    } else {
      button.textContent = button.dataset.originalLabel || button.textContent;
      button.disabled = false;
    }
  }

  function switchTab(name) {
    state.activeTab = name;
    tabs.forEach((tab) => {
      const active = tab.dataset.tab === name;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    panels.forEach((panel) => {
      const active = panel.dataset.panel === name;
      panel.hidden = !active;
      panel.classList.toggle("active", active);
    });
  }

  function enableStudioDepths(enabled) {
    tabs.forEach((tab) => {
      if (tab.dataset.tab !== "direct") tab.disabled = !enabled;
    });
  }

  function setText(id, value) {
    const element = $(id);
    if (element) element.textContent = value == null ? "—" : String(value);
  }

  function formatValue(value) {
    if (value === null || value === undefined) return "null";
    if (typeof value === "string") return JSON.stringify(value);
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function clearChildren(element) {
    while (element.firstChild) element.removeChild(element.firstChild);
  }

  function buildLockList(container, locks) {
    clearChildren(container);
    if (!locks || locks.length === 0) {
      const span = document.createElement("span");
      span.className = "muted";
      span.textContent = "No HARD locks / HARD lock 없음";
      container.appendChild(span);
      return;
    }
    locks.forEach((lock) => {
      const item = document.createElement("div");
      item.className = "lock-item";
      const icon = document.createElement("span");
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = "🔒";
      const body = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = `${lock.lock_id} · ${lock.mode}`;
      const target = document.createElement("code");
      target.textContent = lock.target;
      body.append(title, target);
      item.append(icon, body);
      container.appendChild(item);
    });
  }

  function renderTimeline(session) {
    const timeline = $("sectionTimeline");
    clearChildren(timeline);
    timeline.classList.remove("empty");
    const sections = session.sections || [];
    if (!sections.length) {
      timeline.classList.add("empty");
      timeline.textContent = "No sections / 구간 없음";
      return;
    }
    const duration = Math.max(...sections.map((section) => Number(section.end) || 0), 1);
    sections.forEach((section) => {
      const segment = document.createElement("div");
      segment.className = "timeline-segment";
      segment.style.flexGrow = String(Math.max(Number(section.end) - Number(section.start), 0.1));
      segment.style.flexBasis = "0";
      segment.title = `${section.section_id}: ${section.start}s–${section.end}s`;
      const title = document.createElement("strong");
      title.textContent = section.name;
      const time = document.createElement("small");
      time.textContent = `${Number(section.start).toFixed(1)}–${Number(section.end).toFixed(1)}s`;
      segment.append(title, time);
      timeline.appendChild(segment);
    });
    setText("durationLabel", `${duration.toFixed(1)}s`);
  }

  function renderSectionsSelect(session) {
    const select = $("sectionSelect");
    const previous = select.value;
    clearChildren(select);
    (session.sections || []).forEach((section) => {
      const option = document.createElement("option");
      option.value = section.section_id;
      option.textContent = `${section.section_id} · ${section.name}`;
      select.appendChild(option);
    });
    if ([...select.options].some((option) => option.value === previous)) select.value = previous;
  }

  function renderSemanticState(session) {
    sliders.forEach((slider) => {
      const axis = slider.dataset.axis;
      const value = Number(session.semantic_state && session.semantic_state[axis]);
      if (Number.isFinite(value)) slider.value = String(value);
      const output = slider.parentElement.querySelector("output");
      output.textContent = Number(slider.value).toFixed(2);
      slider.parentElement.classList.toggle("active-axis", axis === state.activeAxis);
    });
    setText("activeAxisBadge", state.activeAxis.toUpperCase());
  }

  function renderBranches(session) {
    const select = $("branchSelect");
    clearChildren(select);
    const branches = session.branches || {};
    Object.keys(branches).sort().forEach((branch) => {
      const option = document.createElement("option");
      option.value = branch;
      option.textContent = `${branch}${branch === session.current_branch ? " · current" : ""}`;
      select.appendChild(option);
    });
    select.value = session.current_branch || "";
    setText("branchCount", String(Object.keys(branches).length));
  }

  function renderDiff(diff) {
    const container = $("diffList");
    clearChildren(container);
    const items = Array.isArray(diff) ? diff : [];
    setText("diffCount", String(items.length));
    if (!items.length) {
      const p = document.createElement("p");
      p.className = "muted";
      p.textContent = state.session && state.session.pending_preview
        ? `Preview reports ${state.session.pending_preview.diff_count} change(s); refresh preview details if needed.`
        : "No pending preview / 대기 중 preview 없음";
      container.appendChild(p);
      return;
    }
    items.forEach((change) => {
      const item = document.createElement("div");
      item.className = "diff-item";
      const path = document.createElement("code");
      path.textContent = `${String(change.op || "change").toUpperCase()} ${change.path || ""}`;
      const values = document.createElement("div");
      values.className = "diff-values";
      const before = document.createElement("span");
      before.textContent = formatValue(change.before);
      const arrow = document.createElement("span");
      arrow.textContent = "→";
      const after = document.createElement("span");
      after.textContent = formatValue(change.after);
      values.append(before, arrow, after);
      item.append(path, values);
      container.appendChild(item);
    });
  }

  function mediaUrl(kind) {
    if (!state.sessionId) return "";
    const file = kind === "audio" ? "audio.wav" : "preview.mid";
    return `/v0/sessions/${encodeURIComponent(state.sessionId)}/media/${file}?v=${Date.now()}`;
  }

  function renderAudio(session) {
    const player = $("audioPlayer");
    const pending = Boolean(session.pending_preview);
    const newUrl = mediaUrl("audio");
    if (newUrl && session.audio_available) {
      player.src = newUrl;
      player.hidden = false;
    } else {
      player.removeAttribute("src");
      player.load();
    }
    setText("audioLabel", pending ? "Preview audio / 미승인 미리듣기" : "Accepted audio / 승인 오디오");
    $("wavLink").href = newUrl || "#";
    $("midiLink").href = mediaUrl("midi") || "#";
  }

  function renderPreviewState(session) {
    const pending = session.pending_preview;
    const badge = $("authorityBadge");
    const projectBadge = $("projectStateBadge");
    if (pending) {
      badge.textContent = "PREVIEW";
      badge.className = "status-pill preview";
      projectBadge.textContent = "PREVIEW · NOT ACCEPTED";
      projectBadge.className = "status-pill preview";
      $("previewDecision").hidden = false;
      setText("previewSummary", `${pending.preview_id} · ${pending.diff_count} change(s) · parent ${pending.parent_revision_id}`);
    } else {
      badge.textContent = "ACCEPTED";
      badge.className = "status-pill accepted";
      projectBadge.textContent = "ACCEPTED";
      projectBadge.className = "status-pill accepted";
      $("previewDecision").hidden = true;
      state.preview = null;
      renderDiff([]);
    }

    const conflict = Boolean(pending);
    $("createBranchButton").disabled = conflict;
    $("checkoutButton").disabled = conflict;
    $("exportButton").disabled = conflict;
  }

  function renderSession(session) {
    state.session = session;
    state.sessionId = session.session_id;
    enableStudioDepths(true);
    $("activeProject").hidden = false;
    setText("projectTitle", session.project_slug || session.project_id || "MUSICA project");
    setText("projectMeta", `${session.project_id} · ${session.current_branch}@${session.head_revision_id}`);
    setText("sideBranch", session.current_branch);
    setText("sideRevision", session.head_revision_id);
    setText("sideIntegrity", session.integrity_status);
    renderSemanticState(session);
    renderTimeline(session);
    renderSectionsSelect(session);
    renderBranches(session);
    buildLockList($("shapeLocks"), session.hard_locks || []);
    buildLockList($("inspectLocks"), session.hard_locks || []);
    renderPreviewState(session);
    renderAudio(session);
    $("jsonView").textContent = JSON.stringify(session, null, 2);
  }

  async function fetchPendingPreviewDetail() {
    if (!state.sessionId || !state.session || !state.session.pending_preview) return;
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/preview`);
      state.preview = data;
      renderDiff(data.diff || []);
    } catch (error) {
      renderDiff([]);
    }
  }

  async function refreshSession({ quiet = false } = {}) {
    if (!state.sessionId) return;
    try {
      const session = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}`);
      renderSession(session);
      await fetchPendingPreviewDetail();
      if (!quiet) showNotice("Studio state refreshed / Studio 상태를 새로고침했습니다.", "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    }
  }

  async function loadHistory() {
    if (!state.sessionId) return;
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/history`);
      const container = $("historyList");
      clearChildren(container);
      const revisions = data.revisions || [];
      if (!revisions.length) {
        const p = document.createElement("p");
        p.className = "muted";
        p.textContent = "No accepted revisions / 승인 리비전 없음";
        container.appendChild(p);
        return;
      }
      revisions.slice().reverse().forEach((revision) => {
        const item = document.createElement("div");
        item.className = "history-item";
        const title = document.createElement("strong");
        title.textContent = revision.revision_id;
        const meta = document.createElement("span");
        meta.textContent = `#${revision.logical_sequence} · ${revision.actor} · parent ${revision.parent_revision_id || "ROOT"}`;
        const reason = document.createElement("span");
        reason.textContent = revision.reason;
        item.append(title, meta, reason);
        container.appendChild(item);
      });
    } catch (error) {
      showNotice(humanError(error), "error");
    }
  }

  function capturePreview(data) {
    state.preview = data;
    renderSession(data.session);
    renderDiff(data.diff || []);
    switchTab("inspect");
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      if (!tab.disabled) switchTab(tab.dataset.tab);
    });
  });

  sliders.forEach((slider) => {
    const update = () => {
      state.activeAxis = slider.dataset.axis;
      const output = slider.parentElement.querySelector("output");
      output.textContent = Number(slider.value).toFixed(2);
      sliders.forEach((other) => other.parentElement.classList.toggle("active-axis", other === slider));
      setText("activeAxisBadge", state.activeAxis.toUpperCase());
    };
    slider.addEventListener("input", update);
    slider.addEventListener("change", update);
  });

  $("scopeKind").addEventListener("change", () => {
    $("sectionSelect").disabled = $("scopeKind").value !== "section_id";
  });

  $("createForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearNotice();
    const button = $("generateButton");
    setBusy(button, true, "Generating… / 생성 중…");
    try {
      const style = $("styleProfile").value || null;
      const data = await api("/v0/projects/create", {
        method: "POST",
        body: {
          project_slug: $("projectSlug").value.trim(),
          user_text: $("createPrompt").value.trim(),
          provider_mode: $("providerMode").value,
          locale: "en-US",
          duration_seconds: Number($("durationSeconds").value),
          use_case: $("useCase").value,
          style_profile: style,
          preserve_on_edit: [],
          exclusions: [],
        },
      });
      state.preview = null;
      renderSession(data.session);
      await loadHistory();
      showNotice("Project created and accepted / 프로젝트가 생성되어 첫 버전이 승인되었습니다.", "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    } finally {
      setBusy(button, false);
    }
  });

  $("openForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearNotice();
    const button = event.submitter;
    setBusy(button, true, "Opening…");
    try {
      const data = await api("/v0/projects/open", {
        method: "POST",
        body: {
          project_slug: $("openProjectSlug").value.trim(),
          provider_mode: $("providerMode").value,
        },
      });
      state.preview = null;
      renderSession(data.session);
      await loadHistory();
      showNotice("Project opened / 프로젝트를 열었습니다.", "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    } finally {
      setBusy(button, false);
    }
  });

  $("refineForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!state.sessionId) return;
    const prompt = $("refinePrompt").value.trim();
    if (!prompt) return showNotice("Enter a refinement instruction / 수정 지시를 입력하세요.", "error");
    const button = event.submitter;
    setBusy(button, true, "Previewing…");
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/preview/direct`, {
        method: "POST",
        body: { user_text: prompt, locale: "en-US" },
      });
      capturePreview(data);
      showNotice("AI Director preview created. Canonical revision is unchanged / AI preview가 생성되었으며 공식 리비전은 변경되지 않았습니다.", "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    } finally {
      setBusy(button, false);
    }
  });

  $("previewSemanticButton").addEventListener("click", async () => {
    if (!state.sessionId) return;
    const slider = sliders.find((item) => item.dataset.axis === state.activeAxis);
    const scopeKind = $("scopeKind").value;
    const body = {
      name: state.activeAxis,
      operation: "set",
      value: Number(slider.value),
      scope_kind: scopeKind,
      section_id: scopeKind === "section_id" ? $("sectionSelect").value : null,
    };
    const button = $("previewSemanticButton");
    setBusy(button, true, "Rendering preview…");
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/preview/semantic`, { method: "POST", body });
      capturePreview(data);
      showNotice(`${state.activeAxis} preview ready. Accepted state is unchanged / 미리듣기가 준비되었고 승인 상태는 그대로입니다.`, "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    } finally {
      setBusy(button, false);
    }
  });

  $("acceptButton").addEventListener("click", async () => {
    if (!state.sessionId) return;
    const button = $("acceptButton");
    setBusy(button, true, "Accepting…");
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/preview/accept`, { method: "POST", body: {} });
      state.preview = null;
      renderSession(data.session);
      await loadHistory();
      showNotice(`Version accepted: ${data.revision_record.revision_id} / 새 버전을 승인했습니다.`, "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    } finally {
      setBusy(button, false);
    }
  });

  $("discardButton").addEventListener("click", async () => {
    if (!state.sessionId) return;
    const button = $("discardButton");
    setBusy(button, true, "Discarding…");
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/preview/discard`, { method: "POST", body: {} });
      state.preview = null;
      renderSession(data.session);
      showNotice("Preview discarded. Accepted revision stayed unchanged / preview를 폐기했고 승인 리비전은 유지됩니다.", "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    } finally {
      setBusy(button, false);
    }
  });

  $("createBranchButton").addEventListener("click", async () => {
    if (!state.sessionId) return;
    const name = $("newBranchName").value.trim();
    if (!name) return showNotice("Enter a branch name / 브랜치 이름을 입력하세요.", "error");
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/branches`, {
        method: "POST",
        body: { branch_name: name, checkout: true },
      });
      renderSession(data.session);
      await loadHistory();
      showNotice(`Branch created and checked out: ${name} / 브랜치를 생성하고 전환했습니다.`, "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    }
  });

  $("checkoutButton").addEventListener("click", async () => {
    if (!state.sessionId) return;
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/checkout`, {
        method: "POST",
        body: { branch_name: $("branchSelect").value },
      });
      renderSession(data.session);
      await loadHistory();
      showNotice(`Checked out ${data.session.current_branch} / 브랜치를 전환했습니다.`, "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    }
  });

  $("exportButton").addEventListener("click", async () => {
    if (!state.sessionId) return;
    try {
      const data = await api(`/v0/sessions/${encodeURIComponent(state.sessionId)}/export`, { method: "POST", body: {} });
      setText("exportResult", `${data.export_relpath} · ${data.size_bytes} bytes · sha256:${data.sha256.slice(0, 16)}…`);
      showNotice("Canonical project exported inside the Studio workspace / 공식 프로젝트를 Studio workspace에 내보냈습니다.", "success");
    } catch (error) {
      showNotice(humanError(error), "error");
    }
  });

  $("refreshButton").addEventListener("click", () => refreshSession());
  $("historyRefreshButton").addEventListener("click", () => loadHistory());

  $("copyJsonButton").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("jsonView").textContent);
      showNotice("Session JSON copied / 세션 JSON을 복사했습니다.", "success");
    } catch (error) {
      showNotice("Clipboard access is unavailable. Select the JSON manually / 클립보드 접근이 불가합니다.", "error");
    }
  });

  async function boot() {
    try {
      const response = await fetch("/v0/health", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      $("connectionBadge").textContent = "LOCAL · READY";
      $("connectionBadge").className = "status-pill accepted";
    } catch (error) {
      $("connectionBadge").textContent = "LOCAL · OFFLINE";
      $("connectionBadge").className = "status-pill preview";
      showNotice("Studio service is not reachable / Studio service에 연결할 수 없습니다.", "error");
    }
    renderDiff([]);
    switchTab("direct");
  }

  boot();
})();
