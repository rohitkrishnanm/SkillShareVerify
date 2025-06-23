import sqlite3

DB_PATH = "submissions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            student_name TEXT,
            institution TEXT,
            question_summary TEXT,
            score INTEGER,
            evaluation_result TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_submission(timestamp, student_name, institution, question_summary, score, evaluation_result):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO submissions (timestamp, student_name, institution, question_summary, score, evaluation_result)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, student_name, institution, question_summary, score, evaluation_result))
    conn.commit()
    conn.close()

def get_all_submissions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM submissions')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_submission(submission_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM submissions WHERE id = ?', (submission_id,))
    conn.commit()
    conn.close()
