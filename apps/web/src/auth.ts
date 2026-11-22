export type Account = { id: string; username: string; role: "administrator" | "operator"; active: boolean };

const originalFetch = window.fetch.bind(window);
let account: Account | null = null;
let dialog: HTMLDialogElement | null = null;
let onReady: (() => void) | null = null;
let statusNode: HTMLElement;
export function currentAccount(): Account | null { return account; }

function field(labelText: string, type: string, autocomplete?: string): [HTMLLabelElement, HTMLInputElement] {
  const label = document.createElement("label"); label.textContent = labelText;
  const input = document.createElement("input"); input.type = type; input.required = true;
  if (autocomplete) input.setAttribute("autocomplete", autocomplete);
  label.append(input); return [label, input];
}

function button(label: string, action: () => void): HTMLButtonElement {
  const result = document.createElement("button"); result.type = "button"; result.textContent = label;
  result.addEventListener("click", action); return result;
}

async function request(url: string, method: string, body?: object): Promise<Response> {
  return originalFetch(url, { method, ...(body === undefined ? {} : { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }) });
}

function updateIdentity(): void {
  statusNode.textContent = account ? `${account.username} · ${account.role === "administrator" ? "Administrator" : "Operator"}` : "";
  document.body.dataset.role = account?.role ?? "";
  document.dispatchEvent(new CustomEvent("lumen:identity", { detail: account }));
}

function openLogin(message: string): void {
  if (dialog?.open) return;
  dialog = document.createElement("dialog"); dialog.className = "auth-dialog";
  dialog.setAttribute("aria-label", "Sign in to Lumen");
  const form = document.createElement("form"); form.className = "auth-form";
  const heading = document.createElement("h2"); heading.textContent = "Sign in to Lumen";
  const description = document.createElement("p"); description.textContent = message;
  const [usernameLabel, username] = field("Username", "text", "username");
  const [passwordLabel, password] = field("Password", "password", "current-password");
  const feedback = document.createElement("p"); feedback.setAttribute("role", "status");
  const submit = document.createElement("button"); submit.type = "submit"; submit.textContent = "Sign in";
  form.append(heading, description, usernameLabel, passwordLabel, feedback, submit); dialog.append(form); document.body.append(dialog);
  dialog.addEventListener("cancel", event => event.preventDefault());
  form.addEventListener("submit", async event => {
    event.preventDefault(); submit.disabled = true; feedback.textContent = "Signing in…";
    try {
      const response = await request("/api/auth/login", "POST", { username: username.value, password: password.value });
      if (!response.ok) { feedback.textContent = response.status === 401 ? "Sign-in failed. Check your credentials or try again later." : "Sign-in is unavailable. Try again."; return; }
      const session = await originalFetch("/api/auth/session", { cache: "no-store" });
      if (!session.ok) throw new Error();
      account = await session.json() as Account; updateIdentity();
      password.value = ""; dialog?.close(); dialog?.remove(); dialog = null;
      if (onReady) { const ready = onReady; onReady = null; ready(); }
    } catch { feedback.textContent = "Could not reach the service. Try again."; }
    finally { submit.disabled = false; }
  });
  dialog.showModal(); username.focus();
}

function openPanel(title: string): [HTMLDialogElement, HTMLElement] {
  const panel = document.createElement("dialog"); panel.className = "auth-dialog";
  panel.setAttribute("aria-label", title);
  const body = document.createElement("div"); body.className = "auth-form";
  const heading = document.createElement("h2"); heading.textContent = title;
  const close = button("Close", () => { panel.close(); panel.remove(); });
  body.append(heading, close); panel.append(body); document.body.append(panel); panel.addEventListener("close", () => panel.remove()); panel.showModal();
  return [panel, body];
}

