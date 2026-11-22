import "./style.css";
import { currentAccount, initializeAuthentication, renderUsers } from "./auth";

type TicketSummary = { id: string; subject: string; received_at: string; classification_status: string; classification_result: string | null; classification_source: string | null; classification_categories: ClassificationOption[]; classification_priority: ClassificationOption | null; effective_categories: ClassificationOption[]; effective_priority: ClassificationOption | null; category_origin: string | null; priority_origin: string | null; classification_revision: number };
type Ticket = TicketSummary & { description: string; classification_failure_reason: string | null };
type TicketResponse = { ticket_id: string; text: string; status: "draft" | "approved"; edited_at: string; revision: number; adopted_generation_id: string | null; provenance: string };
type Generation = { id: string; knowledge_base_id: string | null; status: string; original_text: string | null; rationale: string | null; insufficient_evidence: boolean | null; failure_reason: string | null; created_at: string; attempts: Array<{ status: string; requested_model: string | null; reported_model: string | null; input_tokens: number | null; output_tokens: number | null; embedding_input_tokens: number | null; retrieval_mode: string | null; retrieval_reason: string | null; estimated_cost: number | null; currency: string | null; sources: Array<{ chunk_id: string; document_name: string; version: number; excerpt: string }>; citations: string[] | null; failure_reason: string | null }> };
type TicketPage = { items: TicketSummary[]; page: number; page_size: number; total: number };
type InboxState = { q: string; statuses: string[]; date_from: string; date_to: string; category_ids: string[]; priority_ids: string[]; page: number; page_size: number; invalid?: boolean };
type ClassificationOption = { id: string; kind: "category" | "priority"; name: string; active: boolean; color: string };

function tag(option: ClassificationOption): HTMLElement {
  const chip = element("span", option.name, "tag tag-colored");
  if (/^#[0-9a-f]{6}$/i.test(option.color)) chip.style.setProperty("--tag-color", option.color);
  if (!option.active) chip.append(element("span", "Inactive", "tag-inactive"));
  return chip;
}

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("Application root not found");
app.innerHTML = `
  <div class="shell">
    <aside class="sidebar">
      <a class="brand" href="#/" aria-label="Lumen inbox"><span class="brand-mark" aria-hidden="true"></span><span>Lumen<small>Ticket workspace</small></span></a>
      <nav class="workspace-nav" aria-label="Workspace">
        <span class="nav-label">Workspace</span>
        <a href="#/" data-nav="inbox"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 5h16v14H4z M4 14h5l2 2h2l2-2h5"/></svg></span>Inbox</a>
        <a href="#/knowledge" data-nav="knowledge"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z M5 17a3 3 0 0 1 3-3h11 M9 8h6"/></svg></span>Knowledge</a>
        <div class="admin-nav" id="admin-nav" hidden><span class="nav-label">Administration</span>
          <a href="#/options" data-nav="options"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 4h8l8 8-8 8-8-8z M8 8h.01"/></svg></span>Tags</a>
          <a href="#/users" data-nav="users"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="10" cy="8" r="3"/><path d="M4 19v-1a6 6 0 0 1 12 0v1 M16 5a3 3 0 0 1 0 6 M18 14a5 5 0 0 1 2 4v1"/></svg></span>Users</a>
        </div>
      </nav>
      <div class="account-controls" id="account-controls">
        <button class="account-trigger" id="account-trigger" type="button" aria-expanded="false" aria-controls="account-menu"><span class="account-avatar" aria-hidden="true">L</span><span id="account-identity"></span><span class="chevron" aria-hidden="true"></span></button>
        <div class="account-menu" id="account-menu" hidden>
          <button id="account-settings" type="button">Account settings</button>
          <div class="appearance"><span id="appearance-label">Appearance</span><div class="appearance-control"><button class="appearance-trigger" id="appearance-trigger" type="button" aria-labelledby="appearance-label appearance-value" aria-haspopup="listbox" aria-expanded="false" aria-controls="appearance-options"><span id="appearance-value">System</span><span class="chevron" aria-hidden="true"></span></button><div class="appearance-menu" id="appearance-options" role="listbox" aria-labelledby="appearance-label" hidden><button type="button" role="option" data-value="system">System <span aria-hidden="true">✓</span></button><button type="button" role="option" data-value="light">Light <span aria-hidden="true">✓</span></button><button type="button" role="option" data-value="dark">Dark <span aria-hidden="true">✓</span></button></div></div></div>
          <button id="sign-out" class="sign-out" type="button">Sign out</button>
        </div>
      </div>
    </aside>
    <div class="main-column"><header class="header"><span class="header-context">Workspace <span aria-hidden="true">/</span> <strong id="header-location">Inbox</strong></span><div class="header-actions"><span class="account-notice" id="account-notice" role="status"></span><span class="health" role="status" id="health" title="API process availability only">Checking API…</span></div></header>
    <main><div class="page-heading"><div><h1 id="page-title" tabindex="-1">Inbox</h1><p id="page-description">Received tickets, ready to inspect.</p></div></div>
      <section class="workspace" aria-label="Ticket workspace"><div id="content" aria-live="polite"></div></section>
    </main></div>
  </div>`;
const content = document.querySelector<HTMLElement>("#content")!;
const title = document.querySelector<HTMLElement>("#page-title")!;
const health = document.querySelector<HTMLElement>("#health")!;
const trigger = document.querySelector<HTMLButtonElement>("#appearance-trigger")!;
const appearanceValue = document.querySelector<HTMLElement>("#appearance-value")!;
const menu = document.querySelector<HTMLElement>("#appearance-options")!;
const options = Array.from(menu.querySelectorAll<HTMLButtonElement>("[role=option]"));
type Appearance = "system" | "light" | "dark";
let selectedAppearance: Appearance = "system";
try {
  const saved = localStorage.getItem("lumen-appearance");
  if (saved === "light" || saved === "dark" || saved === "system") selectedAppearance = saved;
} catch { /* Keep the in-memory preference. */ }
function applyAppearance(): void {
  if (selectedAppearance === "system") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = selectedAppearance;
  for (const option of options) {
    const selected = option.dataset.value === selectedAppearance;
    option.setAttribute("aria-selected", String(selected));
    option.tabIndex = selected ? 0 : -1;
    if (selected) appearanceValue.textContent = option.childNodes[0].textContent!.trim();
  }
}
function closeAppearance(restoreFocus = false): void {
  menu.hidden = true;
  trigger.setAttribute("aria-expanded", "false");
  if (restoreFocus) trigger.focus();
}
function openAppearance(): void {
  menu.hidden = false;
  trigger.setAttribute("aria-expanded", "true");
  options.find(option => option.dataset.value === selectedAppearance)?.focus();
}
document.querySelector<HTMLElement>("#account-controls")!.addEventListener("lumen:account-close", () => closeAppearance());
trigger.addEventListener("click", () => menu.hidden ? openAppearance() : closeAppearance());
trigger.addEventListener("keydown", event => {
  if (event.key === "ArrowDown" || event.key === "ArrowUp") { event.preventDefault(); openAppearance(); }
});
menu.addEventListener("click", event => {
  const option = (event.target as HTMLElement).closest<HTMLButtonElement>("[role=option]");
  const value = option?.dataset.value;
  if (value !== "system" && value !== "light" && value !== "dark") return;
  selectedAppearance = value;
  applyAppearance();
  try { localStorage.setItem("lumen-appearance", selectedAppearance); } catch { /* Selection remains active for this session. */ }
  closeAppearance(true);
});
menu.addEventListener("keydown", event => {
  if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); closeAppearance(true); return; }
  if (event.key === "Tab") { closeAppearance(); return; }
  if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
  event.preventDefault();
  const current = options.indexOf(document.activeElement as HTMLButtonElement);
  const next = event.key === "Home" ? 0 : event.key === "End" ? options.length - 1 : (current + (event.key === "ArrowDown" ? 1 : -1) + options.length) % options.length;
  options[next].focus();
});
document.addEventListener("pointerdown", event => {
  if (!(event.target instanceof Element) || !event.target.closest(".appearance-control")) closeAppearance();
});
applyAppearance();
let requestVersion = 0;
let refreshTimer: number | undefined;
let responseEditor: { ticketId: string; node: HTMLElement; dirty: () => boolean } | null = null;
let currentHash = location.hash;
let restoringHash = false;
const pageSizes = [25, 50, 75, 100];
const statuses = ["pending", "processing", "completed", "failed", "unavailable"];
function inboxState(): InboxState {
  const params = new URLSearchParams(location.hash.split("?")[1] ?? "");
  const page = Number(params.get("page"));
  const size = Number(params.get("page_size"));
  const validDate = (value: string): boolean => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
  const from = params.get("date_from") ?? "";
  const to = params.get("date_to") ?? "";
  const uuid = (value: string): boolean => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
  const values = (plural: string, singular: string): string[] => [...new Set([...params.getAll(plural), ...params.getAll(singular)])];
  const selectedStatuses = values("statuses", "status"), categories = values("category_ids", "category_id"), priorities = values("priority_ids", "priority_id");
  const known = ["q", "status", "statuses", "date_from", "date_to", "category_id", "category_ids", "priority_id", "priority_ids", "page", "page_size"];
  let unknown = false; params.forEach((_value, key) => { if (!known.includes(key)) unknown = true; });
  const invalid = unknown || selectedStatuses.some(value => !statuses.includes(value)) || [...categories, ...priorities].some(value => !uuid(value)) || (!!from && !validDate(from)) || (!!to && !validDate(to)) || (!!from && !!to && from > to) || (params.has("page") && (!Number.isSafeInteger(page) || page < 1)) || (params.has("page_size") && !pageSizes.includes(size));
  return { q: params.get("q") ?? "", statuses: selectedStatuses, date_from: from, date_to: to, category_ids: categories, priority_ids: priorities, page: Number.isSafeInteger(page) && page > 0 ? page : 1, page_size: pageSizes.includes(size) ? size : 25, invalid };
}
function stateQuery(state: InboxState): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(state)) {
    if (key === "invalid") continue;
    if (Array.isArray(value)) value.forEach(item => params.append(key, item));
    else if (value !== "" && value !== undefined) params.set(key, String(value));
  }
  return params.toString();
}
function inboxHref(state: InboxState): string { return `#/?${stateQuery(state)}`; }
let preserveDraftOnNavigation = false;
function navigateInbox(state: InboxState, preserveDraft = false): void {
  const target = inboxHref(state);
  if (location.hash === target) { if (!preserveDraft) filterDraft = null; void render(); }
  else { preserveDraftOnNavigation = preserveDraft; location.hash = target; }
}

