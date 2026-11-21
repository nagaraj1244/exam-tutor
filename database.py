import sqlite3
from datetime import datetime

DB_NAME = "tutor.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mastery(
            student_name TEXT,
            concept TEXT,
            score REAL DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            PRIMARY KEY(student_name, concept)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attempts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            concept TEXT,
            question TEXT,
            selected_answer TEXT,
            correct_answer TEXT,
            is_correct INTEGER,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_student(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO students(name) VALUES(?)",
        (name,)
    )
    conn.commit()
    conn.close()

def get_mastery(student_name, concept):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT score FROM mastery WHERE student_name=? AND concept=?",
        (student_name, concept)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_all_mastery(student_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT concept, score FROM mastery WHERE student_name=?",
        (student_name,)
    )
    rows = cur.fetchall()
    conn.close()
    return dict(rows)

def save_attempt(student_name, concept, question, selected, correct_answer, is_correct):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attempts
        (student_name, concept, question, selected_answer,
        correct_answer, is_correct, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_name,
        concept,
        question,
        selected,
        correct_answer,
        int(is_correct),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def save_mastery(student_name, concept, score, attempts, correct):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO mastery(student_name, concept, score, attempts, correct)
        VALUES(?,?,?,?,?)
        ON CONFLICT(student_name, concept)
        DO UPDATE SET
        score=excluded.score,
        attempts=excluded.attempts,
        correct=excluded.correct
    """, (student_name, concept, score, attempts, correct))

    conn.commit()
    conn.close()

def get_student_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    student_count = cur.fetchone()[0]
    cur.execute("SELECT AVG(score) FROM mastery")
    average = cur.fetchone()[0] or 0
    cur.execute("""
        SELECT concept, AVG(score)
        FROM mastery
        GROUP BY concept
        ORDER BY AVG(score)
    """)
    concept_stats = cur.fetchall()
    cur.execute("""
        SELECT student_name, AVG(score)
        FROM mastery
        GROUP BY student_name
    """)
    student_stats = cur.fetchall()
    conn.close()
    return student_count, average, concept_stats, student_stats