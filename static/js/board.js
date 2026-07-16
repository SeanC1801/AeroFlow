// File: static/js/board.js
// The controller: renders every view from state, wires events, talks to the API.

import { BoardState } from "./state.js";

const TASKS_API = "/api/v1/tasks";
const PROJECTS_API = "/api/v1/projects";
const COLORS = ["lime", "sunny", "aqua", "pink"];
const STATUSES = ["todo", "in_progress", "done", "approved"];
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

let dragActive = false;   // suppresses the post-drag click-to-flip

// ===========================================================================
// Network layer
// ===========================================================================
async function apiGetTasks(code) {
  const res = await fetch(`${TASKS_API}?project_code=${encodeURIComponent(code)}`);
  if (!res.ok) throw new Error(`GET tasks failed: ${res.status}`);
  return res.json();
}
async function apiPatchTask(id, changes) {
  const res = await fetch(`${TASKS_API}/${id}`, {
    method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(changes),
  });
  if (!res.ok) throw new Error(`PATCH task failed: ${res.status}`);
  return res.json();
}
async function apiCreateTask(task) {
  const res = await fetch(TASKS_API, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(task),
  });
  if (!res.ok) throw new Error(`POST task failed: ${res.status}`);
  return res.json();
}
async function apiDeleteTask(id) {
  const res = await fetch(`${TASKS_API}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE task failed: ${res.status}`);
}
async function apiGetProjects() {
  const res = await fetch(PROJECTS_API);
  if (!res.ok) throw new Error(`GET projects failed: ${res.status}`);
  return res.json();
}
async function apiGetProject(code) {
  const res = await fetch(`${PROJECTS_API}/${encodeURIComponent(code)}`);
  if (!res.ok) throw new Error(`GET project failed: ${res.status}`);
  return res.json();
}
async function apiPatchProject(code, changes) {
  const res = await fetch(`${PROJECTS_API}/${encodeURIComponent(code)}`, {
    method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(changes),
  });
  if (!res.ok) throw new Error(`PATCH project failed: ${res.status}`);
  return res.json();
}
async function apiCreateProject(title) {
  const res = await fetch(PROJECTS_API, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`POST project failed: ${res.status}`);
  return res.json();
}
async function apiDeleteProject(code) {
  const res = await fetch(`${PROJECTS_API}/${encodeURIComponent(code)}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE project failed: ${res.status}`);
}

// ===========================================================================
// Helpers
// ===========================================================================
function esc(s) { const d = document.createElement("div"); d.textContent = s ?? ""; return d.innerHTML; }
function dotColor(c) { return { lime: "#b6ff6b", sunny: "#ffeb6b", aqua: "#6bf5ff", pink: "#ffa1e8" }[c]; }
function el(id) { return document.getElementById(id); }

// ===========================================================================
// BOARD VIEW — card rendering (front summary + back execution hub)
// ===========================================================================
function subtaskRowHTML(st) {
  // EDIT mode: checkbox + editable text + delete.
  return `
    <div class="subtask-row ${st.done ? "done" : ""}" data-sid="${st.id}">
      <input type="checkbox" class="js-sub-done" ${st.done ? "checked" : ""}>
      <input type="text" class="js-sub-text" value="${esc(st.text)}">
      <span class="material-symbols-outlined subtask-del" data-action="sub-del" title="Remove">close</span>
    </div>`;
}

function subtaskReadHTML(st) {
  // READ-ONLY mode: checkbox stays toggleable (execution tracking); no text edit, no delete.
  return `
    <label class="ro-sub-row ${st.done ? "done" : ""}" data-sid="${st.id}">
      <input type="checkbox" class="js-ro-sub-done" data-sid="${st.id}" ${st.done ? "checked" : ""}>
      <span>${esc(st.text)}</span>
    </label>`;
}

function buildAssigneeOptions(task) {
  const members = BoardState.currentProject?.members || [];
  let html = `<option value="Unassigned" data-initials="??">Unassigned</option>`;
  for (const m of members) {
    const sel = (m.name === task.username) ? "selected" : "";
    html += `<option value="${esc(m.name)}" data-initials="${esc(m.initials)}" ${sel}>${esc(m.name)} (${esc(m.initials)})</option>`;
  }
  return html;
}

