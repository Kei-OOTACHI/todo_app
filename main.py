import sqlite3
from flask import Flask, abort, jsonify, render_template, request
import re
from datetime import datetime

app = Flask(__name__)

DB_NAME = "todo.db"
TABLE_NAME = "tasks"
TABLE_NAME_2 = "tasks2"

CREATE_TASK_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    done INTEGER DEFAULT false
)
"""

CREATE_TASK_TABLE_2 = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME_2} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    done INTEGER DEFAULT false,
    deadline TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    category TEXT,
    assignee_email TEXT
)
"""


@app.route('/')
def home():
    return render_template('index.html')


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(CREATE_TASK_TABLE)
    cursor.execute(CREATE_TASK_TABLE_2)
    conn.close()


def validate_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    raise ValueError('Invalid value for boolean field: must be True or False.')


def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError('Invalid date format: must be YYYY-MM-DD.')


def validate_email(email):
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(email_regex, email):
        return email
    raise ValueError('Invalid email address.')


def batch_insert_tasks(tasks):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for task in tasks:
        if 'done' in task:
            task['done'] = validate_bool(task['done'])
        if 'deadline' in task:
            task['deadline'] = validate_date(task['deadline'])
        if 'assignee_email' in task:
            task['assignee_email'] = validate_email(task['assignee_email'])

        cursor.execute(f"""
            INSERT INTO {TABLE_NAME_2} (content, done, deadline, category, assignee_email) 
            VALUES (?, ?, ?, ?, ?)""",
                       [task['content'], task.get('done', 0), task.get('deadline'), task.get('category'),
                        task.get('assignee_email')])
        task["id"] = cursor.lastrowid
    conn.commit()
    conn.close()
    return tasks


def batch_delete_tasks(task_ids):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany(f"DELETE FROM {TABLE_NAME_2} WHERE id = ?", [(task_id,) for task_id in task_ids])
    conn.commit()
    conn.close()


def update_task(task_id, task_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # フィールドのバリデーション
    if 'done' in task_data:
        task_data['done'] = validate_bool(task_data['done'])

    if 'deadline' in task_data:
        task_data['deadline'] = validate_date(task_data['deadline'])

    if 'assignee_email' in task_data:
        task_data['assignee_email'] = validate_email(task_data['assignee_email'])

    cursor.execute(f"""
        UPDATE {TABLE_NAME_2} SET 
        content = ?, 
        done = ?, 
        deadline = ?, 
        category = ?, 
        assignee_email = ?, 
        updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?""",
                   [task_data.get('content'), task_data.get('done', 0), task_data.get('deadline'),
                    task_data.get('category'), task_data.get('assignee_email'), task_id])
    conn.commit()
    conn.close()


@app.route("/api/tasks2", methods=["GET"])
def list_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME_2}")
    rows = cursor.fetchall()
    conn.close()

    tasks = [
        {
            "id": row[0],
            "content": row[1],
            "done": bool(row[2]),
            "deadline": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "category": row[6],
            "assignee_email": row[7]
        }
        for row in rows
    ]
    return jsonify({"tasks": tasks}), 200


@app.route("/api/tasks2", methods=["POST"])
def batch_create_tasks():
    tasks = request.get_json()
    try:
        tasks = batch_insert_tasks(tasks)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"tasks": tasks}), 201


@app.route("/api/tasks2", methods=["PUT"])
def batch_update_tasks_route():
    tasks = request.get_json()
    try:
        for task in tasks:
            update_task(task['id'], task)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return '', 204


@app.route("/api/tasks2", methods=["DELETE"])
def batch_delete_tasks_route():
    task_ids = request.get_json()
    batch_delete_tasks(task_ids)
    return '', 204


@app.route("/api/tasks2/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME_2} WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        task = {
            "id": row[0],
            "content": row[1],
            "done": bool(row[2]),
            "deadline": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "category": row[6],
            "assignee_email": row[7]
        }
        return jsonify(task), 200
    abort(404)


@app.errorhandler(404)
def handle_404(exception):
    res = {
        "message": "Error: Resource not found.",
        "description": exception.description
    }
    return res, 404


@app.errorhandler(500)
def handle_500(exception):
    res = {
        "message": "Please contact the administrator.",
        "description": exception.description
    }
    return res, 500


if __name__ == '__main__':
    create_tables()
    app.run(host='127.0.0.1', port=8080, debug=True)
