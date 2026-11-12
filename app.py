from flask import Flask, render_template, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from llama_cpp import Llama
import sqlite3

REPO_ID = "bartowski/Qwen2.5-0.5B-Instruct-GGUF"
FILENAME = "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"

print(f"Загрузка модели {FILENAME} из {REPO_ID}...")
llm = Llama.from_pretrained(
    repo_id=REPO_ID,
    filename=FILENAME,
    n_ctx=2048,
    verbose=False
)
print("Модель успешно загружена.")

app = Flask(__name__)
app.secret_key = "1581"

def connect():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                balance REAL DEFAULT 100.0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                cost REAL,
                description TEXT,
                balance_after REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

init_db()

@app.route('/api/user_register', methods=['POST'])
def user_register():
    req = request.get_json(silent=True) or {}
    name = (req.get('name') or '').strip()
    email = (req.get('email') or '').strip()
    password = req.get('password') or ''

    if not name or not email or not password:
        return jsonify({'error': 'Заполните все поля'})

    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cur.fetchone():
            return jsonify({'error': 'Пользователь с таким email уже существует'})

        cur.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (name, email, generate_password_hash(password))
        )
        cnx.commit()

    return jsonify({'ok': True})

@app.route('/api/login', methods=['POST'])
def login():
    req = request.get_json(silent=True) or {}
    email = (req.get('email') or '').strip()
    password = req.get('password') or ''

    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute(
            'SELECT id, username, email, password_hash FROM users WHERE email = ?',
            (email,)
        )
        user = cur.fetchone()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Неверный email или пароль'})

    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']

    return jsonify({
        'ok': True,
        'id': user['id'],
        'username': user['username'],
        'email': user['email']
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    req = request.get_json(silent=True) or {}
    message = (req.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Пустое сообщение'}), 400

    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты вежливый и компетентный онлайн-консультант этого сайта. "
                    "Помогай пользователям с регистрацией, входом в личный кабинет, "
                    "проверкой баланса и любыми другими вопросами. "
                    "Отвечай дружелюбно, понятно и по существу."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
        max_tokens=300,
        temperature=0.3
    )
    reply = output["choices"][0]["message"]["content"].strip()

    return jsonify({"reply": reply})

@app.route('/profile')
def profile_page():
    if 'user_id' not in session:
        return redirect('/login')

    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute(
            'SELECT id, username, email, balance FROM users WHERE id = ?',
            (session['user_id'],)
        )
        user = cur.fetchone()

    if not user:
        session.clear()
        return redirect('/login')

    return render_template('profile.html', user=user)

@app.route('/logout', methods=['POST', 'GET'])
def api_logout():
    session.clear()
    return redirect('/login')

@app.route('/transactions')
def transactions_page():
    if 'user_id' not in session:
        return redirect('/login')

    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute(
            '''SELECT id, amount, type, cost, description, balance_after, created_at
               FROM transactions
               WHERE user_id = ?
               ORDER BY created_at DESC, id DESC''',
            (session['user_id'],)
        )
        transactions = cur.fetchall()

    return render_template('transactions.html', transactions=transactions)

@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login_page():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
