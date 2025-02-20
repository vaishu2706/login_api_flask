from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Change this to a secure key

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ✅ PostgreSQL Connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="Newdb",
            user="postgres",
            password="vaishu",  # Change this to your actual password
            host="localhost",
            port="5432",
            cursor_factory=RealDictCursor  # ✅ Ensures dict output instead of tuples
        )
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None

# ✅ Executes Queries with Optional Fetching
def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Database connection failed"}

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if fetch:
                    return cur.fetchall()
                return {"message": "Success"}
    except Exception as e:
        print("❌ Query Execution Error:", e)  # Debugging
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

# ✅ REGISTER USER
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    result = execute_query(
        "INSERT INTO accounts (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (data['name'], data['email'], hashed_pw, data.get('role', 'user'))
    )

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Fetch user from database
    user = execute_query("SELECT * FROM accounts WHERE email = %s", (data['email'],), fetch=True)

    # Check if 'users' is an error dictionary
    if isinstance(user, dict) and "error" in user:
        return jsonify(user), 500  # Return error response

    # If no users found, return "User not found"
    if not user:
        return jsonify({"error": "User not found"}), 404
    user = user[0]  # Extract user from list
    # Check password hash
    if bcrypt.check_password_hash(str(user['password']), data['password']):  # Column 3 = password field
        token = create_access_token(
            identity=str(user['id']),  # Convert user ID to a string
            additional_claims={"role": user['role']}  # Store role separately
        )  # Generate token
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401  # Incorrect password


# ✅ GET ALL USERS (Protected Route)
@app.route('/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    accounts = execute_query("SELECT id, name, email, role FROM accounts", fetch=True)
    if "error" in accounts:
        return jsonify(accounts), 500

    return jsonify(accounts)

@app.route('/greetings', methods=['GET'])
@jwt_required()
def get_greetings():
    user_id = get_jwt_identity()  # ✅ Gets 'id' as a string
    claims = get_jwt()  # ✅ Gets additional claims like 'role'
    user = execute_query("SELECT * FROM accounts WHERE id = %s", (int(user_id),), fetch=True)
    user = user[0]
    print("User ID:", user_id)
    print("Claims:", claims)
    return jsonify(f"Hi {user['email']}, welcome to the protected route!, Your role is {claims['role']}")

if __name__ == '__main__':
    app.run(debug=True)
