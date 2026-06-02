"""SQLite database for vocabulary progress tracking."""

import sqlite3
import json
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "vocab.db")
WORDS_PATH = os.path.join(os.path.dirname(__file__), "words.json")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS progress (
            word TEXT PRIMARY KEY,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            last_seen DATE,
            mastered INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS daily_log (
            date DATE PRIMARY KEY,
            total INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


def load_words():
    with open(WORDS_PATH, encoding="utf-8") as f:
        return json.load(f)["words"]


def get_progress(word):
    conn = get_conn()
    row = conn.execute("SELECT * FROM progress WHERE word=?", (word,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"word": word, "correct_count": 0, "wrong_count": 0, "last_seen": None, "mastered": 0}


def record_answer(word, correct):
    conn = get_conn()
    today = date.today().isoformat()
    existing = conn.execute("SELECT * FROM progress WHERE word=?", (word,)).fetchone()
    if existing:
        if correct:
            conn.execute("UPDATE progress SET correct_count=correct_count+1, last_seen=?, mastered=CASE WHEN correct_count+1>=5 THEN 1 ELSE 0 END WHERE word=?", (today, word))
        else:
            conn.execute("UPDATE progress SET wrong_count=wrong_count+1, last_seen=?, mastered=0 WHERE word=?", (today, word))
    else:
        conn.execute("INSERT INTO progress (word, correct_count, wrong_count, last_seen, mastered) VALUES (?,?,?,?,?)",
                     (word, 1 if correct else 0, 0 if correct else 1, today, 0))
    conn.commit()
    conn.close()


def update_daily_log(correct):
    conn = get_conn()
    today = date.today().isoformat()
    row = conn.execute("SELECT * FROM daily_log WHERE date=?", (today,)).fetchone()
    if row:
        conn.execute("UPDATE daily_log SET total=total+1, correct=correct+? WHERE date=?",
                     (1 if correct else 0, today))
    else:
        conn.execute("INSERT INTO daily_log (date, total, correct) VALUES (?,?,?)",
                     (today, 1, 1 if correct else 0))
    conn.commit()
    conn.close()


def get_today_log():
    conn = get_conn()
    today = date.today().isoformat()
    row = conn.execute("SELECT * FROM daily_log WHERE date=?", (today,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats():
    conn = get_conn()
    total_words = conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
    mastered = conn.execute("SELECT COUNT(*) FROM progress WHERE mastered=1").fetchone()[0]
    total_correct = conn.execute("SELECT SUM(correct_count) FROM progress").fetchone()[0] or 0
    total_wrong = conn.execute("SELECT SUM(wrong_count) FROM progress").fetchone()[0] or 0
    conn.close()
    return {
        "total_studied": total_words,
        "mastered": mastered,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
    }


def get_wrong_words():
    conn = get_conn()
    rows = conn.execute(
        "SELECT word, wrong_count, correct_count FROM progress WHERE wrong_count > correct_count ORDER BY wrong_count DESC"
    ).fetchall()
    conn.close()
    all_words = load_words()
    word_map = {w["word"]: w for w in all_words}
    result = []
    for r in rows:
        w = r["word"]
        if w in word_map:
            entry = dict(word_map[w])
            entry["wrong_count"] = r["wrong_count"]
            entry["correct_count"] = r["correct_count"]
            result.append(entry)
    return result