function cardHTML(task) {
  const colorDots = COLORS.map(
    (c) => `<span class="color-dot sticky-${c} ${c === task.color ? "selected" : ""}"
                   data-color="${c}" style="background:${dotColor(c)}"></span>`
  ).join("");
  const dayOptions = ['<option value="">— Unscheduled —</option>']
    .concat(DAYS.map((d) => `<option value="${d}" ${task.due_day === d ? "selected" : ""}>${d}</option>`))
    .join("");
  const subtasks = (task.subtasks || []).map(subtaskRowHTML).join("");
  const linkAnchor = task.deliverable_url
    ? `<a class="deliverable-link js-link-anchor" href="${esc(task.deliverable_url)}" target="_blank" rel="noopener">
         <span class="material-symbols-outlined text-[13px]">open_in_new</span>Open deliverable</a>`
    : `<span class="js-link-anchor text-[11px] opacity-50">No link yet</span>`;

  return `
    <div class="card-container sticky-${task.color}" data-id="${task.id}" draggable="true">
      <div class="card-inner">

        <!-- FRONT SUMMARY -->
        <div class="card-face card-face--front">
          <div class="card-face__surface">
            <div class="p-4 relative">
              <div class="avatar-badge">${esc(task.assignee_initials)}</div>
              <h3 class="font-label-sm text-[14px] font-bold text-on-surface leading-tight pr-8 js-title">${esc(task.title)}</h3>
              <p class="text-[11px] text-on-surface-variant mt-1 js-username">${esc(task.username)}</p>
              ${task.due_day ? `<span class="mini-badge inline-block mt-2 text-[9px] bg-white/70 px-2 py-0.5 rounded-full text-primary font-bold">${esc(task.due_day)}</span>` : ""}
            </div>
            <div class="card-toolbar">
              <!-- Pencil => Edit Mode ; Curved arrows (360) => Read-Only Mode -->
              <span class="material-symbols-outlined" data-action="edit" title="Edit task">edit</span>
              <span class="material-symbols-outlined" data-action="read" title="Flip to read">360</span>
              <span class="material-symbols-outlined trash-icon" data-action="delete" draggable="false" title="Delete task">delete</span>
            </div>
          </div>
        </div>

        <!-- BACK EXECUTION HUB — dual state (read-only vs editable) -->
        <div class="card-face card-face--back">
          <div class="card-face__surface">

          <!-- ================= STATE A: READ-ONLY ================= -->
          <div class="card-back-readonly">
            <div class="ro-main p-4 flex flex-col gap-2 board-scroll">
              <h3 class="ro-title">${esc(task.title)}</h3>
              ${task.due_day ? `<span class="ro-day-badge">${esc(task.due_day)}</span>` : ""}
              <label class="ro-label">Description</label>
              ${task.description
                ? `<p class="ro-desc">${esc(task.description)}</p>`
                : `<p class="ro-desc ro-empty">No description yet.</p>`}
              ${task.deliverable_url
                ? `<a class="ro-link" href="${esc(task.deliverable_url)}" target="_blank" rel="noopener">View Deliverable ↗</a>`
                : `<span class="ro-desc ro-empty">No deliverable linked.</span>`}
              ${(task.subtasks || []).length ? `<label class="ro-label mt-1">Sub-tasks</label>
              <div class="ro-subtasks flex flex-col gap-1">${(task.subtasks || []).map(subtaskReadHTML).join("")}</div>` : ""}
            </div>
            <div class="card-toolbar ro-toolbar">
              <span class="text-[10px] font-bold opacity-50 tracking-wide">READ ONLY</span>
              <!-- Bridge: jump into Edit Mode WITHOUT flipping the card around. -->
              <span class="material-symbols-outlined ro-edit-bridge" data-action="to-edit" title="Edit task">edit</span>
            </div>
          </div>

          <!-- ================= STATE B: EDITABLE ================= -->
          <div class="card-back-editable">

            <!-- PRIMARY reading/execution space (dominates the card back) -->
            <div class="card-back-main p-3 flex flex-col gap-2 board-scroll">
              <input class="edit-field js-edit-title font-bold" value="${esc(task.title)}" placeholder="Title">

              <label class="text-[10px] font-bold opacity-70">Assignee</label>
              <select class="assignee-select js-edit-assignee">${buildAssigneeOptions(task)}</select>

              <label class="text-[10px] font-bold opacity-70">Description</label>
              <textarea class="edit-textarea js-edit-desc flex-1" style="min-height:80px" placeholder="Detailed notes & instructions...">${esc(task.description)}</textarea>

              <label class="text-[10px] font-bold opacity-70">Deliverable</label>
              <input class="edit-field js-edit-url" value="${esc(task.deliverable_url)}" placeholder="https://github.com/...">
              <div>${linkAnchor}</div>

              <label class="text-[10px] font-bold opacity-70">Due day</label>
              <select class="edit-select js-edit-day">${dayOptions}</select>

              <div class="flex items-center justify-between mt-1">
                <label class="text-[10px] font-bold opacity-70">Sub-tasks</label>
                <span class="material-symbols-outlined text-primary cursor-pointer text-[18px]" data-action="sub-add" title="Add sub-task">add_circle</span>
              </div>
              <div class="js-subtasks flex flex-col gap-1">${subtasks}</div>
            </div>

            <!-- RELEGATED styling controls: slide-up drawer, never obscures the text -->
            <div class="style-drawer">
              <div class="drawer-title">
                Style &amp; Assign
                <span class="material-symbols-outlined text-[16px] cursor-pointer" data-action="toggle-style" title="Close">close</span>
              </div>
              <label class="text-[10px] font-bold opacity-70">Assignee initials</label>
              <input class="edit-field js-edit-initials" maxlength="3" value="${esc(task.assignee_initials)}">
              <label class="text-[10px] font-bold opacity-70">Color theme</label>
              <div class="flex gap-2 js-color-picker">${colorDots}</div>
            </div>

            <div class="card-toolbar">
              <span class="material-symbols-outlined" data-action="cancel" title="Cancel">undo</span>
              <span class="material-symbols-outlined style-gear" data-action="toggle-style" title="Style & Assign">tune</span>
              <button class="btn-save" data-action="save">Save / Done</button>
            </div>
          </div><!-- /card-back-editable -->

          </div>
        </div>

      </div>
    </div>`;
}

