from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
import psycopg2.extras
import hashlib
from datetime import datetime, date
from zoneinfo import ZoneInfo

ASTANA_TZ = ZoneInfo('Asia/Almaty')

def now_astana():
    return datetime.now(ASTANA_TZ).strftime('%Y-%m-%d %H:%M')

def today_astana():
    return datetime.now(ASTANA_TZ).date()
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
        # Doctors
        cur.execute('''CREATE TABLE IF NOT EXISTS doctors (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            specialty TEXT,
            city TEXT,
            phone TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )''')
        # Admins
        cur.execute('''CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )''')
        # Patients
        cur.execute('''CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            diagnosis TEXT,
            history TEXT,
            phone TEXT,
            address TEXT,
            start_date TEXT,
            username TEXT UNIQUE,
            password TEXT,
            doctor_id INTEGER REFERENCES doctors(id),
            daily_sessions INTEGER DEFAULT 3,
            min_reps INTEGER DEFAULT 20
        )''')
        # Sessions
        cur.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            repetitions INTEGER DEFAULT 0,
            duration INTEGER DEFAULT 0,
            date TEXT,
            mode TEXT DEFAULT 'manual'
        )''')
        # Notes
        cur.execute('''CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            doctor_id INTEGER REFERENCES doctors(id),
            content TEXT NOT NULL,
            is_private BOOLEAN DEFAULT TRUE,
            created_at TEXT
        )''')
        # Feedback
        cur.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            doctor_id INTEGER REFERENCES doctors(id),
            stars INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT
        )''')


        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS mon_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS tue_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS wed_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS thu_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS fri_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sat_sessions INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sun_sessions INTEGER DEFAULT 0")

        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS mon_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS tue_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS wed_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS thu_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS fri_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sat_sessions INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sun_sessions INTEGER DEFAULT 0")

        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS mon_plan TEXT DEFAULT 'option1'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS tue_plan TEXT DEFAULT 'option1'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS wed_plan TEXT DEFAULT 'option1'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS thu_plan TEXT DEFAULT 'option1'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS fri_plan TEXT DEFAULT 'option1'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sat_plan TEXT DEFAULT 'rest'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sun_plan TEXT DEFAULT 'rest'")

        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS mon_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS tue_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS wed_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS thu_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS fri_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sat_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sun_note TEXT DEFAULT ''")

        cur.execute('''CREATE TABLE IF NOT EXISTS assessments (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            session_id INTEGER REFERENCES sessions(id),
            pain_level INTEGER DEFAULT 0,
            fatigue INTEGER DEFAULT 0,
            dizziness INTEGER DEFAULT 0,
            concentration INTEGER DEFAULT 0,
            mental_fatigue INTEGER DEFAULT 0,
            mood INTEGER DEFAULT 3,
            grip_strength TEXT DEFAULT 'medium',
            comment TEXT DEFAULT '',
            created_at TEXT
        )''')
        cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS emergency_stops INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS interruption_reason TEXT DEFAULT ''")

        cur.execute('''CREATE TABLE IF NOT EXISTS assessments (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            session_id INTEGER REFERENCES sessions(id),
            pain_level INTEGER DEFAULT 0,
            fatigue INTEGER DEFAULT 0,
            dizziness INTEGER DEFAULT 0,
            concentration INTEGER DEFAULT 0,
            mental_fatigue INTEGER DEFAULT 0,
            mood INTEGER DEFAULT 3,
            grip_strength TEXT DEFAULT 'medium',
            comment TEXT DEFAULT '',
            created_at TEXT
        )''')
        cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS emergency_stops INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS interruption_reason TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS mon_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS tue_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS wed_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS thu_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS fri_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sat_note TEXT DEFAULT ''")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS sun_note TEXT DEFAULT ''")
        # Migration - add new columns
        cur.execute("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS specialty TEXT")
        cur.execute("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS city TEXT")
        cur.execute("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS phone TEXT")
        cur.execute("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS history TEXT")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS phone TEXT")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS address TEXT")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS start_date TEXT")
        cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'manual'")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS daily_sessions INTEGER DEFAULT 3")
        cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS min_reps INTEGER DEFAULT 20")
        # Default admin
        admin_pwd = hash_password('admin123')
        cur.execute("INSERT INTO admins (username, password, name) VALUES ('admin', %s, 'Super Admin') ON CONFLICT (username) DO NOTHING", (admin_pwd,))
        # Default doctor
        doctor_pwd = hash_password('doctor123')
        cur.execute("INSERT INTO doctors (username, password, name) VALUES ('doctor', %s, 'Dr. Alibek') ON CONFLICT (username) DO NOTHING", (doctor_pwd,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

# ─── HELPERS ───
def get_role():
    if 'admin_id' in session: return 'admin'
    if 'doctor_id' in session: return 'doctor'
    if 'patient_id' in session: return 'patient'
    return None

# ─── ROUTES ───
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
            # Check admin
            cur.execute('SELECT * FROM admins WHERE username=%s AND password=%s', (username, password))
            admin = cur.fetchone()
            if admin:
                session['admin_id'] = admin['id']
                session['admin_name'] = admin['name']
                cur.close(); conn.close()
                return redirect(url_for('admin_dashboard'))
            # Check doctor
            cur.execute('SELECT * FROM doctors WHERE username=%s AND password=%s AND is_active=TRUE', (username, password))
            doctor = cur.fetchone()
            if doctor:
                session['doctor_id'] = doctor['id']
                session['doctor_name'] = doctor['name']
                cur.close(); conn.close()
                return redirect(url_for('dashboard'))
            # Check patient
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

# ─── ADMIN ───
@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('''SELECT d.*, 
        COUNT(DISTINCT p.id) as patient_count,
        COUNT(DISTINCT s.id) as session_count,
        COALESCE(AVG(f.stars), 0) as avg_rating
        FROM doctors d
        LEFT JOIN patients p ON p.doctor_id = d.id
        LEFT JOIN sessions s ON s.patient_id = p.id
        LEFT JOIN feedback f ON f.doctor_id = d.id
        GROUP BY d.id ORDER BY d.name''')
    doctors = cur.fetchall()
    cur.execute('SELECT COUNT(*) as total FROM patients')
    total_patients = cur.fetchone()['total']
    cur.execute('SELECT COUNT(*) as total FROM sessions')
    total_sessions = cur.fetchone()['total']
    cur.execute('''SELECT f.*, p.name as patient_name, d.name as doctor_name
        FROM feedback f
        JOIN patients p ON f.patient_id = p.id
        JOIN doctors d ON f.doctor_id = d.id
        ORDER BY f.created_at DESC LIMIT 20''')
    feedbacks = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin.html', doctors=doctors, total_patients=total_patients, total_sessions=total_sessions, feedbacks=feedbacks)

@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO doctors (username, password, name, specialty, city, phone) VALUES (%s, %s, %s, %s, %s, %s)',
               (request.form['username'], hash_password(request.form['password']),
                request.form['name'], request.form['specialty'],
                request.form['city'], request.form['phone']))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE doctors SET is_active=FALSE WHERE id=%s', (doctor_id,))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('admin_dashboard'))

# ─── DOCTOR ───
@app.route('/dashboard')
def dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE doctor_id=%s ORDER BY name', (session['doctor_id'],))
    patients = cur.fetchall()
    today = today_astana().strftime('%Y-%m-%d')
    patients_with_compliance = []
    for p in patients:
        cur.execute('SELECT COUNT(*) as cnt, COALESCE(SUM(repetitions),0) as reps FROM sessions WHERE patient_id=%s AND date LIKE %s', (p['id'], today+'%'))
        today_stats = cur.fetchone()
        daily_sessions = p['daily_sessions'] or 3
        compliance = min(100, int((today_stats['cnt'] / daily_sessions) * 100)) if daily_sessions > 0 else 0
        patients_with_compliance.append({**dict(p), 'compliance': compliance, 'today_sessions': today_stats['cnt'], 'today_reps': today_stats['reps']})
    cur.execute('SELECT COUNT(*) as total_sessions, COALESCE(SUM(repetitions),0) as total_reps FROM sessions s JOIN patients p ON s.patient_id = p.id WHERE p.doctor_id=%s', (session['doctor_id'],))
    stats = cur.fetchone()
    cur.execute('SELECT COALESCE(AVG(stars), 0) as avg_rating, COUNT(*) as total FROM feedback WHERE doctor_id=%s', (session['doctor_id'],))
    rating = cur.fetchone()
    cur.close(); conn.close()
    return render_template('dashboard.html', patients=patients_with_compliance, stats=stats, rating=rating)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO patients 
        (name, age, diagnosis, history, phone, address, start_date, username, password, doctor_id, daily_sessions, min_reps,
         mon_sessions, tue_sessions, wed_sessions, thu_sessions, fri_sessions, sat_sessions, sun_sessions) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
        (request.form['name'], request.form['age'], request.form['diagnosis'],
         request.form.get('history', ''), request.form.get('phone', ''),
         request.form.get('address', ''), today_astana().strftime('%Y-%m-%d'),
         request.form['username'], hash_password(request.form['password']),
         session['doctor_id'], int(request.form.get('daily_sessions', 3)),
         int(request.form.get('min_reps', 20)),
         int(request.form.get('mon_sessions', 3)), int(request.form.get('tue_sessions', 3)),
         int(request.form.get('wed_sessions', 3)), int(request.form.get('thu_sessions', 3)),
         int(request.form.get('fri_sessions', 3)), int(request.form.get('sat_sessions', 0)),
         int(request.form.get('sun_sessions', 0))))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_patient/<int:patient_id>')
