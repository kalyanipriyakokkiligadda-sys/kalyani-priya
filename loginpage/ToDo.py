from flask import Flask, request, jsonify, render_template
import psycopg2
from flask_bcrypt import Bcrypt
import jwt
import datetime

app = Flask(__name__, template_folder='templates')

bcrypt = Bcrypt(app)

SECRET_KEY = "this is my secret key this is my secret key!!"

# ================= JWT FUNCTIONS ================= #

def create_jwt(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # 🔥 FIX: Convert bytes to string if needed
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def verify_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ================= DATABASE CONFIG ================= #

DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '1404'


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ================= CREATE TABLES ================= #

def create_user_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_db(
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_task_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ToDo_db(
            task_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users_db(user_id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            duedate TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending'
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


create_user_table()
create_task_table()

# ================= ROUTES ================= #

@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/dashboard_page")
def dashboard_page():
    return render_template("dashboard_page.html")


# ================= SIGNUP ================= #

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users_db(username, email, password)
            VALUES (%s, %s, %s)
            RETURNING user_id
        """, (username, email, hashed_password))

        user_id = cur.fetchone()[0]
        conn.commit()

    except psycopg2.Error:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "Email already exists"}), 400

    cur.close()
    conn.close()

    token = create_jwt(user_id, username)

    return jsonify({
        "message": "Signup successful",
        "token": token
    }), 201


# ================= LOGIN ================= #

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "All fields required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, password
        FROM users_db
        WHERE email = %s
    """, (email,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id, username, hashed_password = user

    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({"error": "Invalid password"}), 401

    token = create_jwt(user_id, username)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user_id,
            "username": username,
            "email": email
        }
    }), 200


# ================= CREATE TASK ================= #

@app.route("/create_task", methods=["POST"])
def create_task():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Token missing"}), 401

    user_data = verify_jwt(token)

    if user_data is None:
        return jsonify({"error": "Invalid or expired token"}), 401

    user_id = user_data["user_id"]

    data = request.json
    title = data.get("title")
    description = data.get("description")
    duedate = data.get("duedate")
    priority = data.get("priority", "medium")
    status = data.get("status", "pending")

    if not title or not description or not duedate:
        return jsonify({"error": "Missing task fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ToDo_db(user_id, title, description, duedate, priority, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, title, description, duedate, priority, status))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Task created successfully"}), 201


# ================= GET TASKS ================= #

@app.route("/get_task", methods=["GET"])
def get_task():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Token missing"}), 401

    user_data = verify_jwt(token)

    if user_data is None:
        return jsonify({"error": "Invalid or expired token"}), 401

    user_id = user_data["user_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT task_id, title, description, duedate, priority, status
        FROM ToDo_db
        WHERE user_id = %s
    """, (user_id,))

    tasks = cur.fetchall()
    cur.close()
    conn.close()

    result = [
        {
            "task_id": task[0],
            "title": task[1],
            "description": task[2],
            "duedate": task[3],
            "priority": task[4],
            "status": task[5]
        }
        for task in tasks
    ]

    return jsonify(result), 200

@app.route('/update_task',methods=['PUT'])
def update_task():
    task_id = request.args['task_id']
    title = request.json['title']
    description= request.json['description']
    duedate = request.json['duedate']
    priority=request.json['priority']
    status=request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            UPDATE ToDo_db
                    SET title=%s, description=%s, duedate=%s,priority=%s,status=%s where task_id=%s;
""",(title, description, duedate,priority,status,task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "task updated successfully"}), 200

@app.route('/update_status',methods=['PUT'])
def update_status():
    task_id = request.args.get('task_id')
    status=request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            UPDATE ToDo_db
                    SET status=%s where task_id=%s;
""",(status,task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "status updated successfully"}), 200



# ================= DELETE TASK ================= #

@app.route("/task_delete", methods=["DELETE"])
def task_delete():
    task_id = request.args.get("task_id")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM ToDo_db WHERE task_id = %s;", (task_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Task deleted successfully"}), 200


# ================= RUN APP ================= #

if __name__ == "__main__":
    app.run(debug=True)