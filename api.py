
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# PostgreSQL Connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="Newdb",
            user="postgres",
            password="vaishu",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        return str(e)

# CREATE - Add a new user
@app.route('/users1', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        conn = get_db_connection()
        if isinstance(conn, str):  # Error handling for connection issues
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("INSERT INTO users1 (name, email) VALUES (%s, %s)", (data['name'], data['email']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# READ - Get all users
@app.route('/users1', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("SELECT * FROM users1")
        users = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([{"id": user[0], "name": user[1], "email": user[2]} for user in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UPDATE - Update a user
@app.route('/users1/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("UPDATE users1 SET name = %s, email = %s WHERE id = %s",
                    (data['name'], data['email'], user_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete a user
@app.route('/users1/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        if isinstance(conn, str):
            return jsonify({"error": conn}), 500

        cur = conn.cursor()
        cur.execute("DELETE FROM users1 WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