function renderBoard() {
  for (const status of STATUSES) {
    const column = document.querySelector(`[data-status="${status}"]`);
    const tasks = BoardState.byStatus(status);
    column.innerHTML = tasks.map(cardHTML).join("");
    document.querySelector(`[data-count="${status}"]`).textContent = tasks.length;
  }
}
function refreshCounts() {
  for (const status of STATUSES)
    document.querySelector(`[data-count="${status}"]`).textContent = BoardState.byStatus(status).length;
}

// ---- Card interactions ----------------------------------------------------
function getContainer(elm) { return elm.closest(".card-container"); }

function flipToBack(container, mode) {
  // mode: "edit" (pencil) or "read" (flip icon). We always populate the edit
  // form up front so the bridge to edit mode is instant.
  populateForm(container, BoardState.get(Number(container.dataset.id)));
  container.classList.remove("mode-readonly", "mode-edit");
  container.classList.add(mode === "edit" ? "mode-edit" : "mode-readonly");
  container.classList.add("is-flipped");
}

// Bridge: read-only -> edit WITHOUT flipping the card around.
function setEditMode(container) {
  populateForm(container, BoardState.get(Number(container.dataset.id)));
  container.classList.remove("mode-readonly");
  container.classList.add("mode-edit");
}

function flipToFront(container) {
  container.classList.remove("is-flipped", "mode-readonly", "mode-edit");
  const drawer = container.querySelector(".style-drawer");   // always close the drawer on the way out
  if (drawer) drawer.classList.remove("open");
}

// Read-only checkbox toggle persists immediately (no Save button in this mode).
async function toggleReadonlySubtask(container, checkbox) {
  const row = checkbox.closest(".ro-sub-row");
  row.classList.toggle("done", checkbox.checked);
  const id = Number(container.dataset.id);
  const task = BoardState.get(id);
  const subtasks = (task.subtasks || []).map((st) => {
    const box = container.querySelector(`.js-ro-sub-done[data-sid="${st.id}"]`);
    return box ? { ...st, done: box.checked } : st;
  });
  try {
    const updated = await apiPatchTask(id, { subtasks });
    BoardState.upsert(updated);
  } catch (err) {
    console.error(err);
    checkbox.checked = !checkbox.checked;                    // revert on failure
    row.classList.toggle("done", checkbox.checked);
    alert("Could not update sub-task.");
  }
}

function populateForm(container, task) {
  // Reset the back face to the last-saved state (this is what Cancel reverts to).
  container.querySelector(".js-edit-title").value = task.title;
  container.querySelector(".js-edit-desc").value = task.description || "";
  container.querySelector(".js-edit-url").value = task.deliverable_url || "";
  container.querySelector(".js-edit-day").value = task.due_day || "";
  container.querySelector(".js-edit-initials").value = task.assignee_initials;
  container.querySelector(".js-subtasks").innerHTML = (task.subtasks || []).map(subtaskRowHTML).join("");
  container.querySelectorAll(".color-dot").forEach((d) => d.classList.toggle("selected", d.dataset.color === task.color));
  // Refresh assignee select with current project members.
  const assigneeSelect = container.querySelector(".js-edit-assignee");
  if (assigneeSelect) assigneeSelect.innerHTML = buildAssigneeOptions(task);
}

function gatherSubtasks(container) {
  return [...container.querySelectorAll(".subtask-row")].map((row, i) => ({
    id: Number(row.dataset.sid) || i + 1,
    text: row.querySelector(".js-sub-text").value.trim(),
    done: row.querySelector(".js-sub-done").checked,
  })).filter((st) => st.text.length > 0);
}

