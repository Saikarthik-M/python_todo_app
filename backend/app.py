from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# ─── DB Config ───────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "pass123"),
    "database": os.getenv("DB_NAME", "todo_db"),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/api/todos", methods=["GET"])
def get_todos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
    todos = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(todos)


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO todos (title, completed) VALUES (%s, %s)",
        (title, False)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM todos WHERE id = %s", (new_id,))
    todo = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(todo), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()
    db = get_db()
    cursor = db.cursor(dictionary=True)

    fields, values = [], []
    if "title" in data:
        fields.append("title = %s")
        values.append(data["title"].strip())
    if "completed" in data:
        fields.append("completed = %s")
        values.append(bool(data["completed"]))

    if not fields:
        return jsonify({"error": "Nothing to update"}), 400

    values.append(todo_id)
    cursor.execute(f"UPDATE todos SET {', '.join(fields)} WHERE id = %s", values)
    db.commit()
    cursor.execute("SELECT * FROM todos WHERE id = %s", (todo_id,))
    todo = cursor.fetchone()
    cursor.close()
    db.close()

    if not todo:
        return jsonify({"error": "Not found"}), 404
    return jsonify(todo)


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()

    if affected == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200

@app.route("/api/health/ready", methods=["GET"])
def readiness():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        db.close()

        return jsonify({"status": "ready"}), 200

    except Exception as e:
        return jsonify({
            "status": "not ready",
            "error": str(e)
        }), 500
        
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
