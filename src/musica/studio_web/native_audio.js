(() => {
  "use strict";

  const originalFetch = window.fetch.bind(window);
  const nativeAudio = {
    sessionId: null,
    view: null,
    requestCounter: 0,
    lastSubmittedCandidate: null,
    lastAuthorityResult: null,
    stagedTransfer: null,
  };
  const el = (id) => document.getElementById(id);

  function status(message, kind = "info") {
    const target = el("r3AudioStatus");
    if (!target) return;
    target.hidden = false;
    target.className = `r3-audio-status ${kind}`;
    target.textContent = message;
  }

  function clearStatus() {
    const target = el("r3AudioStatus");
    if (!target) return;
    target.hidden = true;
    target.textContent = "";
  }

  async function audioFetch(path, options = {}) {
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
    const changed = nativeAudio.sessionId !== session.session_id;
    nativeAudio.sessionId = session.session_id;
    if (changed || session.head_revision_id) queueMicrotask(() => refreshAudioView(true));
  }

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string" ? input : input && input.url ? input.url : "";
      if (!url.includes("/audio")) {
        const clone = response.clone();
        const contentType = clone.headers.get("content-type") || "";
        if (contentType.includes("application/json")) observeSessionPayload(await clone.json());
      }
    } catch (_error) {
      // Browser observation is non-authoritative and must never break the core request.
    }
    return response;
  };

  function injectSurface() {
    const panel = el("panel-inspect");
    if (!panel || el("r3AudioCard")) return;
    const anchor = el("m7AutomationCard") || el("m6PrecisionCard") || panel.querySelector(".panel-heading");
    const card = document.createElement("section");
    card.id = "r3AudioCard";
    card.className = "card r3-audio-card";
    card.innerHTML = `
      <div class="card-heading r3-audio-heading">
        <div><span class="eyebrow">ATCM-R3 · NATIVE AUDIO</span><h2>Arrangement + Mixer / 오디오 편곡 + 믹서</h2></div>
        <span id="r3AudioAuthorityBadge" class="status-pill neutral">NO PROJECT</span>
      </div>
      <p class="muted small">Accepted Blueprint revision is authority. Browser controls and WAV playback are derived. Every edit remains PREVIEW until native-audio Accept revalidates R1/R2 authority.</p>
      <div id="r3AudioStatus" class="r3-audio-status" role="status" aria-live="polite" hidden></div>
      <div id="r3AudioImport" class="r3-create-grid" hidden>
        <fieldset>
          <legend>Import WAV / WAV 가져오기</legend>
          <label>Local PCM WAV / 로컬 PCM WAV
            <input id="r3WavFile" type="file" accept=".wav,audio/wav">
          </label>
          <button id="r3ImportWav" class="secondary" type="button">Import as asset only / 오디오 자산 가져오기</button>
          <button id="r3CancelStagedWav" type="button" class="danger" hidden>Cancel staged WAV / 업로드 취소</button>
          <p class="muted small">Resource only; no accepted track/clip. Direct WAV ≤16 MiB; sliced 1 MiB staging up to 64 MiB. 3-minute mix/export remains unproven.</p>
          <p id="r3ImportedAsset" class="mono muted small" role="status" aria-live="polite"></p>
        </fieldset>
      </div>
      <div id="r3AudioUnavailable" class="r3-audio-unavailable">Open a project with accepted native-audio material.</div>
      <div id="r3AudioWorkspace" hidden>
        <div class="r3-audio-toolbar">
          <span id="r3AudioSource" class="mono muted">—</span>
          <div class="r3-audio-actions">
            <button id="r3Discard" class="danger" type="button" hidden>Discard native Preview</button>
            <button id="r3Accept" class="primary" type="button" hidden>Accept native Preview</button>
          </div>
        </div>
        <div class="r3-audition">
          <div><strong id="r3AuditionLabel">Accepted native mix</strong><div id="r3AuditionMeta" class="mono muted small">—</div></div>
          <audio id="r3AudioPlayer" controls preload="metadata"></audio>
        </div>
        <div id="r3TrackList" class="r3-track-list"></div>
        <div class="r3-create-grid">
          <fieldset>
            <legend>Add track / 트랙 추가</legend>
            <label>Track ID<input id="r3NewTrackId" value="AT-UI-NEW"></label>
            <label>Name<input id="r3NewTrackName" value="Audio Track"></label>
            <label>Order<input id="r3NewTrackOrder" type="number" min="0" step="1" value="0"></label>
            <button id="r3SuggestTrackId" class="secondary" type="button">Next unused track ID / 새 트랙 ID</button>
            <button id="r3AddTrack" class="secondary" type="button">Preview add track</button>
          </fieldset>
          <fieldset>
            <legend>Add clip / 클립 추가</legend>
            <label>Track<select id="r3ClipTrack"></select></label>
            <label>Clip ID<input id="r3NewClipId" value="AC-UI-NEW"></label>
            <label>Asset ID<input id="r3NewAssetId" placeholder="sha256:…"></label>
            <div class="r3-inline-fields">
              <label>Timeline<input id="r3NewTimeline" type="number" min="0" step="0.001" value="0"></label>
              <label>Source in<input id="r3NewSourceIn" type="number" min="0" step="0.001" value="0"></label>
              <label>Source out<input id="r3NewSourceOut" type="number" min="0.001" step="0.001" value="0.1"></label>
              <label>Gain dB<input id="r3NewClipGain" type="number" min="-60" max="12" step="0.1" value="0"></label>
            </div>
            <button id="r3SuggestClipId" class="secondary" type="button">Next unused clip ID / 새 클립 ID</button>
            <button id="r3AddClip" class="secondary" type="button">Preview add clip</button>
          </fieldset>
        </div>
      </div>`;
    if (anchor) anchor.insertAdjacentElement("afterend", card);
    else panel.appendChild(card);
    el("r3ImportWav").addEventListener("click", importWav);
    el("r3CancelStagedWav").addEventListener("click", () => {
      if (nativeAudio.stagedTransfer) {
        nativeAudio.stagedTransfer.cancelled = true;
        status("Cancelling WAV upload. Accepted Project is unchanged.", "info");
      }
    });
    el("r3AddTrack").addEventListener("click", previewAddTrack);
    el("r3SuggestTrackId").addEventListener("click", suggestTrackId);
    el("r3SuggestClipId").addEventListener("click", suggestClipId);
    el("r3AddClip").addEventListener("click", previewAddClip);
    el("r3Accept").addEventListener("click", acceptPreview);
    el("r3Discard").addEventListener("click", discardPreview);
  }

  async function stagedRequest(url, options) {
    const response = await originalFetch(url, options);
    const payload = await response.json();
    if (!response.ok || !payload || !payload.ok)
      throw new Error(payload?.error?.message || ("Staged WAV HTTP " + response.status));
    return payload.data;
  }

  async function importStagedWav(file) {
    if (!window.MUSICA_SHA256_FILE || !window.crypto?.subtle)
      throw new Error("Secure browser hashing is unavailable");
    const session = nativeAudio.sessionId;
    const base = "/v0/sessions/" + encodeURIComponent(session) + "/audio/stage";
    const upload = {session, id: null, cancelled: false};
    nativeAudio.stagedTransfer = upload;
    el("r3CancelStagedWav").hidden = false;
    let finished = false;
    try {
      // SHA-256 across 1MiB File slices; never materialize the full file.
      const sha256 = await window.MUSICA_SHA256_FILE.hashFileSlices(
        file,
        (done, total) => status("Hashing WAV " + Math.floor(done * 100 / total) + "% · NOT A CLIP"),
        () => upload.cancelled || nativeAudio.sessionId !== session
      );
      if (upload.cancelled || nativeAudio.sessionId !== session)
        throw new Error("WAV upload cancelled or Studio session changed");
      const start = await stagedRequest(base + "/start", {
        method: "POST",
        headers: {"Content-Type": "application/json", Accept: "application/json"},
        body: JSON.stringify({size_bytes: file.size, sha256})
      });
      if (!start.accepted_revision_unchanged || !/^[A-Za-z0-9_-]{43}$/.test(start.upload_id))
        throw new Error("Server rejected opaque upload authority");
      upload.id = start.upload_id;
      const step = Math.min(1024 * 1024, start.max_chunk_bytes);
      if (!Number.isInteger(step) || step < 1) throw new Error("Invalid server chunk capacity");
      for (let offset=0;offset<file.size;) {
        if (upload.cancelled || nativeAudio.sessionId !== session)
          throw new Error("WAV upload cancelled or Studio session changed");
        const block = await file.slice(offset, Math.min(file.size, offset+step)).arrayBuffer();
        const digest = await window.crypto.subtle.digest("SHA-256", block);
        const chunkSha = Array.from(new Uint8Array(digest))
          .map(x => x.toString(16).padStart(2, "0")).join("");
        const receipt = await stagedRequest(base + "/" + encodeURIComponent(upload.id) + "/chunk", {
          method: "POST",
          headers: {"Content-Type": "application/octet-stream", Accept: "application/json",
                    "X-MUSICA-Chunk-Offset": String(offset),
                    "X-MUSICA-Chunk-SHA256": chunkSha},
          body: block
        });
        if (!receipt.accepted_revision_unchanged || receipt.next_offset !== offset + block.byteLength)
          throw new Error("Staged WAV offset / revision authority mismatch");
        offset = receipt.next_offset;
        status("Uploading WAV " + Math.floor(offset * 100 / file.size) + "% · NOT A CLIP");
      }
      if (upload.cancelled || nativeAudio.sessionId !== session)
        throw new Error("WAV upload cancelled");
      const committed = await stagedRequest(base + "/" + encodeURIComponent(upload.id) + "/finish", {
        method: "POST",
        headers: {"Content-Type": "application/json", Accept: "application/json"},
        body: "{}"
      });
      if (committed.staged_upload_sha256 !== sha256 || committed.staged_upload_size_bytes !== file.size)
        throw new Error("Server returned incorrect file identity");
      finished = true;
      return committed;
    } finally {
      if (!finished && upload.id) {
        try {
          await stagedRequest(base + "/" + encodeURIComponent(upload.id) + "/cancel", {
            method: "POST", headers: {"Content-Type": "application/json", Accept: "application/json"},
            body: "{}"
          });
        } catch (_error) { /* Server also expires and cleans abandoned private uploads. */ }
      }
      if (nativeAudio.stagedTransfer === upload) nativeAudio.stagedTransfer = null;
      el("r3CancelStagedWav").hidden = true;
    }
  }

  async function importWav() {
    if (!nativeAudio.sessionId) return status("Create or open a Studio project first.", "error");
    if (nativeAudio.view && nativeAudio.view.preview)
      return status("Accept or Discard pending native-audio Preview before importing.", "error");
    const picker = el("r3WavFile");
    const file = picker && picker.files && picker.files[0];
    if (!file) return status("Select a PCM WAV file to import.", "error");
    if (file.size < 44 || file.size > 64 * 1024 * 1024)
      return status("WAV file must be between 44 bytes and 64 MiB.", "error");
    const button = el("r3ImportWav");
    button.disabled = true;
    try {
      let value;
      if (file.size > 16 * 1024 * 1024) {
        value = await importStagedWav(file);
      } else {
        const response = await originalFetch(
          "/v0/sessions/" + encodeURIComponent(nativeAudio.sessionId) + "/audio/import-wav",
          {method: "POST", headers: {Accept: "application/json", "Content-Type": "audio/wav"}, body: file}
        );
        const payload = await response.json();
        if (!response.ok || !payload || !payload.ok) {
          throw new Error(payload && payload.error ? payload.error.message : ("HTTP " + response.status));
        }
        value = payload.data;
      }
      if (!value.accepted_revision_unchanged || !value.requires_separate_clip_preview_and_explicit_accept)
        throw new Error("Server did not confirm noncanonical resource-only import.");
      const descriptor = value.asset;
      if (!descriptor || !descriptor.asset_id || !descriptor.format)
        throw new Error("Invalid audio asset descriptor from Studio.");
      el("r3NewAssetId").value = descriptor.asset_id;
      el("r3NewSourceIn").value = "0";
      el("r3NewSourceOut").value = String(descriptor.format.duration_seconds);
      el("r3ImportedAsset").textContent =
        `${file.name} · ${descriptor.asset_id} · ${descriptor.format.sample_rate_hz} Hz · ` +
        `${descriptor.format.channels} ch · ${descriptor.format.duration_seconds} s · NOT A CLIP`;
      await refreshAudioView(true);
      status("WAV imported as immutable resource. Next Preview add track / clip, then explicitly Accept.", "success");
    } catch (error) {
      status(error.message || String(error), "error");
    } finally {
      button.disabled = false;
    }
  }

  function sourceBinding() {
    const view = nativeAudio.view;
    if (!view) throw new Error("Native-audio view is unavailable");
    return {
      project_id: view.project_id,
      revision_id: view.revision_id,
      blueprint_sha256: view.blueprint_sha256,
      audio_material_sha256: view.audio_material_sha256,
    };
  }

  function candidate(kind, operations) {
    nativeAudio.requestCounter += 1;
    return {
      candidate_version: "0",
      candidate_id: `R3-UI-${kind.toUpperCase()}-${String(nativeAudio.requestCounter).padStart(4, "0")}`,
      authority_target: "blueprint_audio_material",
      source: sourceBinding(),
      actor: { kind: "user", actor_id: "studio-browser-r3" },
      reason: `ATCM-R3 Browser ${kind} Preview`,
      operations,
      preview_only: true,
    };
  }

  async function submit(kind, operations) {
    if (!nativeAudio.sessionId) return;
    clearStatus();
    const value = candidate(kind, operations);
    nativeAudio.lastSubmittedCandidate = JSON.parse(JSON.stringify(value));
    try {
      const data = await audioFetch(`/v0/sessions/${encodeURIComponent(nativeAudio.sessionId)}/preview/audio/${kind}`, {
        method: "POST",
        body: { candidate: value },
      });
      nativeAudio.lastAuthorityResult = data.authority_result || null;
      if (!data.preview_installed) {
        const conflicts = (data.authority_result && data.authority_result.conflicts) || [];
        status(conflicts.map((item) => item.reason).join("; ") || "Candidate was blocked", "error");
      } else {
        nativeAudio.view = data.audio_view;
        render();
        status("PREVIEW only — accepted project HEAD is unchanged.", "success");
        const refresh = el("refreshButton");
        if (refresh) refresh.click();
      }
    } catch (error) {
      status(error.message || String(error), "error");
    }
  }

  function number(input, label) {
    const value = Number(input.value);
    if (!Number.isFinite(value)) throw new Error(`${label} must be numeric`);
    return value;
  }


  // R1B-G1 ID suggestions read accepted material only; never create a revision.
  function acceptedTracks() {
    return nativeAudio.view && Array.isArray(nativeAudio.view.tracks) ? nativeAudio.view.tracks : [];
  }

  function uniqueId(prefix, used) {
    for (let index = 1; index <= 9999; index += 1) {
      const value = prefix + "-" + String(index).padStart(3, "0");
      if (!used.has(value)) return value;
    }
    throw new Error("No unused ID remains for " + prefix);
  }

  function suggestTrackId() {
    if (!nativeAudio.view) return status("Open an accepted native-audio project first.", "error");
    const tracks = acceptedTracks();
    el("r3NewTrackId").value = uniqueId("AT-UI", new Set(tracks.map((track) => track.track_id)));
    el("r3NewTrackOrder").value = String(tracks.length);
    status("Suggested unused track ID. Only Preview and explicit Accept can create a track.");
  }

  function suggestClipId() {
    if (!nativeAudio.view) return status("Open an accepted native-audio project first.", "error");
    const used = new Set(acceptedTracks().flatMap((track) =>
      (track.clips || []).map((clip) => clip.clip_id)));
    el("r3NewClipId").value = uniqueId("AC-UI", used);
    status("Suggested unused clip ID. Accepted Project HEAD remains unchanged.");
  }

  function previewAddTrack() {
    try {
      submit("arrangement", [{
        operation_id: `R3-OP-TRACK-${nativeAudio.requestCounter + 1}`,
        op: "ADD_TRACK",
        track_id: el("r3NewTrackId").value.trim(),
        order: Math.trunc(number(el("r3NewTrackOrder"), "Order")),
        name: el("r3NewTrackName").value.trim(),
      }]);
    } catch (error) { status(error.message, "error"); }
  }

  function previewAddClip() {
    try {
      submit("arrangement", [{
        operation_id: `R3-OP-ADDCLIP-${nativeAudio.requestCounter + 1}`,
        op: "ADD_CLIP",
        target: { track_id: el("r3ClipTrack").value },
        clip: {
          clip_id: el("r3NewClipId").value.trim(),
          asset_id: el("r3NewAssetId").value.trim(),
          timeline_start_seconds: number(el("r3NewTimeline"), "Timeline"),
          source_in_seconds: number(el("r3NewSourceIn"), "Source in"),
          source_out_seconds: number(el("r3NewSourceOut"), "Source out"),
          gain_db: number(el("r3NewClipGain"), "Gain"),
        },
      }]);
    } catch (error) { status(error.message, "error"); }
  }

  function previewMixer(track, controls) {
    submit("mixer", [{
      operation_id: `R3-OP-MIX-${nativeAudio.requestCounter + 1}`,
      op: "SET_TRACK_MIXER",
      target: { track_id: track.track_id },
      mixer: {
        gain_db: number(controls.gain, "Track gain"),
        pan: number(controls.pan, "Pan"),
        mute: controls.mute.checked,
        solo: controls.solo.checked,
      },
    }]);
  }

  function previewClip(track, clip, controls) {
    const n = nativeAudio.requestCounter + 1;
    submit("arrangement", [
      { operation_id: `R3-OP-MOVE-${n}`, op: "MOVE_CLIP", target: { track_id: track.track_id, clip_id: clip.clip_id }, timeline_start_seconds: number(controls.timeline, "Timeline") },
      { operation_id: `R3-OP-TRIM-${n}`, op: "TRIM_CLIP", target: { track_id: track.track_id, clip_id: clip.clip_id }, source_in_seconds: number(controls.sourceIn, "Source in"), source_out_seconds: number(controls.sourceOut, "Source out") },
      { operation_id: `R3-OP-GAIN-${n}`, op: "SET_CLIP_GAIN", target: { track_id: track.track_id, clip_id: clip.clip_id }, gain_db: number(controls.gain, "Clip gain") },
    ]);
  }

  async function acceptPreview() {
    if (!nativeAudio.sessionId) return;
    try {
      const data = await audioFetch(`/v0/sessions/${encodeURIComponent(nativeAudio.sessionId)}/audio/accept`, { method: "POST", body: {} });
      nativeAudio.view = data.audio_view;
      render();
      status(`Accepted exactly one revision: ${data.revision_record.revision_id}`, "success");
      const refresh = el("refreshButton");
      if (refresh) refresh.click();
    } catch (error) { status(error.message || String(error), "error"); }
  }

  async function discardPreview() {
    if (!nativeAudio.sessionId) return;
    try {
      const data = await audioFetch(`/v0/sessions/${encodeURIComponent(nativeAudio.sessionId)}/audio/discard`, { method: "POST", body: {} });
      nativeAudio.view = data.audio_view;
      render();
      status("Native-audio Preview discarded; accepted HEAD unchanged.", "success");
      const refresh = el("refreshButton");
      if (refresh) refresh.click();
    } catch (error) { status(error.message || String(error), "error"); }
  }

  function makeInput(type, value, min, max, step) {
    const input = document.createElement("input");
    input.type = type;
    if (type !== "checkbox") input.value = String(value);
    else input.checked = Boolean(value);
    if (min !== undefined) input.min = String(min);
    if (max !== undefined) input.max = String(max);
    if (step !== undefined) input.step = String(step);
    return input;
  }

  function labeled(label, input) {
    const wrapper = document.createElement("label");
    wrapper.textContent = label;
    wrapper.appendChild(input);
    return wrapper;
  }

  function renderTracks(tracks) {
    const list = el("r3TrackList");
    list.replaceChildren();
    const select = el("r3ClipTrack");
    const previouslySelectedTrack = select.value;
    select.replaceChildren();
    tracks.forEach((track) => {
      const option = document.createElement("option");
      option.value = track.track_id;
      option.textContent = `${track.order} · ${track.track_id}`;
      select.appendChild(option);

      const card = document.createElement("article");
      card.className = "r3-track";
      card.dataset.trackId = track.track_id;
      const heading = document.createElement("div");
      heading.className = "r3-track-heading";
      const title = document.createElement("strong");
      title.textContent = `${track.order} · ${track.name} · ${track.track_id}`;
      heading.appendChild(title);

      const mixer = document.createElement("div");
      mixer.className = "r3-mixer-row";
      const gain = makeInput("number", track.mixer.gain_db, -60, 12, 0.1);
      gain.dataset.field = "track-gain";
      const pan = makeInput("number", track.mixer.pan, -1, 1, 0.01);
      pan.dataset.field = "track-pan";
      const mute = makeInput("checkbox", track.mixer.mute);
      mute.dataset.field = "track-mute";
      const solo = makeInput("checkbox", track.mixer.solo);
      solo.dataset.field = "track-solo";
      const mixButton = document.createElement("button");
      mixButton.type = "button";
      mixButton.className = "secondary";
      mixButton.textContent = "Preview mixer";
      mixButton.dataset.action = "preview-mixer";
      mixButton.addEventListener("click", () => previewMixer(track, { gain, pan, mute, solo }));
      mixer.append(labeled("Gain dB", gain), labeled("Pan", pan), labeled("Mute", mute), labeled("Solo", solo), mixButton);

      const clips = document.createElement("div");
      clips.className = "r3-clips";
      (track.clips || []).forEach((clip) => {
        const row = document.createElement("div");
        row.className = "r3-clip";
        row.dataset.clipId = clip.clip_id;
        const identity = document.createElement("div");
        identity.className = "r3-clip-id";
        const clipTitle = document.createElement("strong");
        clipTitle.textContent = clip.clip_id;
        const asset = document.createElement("code");
        asset.textContent = clip.asset_id;
        identity.append(clipTitle, asset);
        const timeline = makeInput("number", clip.timeline_start_seconds, 0, undefined, 0.001);
        timeline.dataset.field = "timeline";
        const sourceIn = makeInput("number", clip.source_in_seconds, 0, undefined, 0.001);
        sourceIn.dataset.field = "source-in";
        const sourceOut = makeInput("number", clip.source_out_seconds, 0.001, undefined, 0.001);
        sourceOut.dataset.field = "source-out";
        const gainClip = makeInput("number", clip.gain_db, -60, 12, 0.1);
        gainClip.dataset.field = "clip-gain";
        const button = document.createElement("button");
        button.type = "button";
        button.className = "secondary";
        button.textContent = "Preview clip edit";
        button.dataset.action = "preview-clip";
        button.addEventListener("click", () => previewClip(track, clip, { timeline, sourceIn, sourceOut, gain: gainClip }));
        row.append(identity, labeled("Timeline", timeline), labeled("In", sourceIn), labeled("Out", sourceOut), labeled("Gain dB", gainClip), button);
        clips.appendChild(row);
      });
      card.append(heading, mixer, clips);
      list.appendChild(card);
    });
    if ([...select.options].some((item) => item.value === previouslySelectedTrack)) {
      select.value = previouslySelectedTrack;
    }
  }

  function render() {
    injectSurface();
    const view = nativeAudio.view;
    el("r3AudioImport").hidden = !nativeAudio.sessionId;
    if (!view) {
      el("r3AudioAuthorityBadge").textContent = "NO PROJECT";
      el("r3AudioWorkspace").hidden = true;
      el("r3AudioUnavailable").hidden = false;
      return;
    }
    el("r3AudioWorkspace").hidden = false;
    el("r3AudioUnavailable").hidden = true;
    const preview = view.preview;
    el("r3AudioAuthorityBadge").textContent = preview ? "PREVIEW · NOT ACCEPTED" : "ACCEPTED";
    el("r3AudioAuthorityBadge").className = `status-pill ${preview ? "preview" : "accepted"}`;
    el("r3AudioSource").textContent = `${view.branch}@${view.revision_id} · ${view.audio_material_sha256.slice(0, 12)}…`;
    el("r3Accept").hidden = !preview;
    el("r3Discard").hidden = !preview;
    const tracks = preview ? preview.tracks : view.tracks;
    // Newly created projects have zero tracks. A default order of 9 makes
    // the first user-created track fail the canonical contiguous-order check.
    if (!preview) el("r3NewTrackOrder").value = String((tracks || []).length);
    renderTracks(tracks || []);
    const audition = preview ? preview.audition : view.accepted_audition;
    el("r3AuditionLabel").textContent = preview ? "Preview-derived native mix · NOT ACCEPTED" : "Accepted-revision derived native mix";
    el("r3AuditionMeta").textContent = audition && audition.available
      ? `plan ${audition.mix_plan_sha256.slice(0, 12)}… · wav ${audition.wav_sha256.slice(0, 12)}… · ${audition.mix_sample_rate_hz} Hz · derived/non-canonical`
      : `Audition unavailable: ${audition && audition.error ? audition.error : "no renderable clips"}`;
    const player = el("r3AudioPlayer");
    if (audition && audition.available && nativeAudio.sessionId) {
      const file = preview ? "preview.wav" : "accepted.wav";
      player.src = `/v0/sessions/${encodeURIComponent(nativeAudio.sessionId)}/audio/${file}?v=${encodeURIComponent(audition.wav_sha256)}`;
      player.hidden = false;
    } else {
      player.removeAttribute("src");
      player.load();
      player.hidden = true;
    }
    const genericAccept = el("acceptButton");
    if (genericAccept && preview) {
      genericAccept.disabled = true;
      genericAccept.title = "Native-audio Preview must use the R1/R2 trusted audio Accept button.";
    }
  }

  async function refreshAudioView(quiet = false) {
    injectSurface();
    if (!nativeAudio.sessionId) return;
    try {
      nativeAudio.view = await audioFetch(`/v0/sessions/${encodeURIComponent(nativeAudio.sessionId)}/audio`);
      render();
      window.dispatchEvent(new CustomEvent("musica:native-audio-view-ready", {
        detail: {sessionId: nativeAudio.sessionId, revisionId: nativeAudio.view.revision_id}
      }));
      if (!quiet) status("Native-audio state refreshed.", "success");
    } catch (error) {
      nativeAudio.view = null;
      render();
      if (!quiet) status(error.message || String(error), "error");
    }
  }

  window.MUSICA_NATIVE_AUDIO = { state: nativeAudio, refresh: refreshAudioView };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { injectSurface(); render(); });
  } else {
    injectSurface();
    render();
  }
})();