def delete_patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM notes WHERE patient_id=%s', (patient_id,))
    cur.execute('DELETE FROM feedback WHERE patient_id=%s', (patient_id,))
    cur.execute('DELETE FROM sessions WHERE patient_id=%s', (patient_id,))
    cur.execute('DELETE FROM patients WHERE id=%s AND doctor_id=%s', (patient_id, session['doctor_id']))
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
    cur.execute('SELECT * FROM notes WHERE patient_id=%s ORDER BY created_at DESC', (patient_id,))
    notes = cur.fetchall()
    cur.close(); conn.close()
    return render_template('patient.html', patient=p, sessions=sessions_list, notes=notes)

@app.route('/add_note/<int:patient_id>', methods=['POST'])
def add_note(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    is_private = request.form.get('is_private') == 'on'
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO notes (patient_id, doctor_id, content, is_private, created_at) VALUES (%s, %s, %s, %s, %s)',
               (patient_id, session['doctor_id'], request.form['content'], is_private, now_astana()))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('patient', patient_id=patient_id))

# ─── PATIENT ───
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
    today = today_astana().strftime('%Y-%m-%d')
    cur.execute('SELECT COUNT(*) as cnt, COALESCE(SUM(repetitions),0) as reps FROM sessions WHERE patient_id=%s AND date LIKE %s', (session['patient_id'], today+'%'))
    today_stats = cur.fetchone()
    cur.execute('SELECT * FROM notes WHERE patient_id=%s AND is_private=FALSE ORDER BY created_at DESC', (session['patient_id'],))
    public_notes = cur.fetchall()
    cur.execute('SELECT * FROM feedback WHERE patient_id=%s ORDER BY created_at DESC LIMIT 1', (session['patient_id'],))
    my_feedback = cur.fetchone()
    cur.execute('SELECT d.name as doctor_name FROM patients p JOIN doctors d ON p.doctor_id = d.id WHERE p.id=%s', (session['patient_id'],))
    doctor_info = cur.fetchone()
    cur.close(); conn.close()
    # Get today's goal based on day of week
    day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
    today_day = day_map[today_astana().weekday()]
    col = f"{today_day}_sessions"
    today_goal = p.get(col, p['daily_sessions'] or 3) or 0
    is_rest_day = today_goal == 0
    compliance = 0 if is_rest_day else min(100, int((today_stats['cnt'] / today_goal) * 100)) if today_goal > 0 else 0
    return render_template('patient_view.html', patient=p, sessions=sessions_list, today_stats=today_stats, compliance=compliance, public_notes=public_notes, my_feedback=my_feedback, doctor_info=doctor_info, today_goal=today_goal, is_rest_day=is_rest_day)