function statusLabel(status: string): string {
  return ({ pending: "Pending", processing: "Processing", completed: "Completed", failed: "Failed" } as Record<string, string>)[status] ?? "Unavailable";
}
function scheduleRefresh(): void {
  refreshTimer = window.setTimeout(() => {
    const results = document.querySelector<HTMLElement>("#inbox-results");
    if (results && (results.contains(document.activeElement) || results.querySelector('.selection-trigger[aria-expanded="true"]'))) { scheduleRefresh(); return; }
    void render(true);
  }, 5000);
}

function element<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string, className?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? value : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}
function backLink(): HTMLAnchorElement {
  const link = element("a", "← Back to inbox", "back-link");
  link.href = inboxHref(inboxState());
  return link;
}
function showState(heading: string, message: string, action?: () => void, back = false, actionLabel = "Try again"): void {
  const state = element("div", undefined, "state");
  state.append(element("h2", heading), element("p", message));
  if (action) {
    const button = element("button", actionLabel);
    button.type = "button";
    button.addEventListener("click", action);
    state.append(button);
  }
  if (back) state.append(backLink());
  content.replaceChildren(state);
}

function makeResponseEditor(ticketId: string): HTMLElement {
  const section = element("section", undefined, "response-editor");
  section.append(element("h3", "Response"), element("p", "Write a response for human review. Approval saves it without sending a message.", "response-intro"));
  const status = element("p", "Loading response…", "response-status"); status.setAttribute("role", "status");
  const form = element("form");
  const label = element("label", "Response text"); label.htmlFor = "response-text";
  const input = element("textarea"); input.id = "response-text"; input.rows = 8; input.required = true; input.disabled = true;
  const actions = element("div", undefined, "response-actions");
  const save = element("button", "Save draft"); save.type = "submit"; save.disabled = true;
  const approve = element("button", "Approve response"); approve.type = "button"; approve.disabled = true;
  const feedback = element("p", "", "response-feedback"); feedback.setAttribute("role", "status");
  const conflict = element("div", undefined, "response-conflict");
  actions.append(save, approve); form.append(label, input, actions, feedback, conflict); section.append(status, form);
  let saved: TicketResponse | null = null;
  let savedText = "";
  let adoptedGeneration: string | null = null;
  let loaded = false;
  const dirty = (): boolean => loaded && (input.value !== savedText || adoptedGeneration !== (saved?.adopted_generation_id ?? null));
  responseEditor = { ticketId, node: section, dirty };
  const endpoint = `/api/tickets/${encodeURIComponent(ticketId)}/response`;
  const describe = (): void => {
    status.textContent = saved ? `${saved.status === "approved" ? "Approved" : "Draft"} · ${saved.provenance === "ai" ? "AI generated" : saved.provenance === "ai_edited" ? "AI generated and edited" : "Written manually"} · Last edited ${formatDate(saved.edited_at)}` : "No response saved yet";
  };
  const load = async (): Promise<void> => {
    try {
      const result = await fetch(endpoint, { cache: "no-store", signal: AbortSignal.timeout(10000) });
      if (!result.ok) throw new Error();
      saved = await result.json() as TicketResponse | null;
      input.value = savedText = saved?.text ?? ""; adoptedGeneration = saved?.adopted_generation_id ?? null; loaded = true;
      input.disabled = save.disabled = approve.disabled = false; feedback.textContent = ""; describe();
    } catch {
      status.textContent = "Response unavailable"; feedback.textContent = "Could not load the response. ";
      const retry = element("button", "Try again", "inline-retry"); retry.type = "button"; retry.addEventListener("click", () => { feedback.textContent = ""; void load(); }); feedback.append(retry);
    }
  };
  const write = async (approval: boolean): Promise<void> => {
    if (!input.value.trim()) { input.setCustomValidity("Enter a response before saving."); input.reportValidity(); return; }
    input.setCustomValidity(""); input.readOnly = true; save.disabled = approve.disabled = true; conflict.replaceChildren();
    feedback.textContent = approval ? "Approving response…" : "Saving response…";
    try {
      const result = await fetch(approval ? `${endpoint}/approval` : endpoint, { method: approval ? "POST" : "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: input.value, expected_revision: saved?.revision ?? null, adopted_generation_id: adoptedGeneration }), signal: AbortSignal.timeout(10000) });
      if (result.status === 409) {
        feedback.textContent = "A newer response was saved elsewhere. Your text is still here.";
        const latestResult = await fetch(endpoint, { cache: "no-store", signal: AbortSignal.timeout(10000) });
        if (!latestResult.ok) throw new Error();
        const latest = await latestResult.json() as TicketResponse | null;
        conflict.append(element("p", "Current saved response:"));
        conflict.append(element("pre", latest?.text ?? "No response saved."));
        const keep = element("button", "Keep my text and review again"); keep.type = "button";
        keep.addEventListener("click", () => { saved = latest; savedText = latest?.text ?? ""; describe(); conflict.replaceChildren(); feedback.textContent = "Your text is ready to save or approve against the latest version."; input.focus(); });
        conflict.append(keep); return;
      }
      if (!result.ok) throw new Error();
      saved = await result.json() as TicketResponse; savedText = saved.text; describe();
      feedback.textContent = approval ? "Response approved and saved. No message was sent." : "Response saved.";
    } catch { feedback.textContent = "Could not save the response. Your text is still here; try again."; }
    finally { input.readOnly = false; save.disabled = approve.disabled = false; }
  };
  input.addEventListener("input", () => {
    input.setCustomValidity("");
    if (!conflict.childElementCount) feedback.textContent = dirty() ? "Unsaved changes." : "";
  });
  form.addEventListener("submit", event => { event.preventDefault(); void write(false); });
  approve.addEventListener("click", () => { void write(true); });
  const generationArea = element("section", undefined, "generation-area");
  generationArea.append(element("h4", "AI suggestion"), element("p", "Choose whether to use a knowledge base. Review the suggestion for accuracy; your editor text stays in place."));
  const generationControls = element("div", undefined, "generation-controls");
  const baseSlot = element("div", undefined, "generation-base-selection");
  const baseNotice = element("p", "", "generation-base-notice");
  let selectedGenerationBase = "";
  let generationChoices: Choice[] = [{ value: "general", label: "Without a knowledge base" }];
  const generate = element("button", "Generate response"); generate.type = "button"; generate.disabled = true;
  const generationStatus = element("p", "Loading knowledge bases…"); generationStatus.setAttribute("role", "status");
  const suggestions = element("div", undefined, "generation-results");
  generationControls.append(baseSlot, generate); generationArea.append(generationControls, baseNotice, generationStatus, suggestions); section.insertBefore(generationArea, form);
  const generationEndpoint = `/api/tickets/${encodeURIComponent(ticketId)}/generations`;
  const generationCards = new Map<string, { node: HTMLDetailsElement; snapshot: string }>();
  const refreshGenerations = async (): Promise<void> => {
    if (!section.isConnected) return;
    try {
      const result = await fetch(generationEndpoint, { cache: "no-store" }); if (!result.ok) throw new Error();
      const items = await result.json() as Generation[];
      if (!section.isConnected) return;
      const ordered = [...items].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
      for (const [id, card] of generationCards) {
        if (!items.some(item => item.id === id)) { card.node.remove(); generationCards.delete(id); }
      }
      for (const [index, item] of ordered.entries()) {
        let entry = generationCards.get(item.id);
        const snapshot = JSON.stringify(item);
        if (entry?.snapshot === snapshot) continue;
        const previous = entry?.node;
        const openStates = new Map(Array.from(previous?.querySelectorAll<HTMLDetailsElement>("details[data-disclosure-key]") ?? [], detail => [detail.dataset.disclosureKey, detail.open]));
        const focused = previous?.contains(document.activeElement) ? document.activeElement : null;
        const focusKey = (focused as HTMLElement | null)?.dataset.focusKey;
        const card = element("details", undefined, "generation-result");
        card.open = previous?.open ?? index === 0;
        const summary = element("summary", `${item.status[0].toUpperCase()}${item.status.slice(1)} · ${formatDate(item.created_at)}`, "generation-summary"); summary.dataset.focusKey = "generation"; card.append(summary);
        const body = element("div", undefined, "generation-body");
        if (item.knowledge_base_id === null) body.append(element("p", "Without a knowledge base: no sources were consulted. General guidance may be incorrect; verify it before use.", "generation-warning"));
        const lastAttempt = item.attempts.at(-1);
        if (lastAttempt?.retrieval_mode === "lexical") body.append(element("p", lastAttempt.retrieval_reason === "index_incomplete" ? "Only keyword search was used because semantic indexing is incomplete. Relevant sources may have been missed." : "Only keyword search was used because semantic search was unavailable. Relevant sources may have been missed.", "generation-warning"));
        if (item.failure_reason) body.append(element("p", `Generation issue: ${item.failure_reason}`, "generation-warning"));
        if (item.original_text) {
          if (item.insufficient_evidence) body.append(element("p", "Insufficient evidence: review the limitation before using this suggestion.", "generation-warning"));
          body.append(element("pre", item.original_text, "generation-text"));
          const adopt = element("button", "Use suggestion"); adopt.type = "button"; adopt.dataset.focusKey = "adopt";
          adopt.addEventListener("click", () => { if (!loaded) return; if (input.value && !window.confirm("Replace the current editor text with this suggestion?")) return; input.value = item.original_text!; adoptedGeneration = item.id; feedback.textContent = "Suggestion added to the editor. Review and save it."; input.focus(); });
          body.append(adopt);
        }
        if (item.rationale) body.append(element("p", `Rationale: ${item.rationale}`, "generation-rationale"));
        const details = element("details", undefined, "generation-audit"); details.dataset.disclosureKey = "audit";
        const auditSummary = element("summary", "Sources and audit"); auditSummary.dataset.focusKey = "audit"; details.append(auditSummary);
        for (const [attemptIndex, attempt] of item.attempts.entries()) {
          details.append(element("p", `Attempt: ${attempt.status} · Model: ${attempt.reported_model ?? attempt.requested_model ?? "Unknown"} · Input tokens: ${attempt.input_tokens ?? "Unknown"} · Output tokens: ${attempt.output_tokens ?? "Unknown"} · Cost: ${attempt.estimated_cost === null ? "Unknown" : `${attempt.estimated_cost} ${attempt.currency ?? ""}`}`));
          if (attempt.retrieval_mode) details.append(element("p", `Retrieval: ${attempt.retrieval_mode}${attempt.retrieval_reason ? ` · ${attempt.retrieval_reason === "index_incomplete" ? "Semantic indexing incomplete" : "Semantic search unavailable"}` : ""} · Embedding input tokens: ${attempt.embedding_input_tokens ?? "Unknown"}`));
          for (const source of attempt.sources) { const sourceDetails = element("details"); const key = `source-${attemptIndex}-${source.chunk_id}`; sourceDetails.dataset.disclosureKey = key; const sourceSummary = element("summary", `${source.document_name} · Version ${source.version}${attempt.citations?.includes(source.chunk_id) ? " · Cited" : " · Retrieved"}`); sourceSummary.dataset.focusKey = key; sourceDetails.append(sourceSummary, element("pre", source.excerpt, "knowledge-content")); details.append(sourceDetails); }
        }
        body.append(details); card.append(body);
        card.querySelectorAll<HTMLDetailsElement>("details[data-disclosure-key]").forEach(detail => { detail.open = openStates.get(detail.dataset.disclosureKey) ?? false; });
        if (previous) previous.replaceWith(card); else suggestions.append(card);
        if (focusKey) Array.from(card.querySelectorAll<HTMLElement>("[data-focus-key]")).find(node => node.dataset.focusKey === focusKey)?.focus();
        entry = { node: card, snapshot }; generationCards.set(item.id, entry);
      }
      // Move only out-of-order nodes, so a focused unchanged entry remains in place.
      for (let index = 0; index < ordered.length; index++) {
        const node = generationCards.get(ordered[index].id)!.node;
        if (suggestions.children[index] !== node) suggestions.insertBefore(node, suggestions.children[index] ?? null);
      }
      const active = items.some(item => item.status === "queued" || item.status === "running");
      generate.disabled = active || !selectedGenerationBase;
      generationStatus.textContent = active ? "Generation is queued or running. You can continue editing." : items.length ? "Review the suggestion and its sources before use." : "No suggestions yet.";
      if (active) window.setTimeout(() => { void refreshGenerations(); }, 3000);
    } catch { generationStatus.textContent = "Could not load generation status. Reopen the ticket to retry."; }
  };
  const renderBaseSelection = (): void => {
    baseSlot.replaceChildren(selectionControl("Information for this suggestion", generationChoices, selectedGenerationBase ? [selectedGenerationBase] : [], false, values => { selectedGenerationBase = values[0]; void refreshGenerations(); }, "Choose an option"));
  };
  renderBaseSelection();
  generate.addEventListener("click", async () => {
    generate.disabled = true; generationStatus.textContent = "Requesting generation…";
    try { const result = await fetch(generationEndpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ knowledge_base_id: selectedGenerationBase === "general" ? null : selectedGenerationBase }) }); if (!result.ok) { generationStatus.textContent = result.status === 429 ? "The generation queue is full. Try again later." : "Could not request generation. Try again."; generate.disabled = false; return; } await refreshGenerations(); }
    catch { generationStatus.textContent = "Could not request generation. Try again."; generate.disabled = false; }
  });
  void fetch("/api/knowledge/bases").then(async response => { if (!response.ok) throw new Error(); const bases = await response.json() as KnowledgeBase[]; generationChoices = [...generationChoices, ...bases.map(base => ({ value: base.id, label: base.name }))]; renderBaseSelection(); }).catch(() => { baseNotice.textContent = "Knowledge bases are unavailable; you can still choose to continue without one."; }).finally(() => { void refreshGenerations(); });
  void load();
  return section;
}
async function render(background = false): Promise<void> {
  window.clearTimeout(refreshTimer);
  const current = ++requestVersion;
  const path = location.hash.split("?")[0];
  const inOptions = path === "#/options";
  const inKnowledge = path === "#/knowledge";
  const inUsers = path === "#/users";
  const restricted = inOptions || inUsers;
  document.querySelectorAll<HTMLAnchorElement>(".workspace-nav a").forEach(link => {
    const active = link.dataset.nav === (inKnowledge ? "knowledge" : inOptions ? "options" : inUsers ? "users" : "inbox");
    if (active) link.setAttribute("aria-current", "page"); else link.removeAttribute("aria-current");
  });
  document.querySelector<HTMLElement>("#header-location")!.textContent = inKnowledge ? "Knowledge" : inOptions ? "Tags" : inUsers ? "Users" : "Inbox";
  if (restricted && currentAccount()?.role !== "administrator") {
    title.textContent = "Access unavailable";
    document.querySelector<HTMLElement>("#page-description")!.textContent = "This area is available to administrators.";
    showState("You do not have access", "Return to the inbox to continue working.", () => { location.hash = "#/"; }, false, "Go to inbox");
    return;
  }
  if (inUsers) {
    title.textContent = "Users";
    document.querySelector<HTMLElement>("#page-description")!.textContent = "Manage workspace access.";
    const users = element("div", undefined, "auth-form users-workspace");
    content.replaceChildren(users);
    renderUsers(users);
    return;
  }
  if (inKnowledge) { await renderKnowledge(current); return; }
  if (path === "#/options") { await renderOptions(current); return; }
  const id = path.startsWith("#/tickets/") ? path.slice("#/tickets/".length) : "";
  const state = inboxState();
  title.textContent = id ? "Ticket details" : "Inbox";
  document.querySelector<HTMLElement>("#page-description")!.textContent = "Received tickets, ready to inspect.";
  if (state.invalid) { showState("Invalid inbox link", "This link contains an invalid filter or page. Clear the filters to continue.", () => { filterDraft = null; location.hash = "#/"; }, false, "Clear filters"); return; }
  if (!id && (!background || !document.querySelector("#inbox-results"))) renderInboxControls(state);
  if (id && !background) showState("Loading tickets…", "Please wait while we retrieve the latest information.");
  try {
    const response = await fetch(id ? `/api/tickets/${encodeURIComponent(id)}` : `/api/tickets?${stateQuery(state)}`, { cache: "no-store", signal: AbortSignal.timeout(10000) });
    if (current !== requestVersion) return;
    if (id && response.status === 404) { showState("Ticket unavailable", "This ticket could not be found.", undefined, true); return; }
    if (!response.ok) throw new Error("Request failed");
    if (id) {
      const ticket = await response.json() as Ticket;
      if (current !== requestVersion) return;
      const article = element("article", undefined, "detail");
      const heading = element("h2", ticket.subject, "ticket-subject");
      const metadata = element("dl", undefined, "metadata");
      metadata.append(element("dt", "Received"), element("dd", formatDate(ticket.received_at)), element("dt", "Ticket ID"), element("dd", ticket.id, "ticket-id"));
      const body = element("div", undefined, "description");
      body.append(element("h3", "Description"), element("p", ticket.description));
      const classification = element("section", undefined, "classification");
      classification.setAttribute("aria-label", "Ticket tags");
      for (const kind of ["category", "priority"] as const) {
        const currentOptions = kind === "category" ? ticket.effective_categories : ticket.effective_priority ? [ticket.effective_priority] : [];
        const label = kind === "category" ? "Categories" : "Priority";
        const row = element("div", undefined, "detail-tag-row");
        row.append(element("span", label, "detail-tag-label"));
        const control = element("div", undefined, "detail-tag-control");
        const editButton = element("button", undefined, "tag-edit-button"); editButton.type = "button";
        editButton.setAttribute("aria-label", `Change ${label.toLowerCase()}${currentOptions.length ? `: ${currentOptions.map(option => option.name).join(", ")}` : ""}`);
        if (currentOptions.length) currentOptions.forEach(option => editButton.append(tag(option)));
        else editButton.append(element("span", ticket.category_origin === "manual" && kind === "category" ? "No categories" : ticket.classification_status === "completed" ? "Undetermined" : "Not assigned", "tag tag-empty"));
        editButton.append(element("span", "Edit", "tag-edit-label"));
        const form = element("form", undefined, "tag-editor"); form.hidden = true;
        const field = element("div", undefined, "tag-editor-field");
        const save = element("button", "Save"); save.type = "submit";
        const cancel = element("button", "Cancel"); cancel.type = "button";
        const feedback = element("p", "", "tag-feedback"); feedback.setAttribute("role", "status");
        form.append(field, save, cancel, feedback);
        let needsReload = false;
        const close = (): void => { form.hidden = true; editButton.hidden = false; delete classification.dataset.editing; classification.querySelectorAll<HTMLButtonElement>(".tag-edit-button").forEach(button => { button.disabled = false; }); if (needsReload) void render(true); else editButton.focus(); };
        cancel.addEventListener("click", close);
        editButton.addEventListener("click", async () => {
          classification.dataset.editing = "true"; classification.querySelectorAll<HTMLButtonElement>(".tag-edit-button").forEach(button => { button.disabled = true; }); editButton.hidden = true; form.hidden = false; feedback.textContent = "Loading options…"; save.disabled = true;
          try {
            const result = await fetch("/api/classification-options", { cache: "no-store", signal: AbortSignal.timeout(10000) });
            if (!result.ok) throw new Error();
            const choices = await result.json() as ClassificationOption[];
            field.replaceChildren();
            if (kind === "category") {
              const group = element("fieldset", undefined, "category-choices"); group.append(element("legend", "Select categories"));
              for (const choice of choices.filter(item => item.kind === kind && (item.active || currentOptions.some(option => option.id === item.id)))) {
                const row = element("label"); const input = element("input"); input.type = "checkbox"; input.value = choice.id; input.checked = currentOptions.some(option => option.id === choice.id);
                row.append(input, element("span", `${choice.name}${choice.active ? "" : " (inactive)"}`)); group.append(row);
              }
              field.append(group);
            } else {
              const fieldLabel = element("label", "Select priority"); const select = element("select"); select.required = true;
              const prompt = element("option", "Choose priority"); prompt.value = ""; select.append(prompt);
              for (const choice of choices.filter(item => item.kind === kind && item.active)) { const option = element("option", choice.name); option.value = choice.id; select.append(option); }
              if (currentOptions[0]?.active) select.value = currentOptions[0].id;
              fieldLabel.append(select); field.append(fieldLabel);
            }
            feedback.textContent = ""; save.disabled = false; field.querySelector<HTMLElement>("input, select")?.focus();
          } catch { feedback.textContent = "Could not load options. Cancel and try again."; }
        });
        form.addEventListener("submit", async event => {
          event.preventDefault(); const select = field.querySelector<HTMLSelectElement>("select"); if (select && !select.value) { select.reportValidity(); return; }
          const categoryIds = Array.from(field.querySelectorAll<HTMLInputElement>('input[type="checkbox"]:checked'), input => input.value);
          save.disabled = true; cancel.disabled = true; feedback.textContent = "Saving…";
          try {
            const result = await fetch(`/api/tickets/${encodeURIComponent(ticket.id)}/classification`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ expected_revision: ticket.classification_revision, ...(kind === "category" ? { category_ids: categoryIds } : { priority_id: select!.value }) }), signal: AbortSignal.timeout(10000) });
            if (result.status === 409) { needsReload = true; cancel.textContent = "Reload"; feedback.textContent = "This classification changed elsewhere. Reload to see the latest values."; return; }
            if (result.status === 422) { feedback.textContent = "This option is no longer available. Cancel and choose another."; return; }
            if (!result.ok) throw new Error();
            delete classification.dataset.editing; await render(true);
          } catch { feedback.textContent = "Could not save this tag. Check the connection and try again."; }
          finally { save.disabled = false; cancel.disabled = false; }
        });
        control.append(editButton, form); row.append(control); classification.append(row);
      }
      classification.append(element("p", `Classification: ${statusLabel(ticket.classification_status)}`, "classification-status"));
      const details = element("details", undefined, "classification-details");
      details.append(element("summary", "Classification details"));
      if (ticket.classification_status === "completed" && ticket.classification_result) {
        details.append(element("p", `${ticket.classification_result} (${ticket.classification_source === "simulated" ? "simulated" : "classification"})`));
      }
      const origin = (value: string | null): string => value === "manual" ? "Manual" : value === "model" ? "Model suggestion" : value === "simulated" ? "Simulated" : "Undetermined";
      details.append(element("p", `Category: ${origin(ticket.category_origin)} · Priority: ${origin(ticket.priority_origin)}`));
      if (ticket.classification_source === "model") details.append(element("p", `Model categories: ${ticket.classification_categories.map(option => `${option.name}${option.active ? " (inactive)" : ""}`).join(", ") || "Undetermined"}`));
      classification.append(details);
      if (ticket.classification_status === "failed") {
        const reasons: Record<string, string> = { MODEL_CONFIGURATION: "Check the worker model, credential and timeout settings, then restart the worker.", NO_OPTIONS: "Activate at least one category and one priority.", INVALID_MODEL_OUTPUT: "The model returned an invalid or outdated suggestion.", MODEL_PROVIDER: "The model provider could not complete the request." };
        classification.append(element("p", `${reasons[ticket.classification_failure_reason ?? ""] ?? "Classification could not be completed."} You can try again.`));
        const retry = element("button", "Retry classification");
        retry.type = "button";
        const feedback = element("p", "", "retry-feedback");
        feedback.setAttribute("role", "status");
        retry.addEventListener("click", async () => {
          retry.disabled = true;
          feedback.textContent = "Requesting another attempt…";
          try {
            const response = await fetch(`/api/tickets/${encodeURIComponent(ticket.id)}/classification/retry`, { method: "POST", signal: AbortSignal.timeout(10000) });
            if (response.status === 409) { await render(true); return; }
            if (!response.ok) throw new Error("Retry failed");
            await render(true);
          } catch {
            retry.disabled = false;
            feedback.textContent = "Could not request a retry. Please try again.";
          }
        });
        classification.append(retry, feedback);
      }
      if (background && responseEditor?.ticketId === id && responseEditor.node.isConnected) {
        if (document.querySelector('.detail .classification[data-editing="true"]')) { scheduleRefresh(); return; }
        document.querySelector(".detail .classification")?.replaceWith(classification);
        if (["pending", "processing"].includes(ticket.classification_status)) scheduleRefresh();
        return;
      }
      const editor = responseEditor?.ticketId === id ? responseEditor.node : makeResponseEditor(id);
      article.append(backLink(), heading, classification, metadata, body, editor);
      content.replaceChildren(article);
      if (["pending", "processing"].includes(ticket.classification_status)) scheduleRefresh();
    } else {
      const page = await response.json() as TicketPage;
      if (current !== requestVersion) return;
      const activeResults = document.querySelector<HTMLElement>("#inbox-results");
      if (background && activeResults && (activeResults.contains(document.activeElement) || activeResults.querySelector('.selection-trigger[aria-expanded="true"]'))) { scheduleRefresh(); return; }
      const lastPage = Math.max(1, Math.ceil(page.total / page.page_size));
      if (state.page > lastPage) { history.replaceState(null, "", inboxHref({ ...state, page: lastPage })); void render(); return; }
      const results = document.querySelector<HTMLElement>("#inbox-results")!;
      if (!page.items.length) {
        const empty = element("div", undefined, "state");
        const filtered = !!(state.q.trim() || state.statuses.length || state.date_from || state.date_to || state.category_ids.length || state.priority_ids.length);
        empty.append(element("h2", filtered ? "No matching tickets" : "No tickets yet"), element("p", filtered ? "Try changing or clearing the filters." : "Received tickets will appear here when they are submitted."));
        if (filtered) { const clear = element("button", "Clear filters"); clear.type = "button"; clear.addEventListener("click", () => { filterDraft = null; navigateInbox(clearFilters(state)); }); empty.append(clear); }
        results.replaceChildren(empty, pagination(state, page, lastPage)); if (state.statuses.some(value => value === "pending" || value === "processing")) scheduleRefresh(); return;
      }
      const list = element("ul", undefined, "ticket-list");
      for (const ticket of page.items) {
        const row = element("li");
        const link = element("a", undefined, "ticket-row");
        link.href = `#/tickets/${encodeURIComponent(ticket.id)}?${stateQuery(state)}`;
        link.addEventListener("click", () => { filterDraft = null; });
        const subject = element("span", ticket.subject, "row-subject");
        const tags = element("span", undefined, "row-tags");
        for (const [label, choices] of [["Categories", ticket.effective_categories], ["Priority", ticket.effective_priority ? [ticket.effective_priority] : []]] as const) {
          const group = element("span", undefined, "row-tag-group");
          const missing = ticket.classification_status === "completed" ? "Undetermined" : ["pending", "processing"].includes(ticket.classification_status) ? "Pending" : "Unavailable";
          if (choices.length) { group.append(element("span", `${label}: `, "visually-hidden")); choices.forEach(option => group.append(tag(option))); }
          else group.append(element("span", `${label}: ${label === "Categories" && ticket.category_origin === "manual" ? "None" : missing}`, "tag tag-empty"));
          tags.append(group);
        }
        if (ticket.classification_source === "simulated") subject.append(element("small", `${ticket.classification_result ?? "Classification"} (simulated)`, "row-suggestion"));
        const date = element("time", formatDate(ticket.received_at), "row-date");
        const status = element("span", statusLabel(ticket.classification_status), "row-status");
        status.dataset.status = ticket.classification_status;
        date.dateTime = ticket.received_at;
        const arrow = element("span", "→", "arrow"); arrow.setAttribute("aria-hidden", "true");
        link.append(subject, tags, status, date, arrow); row.append(link); list.append(row);
      }
      results.replaceChildren(list, pagination(state, page, lastPage));
      if (page.items.some(ticket => ["pending", "processing"].includes(ticket.classification_status)) || state.statuses.some(value => value === "pending" || value === "processing")) scheduleRefresh();
    }
  } catch {
    if (background && responseEditor?.ticketId === id && responseEditor.node.isConnected) { scheduleRefresh(); return; }
    if (current === requestVersion) {
      if (id) showState("Unable to load tickets", "Check the API connection and try again.", () => { void render(); void checkHealth(); }, true);
      else { const results = document.querySelector<HTMLElement>("#inbox-results")!; const error = element("div", undefined, "state"); const retry = element("button", "Try again"); retry.type = "button"; retry.addEventListener("click", () => { void render(true); void checkHealth(); }); error.append(element("h2", "Unable to load tickets"), element("p", "Check the API connection and try again."), retry); results.replaceChildren(error); }
    }
  }
}
type KnowledgeBase = { id: string; name: string };
type KnowledgeDocument = { id: string; name: string; active: boolean; version_id: string; version: number; status: string; failure_reason: string | null; semantic_status: string | null; semantic_failure_reason: string | null };
let selectedKnowledgeBase = "";

