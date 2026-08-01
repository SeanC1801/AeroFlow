# File: main.py
"""AeroFlow FastAPI application.

Responsibilities:
  1. Serve the single-page UI (index.html) via Jinja2Templates.
  2. Mount /static for CSS/JS.
  3. Expose a RESTful task + project API backed by two in-memory dicts (no DB yet).
"""

import random
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

app = FastAPI(title="AeroFlow API", version="2.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- In-memory "database" ----------------------------------------------------
# Two stores: PROJECTS (keyed by project_code) and TASKS (keyed by int id).
# Swapping these for SQL later only touches this file.
PROJECTS: dict[str, dict] = {}
TASKS: dict[int, dict] = {}
_next_id = 1


def _create_task(payload: TaskCreate) -> dict:
    global _next_id
    task = payload.model_dump()
    task["id"] = _next_id
    TASKS[_next_id] = task
    _next_id += 1
    return task


def _seed() -> None:
    """Pre-populate rich, realistic student project data."""
    projects = [
        {
            "project_code": "MAT01-STATS",
            "name": "Advanced Statistics Final Project",
            "members": [
                {"initials": "SC", "name": "Sean C.", "role": "Data Lead"},
                {"initials": "JD", "name": "Jane Doe", "role": "Research Analyst"},
            ],
            "resources": [
                {"title": "Dataset (Kaggle)", "url": "https://kaggle.com/datasets", "category": "Data"},
                {"title": "Course Syllabus", "url": "https://university.edu/mat01", "category": "Syllabus"},
            ],
        },
        {
            "project_code": "STS-101",
            "name": "Science, Technology & Society Paper",
            "members": [
                {"initials": "MK", "name": "Mika K.", "role": "Lead Writer"},
                {"initials": "AL", "name": "Alex L.", "role": "Editor"},
            ],
            "resources": [
                {"title": "Shared Google Doc", "url": "https://docs.google.com/document/d/abc", "category": "Google Drive"},
                {"title": "JSTOR Reading List", "url": "https://jstor.org", "category": "References"},
            ],
        },
        {
            "project_code": "DEMO-123",
            "name": "AeroFlow Backend AI Engineering",
            "members": [
                {"initials": "SC", "name": "Sean C.", "role": "Backend Lead"},
                {"initials": "JD", "name": "Jane Doe", "role": "Frontend Dev"},
                {"initials": "MK", "name": "Mika K.", "role": "DevOps"},
            ],
            "resources": [
                {"title": "GitHub Repository", "url": "https://github.com/SeanC1801/aeroflow", "category": "GitHub"},
                {"title": "FastAPI Docs", "url": "https://fastapi.tiangolo.com", "category": "References"},
            ],
        },
    ]
    for p in projects:
        PROJECTS[p["project_code"]] = p

    tasks = [
        # MAT01-STATS — module reviews (Mon/Wed) + data cleaning + subtasks
        {"title": "Module 4 Review: Regression", "username": "Sean C.", "assignee_initials": "SC",
         "color": "aqua", "status": "todo", "due_day": "Monday", "project_code": "MAT01-STATS",
         "description": "Review lecture notes and worked examples for the final.",
         "subtasks": [{"id": 1, "text": "Watch recording", "done": True},
                      {"id": 2, "text": "Redo problem set 4", "done": False}]},
        {"title": "Data cleaning script", "username": "Jane Doe", "assignee_initials": "JD",
         "color": "lime", "status": "in_progress", "due_day": "Wednesday", "project_code": "MAT01-STATS",
         "description": "Write pandas script to drop NaNs and normalize columns.",
         "deliverable_url": "https://github.com/SeanC1801/aeroflow/pull/12",
         "subtasks": [{"id": 1, "text": "Handle missing values", "done": True},
                      {"id": 2, "text": "Normalize numeric cols", "done": False},
                      {"id": 3, "text": "Export clean CSV", "done": False}]},
        {"title": "Module 6 Review: ANOVA", "username": "Sean C.", "assignee_initials": "SC",
         "color": "sunny", "status": "todo", "due_day": "Monday", "project_code": "MAT01-STATS"},

        # STS-101 — literature review (Fri/Sun) + Google Doc deliverable + notes
        {"title": "Literature review", "username": "Mika K.", "assignee_initials": "MK",
         "color": "pink", "status": "in_progress", "due_day": "Friday", "project_code": "STS-101",
         "description": "Summarize 8 sources on algorithmic bias.",
         "deliverable_url": "https://docs.google.com/document/d/abc",
         "subtasks": [{"id": 1, "text": "Find 8 peer-reviewed sources", "done": True},
                      {"id": 2, "text": "Write annotated bibliography", "done": False}]},
        {"title": "Draft reading notes", "username": "Alex L.", "assignee_initials": "AL",
         "color": "aqua", "status": "todo", "due_day": "Sunday", "project_code": "STS-101",
         "description": "Chapter 3 & 4 notes for the discussion section."},
        {"title": "Final proofread", "username": "Alex L.", "assignee_initials": "AL",
         "color": "lime", "status": "todo", "project_code": "STS-101"},

        # DEMO-123 — FastAPI routing + Docker
        {"title": "FastAPI endpoint routing", "username": "Sean C.", "assignee_initials": "SC",
         "color": "aqua", "status": "in_progress", "due_day": "Tuesday", "project_code": "DEMO-123",
         "description": "Implement /projects and /tasks v1 routes with Pydantic validation.",
         "deliverable_url": "https://github.com/SeanC1801/aeroflow/pull/8",
         "subtasks": [{"id": 1, "text": "GET/POST/PATCH tasks", "done": True},
                      {"id": 2, "text": "PATCH projects rename", "done": True},
                      {"id": 3, "text": "DELETE task", "done": False}]},
        {"title": "Docker deployment", "username": "Mika K.", "assignee_initials": "MK",
         "color": "sunny", "status": "todo", "due_day": "Thursday", "project_code": "DEMO-123",
         "description": "Write Dockerfile + compose for local + prod parity."},
        {"title": "Glassmorphism card polish", "username": "Jane Doe", "assignee_initials": "JD",
         "color": "pink", "status": "done", "project_code": "DEMO-123"},
    ]
    for item in tasks:
        _create_task(TaskCreate(**item))


_seed()


# --- UI route ----------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# --- PROJECT API -------------------------------------------------------------
@app.get("/api/v1/projects", response_model=list[ProjectResponse])
def list_projects():
    """All project workspaces (for the sidebar switcher)."""
    return list(PROJECTS.values())


def _slugify_title(title: str) -> str:
    """Turn a human title into an uppercase code base, e.g.
    "Advanced Statistics Final" -> "ADV-STAT". Takes the first two meaningful
    words, keeps up to 4 letters of each. The random suffix is added separately."""
    words = re.findall(r"[A-Za-z0-9]+", title.upper())
    if not words:
        words = ["PROJ"]
    parts = [w[:4] for w in words[:2]]
    return "-".join(parts)


def _unique_project_code(title: str) -> str:
    """Append a random 3-digit suffix, retrying on the rare collision."""
    base = _slugify_title(title)
    for _ in range(50):
        code = f"{base}-{random.randint(100, 999)}"
        if code not in PROJECTS:
            return code
    # Extremely unlikely fallback: widen the number space.
    return f"{base}-{random.randint(1000, 9999)}"


@app.post("/api/v1/projects", response_model=ProjectResponse, status_code=201)
def create_project(payload: ProjectCreate):
    """Create an empty project workspace from just a title. The server owns the code."""
    title = payload.title.strip()
    code = _unique_project_code(title)
    project = {"project_code": code, "name": title, "members": [], "resources": []}
    PROJECTS[code] = project
    return project


@app.delete("/api/v1/projects/{project_code}", status_code=204)
def delete_project(project_code: str):
    """Delete a project workspace AND all of its tasks."""
    if project_code not in PROJECTS:
        raise HTTPException(status_code=404, detail=f"Project {project_code} not found")
    del PROJECTS[project_code]
    # Cascade: drop every task belonging to this project.
    for tid in [tid for tid, t in TASKS.items() if t["project_code"] == project_code]:
        del TASKS[tid]


@app.get("/api/v1/projects/{project_code}", response_model=ProjectResponse)
def get_project(project_code: str):
    if project_code not in PROJECTS:
        raise HTTPException(status_code=404, detail=f"Project {project_code} not found")
    return PROJECTS[project_code]


@app.patch("/api/v1/projects/{project_code}", response_model=ProjectResponse)
def update_project(project_code: str, payload: ProjectUpdate):
    """Rename a project and/or replace its resource list."""
    if project_code not in PROJECTS:
        raise HTTPException(status_code=404, detail=f"Project {project_code} not found")
    changes = payload.model_dump(exclude_unset=True)
    PROJECTS[project_code].update(changes)
    return PROJECTS[project_code]


# --- TASK API ----------------------------------------------------------------
@app.get("/api/v1/tasks", response_model=list[TaskResponse])
def list_tasks(project_code: str | None = None):
    tasks = list(TASKS.values())
    if project_code is not None:
        tasks = [t for t in tasks if t["project_code"] == project_code]
    return tasks


@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate):
    return _create_task(payload)


@app.patch("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    changes = payload.model_dump(exclude_unset=True)
    TASKS[task_id].update(changes)
    return TASKS[task_id]


@app.delete("/api/v1/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    del TASKS[task_id]


# --- Entry point -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