@app.route('/leave_feedback', methods=['POST'])
def leave_feedback():
    if 'patient_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT doctor_id FROM patients WHERE id=%s', (session['patient_id'],))
    p = cur.fetchone()
    cur.execute('DELETE FROM feedback WHERE patient_id=%s', (session['patient_id'],))
    cur.execute('INSERT INTO feedback (patient_id, doctor_id, stars, comment, created_at) VALUES (%s, %s, %s, %s, %s)',
               (session['patient_id'], p['doctor_id'], int(request.form['stars']),
                request.form.get('comment', ''), now_astana()))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('patient_dashboard'))

# ─── API ───
@app.route('/api/session', methods=['POST'])
def receive_session():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO sessions (patient_id, repetitions, duration, date, mode) VALUES (%s, %s, %s, %s, %s)',
               (data.get('patient_id'), data.get('repetitions', 0), data.get('duration', 0),
                now_astana(), data.get('mode', 'manual')))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'status': 'ok'})

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s AND doctor_id=%s', (patient_id, session['doctor_id']))
    p = cur.fetchone()
    if not p:
        cur.close(); conn.close()
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        cur2 = conn.cursor()
        cur2.execute('''UPDATE patients SET name=%s, age=%s, diagnosis=%s, history=%s, phone=%s, address=%s, daily_sessions=%s, min_reps=%s WHERE id=%s''',
                   (request.form['name'], request.form['age'], request.form['diagnosis'],
                    request.form.get('history', ''), request.form.get('phone', ''),
                    request.form.get('address', ''), int(request.form.get('daily_sessions', 3)),
                    int(request.form.get('min_reps', 20)), patient_id))
        if request.form.get('password'):
            cur2.execute('UPDATE patients SET password=%s WHERE id=%s', (hash_password(request.form['password']), patient_id))
        conn.commit()
        cur2.close(); conn.close()
        return redirect(url_for('patient', patient_id=patient_id))
    cur.close(); conn.close()
    return render_template('edit_patient.html', patient=p)

