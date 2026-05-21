import psycopg2
import psycopg2.extras
import os
import hashlib

def get_db():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
    conn.autocommit = False
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS doctors (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS patients (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        diagnosis TEXT,
        username TEXT UNIQUE,
        password TEXT,
        doctor_id INTEGER REFERENCES doctors(id)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        patient_id INTEGER REFERENCES patients(id),
        repetitions INTEGER DEFAULT 0,
        duration INTEGER DEFAULT 0,
        date TEXT
    )''')
    # Default doctor
    password = hashlib.sha256('doctor123'.encode()).hexdigest()
    cur.execute("""
        INSERT INTO doctors (username, password, name) 
        VALUES ('doctor', %s, 'Dr. Alibek')
        ON CONFLICT (username) DO NOTHING
    """, (password,))
    conn.commit()
    cur.close()
    conn.close()
