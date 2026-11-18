
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import sqlite3
from pathlib import Path
from contextlib import contextmanager

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"
FRONTEND_BUILD = BASE_DIR.parent / "frontend" / "build"


@contextmanager
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)


# GET: View all tasks
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    with get_db() as db:
        tasks = db.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(task) for task in tasks])


# POST: Add a task
@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Task title required"}), 400

    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        task_id = cursor.lastrowid

    return jsonify({
        "id": task_id,
        "title": title,
        "completed": 0
    }), 201


# PUT: Update task status
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    if "completed" not in data:
        return jsonify({"error": "Status required"}), 400

    completed = 1 if data["completed"] else 0

    with get_db() as db:
        cursor = db.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (completed, task_id)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task updated"})


# DELETE: Remove a task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted"})


# Serve React frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path.startswith("api/"):
        abort(404)

    if not FRONTEND_BUILD.exists():
        return "React build not found", 404

    file_path = FRONTEND_BUILD / path

    if path and file_path.is_file():
        return send_from_directory(FRONTEND_BUILD, path)

    return send_from_directory(FRONTEND_BUILD, "index.html")


init_db()

if __name__ == "__main__":
    app.run(debug=True)
