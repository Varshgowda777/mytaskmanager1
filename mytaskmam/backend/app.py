
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from contextlib import contextmanager

app = Flask(__name__)

# CORS configuration
CORS(app)

# Database configuration
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"


# Database connection
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


# Initialize database
def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)


# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "Task Manager Backend is running"
    })


# GET: Fetch all tasks
@app.route("/api/tasks", methods=["GET"])
def get_tasks():

    with get_db() as db:
        tasks = db.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    return jsonify([
        dict(task) for task in tasks
    ])


# POST: Create a new task
@app.route("/api/tasks", methods=["POST"])
def add_task():

    data = request.get_json(silent=True) or {}

    title = data.get("title", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            "error": "Task title is required"
        }), 400

    title = title.strip()

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


# PUT: Update task completion status
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):

    data = request.get_json(silent=True) or {}

    if "completed" not in data:
        return jsonify({
            "error": "Status is required"
        }), 400

    completed = 1 if data["completed"] else 0

    with get_db() as db:

        cursor = db.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (completed, task_id)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Task not found"
            }), 404

    return jsonify({
        "message": "Task updated successfully"
    })


# DELETE: Delete a task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    with get_db() as db:

        cursor = db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Task not found"
            }), 404

    return jsonify({
        "message": "Task deleted successfully"
    })


# Initialize database when application starts
init_db()


# Local development
if __name__ == "__main__":
    app.run(debug=False)
