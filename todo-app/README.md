# TaskPilot - DevOps To-Do Application

A lightweight, modern web-based To-Do management application designed as the core application for an **End-to-End DevOps Pipeline**. Built with Python, Flask, SQLite, and Prometheus metrics instrumentation, complete with automated unit and API testing.

---

## 🚀 Features

- **Interactive UI**: Clean, responsive dashboard to create, view, edit, filter, search, and delete tasks.
- **Task Management**:
  - Add tasks with title, description, priority levels (`Low`, `Medium`, `High`), and due dates.
  - Interactive status toggling (Pending ↔ Completed) with real-time stats counter.
  - Filter tasks by status (`All`, `Pending`, `Completed`) and instantaneous search.
- **RESTful API**: Full CRUD API endpoints adhering to standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`).
- **DevOps Ready**:
  - `/health` endpoint for uptime monitoring and container orchestration health checks.
  - `/metrics` endpoint exporting Prometheus-compatible metrics (`http_requests_total`, `http_request_duration_seconds`, `todo_tasks_total`).
- **Automated Testing**: 100% test coverage for API routes, validations, and UI rendering using `pytest`.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, Flask 3.0 |
| **Database** | SQLite via Flask-SQLAlchemy |
| **Monitoring** | `prometheus-client` |
| **Testing** | `pytest` |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla fetch API) |

---

## 📂 Project Structure

```text
Agile Project/
├── app.py              # Main Flask application and REST API
├── requirements.txt    # Project dependencies
├── test_app.py         # PyTest automated test suite
├── .gitignore          # Git ignore file
├── README.md           # Documentation
├── templates/
│   └── index.html      # Frontend HTML template
└── static/
    ├── style.css       # Custom stylesheet
    └── app.js          # Interactive frontend logic
```

---

## ⚡ Getting Started (Local Setup)

### 1. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
Open your browser and navigate to: **`http://localhost:5000`**

---

## 🧪 Running Automated Tests

Run the automated PyTest suite to verify application logic:

```bash
pytest -v
```

All 13 test cases validate:
- Home page loading (`200 OK`)
- Health check status (`/health`)
- Prometheus metrics output (`/metrics`)
- Task creation (`POST /api/tasks`)
- Input validation (rejecting empty task titles with `400 Bad Request`)
- Task retrieval and single item lookups (`GET /api/tasks`, `GET /api/tasks/<id>`)
- 404 error handling for non-existent items
- Task modification (`PUT /api/tasks/<id>`)
- Task status toggling (`PATCH /api/tasks/<id>/toggle`)
- Task deletion (`DELETE /api/tasks/<id>`)
- Status filtering (`?status=pending` / `?status=completed`)

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web user interface |
| `GET` | `/health` | Health check endpoint returning `{"status": "UP"}` |
| `GET` | `/metrics` | Prometheus metrics scrape target |
| `GET` | `/api/tasks` | List tasks (supports query parameter `?status=pending\|completed`) |
| `POST` | `/api/tasks` | Create a new task |
| `GET` | `/api/tasks/<id>` | Fetch specific task by ID |
| `PUT` | `/api/tasks/<id>` | Update an existing task |
| `PATCH` | `/api/tasks/<id>/toggle` | Toggle task completion status |
| `DELETE` | `/api/tasks/<id>` | Delete a task |

---

## 🧭 DevOps Pipeline Roadmap

- [x] **Stage 1 & 2: Plan & Develop** — Completed To-Do application with clean UI and REST API
- [x] **Stage 7: Automated Testing** — PyTest suite configured and verified
- [ ] **Stage 6: Git & GitHub** — Repository initialization and commits
- [ ] **Stage 10: Dockerization** — Create `Dockerfile` and run in container
- [ ] **Stage 8 & 9: Jenkins CI/CD** — Jenkins pipeline setup (`Jenkinsfile`)
- [ ] **Stage 13 & 14: Prometheus & Grafana** — Metric collection, dashboard, and alerts