async function saveCard(container) {
  const id = Number(container.dataset.id);
  const selectedDot = container.querySelector(".color-dot.selected");
  const assigneeSelect = container.querySelector(".js-edit-assignee");
  const selectedOption = assigneeSelect?.selectedOptions[0];
  const changes = {
    title: container.querySelector(".js-edit-title").value.trim(),
    description: container.querySelector(".js-edit-desc").value,
    deliverable_url: container.querySelector(".js-edit-url").value.trim(),
    due_day: container.querySelector(".js-edit-day").value,
    assignee_initials: selectedOption ? (selectedOption.dataset.initials || container.querySelector(".js-edit-initials").value.trim()) : container.querySelector(".js-edit-initials").value.trim(),
    username: selectedOption ? selectedOption.value : "Unassigned",
    color: selectedDot ? selectedDot.dataset.color : BoardState.get(id).color,
    subtasks: gatherSubtasks(container),
  };
  try {
    const updated = await apiPatchTask(id, changes);
    BoardState.upsert(updated);
    renderBoard();   // simplest correct refresh — front summary + badges reflect new data
  } catch (err) { console.error(err); alert("Could not save. Is the server running?"); }
}

function cancelCard(container) { populateForm(container, BoardState.get(Number(container.dataset.id))); flipToFront(container); }

async function deleteCard(container) {
  const id = Number(container.dataset.id);
  if (!confirm("Are you sure you want to delete this task?")) return;
  try {
    await apiDeleteTask(id);
    BoardState.remove(id);
    container.remove();
    refreshCounts();
  } catch (err) { console.error(err); alert("Could not delete. Is the server running?"); }
}

function addSubtaskRow(container) {
  const wrap = container.querySelector(".js-subtasks");
  const nextId = wrap.querySelectorAll(".subtask-row").length + 1;
  wrap.insertAdjacentHTML("beforeend", subtaskRowHTML({ id: nextId, text: "", done: false }));
  const last = wrap.querySelector(".subtask-row:last-child .js-sub-text");
  if (last) last.focus();
}

function onBoardClick(evt) {
  if (dragActive) return;
  const actionEl = evt.target.closest("[data-action]");
  const colorDot = evt.target.closest(".color-dot");
  const container = getContainer(evt.target);
  if (!container) return;

  if (colorDot) {
    container.querySelectorAll(".color-dot").forEach((d) => d.classList.remove("selected"));
    colorDot.classList.add("selected");
    return;
  }
  if (evt.target.closest(".js-sub-done")) {   // EDIT-mode: toggle strikethrough live
    evt.target.closest(".subtask-row").classList.toggle("done", evt.target.checked);
    return;
  }
  const roChk = evt.target.closest(".js-ro-sub-done");   // READ-ONLY: toggle + persist
  if (roChk) { toggleReadonlySubtask(container, roChk); return; }

  if (!actionEl) return;
  switch (actionEl.dataset.action) {
    case "edit":    flipToBack(container, "edit"); break;   // pencil -> Edit Mode
    case "read":    flipToBack(container, "read"); break;   // flip icon -> Read-Only Mode
    case "to-edit": setEditMode(container);        break;   // read-only bridge -> Edit Mode
    case "save":    saveCard(container);    break;
    case "cancel":  cancelCard(container);  break;
    case "delete":  deleteCard(container);  break;
    case "sub-add": addSubtaskRow(container); break;
    case "sub-del": actionEl.closest(".subtask-row").remove(); break;
    case "toggle-style": container.querySelector(".style-drawer").classList.toggle("open"); break;
  }
}

// Trash icon, edit fields, textareas, selects and links must never bubble into flip/drag.
function onBoardPointerGuards(evt) {
  if (evt.target.closest(".trash-icon, .edit-field, .edit-textarea, .edit-select, .subtask-row, .deliverable-link, .ro-sub-row, .ro-link"))
    evt.stopPropagation();
}

// ---- Drag & drop ----------------------------------------------------------
function onDragStart(evt) {
  const container = evt.target.closest(".card-container");
  if (!container) return;
  if (container.classList.contains("is-flipped")) { evt.preventDefault(); return; }  // front-only
  dragActive = true;
  container.classList.add("dragging");
  evt.dataTransfer.effectAllowed = "move";
  evt.dataTransfer.setData("text/plain", container.dataset.id);
}
function onDragEnd(evt) {
  const container = evt.target.closest(".card-container");
  if (container) container.classList.remove("dragging");
  setTimeout(() => { dragActive = false; }, 0);
}
function columnFromEvent(evt) { return evt.target.closest("[data-status]"); }
function onDragOver(evt) {
  const column = columnFromEvent(evt);
  if (!column) return;
  evt.preventDefault();
  evt.dataTransfer.dropEffect = "move";
  column.classList.add("drag-over");
}
function onDragLeave(evt) {
  const column = columnFromEvent(evt);
  if (column && !column.contains(evt.relatedTarget)) column.classList.remove("drag-over");
}
async function onDrop(evt) {
  const column = columnFromEvent(evt);
  if (!column) return;
  evt.preventDefault();
  column.classList.remove("drag-over");
  const id = Number(evt.dataTransfer.getData("text/plain"));
  const newStatus = column.dataset.status;
  const task = BoardState.get(id);
  if (!task || task.status === newStatus) return;
  try {
    const updated = await apiPatchTask(id, { status: newStatus });
    BoardState.upsert(updated);
    renderBoard();
  } catch (err) { console.error(err); alert("Could not move task. Is the server running?"); }
}