@app.route('/admin/doctors_list')
def admin_doctors_list():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM doctors ORDER BY name')
    doctors = cur.fetchall()
    cur.execute('''SELECT p.*, d.name as doctor_name FROM patients p 
                   JOIN doctors d ON p.doctor_id = d.id ORDER BY p.name''')
    patients = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin_accounts.html', doctors=doctors, patients=patients)

@app.route('/admin/reset_password', methods=['POST'])
def reset_password():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    user_type = request.form['user_type']
    user_id = request.form['user_id']
    new_password = hash_password(request.form['new_password'])
    conn = get_db()
    cur = conn.cursor()
    if user_type == 'doctor':
        cur.execute('UPDATE doctors SET password=%s WHERE id=%s', (new_password, user_id))
    elif user_type == 'patient':
        cur.execute('UPDATE patients SET password=%s WHERE id=%s', (new_password, user_id))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('admin_doctors_list'))

@app.route('/therapy_plan/<int:patient_id>', methods=['GET', 'POST'])
def therapy_plan(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s AND doctor_id=%s', (patient_id, session['doctor_id']))
    p = cur.fetchone()
    if not p:
        cur.close(); conn.close()
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        cur2 = conn.cursor()
        cur2.execute('''UPDATE patients SET 
            mon_plan=%s, tue_plan=%s, wed_plan=%s, thu_plan=%s,
            fri_plan=%s, sat_plan=%s, sun_plan=%s,
            mon_sessions=%s, tue_sessions=%s, wed_sessions=%s, thu_sessions=%s,
            fri_sessions=%s, sat_sessions=%s, sun_sessions=%s,
            mon_note=%s, tue_note=%s, wed_note=%s, thu_note=%s,
            fri_note=%s, sat_note=%s, sun_note=%s
            WHERE id=%s''',
            (request.form.get('mon', 'rest'), request.form.get('tue', 'rest'),
             request.form.get('wed', 'rest'), request.form.get('thu', 'rest'),
             request.form.get('fri', 'rest'), request.form.get('sat', 'rest'),
             request.form.get('sun', 'rest'),
             int(request.form.get('mon_count', 1)), int(request.form.get('tue_count', 1)),
             int(request.form.get('wed_count', 1)), int(request.form.get('thu_count', 1)),
             int(request.form.get('fri_count', 1)), int(request.form.get('sat_count', 1)),
             int(request.form.get('sun_count', 1)),
             request.form.get('mon_note', ''), request.form.get('tue_note', ''),
             request.form.get('wed_note', ''), request.form.get('thu_note', ''),
             request.form.get('fri_note', ''), request.form.get('sat_note', ''),
             request.form.get('sun_note', ''), patient_id))
        conn.commit()
        cur2.close(); conn.close()
        return redirect(url_for('patient', patient_id=patient_id))
    cur.close(); conn.close()
    return render_template('therapy_plan.html', patient=p)


@app.route('/admin/doctor/<int:doctor_id>')
def admin_doctor_detail(doctor_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('''SELECT d.*, 
        COUNT(DISTINCT p.id) as patient_count,
        COUNT(DISTINCT s.id) as session_count,
        COALESCE(AVG(f.stars), 0) as avg_rating,
        COALESCE(SUM(s.repetitions), 0) as total_reps
        FROM doctors d
        LEFT JOIN patients p ON p.doctor_id = d.id
        LEFT JOIN sessions s ON s.patient_id = p.id
        LEFT JOIN feedback f ON f.doctor_id = d.id
        WHERE d.id=%s GROUP BY d.id''', (doctor_id,))
    doctor = cur.fetchone()
    cur.execute('SELECT * FROM patients WHERE doctor_id=%s ORDER BY name', (doctor_id,))
    patients = cur.fetchall()
    cur.execute('''SELECT s.*, p.name as patient_name FROM sessions s 
        JOIN patients p ON s.patient_id = p.id 
        WHERE p.doctor_id=%s ORDER BY s.date DESC LIMIT 20''', (doctor_id,))
    recent_sessions = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin_doctor_detail.html', doctor=doctor, patients=patients, recent_sessions=recent_sessions)

@app.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def admin_edit_doctor(doctor_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM doctors WHERE id=%s', (doctor_id,))
    doctor = cur.fetchone()
    if request.method == 'POST':
        cur2 = conn.cursor()
        cur2.execute('''UPDATE doctors SET name=%s, username=%s, specialty=%s, city=%s, phone=%s WHERE id=%s''',
                   (request.form['name'], request.form['username'],
                    request.form.get('specialty', ''), request.form.get('city', ''),
                    request.form.get('phone', ''), doctor_id))
        if request.form.get('password'):
            cur2.execute('UPDATE doctors SET password=%s WHERE id=%s', (hash_password(request.form['password']), doctor_id))
        conn.commit()
        cur2.close(); conn.close()
        return redirect(url_for('admin_doctor_detail', doctor_id=doctor_id))
    cur.close(); conn.close()
    return render_template('admin_edit_doctor.html', doctor=doctor)

@app.route('/assessment/<int:session_id>', methods=['GET', 'POST'])
def assessment(session_id):
    if 'patient_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM sessions WHERE id=%s AND patient_id=%s', (session_id, session['patient_id']))
    sess = cur.fetchone()
    if not sess:
        cur.close(); conn.close()
        return redirect(url_for('patient_dashboard'))
    if request.method == 'POST':
        pain = int(request.form.get('pain_level', 0))
        fatigue = int(request.form.get('fatigue', 0))
        dizziness = int(request.form.get('dizziness', 0))
        concentration = int(request.form.get('concentration', 0))
        mental_fatigue = int(request.form.get('mental_fatigue', 0))
        mood = int(request.form.get('mood', 3))
        grip = request.form.get('grip_strength', 'medium')
        comment = request.form.get('comment', '')
        cur2 = conn.cursor()
        cur2.execute('''INSERT INTO assessments 
            (patient_id, session_id, pain_level, fatigue, dizziness, concentration, mental_fatigue, mood, grip_strength, comment, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (session['patient_id'], session_id, pain, fatigue, dizziness, concentration, mental_fatigue, mood, grip, comment, now_astana()))
        conn.commit()
        cur2.close(); conn.close()
        return redirect(url_for('patient_dashboard'))
    cur.close(); conn.close()
    return render_template('assessment.html', sess=sess)

@app.route('/export/patient/<int:patient_id>')
def export_patient(patient_id):
    if 'doctor_id' not in session and 'admin_id' not in session:
        return redirect(url_for('login'))
    import csv
    import io
    from flask import Response
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s', (patient_id,))
    p = cur.fetchone()
    cur.execute('''SELECT s.*, a.pain_level, a.fatigue, a.dizziness, a.concentration, 
        a.mental_fatigue, a.mood, a.grip_strength, a.comment as assessment_comment
        FROM sessions s
        LEFT JOIN assessments a ON a.session_id = s.id
        WHERE s.patient_id=%s ORDER BY s.date DESC''', (patient_id,))
    sessions_data = cur.fetchall()
    cur.close(); conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Repetitions', 'Duration', 'Mode', 'Pain', 'Fatigue', 'Dizziness', 'Concentration', 'Mental Fatigue', 'Mood', 'Grip Strength', 'Comment'])
    for s in sessions_data:
        writer.writerow([s['date'], s['repetitions'], s['duration'], s['mode'],
                        s['pain_level'] or '', s['fatigue'] or '', s['dizziness'] or '',
                        s['concentration'] or '', s['mental_fatigue'] or '',
                        s['mood'] or '', s['grip_strength'] or '', s['assessment_comment'] or ''])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                   headers={'Content-Disposition': f'attachment; filename={p["name"]}_data.csv'})

@app.route('/analytics/<int:patient_id>')
def analytics(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s AND doctor_id=%s', (patient_id, session['doctor_id']))
    p = cur.fetchone()
    if not p:
        cur.close(); conn.close()
        return redirect(url_for('dashboard'))
    cur.execute('''SELECT s.date, s.repetitions, s.duration, s.mode,
        a.pain_level, a.fatigue, a.dizziness, a.mood, a.grip_strength
        FROM sessions s LEFT JOIN assessments a ON a.session_id = s.id
        WHERE s.patient_id=%s ORDER BY s.date ASC LIMIT 30''', (patient_id,))
    data = cur.fetchall()
    # Streak calculation
    cur.execute('''SELECT DISTINCT date_trunc('day', date::timestamp) as day 
        FROM sessions WHERE patient_id=%s ORDER BY day DESC''', (patient_id,))
    active_days = cur.fetchall()
    # Alerts
    cur.execute('''SELECT a.* FROM assessments a WHERE a.patient_id=%s 
        AND (a.pain_level > 7 OR a.fatigue > 8 OR a.dizziness > 6)
        ORDER BY a.created_at DESC LIMIT 5''', (patient_id,))
    alerts = cur.fetchall()
    # Recommendation
    cur.execute('''SELECT AVG(pain_level) as avg_pain, AVG(fatigue) as avg_fatigue, 
        AVG(dizziness) as avg_diz FROM assessments WHERE patient_id=%s''', (patient_id,))
    avgs = cur.fetchone()
    recommendation = None
    if avgs and avgs['avg_pain']:
        if float(avgs['avg_pain']) > 7 or float(avgs['avg_fatigue'] or 0) > 8:
            recommendation = {'type': 'reduce', 'msg': 'High pain/fatigue detected. Consider switching to Option 1 and reducing session duration.'}
        elif float(avgs['avg_diz'] or 0) > 6:
            recommendation = {'type': 'rest', 'msg': 'High dizziness detected. Consider adding more rest days.'}
        elif float(avgs['avg_pain']) < 3 and float(avgs['avg_fatigue'] or 0) < 4:
            recommendation = {'type': 'increase', 'msg': 'Patient is handling therapy well. Consider increasing to Option 2 or 3.'}
    cur.close(); conn.close()
    return render_template('analytics.html', patient=p, data=data, alerts=alerts, recommendation=recommendation, active_days=active_days)

@app.route('/assessment/<int:session_id>', methods=['GET', 'POST'])
def assessment(session_id):
    if 'patient_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM sessions WHERE id=%s AND patient_id=%s', (session_id, session['patient_id']))
    sess = cur.fetchone()
    if not sess:
        cur.close(); conn.close()
        return redirect(url_for('patient_dashboard'))
    if request.method == 'POST':
        pain = int(request.form.get('pain_level', 0))
        fatigue = int(request.form.get('fatigue', 0))
        dizziness = int(request.form.get('dizziness', 0))
        concentration = int(request.form.get('concentration', 0))
        mental_fatigue = int(request.form.get('mental_fatigue', 0))
        mood = int(request.form.get('mood', 3))
        grip = request.form.get('grip_strength', 'medium')
        comment = request.form.get('comment', '')
        cur2 = conn.cursor()
        cur2.execute('''INSERT INTO assessments 
            (patient_id, session_id, pain_level, fatigue, dizziness, concentration, mental_fatigue, mood, grip_strength, comment, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (session['patient_id'], session_id, pain, fatigue, dizziness, concentration, mental_fatigue, mood, grip, comment, now_astana()))
        conn.commit()
        cur2.close(); conn.close()
        return redirect(url_for('patient_dashboard'))
    cur.close(); conn.close()
    return render_template('assessment.html', sess=sess)

@app.route('/export/patient/<int:patient_id>')
def export_patient(patient_id):
    if 'doctor_id' not in session and 'admin_id' not in session:
        return redirect(url_for('login'))
    import csv
    import io
    from flask import Response
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s', (patient_id,))
    p = cur.fetchone()
    cur.execute('''SELECT s.*, a.pain_level, a.fatigue, a.dizziness, a.concentration, 
        a.mental_fatigue, a.mood, a.grip_strength, a.comment as assessment_comment
        FROM sessions s
        LEFT JOIN assessments a ON a.session_id = s.id
        WHERE s.patient_id=%s ORDER BY s.date DESC''', (patient_id,))
    sessions_data = cur.fetchall()
    cur.close(); conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Repetitions', 'Duration', 'Mode', 'Pain', 'Fatigue', 'Dizziness', 'Concentration', 'Mental Fatigue', 'Mood', 'Grip Strength', 'Comment'])
    for s in sessions_data:
        writer.writerow([s['date'], s['repetitions'], s['duration'], s['mode'],
                        s['pain_level'] or '', s['fatigue'] or '', s['dizziness'] or '',
                        s['concentration'] or '', s['mental_fatigue'] or '',
                        s['mood'] or '', s['grip_strength'] or '', s['assessment_comment'] or ''])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                   headers={'Content-Disposition': f'attachment; filename={p["name"]}_data.csv'})

@app.route('/analytics/<int:patient_id>')
def analytics(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM patients WHERE id=%s AND doctor_id=%s', (patient_id, session['doctor_id']))
    p = cur.fetchone()
    if not p:
        cur.close(); conn.close()
        return redirect(url_for('dashboard'))
    cur.execute('''SELECT s.date, s.repetitions, s.duration, s.mode,
        a.pain_level, a.fatigue, a.dizziness, a.mood, a.grip_strength
        FROM sessions s LEFT JOIN assessments a ON a.session_id = s.id
        WHERE s.patient_id=%s ORDER BY s.date ASC LIMIT 30''', (patient_id,))
    data = cur.fetchall()
    cur.execute('''SELECT DISTINCT date_trunc('day', date::timestamp) as day 
        FROM sessions WHERE patient_id=%s ORDER BY day DESC''', (patient_id,))
    active_days = cur.fetchall()
    cur.execute('''SELECT a.* FROM assessments a WHERE a.patient_id=%s 
        AND (a.pain_level > 7 OR a.fatigue > 8 OR a.dizziness > 6)
        ORDER BY a.created_at DESC LIMIT 5''', (patient_id,))
    alerts = cur.fetchall()
    cur.execute('''SELECT AVG(pain_level) as avg_pain, AVG(fatigue) as avg_fatigue, 
        AVG(dizziness) as avg_diz FROM assessments WHERE patient_id=%s''', (patient_id,))
    avgs = cur.fetchone()
    recommendation = None
    if avgs and avgs['avg_pain']:
        if float(avgs['avg_pain']) > 7 or float(avgs['avg_fatigue'] or 0) > 8:
            recommendation = {'type': 'reduce', 'msg': 'High pain/fatigue detected. Consider switching to Option 1 and reducing session duration.'}
        elif float(avgs['avg_diz'] or 0) > 6:
            recommendation = {'type': 'rest', 'msg': 'High dizziness detected. Consider adding more rest days.'}
        elif float(avgs['avg_pain']) < 3 and float(avgs['avg_fatigue'] or 0) < 4:
            recommendation = {'type': 'increase', 'msg': 'Patient is handling therapy well. Consider increasing to Option 2 or 3.'}
    cur.close(); conn.close()
    return render_template('analytics.html', patient=p, data=data, alerts=alerts, recommendation=recommendation, active_days=active_days)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
