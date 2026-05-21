from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
import psycopg2.extras
import hashlib
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'glove_secret_key_2024')

def get_db():
    return psycopg2.connect(os.environ.get('DATABASE_URL', ''), sslmode='require')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS doctors (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, name TEXT NOT NULL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS patients (id SERIAL PRIMARY KEY, name TEXT NOT NULL, age INTEGER, diagnosis TEXT, username TEXT UNIQUE, password TEXT, doctor_id INTEGER REFERENCES doctors(id), daily_sessions INTEGER DEFAULT 3, min_reps INTEGER DEFAULT 20)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS sessions (id SERIAL PRIMARY KEY, patient_id INTEGER REFERENCES patients(id), repetitions INTEGER DEFAULT 0, duration INTEGER DEFAULT 0, date TEXT, mode TEXT DEFAULT 'manual')''')
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS daily_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS min_reps INTEGER DEFAULT 20")
        cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'manual'")
        password = hash_password('doctor123')
        cur.execute("INSERT INTO doctors (username, password, name) VALUES ('doctor', %s, 'Dr. Alibek') ON CONFLICT (username) DO NOTHING", (password,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        try:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute('SELECT * FROM doctors WHERE username=%s AND password=%s', (username, password))
            doctor = cur.fetchone()
            if doctor:
                session['doctor_id'] = doctor['id']
                session['doctor_name'] = doctor['name']
                cur.close(); conn.close()
                return redirect(url_for('dashboard'))
            cur.execute('SELECT * FROM patients WHERE username=%s AND password=%s', (username, password))
            patient = cur.fetchone()
            if patient:
                session['patient_id'] = patient['id']
                session['patient_name'] = patient['name']
                cur.close(); conn.close()
                return redirect(url_for('patient_dashboard'))
            cur.close(); conn.close()
        except Exception as e:
            print(f"Login error: {e}")
        error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE doctor_id=%s ORDER BY name', (session['doctor_id'],))
    patients = cur.fetchall()
    today = date.today().strftime('%Y-%m-%d')
    patients_with_compliance = []
    for p in patients:
        cur.execute('SELECT COUNT(*) as cnt, COALESCE(SUM(repetitions),0) as reps FROM sessions WHERE patient_id=%s AND date LIKE %s', (p['id'], today+'%'))
        today_stats = cur.fetchone()
        daily_sessions = p['daily_sessions'] or 3
        compliance = min(100, int((today_stats['cnt'] / daily_sessions) * 100)) if daily_sessions > 0 else 0
        patients_with_compliance.append({**dict(p), 'compliance': compliance, 'today_sessions': today_stats['cnt'], 'today_reps': today_stats['reps']})
    cur.execute('SELECT COUNT(*) as total_sessions, COALESCE(SUM(repetitions),0) as total_reps FROM sessions s JOIN patients p ON s.patient_id = p.id WHERE p.doctor_id=%s', (session['doctor_id'],))
    stats = cur.fetchone()
    cur.close(); conn.close()
    return render_template('dashboard.html', patients=patients_with_compliance, stats=stats)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    age = request.form['age']
    diagnosis = request.form['diagnosis']
    username = request.form['username']
    password = hash_password(request.form['password'])
    daily_sessions = int(request.form.get('daily_sessions', 3))
    min_reps = int(request.form.get('min_reps', 20))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO patients (name, age, diagnosis, username, password, doctor_id, daily_sessions, min_reps) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (name, age, diagnosis, username, password, session['doctor_id'], daily_sessions, min_reps))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('dashboard'))

@app.route('/patient/<int:patient_id>')
def patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s AND doctor_id=%s', (patient_id, session['doctor_id']))
    p = cur.fetchone()
    if not p:
        cur.close(); conn.close()
        return redirect(url_for('dashboard'))
    cur.execute('SELECT * FROM sessions WHERE patient_id=%s ORDER BY date DESC', (patient_id,))
    sessions_list = cur.fetchall()
    cur.close(); conn.close()
    return render_template('patient.html', patient=p, sessions=sessions_list)

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'patient_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s', (session['patient_id'],))
    p = cur.fetchone()
    cur.execute('SELECT * FROM sessions WHERE patient_id=%s ORDER BY date DESC', (session['patient_id'],))
    sessions_list = cur.fetchall()
    today = date.today().strftime('%Y-%m-%d')
    cur.execute('SELECT COUNT(*) as cnt, COALESCE(SUM(repetitions),0) as reps FROM sessions WHERE patient_id=%s AND date LIKE %s', (session['patient_id'], today+'%'))
    today_stats = cur.fetchone()
    cur.close(); conn.close()
    daily_sessions = p['daily_sessions'] or 3
    compliance = min(100, int((today_stats['cnt'] / daily_sessions) * 100)) if daily_sessions > 0 else 0
    return render_template('patient_view.html', patient=p, sessions=sessions_list, today_stats=today_stats, compliance=compliance)

@app.route('/api/session', methods=['POST'])
def receive_session():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO sessions (patient_id, repetitions, duration, date, mode) VALUES (%s, %s, %s, %s, %s)', (data.get('patient_id'), data.get('repetitions', 0), data.get('duration', 0), datetime.now().strftime('%Y-%m-%d %H:%M'), data.get('mode', 'manual')))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