async function renderKnowledge(current: number): Promise<void> {
  title.textContent = "Knowledge";
  document.querySelector<HTMLElement>("#page-description")!.textContent = "Manage the sources used to draft grounded responses.";
  showState("Loading knowledge…", "Retrieving your knowledge bases.");
  try {
    const response = await fetch("/api/knowledge/bases", { cache: "no-store" });
    if (!response.ok) throw new Error();
    const bases = await response.json() as KnowledgeBase[];
    if (current !== requestVersion) return;
    if (!bases.some(base => base.id === selectedKnowledgeBase)) selectedKnowledgeBase = bases[0]?.id ?? "";
    const wrapper = element("div", undefined, "options-page knowledge-page");
    const feedback = element("p", "", "options-feedback"); feedback.setAttribute("role", "status");
    const request = async (url: string, init: RequestInit, message: string): Promise<void> => {
      feedback.textContent = "Saving…";
      try {
        const result = await fetch(url, init);
        if (!result.ok) { const error = await result.json().catch(() => null); feedback.textContent = typeof error?.error?.message === "string" ? error.error.message : "Could not save. Check the content and try again."; return; }
        await renderKnowledge(current);
        const target = document.querySelector<HTMLElement>(".options-feedback"); if (target) target.textContent = message;
      } catch { feedback.textContent = "Could not save. Check the connection and try again."; }
    };
    const basesSection = element("section", undefined, "options-section");
    basesSection.append(element("h2", "Knowledge bases"));
    const baseForm = element("form", undefined, "option-form");
    const baseLabel = element("label", "New knowledge base"); const baseName = element("input"); baseName.required = true; baseName.maxLength = 200; baseLabel.append(baseName);
    const addBase = element("button", "Create base"); addBase.type = "submit"; baseForm.append(baseLabel, addBase);
    baseForm.addEventListener("submit", event => { event.preventDefault(); if (baseName.value.trim()) void request("/api/knowledge/bases", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: baseName.value }) }, "Knowledge base created."); });
    basesSection.append(baseForm);
    basesSection.append(selectionControl("Selected knowledge base", bases.map(base => ({ value: base.id, label: base.name })), selectedKnowledgeBase ? [selectedKnowledgeBase] : [], false, values => { selectedKnowledgeBase = values[0]; void renderKnowledge(current); }, "No knowledge bases"));
    wrapper.append(feedback, basesSection);
    if (selectedKnowledgeBase) {
      const docsResponse = await fetch(`/api/knowledge/bases/${encodeURIComponent(selectedKnowledgeBase)}/documents`, { cache: "no-store" });
      if (!docsResponse.ok) throw new Error();
      const documents = await docsResponse.json() as KnowledgeDocument[];
      if (current !== requestVersion) return;
      const section = element("section", undefined, "options-section"); section.append(element("h2", "Sources"), element("p", "Paste text or upload a UTF-8 .txt or .md file, up to 1 MB by default."));
      const form = element("form", undefined, "knowledge-form");
      const nameLabel = element("label", "Source name"); const name = element("input"); name.required = true; name.maxLength = 200; nameLabel.append(name);
      const textLabel = element("label", "Text"); const textInput = element("textarea"); textInput.rows = 5; textLabel.append(textInput);
      const fileLabel = element("label", "Or choose a file"); const file = element("input"); file.type = "file"; file.accept = ".txt,.md,text/plain,text/markdown"; fileLabel.append(file);
      const add = element("button", "Add source"); add.type = "submit"; form.append(nameLabel, textLabel, fileLabel, add);
      form.addEventListener("submit", event => { event.preventDefault(); const chosen = file.files?.[0]; if (!name.value.trim() || (!chosen && !textInput.value.trim())) { feedback.textContent = "Enter a name and text, or choose a file."; return; } const params = new URLSearchParams({ name: name.value }); if (chosen) params.set("filename", chosen.name); void request(`/api/knowledge/bases/${encodeURIComponent(selectedKnowledgeBase)}/documents?${params}`, { method: "POST", body: chosen ?? textInput.value }, "Source added for processing."); });
      section.append(form);
      if (!documents.length) section.append(element("p", "No sources yet. Add one to make it available for retrieval."));
      const list = element("ul", undefined, "option-list");
      for (const doc of documents) {
        const row = element("li", undefined, "knowledge-row");
        row.append(element("strong", doc.name), element("span", `Version ${doc.version} · ${doc.status}${doc.active ? "" : " · Inactive"}`));
        if (doc.failure_reason) row.append(element("p", doc.failure_reason));
        if (doc.semantic_status) row.append(element("span", `Semantic indexing: ${doc.semantic_status}`));
        if (doc.semantic_failure_reason && doc.semantic_status === "failed") row.append(element("p", doc.semantic_failure_reason));
        const inspect = element("button", "View text"); inspect.type = "button";
        inspect.addEventListener("click", async () => { try { const result = await fetch(`/api/knowledge/versions/${encodeURIComponent(doc.version_id)}`); if (!result.ok) throw new Error(); const version = await result.json() as { content: string }; const pre = element("pre", version.content, "knowledge-content"); row.append(pre); inspect.disabled = true; } catch { feedback.textContent = "Could not load this version."; } });
        row.append(inspect);
        if (doc.version === Math.max(...documents.filter(item => item.id === doc.id).map(item => item.version))) {
          const toggle = element("button", doc.active ? "Deactivate" : "Reactivate"); toggle.type = "button"; toggle.addEventListener("click", () => { void request(`/api/knowledge/documents/${encodeURIComponent(doc.id)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ active: !doc.active }) }, "Source updated."); }); row.append(toggle);
          const update = element("details"); update.append(element("summary", "Add a new version")); const updateForm = element("form", undefined, "knowledge-form"); const updateLabel = element("label", "Replacement text"); const updateText = element("textarea"); updateText.rows = 4; updateLabel.append(updateText); const updateFileLabel = element("label", "Or choose a replacement file"); const updateFile = element("input"); updateFile.type = "file"; updateFile.accept = ".txt,.md"; updateFileLabel.append(updateFile); const submit = element("button", "Add version"); submit.type = "submit"; updateForm.append(updateLabel, updateFileLabel, submit); updateForm.addEventListener("submit", event => { event.preventDefault(); const chosen = updateFile.files?.[0]; if (!chosen && !updateText.value.trim()) { feedback.textContent = "Enter text or choose a file."; return; } const params = new URLSearchParams(); if (chosen) params.set("filename", chosen.name); void request(`/api/knowledge/documents/${encodeURIComponent(doc.id)}/versions?${params}`, { method: "POST", body: chosen ?? updateText.value }, "New version queued."); }); update.append(updateForm); row.append(update);
        }
        if (doc.status === "failed") { const retry = element("button", "Retry processing"); retry.type = "button"; retry.addEventListener("click", () => { void request(`/api/knowledge/versions/${encodeURIComponent(doc.version_id)}/retry`, { method: "POST" }, "Processing queued."); }); row.append(retry); }
        if (doc.semantic_status === "failed") { const retry = element("button", "Retry semantic indexing"); retry.type = "button"; retry.addEventListener("click", () => { void request(`/api/knowledge/versions/${encodeURIComponent(doc.version_id)}/semantic-retry`, { method: "POST" }, "Semantic indexing queued."); }); row.append(retry); }
        list.append(row);
      }
      section.append(list); wrapper.append(section);
    } else wrapper.append(element("p", "Create a knowledge base to add your first source."));
    content.replaceChildren(wrapper);
  } catch { if (current === requestVersion) showState("Unable to load knowledge", "Check the API connection and try again.", () => { void render(); }); }
}

async function renderOptions(current: number): Promise<void> {
  title.textContent = "Tags";
  document.querySelector<HTMLElement>("#page-description")!.textContent = "Manage categories, priorities and their colors.";
  showState("Loading options…", "Please wait while we retrieve the current options.");
  try {
    const response = await fetch("/api/classification-options", { cache: "no-store", signal: AbortSignal.timeout(10000) });
    if (!response.ok) throw new Error();
    const items = await response.json() as ClassificationOption[];
    if (current !== requestVersion) return;
    const wrapper = element("div", undefined, "options-page");
    const feedback = element("p", "", "options-feedback"); feedback.setAttribute("role", "status");
    const save = async (url: string, method: string, data: object, success: string): Promise<void> => {
      feedback.textContent = "Saving…";
      wrapper.querySelectorAll("button").forEach(button => { button.disabled = true; });
      try {
        const result = await fetch(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(data), signal: AbortSignal.timeout(10000) });
        if (!result.ok) { feedback.textContent = result.status === 409 ? "An option with that name already exists in this list." : result.status === 422 ? "Enter a valid name and color." : "Could not save the option. Try again."; return; }
        await renderOptions(current);
        const updated = document.querySelector<HTMLElement>(".options-feedback"); if (updated && current === requestVersion) updated.textContent = success;
      } catch { feedback.textContent = "Could not save the option. Check the connection and try again."; }
      finally { wrapper.querySelectorAll("button").forEach(button => { button.disabled = false; }); }
    };
    wrapper.append(feedback);
    for (const kind of ["category", "priority"] as const) {
      const section = element("section", undefined, "options-section");
      section.append(element("h2", kind === "category" ? "Categories" : "Priorities"));
      const form = element("form", undefined, "option-form");
      const label = element("label", `New ${kind}`); const input = element("input"); input.required = true; input.maxLength = 200; label.append(input);
      const colorLabel = element("label", "Color", "color-label"); const color = element("input"); color.type = "color"; color.value = "#64748b"; colorLabel.append(color);
      const add = element("button", "Add option"); add.type = "submit"; form.append(label, colorLabel, add);
      form.addEventListener("submit", event => { event.preventDefault(); if (!input.value.trim()) { feedback.textContent = "Enter a nonblank name."; return; } void save("/api/classification-options", "POST", { kind, name: input.value, color: color.value }, "Option added."); });
      section.append(form);
      const matching = items.filter(item => item.kind === kind);
      if (!matching.length) section.append(element("p", "No options yet. Add one to enable classification."));
      const list = element("ul", undefined, "option-list");
      for (const item of matching) {
        const row = element("li", undefined, "option-row");
        const nameText = element("span", undefined, "option-name"); nameText.append(tag(item));
        const edit = element("form", undefined, "option-edit"); edit.hidden = true;
        const nameLabel = element("label", `Name for ${item.name}`); nameLabel.className = "visually-hidden"; const name = element("input"); name.id = `option-${item.id}`; nameLabel.htmlFor = name.id; name.value = item.name; name.required = true; name.maxLength = 200;
        const editColorLabel = element("label", `Color for ${item.name}`, "visually-hidden"); const editColor = element("input"); editColor.type = "color"; editColor.id = `color-${item.id}`; editColorLabel.htmlFor = editColor.id; editColor.value = item.color;
        const rename = element("button", "Save"); rename.type = "submit"; const cancel = element("button", "Cancel"); cancel.type = "button"; edit.append(nameLabel, name, editColorLabel, editColor, rename, cancel);
        const editButton = element("button", "Edit"); editButton.type = "button"; editButton.setAttribute("aria-label", `Edit ${item.name}`);
        editButton.addEventListener("click", () => { nameText.hidden = true; editButton.hidden = true; edit.hidden = false; name.focus(); });
        cancel.addEventListener("click", () => { name.value = item.name; editColor.value = item.color; feedback.textContent = ""; edit.hidden = true; nameText.hidden = false; editButton.hidden = false; editButton.focus(); });
        edit.addEventListener("submit", event => { event.preventDefault(); if (!name.value.trim()) { feedback.textContent = "Enter a nonblank name."; return; } void save(`/api/classification-options/${encodeURIComponent(item.id)}`, "PATCH", { name: name.value, color: editColor.value }, "Option updated."); });
        const state = element("span", item.active ? "Active" : "Inactive", "option-state");
        const toggle = element("button", item.active ? "Deactivate" : "Reactivate"); toggle.type = "button";
        toggle.addEventListener("click", () => { if (item.active && !window.confirm(`Deactivate “${item.name}”? Existing ticket associations will remain visible.`)) return; void save(`/api/classification-options/${encodeURIComponent(item.id)}`, "PATCH", { active: !item.active }, item.active ? "Option deactivated." : "Option reactivated."); });
        row.append(nameText, edit, state, editButton, toggle); list.append(row);
      }
      section.append(list); wrapper.append(section);
    }
    content.replaceChildren(wrapper);
  } catch { if (current === requestVersion) showState("Unable to load options", "Check the API connection and try again.", () => { void render(); }); }
}

type FilterDraft = Pick<InboxState, "q" | "statuses" | "date_from" | "date_to" | "category_ids" | "priority_ids">;
type Choice = { value: string; label: string };
let filterDraft: FilterDraft | null = null;
let knownOptions: ClassificationOption[] = [];
function copyDraft(state: InboxState): FilterDraft {
  return { q: state.q, statuses: [...state.statuses], date_from: state.date_from, date_to: state.date_to, category_ids: [...state.category_ids], priority_ids: [...state.priority_ids] };
}
function clearFilters(state: InboxState): InboxState {
  return { ...state, q: "", statuses: [], date_from: "", date_to: "", category_ids: [], priority_ids: [], page: 1, invalid: false };
}
let selectSequence = 0;
function selectionControl(label: string, choices: Choice[], values: string[], multiple: boolean, change: (values: string[]) => void, placeholder: string): HTMLElement {
  const wrapper = element("div", undefined, "selection-control");
  const labelNode = element("span", label, "control-label");
  const triggerButton = element("button", undefined, "selection-trigger"); triggerButton.type = "button";
  const labelId = `selection-label-${++selectSequence}`; labelNode.id = labelId;
  const valueNode = element("span", "", "selection-value"); valueNode.id = `${labelId}-value`;
  const chevron = element("span", undefined, "chevron"); chevron.setAttribute("aria-hidden", "true");
  triggerButton.append(valueNode, chevron); triggerButton.setAttribute("aria-labelledby", `${labelId} ${valueNode.id}`);
  triggerButton.setAttribute("aria-expanded", "false");
  const popup = element("div", undefined, "selection-menu"); popup.hidden = true;
  popup.setAttribute("role", "group"); popup.setAttribute("aria-labelledby", labelId);
  popup.id = `${labelId}-menu`; triggerButton.setAttribute("aria-controls", popup.id);
  let selected = [...values];
  const update = (): void => {
    const labels = selected.map(value => choices.find(choice => choice.value === value)?.label ?? "Unavailable option");
    valueNode.textContent = labels.length === 0 ? placeholder : labels.length === 1 ? labels[0] : `${labels.length} selected`;
    popup.querySelectorAll<HTMLInputElement>("input").forEach(input => { input.checked = selected.includes(input.value); });
  };
  const close = (focus = false): void => { popup.hidden = true; triggerButton.setAttribute("aria-expanded", "false"); if (focus) triggerButton.focus(); };
  for (const choice of choices) {
    const row = element("label", undefined, "selection-option");
    const input = element("input"); input.type = multiple ? "checkbox" : "radio"; input.name = labelId; input.value = choice.value;
    row.append(input, element("span", choice.label)); popup.append(row);
    input.addEventListener("change", () => {
      selected = multiple ? (input.checked ? [...selected, choice.value] : selected.filter(value => value !== choice.value)) : [choice.value];
      update(); change([...selected]); if (!multiple) close(true);
    });
  }
  triggerButton.disabled = choices.length === 0;
  triggerButton.addEventListener("click", () => {
    if (!popup.hidden) { close(); return; }
    popup.hidden = false; triggerButton.setAttribute("aria-expanded", "true");
    (popup.querySelector<HTMLInputElement>("input:checked") ?? popup.querySelector<HTMLInputElement>("input"))?.focus();
  });
  popup.addEventListener("keydown", event => {
    if (event.key === "Escape") { event.preventDefault(); close(true); return; }
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
    event.preventDefault(); const inputs = Array.from(popup.querySelectorAll<HTMLInputElement>("input"));
    const index = inputs.indexOf(document.activeElement as HTMLInputElement);
    inputs[(index + (event.key === "ArrowDown" ? 1 : -1) + inputs.length) % inputs.length]?.focus();
  });
  const dismiss = (event: PointerEvent): void => {
    if (!wrapper.isConnected) { document.removeEventListener("pointerdown", dismiss); return; }
    if (!wrapper.contains(event.target as Node)) close();
  };
  document.addEventListener("pointerdown", dismiss);
  wrapper.append(labelNode, triggerButton, popup); update(); return wrapper;
}
function pagination(state: InboxState, page: TicketPage, lastPage: number): HTMLElement {
  const navigation = element("nav", undefined, "pagination"); navigation.setAttribute("aria-label", "Ticket pages");
  const summary = element("span", page.total ? `${(page.page - 1) * page.page_size + 1}–${(page.page - 1) * page.page_size + page.items.length} of ${page.total} tickets` : "0 tickets", "page-summary");
  const controls = element("div", undefined, "page-controls");
  const size = selectionControl("Per page", pageSizes.map(value => ({ value: String(value), label: String(value) })), [String(state.page_size)], false, values => navigateInbox({ ...state, page: 1, page_size: Number(values[0]) }, true), "25");
  size.classList.add("page-size");
  const prev = element("button", "Previous"); prev.type = "button"; prev.disabled = page.page <= 1; prev.addEventListener("click", () => navigateInbox({ ...state, page: state.page - 1 }, true));
  const next = element("button", "Next"); next.type = "button"; next.disabled = page.page >= lastPage; next.addEventListener("click", () => navigateInbox({ ...state, page: state.page + 1 }, true));
  controls.append(prev, element("span", `${page.page} / ${lastPage}`), next); navigation.append(summary, size, controls); return navigation;
}
function renderInboxControls(state: InboxState): void {
  if (!filterDraft) filterDraft = copyDraft(state);
  const draft = filterDraft;
  const form = element("form", undefined, "filters"); form.setAttribute("aria-label", "Filter tickets");
  const makeInput = (labelText: string, type: string, value: string, onInput: (value: string) => void): HTMLInputElement => {
    const label = element("label", labelText); const input = element("input"); input.type = type; input.value = value; label.append(input);
    input.addEventListener("input", () => onInput(input.value)); form.append(label); return input;
  };
  const q = makeInput("Search title", "search", draft.q, value => { draft.q = value; }); q.placeholder = "Search ticket titles"; q.parentElement!.classList.add("search-field");
  const selects = element("div", undefined, "filter-selects");
  const status = selectionControl("Classification status", statuses.map(value => ({ value, label: statusLabel(value) })), draft.statuses, true, values => { draft.statuses = values; }, "All statuses");
  const categorySlot = element("div"), prioritySlot = element("div");
  selects.append(status, categorySlot, prioritySlot); form.append(selects);
  const dates = element("div", undefined, "date-group"); const dateTitle = element("span", "Received date (UTC)", "control-label"); dates.append(dateTitle);
  const dateFields = element("div", undefined, "date-fields");
  const dateInput = (labelText: string, value: string, key: "date_from" | "date_to"): HTMLInputElement => {
    const label = element("label", labelText); const input = element("input"); input.type = "date"; input.value = value;
    input.addEventListener("input", () => { draft[key] = input.value; validateDates(); }); label.append(input); dateFields.append(label); return input;
  };
  const from = dateInput("From", draft.date_from, "date_from"); const to = dateInput("To", draft.date_to, "date_to");
  const validateDates = (): void => { to.setCustomValidity(from.value && to.value && from.value > to.value ? "End date must be on or after start date." : ""); };
  dates.append(dateFields); form.append(dates);
  const actions = element("div", undefined, "filter-actions"); const apply = element("button", "Apply filters"); apply.type = "submit"; const clear = element("button", "Clear filters"); clear.type = "button"; actions.append(apply, clear); form.append(actions);
  form.addEventListener("submit", event => { event.preventDefault(); validateDates(); if (!form.reportValidity()) return; const next = { ...state, ...draft, q: draft.q.trim(), page: 1 }; filterDraft = null; navigateInbox(next); });
  clear.addEventListener("click", () => { filterDraft = null; navigateInbox(clearFilters(state)); });
  const chips = element("div", undefined, "active-filters");
  const drawChips = (): void => {
    chips.replaceChildren();
    const addChip = (label: string, key: "statuses" | "category_ids" | "priority_ids", value: string): void => {
      const button = element("button", `${label} ×`, "filter-chip"); button.type = "button"; button.setAttribute("aria-label", `Remove ${label} filter`);
      button.addEventListener("click", () => { draft[key] = draft[key].filter(item => item !== value); navigateInbox({ ...state, [key]: state[key].filter(item => item !== value), page: 1 }, true); }); chips.append(button);
    };
    for (const value of state.statuses) addChip(statusLabel(value), "statuses", value);
    for (const key of ["category_ids", "priority_ids"] as const) for (const value of state[key]) addChip(knownOptions.find(option => option.id === value)?.name ?? "Unavailable option", key, value);
    for (const [key, label] of [["q", "Search"], ["date_from", "From"], ["date_to", "To"]] as const) if (state[key]) {
      const button = element("button", `${label}: ${state[key]} ×`, "filter-chip"); button.type = "button"; button.setAttribute("aria-label", `Remove ${label} filter`);
      button.addEventListener("click", () => { draft[key] = ""; navigateInbox({ ...state, [key]: "", page: 1 }, true); }); chips.append(button);
    }
    if (chips.childElementCount) chips.prepend(element("span", "Applied filters", "chip-label"));
  };
  const drawOptions = (items: ClassificationOption[], unavailable = false, loading = false): void => {
    knownOptions = items;
    for (const [kind, slot, key, label] of [["category", categorySlot, "category_ids", "Category"], ["priority", prioritySlot, "priority_ids", "Priority"]] as const) {
      const choices = items.filter(item => item.kind === kind).map(item => ({ value: item.id, label: `${item.name}${item.active ? "" : " (inactive)"}` }));
      for (const selected of draft[key]) if (!choices.some(choice => choice.value === selected)) choices.push({ value: selected, label: "Unavailable option" });
      slot.replaceChildren(selectionControl(label, choices, draft[key], true, values => { draft[key] = values; }, loading ? "Loading options…" : unavailable ? "Options unavailable" : `All ${kind === "category" ? "categories" : "priorities"}`));
    }
    drawChips();
  };
  const optionFeedback = element("div", undefined, "option-load-feedback"); optionFeedback.setAttribute("role", "status");
  form.insertBefore(optionFeedback, dates);
  const loadOptions = (): void => {
    optionFeedback.textContent = "Loading classification options…";
    void fetch("/api/classification-options", { cache: "no-store", signal: AbortSignal.timeout(10000) }).then(async response => {
      if (!response.ok) throw new Error();
      const items = await response.json() as ClassificationOption[];
      if (form.isConnected) { optionFeedback.textContent = ""; drawOptions(items); }
    }).catch(() => {
      if (!form.isConnected) return;
      drawOptions(knownOptions, true);
      optionFeedback.textContent = "Classification options could not be loaded. ";
      const retry = element("button", "Try again", "inline-retry"); retry.type = "button"; retry.addEventListener("click", loadOptions); optionFeedback.append(retry);
    });
  };
  drawOptions(knownOptions, false, knownOptions.length === 0); loadOptions();
  const results = element("div"); results.id = "inbox-results"; results.setAttribute("aria-live", "polite"); const loading = element("div", undefined, "state"); loading.append(element("h2", "Loading tickets…"), element("p", "Please wait while we retrieve the latest information.")); results.append(loading);
  content.replaceChildren(form, chips, results);
}
async function checkHealth(): Promise<void> {
  try {
    const response = await fetch("/health", { signal: AbortSignal.timeout(5000), cache: "no-store" });
    if (!response.ok || (await response.json()).status !== "ok") throw new Error("Unavailable");
    health.textContent = "API available"; health.dataset.state = "available";
  } catch { health.textContent = "API unavailable"; health.dataset.state = "unavailable"; }
}
window.addEventListener("beforeunload", event => {
  if (responseEditor?.dirty()) { event.preventDefault(); event.returnValue = ""; }
});
window.addEventListener("hashchange", () => {
  if (restoringHash) { restoringHash = false; return; }
  const nextPath = location.hash.split("?")[0];
  const leavingEditor = responseEditor && nextPath !== `#/tickets/${responseEditor.ticketId}`;
  if (leavingEditor && responseEditor?.dirty() && !window.confirm("You have unsaved response changes. Leave without saving?")) {
    restoringHash = true; location.replace(currentHash || "#/"); return;
  }
  if (leavingEditor) responseEditor = null;
  currentHash = location.hash;
  if (!preserveDraftOnNavigation) filterDraft = null;
  preserveDraftOnNavigation = false; void render(); title.focus();
});
document.addEventListener("lumen:identity", () => {
  const account = currentAccount();
  document.querySelector<HTMLElement>("#admin-nav")!.hidden = account?.role !== "administrator";
  const avatar = document.querySelector<HTMLElement>(".account-avatar")!;
  avatar.textContent = account?.username.slice(0, 1).toUpperCase() || "L";
  if (account && ["#/options", "#/users"].includes(location.hash.split("?")[0])) void render();
});
void initializeAuthentication(() => { void render(); }); void checkHealth();
