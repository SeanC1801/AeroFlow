# File: schemas.py
"""Pydantic data models for AeroFlow.

Single source of truth for what tasks and projects look like on the wire.
FastAPI uses these to validate incoming JSON and to shape outgoing JSON.

The `project_code` on every task is the room/join code the whole app is scoped
to — today it's an in-memory key, tomorrow it becomes the real "Join a Project"
privacy boundary.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    """The four Kanban columns."""
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    approved = "approved"


class Color(str, Enum):
    """Sticky-note color themes. Map 1:1 to the `.sticky-*` CSS classes."""
    lime = "lime"
    sunny = "sunny"
    aqua = "aqua"
    pink = "pink"


# =============================================================================
# TASKS
# =============================================================================
class TaskBase(BaseModel):
    """Fields shared by create/response — everything editable on the card."""
    title: str = Field(..., min_length=1, max_length=120)
    username: str = Field(default="Unassigned", max_length=40)
    assignee_initials: str = Field(default="??", min_length=1, max_length=3)
    color: Color = Color.aqua
    status: Status = Status.todo

    # --- Card-back "execution hub" fields ---
    description: str = Field(default="", max_length=2000)          # multi-line notes
    deliverable_url: str = Field(default="", max_length=500)       # PR / Doc / Figma link
    # Sub-tasks are loose dicts: {"id": int, "text": str, "done": bool}. Kept as
    # plain dicts (not a strict model) so the frontend can evolve the shape freely.
    subtasks: List[Dict[str, Any]] = Field(default_factory=list)
    due_day: str = Field(default="", max_length=12)               # "Monday".."Sunday" or ""

    # --- Room / join code ---
    project_code: str = Field(default="DEMO-123", max_length=32)


class TaskCreate(TaskBase):
    """Payload for POST /api/v1/tasks. Server assigns the id."""
    pass


class TaskUpdate(BaseModel):
    """Payload for PATCH /api/v1/tasks/{id}. All fields optional (partial update)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    username: Optional[str] = Field(default=None, max_length=40)
    assignee_initials: Optional[str] = Field(default=None, min_length=1, max_length=3)
    color: Optional[Color] = None
    status: Optional[Status] = None
    description: Optional[str] = Field(default=None, max_length=2000)
    deliverable_url: Optional[str] = Field(default=None, max_length=500)
    subtasks: Optional[List[Dict[str, Any]]] = None
    due_day: Optional[str] = Field(default=None, max_length=12)
    project_code: Optional[str] = Field(default=None, max_length=32)


class TaskResponse(TaskBase):
    """What the task API returns. Adds the server-assigned id."""
    id: int


# =============================================================================
# PROJECTS
# =============================================================================
class Member(BaseModel):
    """A person on a project board."""
    initials: str = Field(..., max_length=3)   # avatar badge, e.g. "SC"
    name: str
    role: str = ""                              # e.g. "Backend Lead"


class Resource(BaseModel):
    """A pinned external link in the Resource Hub (no physical files)."""
    title: str
    url: str
    category: str = "General"                   # e.g. "GitHub", "Google Drive"


class ProjectBase(BaseModel):
    project_code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=120)
    members: List[Member] = Field(default_factory=list)
    resources: List[Resource] = Field(default_factory=list)


class ProjectResponse(ProjectBase):
    """What the project API returns."""
    pass


class ProjectCreate(BaseModel):
    """Payload for POST /api/v1/projects.

    The client sends ONLY a human title; the backend is the authority that turns
    it into a guaranteed-unique code slug (e.g. "Advanced Statistics" -> ADV-STAT-482)."""
    title: str = Field(..., min_length=1, max_length=120)


class ProjectUpdate(BaseModel):
    """Payload for PATCH /api/v1/projects/{project_code}.

    Rename a project and/or replace its resource list (used by the Resource Hub
    when the user adds a link)."""
    name: Optional[str] = Field(default=None, max_length=120)
    resources: Optional[List[Resource]] = None