async function addTask() {
  const newTask = {
    title: "New task", description: "", username: "Unassigned", assignee_initials: "??",
    color: "aqua", status: "todo", due_day: "", deliverable_url: "", subtasks: [],
    project_code: BoardState.projectCode,
  };
  try {
    const created = await apiCreateTask(newTask);
    BoardState.upsert(created);
    renderBoard();
  } catch (err) { console.error(err); alert("Could not add task. Is the server running?"); }
}

// ===========================================================================
// MEMBERS VIEW
// ===========================================================================
function renderMembers() {
  const grid = el("members-grid");
  const members = BoardState.currentProject?.members || [];
  if (!members.length) { grid.innerHTML = `<p class="opacity-60">No members yet.</p>`; return; }
  grid.innerHTML = members.map((m) => `
    <div class="member-card">
      <div class="member-avatar">${esc(m.initials)}</div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-on-surface truncate">${esc(m.name)}</h3>
        <p class="text-[12px] text-on-surface-variant">${esc(m.role || "Member")}</p>
      </div>
      <span class="member-count-pill">${BoardState.taskCountFor(m.initials)} tasks</span>
    </div>`).join("");
}

// ===========================================================================
// CALENDAR VIEW (Monday–Sunday)
// ===========================================================================
function miniCardHTML(task) {
  return `<div class="mini-card sticky-${task.color}" draggable="true" data-id="${task.id}" style="background:${dotColor(task.color)}55">
            ${esc(task.title)}<br><span class="mini-badge">${esc(task.assignee_initials)}</span>
          </div>`;
}
function renderCalendar() {
  const grid = el("calendar-grid");
  const unscheduled = el("calendar-unscheduled");
  const tasks = BoardState.all();

  grid.innerHTML = DAYS.map((day) => {
    const dayTasks = tasks.filter((t) => t.due_day === day);
    return `
      <div class="calendar-day" data-cal-day="${day}">
        <div class="calendar-day-header">${day.slice(0, 3)}</div>
        ${dayTasks.map(miniCardHTML).join("") || `<span class="text-[10px] opacity-40 text-center mt-2">--</span>`}
      </div>`;
  }).join("");

  const none = tasks.filter((t) => !t.due_day);
  unscheduled.innerHTML = none.length
    ? none.map(miniCardHTML).join("")
    : `<span class="text-[11px] opacity-50">Everything is scheduled!</span>`;

  wireCalendarDnD();
}

// ===========================================================================
// CALENDAR DRAG-AND-DROP
// ===========================================================================
function wireCalendarDnD() {
  const dropZones = document.querySelectorAll("[data-cal-day]");
  dropZones.forEach((zone) => {
    zone.addEventListener("dragover", (e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; zone.classList.add("cal-drag-over"); });
    zone.addEventListener("dragleave", (e) => { if (!zone.contains(e.relatedTarget)) zone.classList.remove("cal-drag-over"); });
    zone.addEventListener("drop", async (e) => {
      e.preventDefault();
      zone.classList.remove("cal-drag-over");
      const id = Number(e.dataTransfer.getData("text/plain"));
      if (!id) return;
      const newDay = zone.dataset.calDay;  // "" for unscheduled, "Monday" etc.
      try {
        const updated = await apiPatchTask(id, { due_day: newDay });
        BoardState.upsert(updated);
        renderCalendar();
      } catch (err) { console.error(err); alert("Could not update due day."); }
    });
  });
  // Drag start on mini-cards
  document.querySelectorAll(".mini-card[draggable]").forEach((card) => {
    card.addEventListener("dragstart", (e) => {
      card.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", card.dataset.id);
    });
    card.addEventListener("dragend", () => card.classList.remove("dragging"));
  });
}

// ===========================================================================
// RESOURCE HUB VIEW
// ===========================================================================
function renderResources() {
  const list = el("resources-list");
  const resources = BoardState.currentProject?.resources || [];
  if (!resources.length) { list.innerHTML = `<p class="opacity-60">No links pinned yet. Add one above.</p>`; return; }
  // Group by category.
  const byCat = {};
  for (const r of resources) (byCat[r.category] ||= []).push(r);
  list.innerHTML = Object.entries(byCat).map(([cat, items]) => `
    <div>
      <div class="resource-category-title"><span class="material-symbols-outlined text-[18px]">folder</span>${esc(cat)}</div>
      <div class="flex flex-col gap-2">
        ${items.map((r) => `
          <div class="resource-item">
            <span class="material-symbols-outlined text-primary">link</span>
            <div class="flex-1 min-w-0">
              <a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>
              <div class="res-url">${esc(r.url)}</div>
            </div>
          </div>`).join("")}
      </div>
    </div>`).join("");
}

