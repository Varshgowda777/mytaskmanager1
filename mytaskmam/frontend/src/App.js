
import React, { useEffect, useState } from "react";

const API = "/api/tasks";

function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadTasks = async () => {
    try {
      const response = await fetch(API);
      if (!response.ok) throw new Error("Unable to load tasks");

      setTasks(await response.json());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const addTask = async () => {
    if (!title.trim()) return;

    try {
      const response = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
      });

      if (!response.ok) throw new Error("Could not add task");

      setTitle("");
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const completeTask = async (task) => {
    try {
      const response = await fetch(`${API}/${task.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          completed: !task.completed
        })
      });

      if (!response.ok) throw new Error("Could not update task");
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteTask = async (id) => {
    try {
      const response = await fetch(`${API}/${id}`, {
        method: "DELETE"
      });

      if (!response.ok) throw new Error("Could not delete task");
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const completed = tasks.filter(t => t.completed).length;
  const pending = tasks.length - completed;

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.heading}>My Task Manager</h1>
        <p style={styles.subtitle}>
          Organize your day. Complete your goals.
        </p>

        <div style={styles.stats}>
          <div>
            <h2>{tasks.length}</h2>
            <span>Total</span>
          </div>
          <div>
            <h2>{completed}</h2>
            <span>Completed</span>
          </div>
          <div>
            <h2>{pending}</h2>
            <span>Pending</span>
          </div>
        </div>

        <div style={styles.inputBox}>
          <input
            style={styles.input}
            placeholder="Enter a new task..."
            value={title}
            onChange={e => setTitle(e.target.value)}
            onKeyDown={e => e.key === "Enter" && addTask()}
          />
          <button style={styles.addButton} onClick={addTask}>
            + Add
          </button>
        </div>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <h3>My Tasks</h3>

        {loading ? (
          <p>Loading tasks...</p>
        ) : tasks.length === 0 ? (
          <p style={styles.empty}>No tasks yet. Add your first task!</p>
        ) : (
          tasks.map(task => (
            <div key={task.id} style={styles.task}>
              <label style={styles.taskLabel}>
                <input
                  type="checkbox"
                  checked={Boolean(task.completed)}
                  onChange={() => completeTask(task)}
                />
                <span style={{
                  textDecoration: task.completed
                    ? "line-through" : "none",
                  color: task.completed ? "#999" : "#222"
                }}>
                  {task.title}
                </span>
              </label>

              <button
                style={styles.deleteButton}
                onClick={() => deleteTask(task.id)}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f3f4f8",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
    fontFamily: "Arial, sans-serif"
  },
  card: {
    background: "white",
    width: "100%",
    maxWidth: 600,
    padding: 30,
    borderRadius: 16,
    boxShadow: "0 5px 25px #0001"
  },
  heading: { color: "#5b4bdb", marginBottom: 5 },
  subtitle: { color: "#888" },
  stats: {
    display: "flex",
    justifyContent: "space-around",
    background: "#f6f5ff",
    padding: 15,
    borderRadius: 12,
    margin: "25px 0",
    textAlign: "center"
  },
  inputBox: { display: "flex", gap: 10, marginBottom: 25 },
  input: {
    flex: 1,
    minWidth: 0,
    padding: 13,
    border: "1px solid #ddd",
    borderRadius: 8,
    fontSize: 15
  },
  addButton: {
    background: "#5b4bdb",
    color: "white",
    border: "none",
    borderRadius: 8,
    padding: "12px 20px",
    cursor: "pointer"
  },
  task: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 15,
    borderBottom: "1px solid #eee",
    gap: 10
  },
  taskLabel: {
    display: "flex",
    alignItems: "center",
    gap: 12
  },
  deleteButton: {
    background: "#ffecec",
    color: "#e33",
    border: "none",
    padding: "8px 12px",
    borderRadius: 6,
    cursor: "pointer"
  },
  empty: { color: "#888", textAlign: "center" }
};

export default App;
