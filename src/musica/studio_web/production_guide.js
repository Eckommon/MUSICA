(() => {
  "use strict";

  // PROD-E2E-R1B-G0: a read-only, user-operated guide for existing trusted Studio surfaces.
  // No creative revision mutations and no automated Accept/Discard.
  const el = (id) => document.getElementById(id);
  const steps = [
    ["Project / 프로젝트", "Create or reopen an accepted local project.", "direct", "createForm"],
    ["WAV asset / 파일 가져오기", "Choose an immutable PCM WAV resource; import never creates a clip.", "inspect", "r3WavFile"],
    ["Arrangement / 편곡", "Preview a track, Accept it, then Preview a clip and Accept separately.", "inspect", "r3AddTrack"],
    ["Mixer / 믹서", "Adjust native track gain and pan through separate trusted Preview/Accept.", "inspect", "r3TrackList"],
    ["Routing / 라우팅", "Optional: inspect supported routing topology and Preview any change.", "inspect", "mramRoutingCard"],
    ["Automation / 자동화", "Optional: use only supported canonical lanes and accepted changes.", "inspect", "m7AutomationCard"],
    ["Delivery / 결과 출력", "Export .musica and download only the accepted-derived WAV.", "inspect", "exportButton"]
  ];
  let downloading = false;

  function projectState() {
    const native = window.MUSICA_NATIVE_AUDIO && window.MUSICA_NATIVE_AUDIO.state;
    const view = native && native.view;
    const tracks = view && Array.isArray(view.tracks) ? view.tracks : [];
    const clips = tracks.reduce((sum, track) => sum + (Array.isArray(track.clips) ? track.clips.length : 0), 0);
    const genericPending = Boolean(el("authorityBadge") && el("authorityBadge").textContent.trim() === "PREVIEW");
    const pending = Boolean(view && view.preview) || genericPending;
    const audition = view && view.accepted_audition;
    return {
      sessionId: native && native.sessionId,
      view,
      trackCount: tracks.length,
      clipCount: clips,
      pending,
      audioReady: Boolean(audition && audition.available && audition.wav_sha256),
      audition
    };
  }

  function message(value, kind = "info") {
    const target = el("r1bGuideStatus");
    if (!target) return;
    target.textContent = value;
    target.className = "r1b-guide-status " + kind;
  }

  function inject() {
    const panel = el("panel-inspect");
    if (!panel || el("r1bGuide")) return;
    const card = document.createElement("section");
    card.id = "r1bGuide";
    card.className = "card r1b-guide";
    card.setAttribute("aria-label", "One-song production guide / 한 곡 제작 안내");
    const top = document.createElement("div");
    top.className = "card-heading";
    const name = document.createElement("div");
    name.innerHTML = '<span class="eyebrow">PROD-E2E-R1B · OPERATOR JOURNEY</span><h2>One-song production guide / 한 곡 제작</h2>';
    const badge = document.createElement("span");
    badge.id = "r1bGuideBadge";
    badge.className = "status-pill neutral";
    badge.textContent = "NO PROJECT";
    top.append(name, badge);
    const description = document.createElement("p");
    description.className = "muted small";
    description.textContent = "This guide navigates verified Studio controls only. Import is not Accept; Preview is not accepted audio. No automatic creative decisions.";
    const stages = document.createElement("ol");
    stages.id = "r1bGuideSteps";
    stages.className = "r1b-guide-steps";
    steps.forEach(([title, instruction, tab, target], index) => {
      const item = document.createElement("li");
      item.className = "r1b-guide-step";
      const copy = document.createElement("div");
      const heading = document.createElement("strong");
      heading.textContent = title;
      const detail = document.createElement("p");
      detail.className = "muted small";
      detail.textContent = instruction;
      const state = document.createElement("span");
      state.id = "r1bStepState" + index;
      state.className = "r1b-step-state";
      state.textContent = "PENDING";
      copy.append(heading, detail, state);
      const button = document.createElement("button");
      button.type = "button";
      button.id = "r1bGo" + index;
      button.className = "secondary";
      button.textContent = "Open / 열기";
      button.addEventListener("click", () => navigate(tab, target));
      item.append(copy, button);
      stages.appendChild(item);
    });
    const delivery = document.createElement("div");
    delivery.className = "r1b-guide-delivery";
    const download = document.createElement("button");
    download.type = "button";
    download.id = "r1bDownloadWav";
    download.className = "primary";
    download.textContent = "Download accepted WAV / 승인 WAV 다운로드";
    download.addEventListener("click", downloadAcceptedWav);
    const summary = document.createElement("p");
    summary.id = "r1bDeliverySummary";
    summary.className = "muted small mono";
    delivery.append(download, summary);
    const status = document.createElement("p");
    status.id = "r1bGuideStatus";
    status.className = "r1b-guide-status info";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    card.append(top, description, stages, delivery, status);
    panel.prepend(card); // Main operator entry must precede all optional advanced panels.
  }

  function navigate(tab, targetId) {
    const tabButton = document.querySelector('.depth-tab[data-tab="' + tab + '"]');
    if (!tabButton || tabButton.disabled) {
      message("Create or open a project to enable this Studio section.", "error");
      return;
    }
    tabButton.click();
    const target = el(targetId);
    if (!target || target.closest("[hidden]")) {
      message("This capability is unavailable for the current accepted project. No fallback was applied.", "error");
      return;
    }
    target.scrollIntoView({ block: "center", behavior: "instant" });
    if (target.matches("input,button,select")) target.focus({ preventScroll: true });
    message("Use the existing trusted controls. Review Preview and click the correct explicit Accept yourself.");
  }

  function render() {
    inject();
    const p = projectState();
    const statusTexts = [
      p.sessionId && p.view ? "ACCEPTED SESSION" : "CREATE / OPEN",
      p.clipCount ? "SOURCE USED BY ACCEPTED CLIP" : "MANUAL ASSET IMPORT",
      p.trackCount >= 2 && p.clipCount >= 2 ? String(p.trackCount) + " TRACKS / " + String(p.clipCount) + " CLIPS ACCEPTED" : p.clipCount ? "ACCEPTED CLIP" : p.trackCount ? "TRACK ACCEPTED · CLIP NEEDED" : "TRACK / CLIP NEEDED",
      p.trackCount ? "AVAILABLE · MANUAL EDIT" : "NEEDS TRACK",
      "OPTIONAL · TOPOLOGY-GATED",
      "OPTIONAL · LANE-GATED",
      p.pending ? "PREVIEW · DELIVERY BLOCKED" : p.audioReady ? "ACCEPTED AUDIO READY" : "NO ACCEPTED MIX"
    ];
    statusTexts.forEach((value, index) => {
      const badge = el("r1bStepState" + index);
      if (badge) badge.textContent = value;
      const button = el("r1bGo" + index);
      if (button) button.disabled = index !== 0 && !p.sessionId;
    });
    const available = Boolean(p.sessionId && p.view && p.audioReady && !p.pending);
    const download = el("r1bDownloadWav");
    if (download) download.disabled = !available || downloading;
    const badge = el("r1bGuideBadge");
    if (badge) {
      badge.textContent = p.pending ? "PREVIEW · NOT ACCEPTED" : p.audioReady ? "ACCEPTED MIX" : p.sessionId ? "IN PROGRESS" : "NO PROJECT";
      badge.className = "status-pill " + (p.pending ? "preview" : p.audioReady ? "accepted" : "neutral");
    }
    const summary = el("r1bDeliverySummary");
    if (summary) {
      summary.textContent = p.pending
        ? "Pending Preview: resolve with the owning surface's Accept/Discard first."
        : p.audioReady
          ? "Accepted-derived, noncanonical WAV SHA-256: " + p.audition.wav_sha256 + " · " + p.audition.mix_sample_rate_hz + " Hz"
          : "No accepted native mix. Add an accepted clip first.";
    }
  }

  async function studioGet(path) {
    const response = await fetch(path, { headers: { Accept: "application/json" } });
    const payload = await response.json();
    if (!response.ok || !payload || payload.ok === false || !payload.data) {
      throw new Error(payload && payload.error && payload.error.message || "Studio read failed");
    }
    return payload.data;
  }

  async function downloadAcceptedWav() {
    if (downloading) return;
    const before = projectState();
    if (!before.sessionId || !before.view || !before.audioReady || before.pending) {
      message("No accepted WAV delivery while a Preview is pending or no mix exists.", "error");
      return;
    }
    downloading = true;
    render();
    try {
      const base = "/v0/sessions/" + encodeURIComponent(before.sessionId);
      // Fresh server reads: do not trust a stale DOM badge or past browser state.
      const session = await studioGet(base);
      const audio = await studioGet(base + "/audio");
      const valid = !session.pending_preview && !audio.preview
        && session.head_revision_id === audio.revision_id
        && session.head_revision_id === before.view.revision_id
        && audio.accepted_audition && audio.accepted_audition.available
        && audio.accepted_audition.wav_sha256 === before.audition.wav_sha256;
      if (!valid) {
        throw new Error("Accepted source changed or a Preview is pending. Refresh and review before delivery.");
      }
      const hash = audio.accepted_audition.wav_sha256;
      const link = document.createElement("a");
      link.href = base + "/audio/accepted.wav?v=" + encodeURIComponent(hash);
      link.download = "musica-accepted-" + hash.slice(0, 12) + ".wav";
      document.body.appendChild(link);
      link.click();
      link.remove();
      message("Requested accepted-derived WAV (" + hash.slice(0, 16) + "…). This is not a mastered commercial release.", "success");
    } catch (error) {
      message(error.message || String(error), "error");
    } finally {
      downloading = false;
      render();
    }
  }

  function init() {
    inject();
    render();
    const audioCard = el("r3AudioCard");
    if (audioCard) new MutationObserver(render).observe(audioCard, { childList: true, subtree: true, attributes: true, attributeFilter: ["hidden"] });
    const generic = el("authorityBadge");
    if (generic) new MutationObserver(render).observe(generic, { childList: true, characterData: true, subtree: true });
    window.MUSICA_PRODUCTION_GUIDE = { refresh: render, status: projectState };
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();