async function onResourceSubmit(evt) {
  evt.preventDefault();
  const title = el("res-title").value.trim();
  const url = el("res-url").value.trim();
  const category = el("res-category").value.trim() || "General";
  if (!title || !url) return;
  // Send the FULL new resource list (backend replaces it wholesale).
  const resources = [...(BoardState.currentProject.resources || []), { title, url, category }];
  try {
    const updated = await apiPatchProject(BoardState.projectCode, { resources });
    BoardState.setCurrentProject(updated);
    evt.target.reset();
    renderResources();
  } catch (err) { console.error(err); alert("Could not add resource. Is the server running?"); }
}

// ===========================================================================
// VIEW SWITCHING
// ===========================================================================
const VIEW_SUBTITLES = {
  board: "Manage and track your active tasks.",
  members: "Team overview and active workload.",
  calendar: "Weekly sprint schedule (Mon–Sun).",
  resources: "Pinned links & external resources.",
};

function showView(name) {
  document.querySelectorAll(".view").forEach((v) => v.classList.add("hidden"));
  el(`view-${name}`).classList.remove("hidden");
  el("view-subtitle").textContent = VIEW_SUBTITLES[name] || "";

  // Highlight the matching nav tab(s).
  document.querySelectorAll("[data-view]").forEach((t) =>
    t.classList.toggle("active-tab", t.dataset.view === name));

  if (name === "board") renderBoard();
  else if (name === "members") renderMembers();
  else if (name === "calendar") renderCalendar();
  else if (name === "resources") renderResources();
}

// ===========================================================================
// HEADER — inline project title editing
// ===========================================================================
function beginTitleEdit() {
  const h1 = el("project-title");
  if (document.getElementById("project-title-input")) return;   // already editing
  const current = BoardState.currentProject?.name || h1.textContent;
  const input = document.createElement("input");
  input.id = "project-title-input";
  input.value = current;
  h1.replaceWith(input);
  input.focus();
  input.select();

  const commit = async () => {
    const newName = input.value.trim();
    input.removeEventListener("blur", commit);
    if (newName && newName !== current) {
      try {
        const updated = await apiPatchProject(BoardState.projectCode, { name: newName });
        BoardState.setCurrentProject(updated);
        BoardState.syncProjectSummary();
        renderProjectList();
      } catch (err) { console.error(err); alert("Could not rename project."); }
    }
    restoreTitle();
  };
  input.addEventListener("blur", commit);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") input.blur();
    if (e.key === "Escape") { input.removeEventListener("blur", commit); restoreTitle(); }
  });
}

function restoreTitle() {
  const input = el("project-title-input");
  const h1 = document.createElement("h1");
  h1.id = "project-title";
  h1.className = "font-headline-xl text-headline-xl text-on-surface drop-shadow-md cursor-text truncate";
  h1.title = "Click to rename";
  h1.textContent = BoardState.currentProject?.name || "Sprint Board";
  h1.addEventListener("click", beginTitleEdit);
  (input || el("project-title")).replaceWith(h1);
}

function updateHeader() {
  const h1 = el("project-title");
  if (h1) h1.textContent = BoardState.currentProject?.name || "Sprint Board";
  el("project-code-label").textContent = BoardState.projectCode;
}

// ===========================================================================
// SIDEBAR — project switcher
// ===========================================================================
function renderProjectList() {
  const wrap = el("sidebar-project-list");
  // Preserve any open inline-creator input across re-renders.
  const openInput = wrap.querySelector(".project-create-input");
  wrap.querySelectorAll(".project-switch-row").forEach((r) => r.remove());
  const rowsHTML = BoardState.projects.map((p) => `
    <div class="project-switch-row" data-code="${esc(p.project_code)}">
      <button class="project-switch-btn ${p.project_code === BoardState.projectCode ? "active" : ""}"
              data-code="${esc(p.project_code)}" title="${esc(p.name)}">${esc(p.name)}</button>
      <span class="material-symbols-outlined project-del" data-action="project-del"
            data-code="${esc(p.project_code)}" title="Delete project">delete</span>
    </div>`).join("");
  wrap.insertAdjacentHTML("afterbegin", rowsHTML);
  if (openInput) wrap.appendChild(openInput);   // keep the creator at the bottom
}

async function switchProject(code) {
  try {
    const [project, tasks] = await Promise.all([apiGetProject(code), apiGetTasks(code)]);
    BoardState.setCurrentProject(project);
    BoardState.setAll(tasks);
    updateHeader();
    renderProjectList();
    showView("board");
  } catch (err) { console.error(err); alert("Could not load project."); }
}

