# AeroFlow

**A Kanban board for managing team projects and sprints.**

AeroFlow is a productivity suite built for students and small teams who need a lightweight, visually polished way to organise tasks across multiple project workspaces. It features a drag-and-drop sprint board, team member overview, weekly calendar grid, and a resource hub — all wrapped in a Frutiger Aero–inspired glass UI.

---

## Why AeroFlow?

Managing group projects — especially in a university setting — often means juggling scattered Google Docs, loose Messenger threads, and mental to-do lists. AeroFlow brings everything into one clean dashboard:

- **One board per project** — switch between courses or team projects instantly from the sidebar.
- **Visual task tracking** — colour-coded sticky-note cards you can drag between To-Do → In Progress → Done → Approved.
- **Execution hub on every card** — flip a card to add descriptions, deliverable links, due days, and sub-task checklists without leaving the board.
- **Resource Hub** — pin external links (GitHub repos, Google Docs, Figma boards) so the whole team can find them.
- **Zero sign-up** — runs locally with no database; great for demos and personal use.

---

## Features

| View | Description |
|---|---|
| **Sprint Board** | Four-column Kanban with drag-and-drop. Cards flip to reveal an execution hub (description, deliverable link, sub-tasks, due day). |
| **Members** | Team roster showing each member's role and active task count. |
| **Calendar Grid** | Monday–Sunday view of tasks grouped by their due day. |
| **Resource Hub** | Categorised link library pinned to each project workspace. |

**Additional highlights:**

- Four sticky-note colour themes (Lime, Sunny, Aqua, Pink)
- Inline project renaming from the header
- Create and delete projects from the sidebar
- Search bar (ready to wire up)
- Responsive layout with collapsible sidebar

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com) (Python) |
| **Templating** | Jinja2 |
| **Frontend** | Vanilla JavaScript (ES Modules), Tailwind CSS (CDN), Google Material Symbols |
| **Data** | In-memory Python dicts (no database required) |
| **Validation** | Pydantic v2 models |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** (or any Python package manager)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/SeanC1801/AeroFlow.git
   cd AeroFlow
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # macOS / Linux
   .venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server**

   ```bash
   uvicorn main:app --reload
   ```

5. **Open the app**

   Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

The app ships with seed data (three sample projects with realistic tasks) so you can explore the UI immediately.

---

## Project Structure

```
AeroFlow/
├── main.py              # FastAPI app — routes, in-memory DB, seed data
├── schemas.py           # Pydantic models (Task, Project, enums)
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Single-page Jinja2 template (Tailwind + Glass UI)
└── static/
    ├── css/
    │   └── styles.css   # Frutiger Aero glassmorphism, 3D flip cards, animations
    └── js/
        ├── board.js     # Controller — renders views, wires events, talks to API
        └── state.js     # Client-side state management (BoardState)
```

---

## API Reference

All endpoints are under `/api/v1`. The interactive Swagger docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) when the server is running.

### Projects

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/projects` | List all project workspaces |
| `POST` | `/api/v1/projects` | Create a new project (send `{ "title": "..." }`) |
| `GET` | `/api/v1/projects/{code}` | Get a single project by its code |
| `PATCH` | `/api/v1/projects/{code}` | Rename a project or update its resources |
| `DELETE` | `/api/v1/projects/{code}` | Delete a project and all its tasks |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/tasks` | List tasks (optionally filter by `?project_code=`) |
| `POST` | `/api/v1/tasks` | Create a new task |
| `PATCH` | `/api/v1/tasks/{id}` | Partial update (status, title, subtasks, etc.) |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task |

---

## Usage Tips

- **Drag cards** between columns to change their status.
- **Click the pencil ✏️** on a card to flip it and edit details (description, deliverable link, sub-tasks).
- **Click the flip icon ↻** to view the card back in read-only mode — sub-task checkboxes still save instantly.
- **Click the project title** in the header to rename the current project inline.
- **Use the `+` button** next to "Projects" in the sidebar to create a new workspace.

---

## License

This project is open source and available for personal and educational use.

---

<p align="center">
  Built with FastAPI by <a href="https://github.com/SeanC1801">Sean C.</a>
</p>