function passwordPanel(): void {
  const [panel, body] = openPanel("Change password");
  const form = document.createElement("form"); form.className = "auth-form";
  const [oldLabel, oldPassword] = field("Current password", "password", "current-password");
  const [newLabel, newPassword] = field("New password (at least 12 characters)", "password", "new-password"); newPassword.minLength = 12;
  const feedback = document.createElement("p"); feedback.setAttribute("role", "status");
  const submit = document.createElement("button"); submit.type = "submit"; submit.textContent = "Change password";
  form.append(oldLabel, newLabel, feedback, submit); body.append(form);
  form.addEventListener("submit", async event => {
    event.preventDefault(); submit.disabled = true;
    try {
      const result = await fetch("/api/auth/password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current_password: oldPassword.value, new_password: newPassword.value }) });
      if (!result.ok) { feedback.textContent = "Could not change password. Check your current password and try again."; return; }
      panel.close(); panel.remove(); openLogin("Password changed. Sign in again to continue.");
    } catch { feedback.textContent = "The service is unavailable. Try again."; } finally { submit.disabled = false; }
  });
}

export function renderUsers(body: HTMLElement): void {
  const feedback = document.createElement("p"); feedback.setAttribute("role", "status");
  const form = document.createElement("form"); form.className = "auth-form";
  const [nameLabel, username] = field("Username", "text", "off");
  const [passwordLabel, password] = field("Initial password (at least 12 characters)", "password", "new-password"); password.minLength = 12;
  const roleLabel = document.createElement("label"); roleLabel.textContent = "Role";
  const role = document.createElement("select"); for (const value of ["operator", "administrator"]) role.add(new Option(value === "operator" ? "Operator" : "Administrator", value)); roleLabel.append(role);
  const submit = document.createElement("button"); submit.textContent = "Create user"; submit.type = "submit";
  form.append(nameLabel, passwordLabel, roleLabel, submit);
  const list = document.createElement("div"); list.className = "account-list"; body.append(form, feedback, list);
  async function refresh(): Promise<void> {
    const response = await fetch("/api/auth/users"); if (!response.ok) { feedback.textContent = "Could not load users."; return; }
    const users = await response.json() as Account[]; list.replaceChildren();
    for (const user of users) {
      const row = document.createElement("section"); row.className = "account-row";
      const label = document.createElement("strong"); label.textContent = `${user.username} · ${user.role} · ${user.active ? "Active" : "Inactive"}`;
      const change = async (values: object): Promise<void> => {
        try {
          const result = await fetch(`/api/auth/users/${encodeURIComponent(user.id)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(values) });
          if (!result.ok) { const data = await result.json().catch(() => null) as { detail?: string } | null; feedback.textContent = data?.detail ?? "Could not update user."; return; }
          const updated = await result.json() as Account;
          if (account?.id === updated.id) {
            account = updated.active ? updated : null; updateIdentity();
            if (!updated.active || updated.role !== "administrator") return;
          }
          feedback.textContent = "User updated."; await refresh();
        } catch { feedback.textContent = "The service is unavailable. Try again."; }
      };
      const reset = document.createElement("form"); reset.className = "account-reset";
      const [resetLabel, resetPassword] = field(`New password for ${user.username}`, "password", "new-password"); resetPassword.minLength = 12;
      const resetButton = document.createElement("button"); resetButton.type = "submit"; resetButton.textContent = "Reset password";
      reset.append(resetLabel, resetButton); reset.addEventListener("submit", event => { event.preventDefault(); void change({ password: resetPassword.value }).then(() => { resetPassword.value = ""; }); });
      row.append(label, button(user.active ? "Deactivate" : "Activate", () => { void change({ active: !user.active }); }), button(user.role === "operator" ? "Make administrator" : "Make operator", () => { void change({ role: user.role === "operator" ? "administrator" : "operator" }); }), reset); list.append(row);
    }
  }
  form.addEventListener("submit", async event => {
    event.preventDefault(); submit.disabled = true;
    try { const result = await fetch("/api/auth/users", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: username.value, password: password.value, role: role.value }) });
      if (!result.ok) { feedback.textContent = "Could not create user. Check the username and password."; return; }
      username.value = ""; password.value = ""; feedback.textContent = "User created."; await refresh();
    } catch { feedback.textContent = "The service is unavailable."; } finally { submit.disabled = false; }
  });
  void refresh().catch(() => { feedback.textContent = "The service is unavailable."; });
}

export async function initializeAuthentication(ready: () => void): Promise<void> {
  const controls = document.querySelector<HTMLElement>("#account-controls")!;
  statusNode = document.querySelector<HTMLElement>("#account-identity")!;
  const trigger = document.querySelector<HTMLButtonElement>("#account-trigger")!;
  const menu = document.querySelector<HTMLElement>("#account-menu")!;
  const closeMenu = (focus = false): void => { menu.hidden = true; trigger.setAttribute("aria-expanded", "false"); controls.dispatchEvent(new Event("lumen:account-close")); if (focus) trigger.focus(); };
  trigger.addEventListener("click", () => { if (!menu.hidden) { closeMenu(); return; } menu.hidden = false; trigger.setAttribute("aria-expanded", "true"); menu.querySelector<HTMLButtonElement>("button")?.focus(); });
  controls.addEventListener("keydown", event => { if (event.key === "Escape" && !menu.hidden) { event.preventDefault(); event.stopPropagation(); closeMenu(true); } });
  document.addEventListener("pointerdown", event => { if (event.target instanceof Node && !controls.contains(event.target)) closeMenu(); });
  controls.addEventListener("focusout", event => { if (event.relatedTarget instanceof Node && !controls.contains(event.relatedTarget)) closeMenu(); });
  document.querySelector<HTMLButtonElement>("#account-settings")!.addEventListener("click", () => { closeMenu(); passwordPanel(); });
  document.querySelector<HTMLButtonElement>("#sign-out")!.addEventListener("click", () => { closeMenu(); if (!window.confirm("Sign out? Unsaved work may be lost.")) return; void request("/api/auth/logout", "POST").then(result => { if (!result.ok && result.status !== 401) throw new Error(); account = null; updateIdentity(); openLogin("Sign in to continue."); }).catch(() => { window.alert("Could not sign out. Try again."); }); });
  const notice = document.querySelector<HTMLElement>("#account-notice")!;
  updateIdentity();
  window.fetch = async (input, init) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.pathname : new URL(input.url).pathname;
    let response: Response;
    try { response = await originalFetch(input, init); }
    catch (error) { if (url.startsWith("/api/")) notice.textContent = "The service is unavailable. Try again."; throw error; }
    if (url.startsWith("/api/")) {
      if (response.status === 401 && url !== "/api/auth/login") openLogin("Your session has ended. Sign in, then retry your action.");
      else if (response.status === 403) {
        notice.textContent = "You do not have permission for this action.";
        try {
          const session = await originalFetch("/api/auth/session", { cache: "no-store" });
          if (session.ok) {
            account = await session.json() as Account; updateIdentity();
            if (account.role !== "administrator") document.querySelectorAll<HTMLDialogElement>('dialog[data-admin-panel="true"]').forEach(panel => { panel.close(); panel.remove(); });
          } else if (session.status === 401) openLogin("Your session has ended. Sign in, then retry your action.");
        } catch { notice.textContent = "The service is unavailable. Try again."; }
      }
      else if (response.status >= 500) notice.textContent = "The service is unavailable. Try again.";
      else if (response.ok) notice.textContent = "";
    }
    return response;
  };
  try {
    const result = await originalFetch("/api/auth/session", { cache: "no-store" });
    if (result.ok) { account = await result.json() as Account; updateIdentity(); ready(); return; }
  } catch { /* The sign-in dialog reports connection failures. */ }
  onReady = ready; openLogin("Use your local account to access the shared workspace.");
}