// ---- Inline project creation ----------------------------------------------
function openProjectCreator() {
  const wrap = el("sidebar-project-list");
  wrap.classList.remove("hidden");                       // ensure list is visible
  if (wrap.querySelector(".project-create-input")) {     // already open -> focus it
    wrap.querySelector(".project-create-input").focus();
    return;
  }
  const input = document.createElement("input");
  input.className = "project-create-input";
  input.placeholder = "Project title, then Enter…";
  wrap.appendChild(input);
  input.focus();

  let done = false;
  const close = () => { if (!done) { done = true; input.remove(); } };
  const submit = async () => {
    const title = input.value.trim();
    if (!title) { close(); return; }
    done = true;
    try {
      const project = await apiCreateProject(title);     // server owns the code slug
      BoardState.addProject(project);
      input.remove();
      await switchProject(project.project_code);         // jump straight into it
    } catch (err) { console.error(err); alert("Could not create project."); input.remove(); }
  };
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); submit(); }
    if (e.key === "Escape") close();                     // cancel cleanly, no save
  });
  input.addEventListener("blur", close);                 // click away = cancel
}

async function deleteProject(code) {
  if (!confirm("Delete this project workspace and all its tasks?")) return;
  try {
    await apiDeleteProject(code);
    BoardState.removeProject(code);
    // If we deleted the active project, fall back to the first remaining one.
    if (code === BoardState.projectCode) {
      const next = BoardState.projects[0];
      if (next) { await switchProject(next.project_code); return; }
      BoardState.setCurrentProject(null);
      BoardState.setAll([]);
      updateHeader();
      showView("board");
    }
    renderProjectList();
  } catch (err) { console.error(err); alert("Could not delete project."); }
}

// ===========================================================================
// COMMAND PALETTE — /summary and /filter
// ===========================================================================
function generateStandup() {
  const tasks = BoardState.all();
  const project = BoardState.currentProject;
  const total = tasks.length;
  const completed = tasks.filter((t) => t.status === "done" || t.status === "approved").length;
  const pct = total ? Math.round((completed / total) * 100) : 0;

  // Active workload (in_progress tasks grouped by member).
  const inProgress = tasks.filter((t) => t.status === "in_progress");
  const byMember = {};
  for (const t of inProgress) {
    const name = t.username || "Unassigned";
    (byMember[name] ||= []).push(t.title);
  }
  let workloadBlock = "";
  if (Object.keys(byMember).length) {
    for (const [name, titles] of Object.entries(byMember)) {
      workloadBlock += `  ${name}:\n`;
      for (const title of titles) workloadBlock += `    - ${title}\n`;
    }
  } else {
    workloadBlock = "  (none currently in progress)\n";
  }

  // Recently completed wins.
  const wins = tasks.filter((t) => t.status === "done" || t.status === "approved");
  let winsBlock = "";
  if (wins.length) {
    for (const t of wins) winsBlock += `  - ${t.title}  (${t.username})\n`;
  } else {
    winsBlock = "  (none yet)\n";
  }

  const today = new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  return `DAILY STANDUP REPORT
${project?.name || "Project"} (${BoardState.projectCode})
${today}
${"-".repeat(48)}

PROJECT PROGRESS
  ${completed}/${total} tasks complete (${pct}%)
  ${"|" + "#".repeat(Math.round(pct / 5)) + "-".repeat(20 - Math.round(pct / 5)) + "|"} ${pct}%

ACTIVE WORKLOAD (In Progress)
${workloadBlock}
RECENTLY COMPLETED
${winsBlock}
${"-".repeat(48)}
Generated by AeroFlow`;
}

function showSummaryModal(text) {
  el("summary-content").textContent = text;
  el("summary-modal").classList.remove("hidden");
}

function applyFilter(query) {
  const q = query.toLowerCase();
  // Board cards
  document.querySelectorAll(".card-container[data-id]").forEach((card) => {
    const task = BoardState.get(Number(card.dataset.id));
    if (!task) return;
    const match = task.title.toLowerCase().includes(q) || task.username.toLowerCase().includes(q);
    card.classList.toggle("filter-dim", !match);
  });
  // Calendar mini-cards
  document.querySelectorAll(".mini-card[data-id]").forEach((card) => {
    const task = BoardState.get(Number(card.dataset.id));
    if (!task) return;
    const match = task.title.toLowerCase().includes(q) || task.username.toLowerCase().includes(q);
    card.classList.toggle("filter-dim", !match);
  });
}

function clearFilter() {
  document.querySelectorAll(".filter-dim").forEach((el) => el.classList.remove("filter-dim"));
}

