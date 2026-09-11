(() => {
  "use strict";

  const OPTIONS = [
    { value: "tempo", label: "Tempo", ko: "템포" },
    { value: "melody_identity", label: "Melody identity", ko: "멜로디 정체성" },
    { value: "rhythm_identity", label: "Rhythm identity", ko: "리듬 정체성" },
  ];

  const createForm = document.getElementById("createForm");
  const generateButton = document.getElementById("generateButton");
  if (!createForm || !generateButton) return;

  const picker = document.createElement("section");
  picker.className = "identity-lock-picker";
  picker.setAttribute("aria-labelledby", "identityLocksTitle");

  const heading = document.createElement("div");
  heading.className = "identity-lock-heading";

  const title = document.createElement("strong");
  title.id = "identityLocksTitle";
  title.textContent = "Identity locks / 정체성 잠금";

  const note = document.createElement("span");
  note.textContent = "Protected through later edits / 이후 수정에서도 보호";

  heading.append(title, note);
  picker.appendChild(heading);

  const options = document.createElement("div");
  options.className = "identity-lock-options";

  for (const item of OPTIONS) {
    const label = document.createElement("label");
    label.className = "identity-lock-option";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = "identity_lock";
    input.value = item.value;
    input.checked = true;

    const copy = document.createElement("span");
    const primary = document.createElement("strong");
    primary.textContent = item.label;
    const secondary = document.createElement("small");
    secondary.textContent = item.ko;
    copy.append(primary, secondary);

    label.append(input, copy);
    options.appendChild(label);
  }

  picker.appendChild(options);
  createForm.insertBefore(picker, generateButton);

  const originalFetch = window.fetch.bind(window);
  window.fetch = (input, init = undefined) => {
    const requestUrl = typeof input === "string" ? input : input?.url;
    const method = String(init?.method || input?.method || "GET").toUpperCase();
    let nextInit = init;

    if (requestUrl && method === "POST") {
      const pathname = new URL(requestUrl, window.location.href).pathname;
      if (pathname === "/v0/projects/create" && typeof init?.body === "string") {
        try {
          const body = JSON.parse(init.body);
          body.preserve_on_edit = Array.from(
            createForm.querySelectorAll('input[name="identity_lock"]:checked')
          ).map((control) => control.value);
          nextInit = { ...init, body: JSON.stringify(body) };
        } catch {
          // The normal Studio API layer remains responsible for invalid JSON errors.
        }
      }
    }

    return originalFetch(input, nextInit);
  };
})();
