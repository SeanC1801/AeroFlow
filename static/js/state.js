// File: static/js/state.js
// Local State Object Pattern — the SINGLE source of truth on the frontend.
// The DOM is always a reflection of this state, never the other way around.

export const BoardState = {
  // --- Tasks for the ACTIVE project, keyed by id ---
  tasks: new Map(),

  // --- Projects ---
  projects: [],            // [{project_code, name, members, resources}, ...] (summary list)
  currentProject: null,    // full detail of the selected project

  /** The active project's room code (drives task fetches). */
  get projectCode() {
    return this.currentProject ? this.currentProject.project_code : "DEMO-123";
  },

  // ---- Tasks --------------------------------------------------------------
  setAll(taskList) {
    this.tasks.clear();
    for (const task of taskList) this.tasks.set(task.id, task);
  },
  get(id) { return this.tasks.get(id); },
  snapshot(id) { return { ...this.tasks.get(id) }; },
  upsert(task) { this.tasks.set(task.id, task); },
  remove(id) { this.tasks.delete(id); },
  byStatus(status) { return [...this.tasks.values()].filter((t) => t.status === status); },
  all() { return [...this.tasks.values()]; },

  // ---- Projects -----------------------------------------------------------
  setProjects(list) { this.projects = list; },
  setCurrentProject(project) { this.currentProject = project; },
  addProject(project) { this.projects.push({ ...project }); },
  removeProject(code) { this.projects = this.projects.filter((p) => p.project_code !== code); },

  /** Keep the summary list in sync when the current project is edited. */
  syncProjectSummary() {
    if (!this.currentProject) return;
    const idx = this.projects.findIndex((p) => p.project_code === this.currentProject.project_code);
    if (idx !== -1) this.projects[idx].name = this.currentProject.name;
  },

  // ---- Members helper: task counts per assignee ---------------------------
  taskCountFor(initials) {
    return this.all().filter((t) => t.assignee_initials === initials).length;
  },

  // ---- Dynamic Members registry -------------------------------------------
  members: {},   // { "Sean C.": { role: "Backend Lead", initials: "SC" } }

  /** Derive uppercase initials from a name string (e.g. "Sean Caling" → "SC"). */
  _deriveInitials(name) {
    return name.split(/\s+/).map((w) => w[0]?.toUpperCase() || "").join("").slice(0, 2) || "??";
  },

  /** Ensure a member exists in the registry; auto-register if unknown. */
  ensureMember(name, initials) {
    if (!name || name === "Unassigned") return;
    if (!this.members[name]) {
      this.members[name] = {
        role: "Team Member",
        initials: initials || this._deriveInitials(name),
      };
    }
  },

  /** Get a member record by name. */
  getMember(name) { return this.members[name]; },

  /** Update a member's role. */
  setMemberRole(name, role) {
    if (this.members[name]) this.members[name].role = role;
  },

  /** Return all registered members as an array of { name, role, initials }. */
  allMembers() {
    return Object.entries(this.members).map(([name, data]) => ({
      name, role: data.role, initials: data.initials,
    }));
  },

  /** Sync members from the current project's member list + all task assignees. */
  syncMembers() {
    // Seed from project members
    const projMembers = this.currentProject?.members || [];
    for (const m of projMembers) {
      if (!this.members[m.name]) {
        this.members[m.name] = { role: m.role || "Team Member", initials: m.initials };
      }
    }
    // Seed from task assignees
    for (const t of this.all()) {
      this.ensureMember(t.username, t.assignee_initials);
    }
  },
};