function initCommandPalette() {
  const input = el("command-input");
  const dropdown = el("command-dropdown");
  if (!input || !dropdown) return;

  input.addEventListener("input", () => {
    const v = input.value.trim();
    // Show/hide command dropdown on sole "/"
    if (v === "/") {
      dropdown.classList.remove("hidden");
    } else {
      dropdown.classList.add("hidden");
    }
    // Live filter logic
    if (v.startsWith("/filter ") && v.length > 8) {
      applyFilter(v.slice(8));
    } else {
      clearFilter();
    }
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const v = input.value.trim().toLowerCase();
      if (v === "/summary" || v === "/standup") {
        e.preventDefault();
        showSummaryModal(generateStandup());
        input.value = "";
        dropdown.classList.add("hidden");
        clearFilter();
      } else if (v.startsWith("/filter ") && v.length > 8) {
        e.preventDefault();
        applyFilter(v.slice(8));
        dropdown.classList.add("hidden");
      }
    }
    if (e.key === "Escape") {
      dropdown.classList.add("hidden");
      input.value = "";
      clearFilter();
      input.blur();
    }
  });

  // Command option click -> fill input
  dropdown.addEventListener("click", (e) => {
    const opt = e.target.closest(".command-option");
    if (!opt) return;
    const cmd = opt.dataset.cmd;
    input.value = cmd;
    dropdown.classList.add("hidden");
    input.focus();
    // If the command has no trailing space (like /summary), execute immediately.
    if (!cmd.endsWith(" ")) {
      if (cmd === "/summary") showSummaryModal(generateStandup());
      input.value = "";
    }
  });

  // Click outside closes dropdown
  document.addEventListener("click", (e) => {
    if (!e.target.closest("#command-input") && !e.target.closest("#command-dropdown")) {
      dropdown.classList.add("hidden");
    }
  });

  // Summary modal controls
  el("summary-close").addEventListener("click", () => el("summary-modal").classList.add("hidden"));
  el("summary-modal").addEventListener("click", (e) => { if (e.target === el("summary-modal")) el("summary-modal").classList.add("hidden"); });
  el("summary-copy").addEventListener("click", () => {
    const text = el("summary-content").textContent;
    navigator.clipboard.writeText(text).then(() => {
      const btn = el("summary-copy");
      const orig = btn.innerHTML;
      btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">check</span> Copied!`;
      setTimeout(() => { btn.innerHTML = orig; }, 1800);
    });
  });
}

// ===========================================================================
// Boot
// ===========================================================================
async function init() {
  // Load the project list + default project (DEMO-123) with its tasks.
  try {
    const projects = await apiGetProjects();
    BoardState.setProjects(projects);
    const defaultCode = projects.some((p) => p.project_code === "DEMO-123") ? "DEMO-123" : projects[0]?.project_code;
    const [project, tasks] = await Promise.all([apiGetProject(defaultCode), apiGetTasks(defaultCode)]);
    BoardState.setCurrentProject(project);
    BoardState.setAll(tasks);
  } catch (err) { console.error(err); }

  updateHeader();
  renderProjectList();
  showView("board");

  // --- Board (event delegation on the grid) ---
  const board = document.querySelector("#view-board .grid");
  board.addEventListener("click", onBoardClick);
  board.addEventListener("mousedown", onBoardPointerGuards);
  board.addEventListener("dragstart", (e) => { onBoardPointerGuards(e); onDragStart(e); });
  board.addEventListener("dragend", onDragEnd);
  board.addEventListener("dragover", onDragOver);
  board.addEventListener("dragleave", onDragLeave);
  board.addEventListener("drop", onDrop);

  // --- Top-level buttons ---
  el("add-task-btn").addEventListener("click", () => { showView("board"); addTask(); });

  // --- Nav tabs + sidebar links (data-view) ---
  document.querySelectorAll("[data-view]").forEach((tab) =>
    tab.addEventListener("click", (e) => { e.preventDefault(); showView(tab.dataset.view); }));

  // --- Sidebar: projects toggle + switcher ---
  el("projects-toggle").addEventListener("click", (e) => {
    e.preventDefault();
    el("sidebar-project-list").classList.toggle("hidden");
  });
  el("sidebar-project-list").addEventListener("click", (e) => {
    const del = e.target.closest(".project-del");
    if (del) { e.stopPropagation(); deleteProject(del.dataset.code); return; }
    const btn = e.target.closest(".project-switch-btn");
    if (btn) switchProject(btn.dataset.code);
  });
  el("project-add-btn").addEventListener("click", (e) => { e.preventDefault(); openProjectCreator(); });

  // --- Header inline title edit ---
  el("project-title").addEventListener("click", beginTitleEdit);
  el("project-title-edit").addEventListener("click", beginTitleEdit);

  // --- Resource hub add form ---
  el("resource-form").addEventListener("submit", onResourceSubmit);

  // --- Sidebar collapse ---
  el("sidebar-toggle").addEventListener("click", () =>
    el("app-sidebar").classList.toggle("sidebar-collapsed"));

  // --- Command palette ---
  initCommandPalette();
}

init();
