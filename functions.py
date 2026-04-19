import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "budget.db")


def overview():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = cur.fetchall()

    for (table,) in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        cur.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        print(f"{table} ({count} rows): {', '.join(cols)}")

        cur.execute(f"SELECT * FROM {table}")
        for row in cur.fetchall():
            print(f"  {row}")
        print()

    cur.execute("SELECT total FROM unbucketed")
    unbucketed = cur.fetchone()[0]
    print(f"unbucketed (computed): {unbucketed}")

    conn.close()


def set_bucket_percentage(bucket_name, percentage):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE buckets SET check_percentage = ? WHERE name = ?",
        (percentage, bucket_name)
    )
    conn.commit()
    conn.close()


def add_transaction(name, amount, bucket=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    bucket_id = None
    if bucket is not None:
        if isinstance(bucket, int):
            bucket_id = bucket
        else:
            row = cur.execute("SELECT id FROM buckets WHERE name = ?", (bucket,)).fetchone()
            if row:
                bucket_id = row[0]
    cur.execute(
        "INSERT INTO transactions (name, amount, bucket_id) VALUES (?, ?, ?)",
        (name, amount, bucket_id)
    )
    conn.commit()
    conn.close()


def move_between_buckets(from_bucket, to_bucket, amount):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    def resolve(bucket):
        if isinstance(bucket, int):
            return bucket
        row = cur.execute("SELECT id FROM buckets WHERE name = ?", (bucket,)).fetchone()
        return row[0] if row else None

    from_id = resolve(from_bucket)
    to_id = resolve(to_bucket)

    cur.execute("UPDATE buckets SET total = total - ? WHERE id = ?", (amount, from_id))
    cur.execute("UPDATE buckets SET total = total + ? WHERE id = ?", (amount, to_id))
    conn.commit()
    conn.close()


def add_to_bucket(bucket, amount):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if isinstance(bucket, int):
        cur.execute("UPDATE buckets SET total = total + ? WHERE id = ?", (amount, bucket))
    else:
        cur.execute("UPDATE buckets SET total = total + ? WHERE name = ?", (amount, bucket))
    conn.commit()
    conn.close()


def dump_bucket(bucket_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE buckets SET total = 0.0 WHERE name = ?", (bucket_name,))
    conn.commit()
    conn.close()


def delete_bucket(bucket_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE transactions SET bucket_id = NULL WHERE bucket_id = (SELECT id FROM buckets WHERE name = ?)", (bucket_name,))
    cur.execute("DELETE FROM buckets WHERE name = ?", (bucket_name,))
    conn.commit()
    conn.close()


def add_bucket(name, check_percentage=0.0):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO buckets (name, total, check_percentage) VALUES (?, 0.0, ?)",
        (name, check_percentage)
    )
    conn.commit()
    conn.close()


def set_total(amount):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET total = ? WHERE name = 'total'", (amount,))
    conn.commit()
    conn.close()


def add_deposit(amount, label=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deposits (amount, label) VALUES (?, ?)",
        (amount, label)
    )
    cur.execute("UPDATE accounts SET total = total + ? WHERE name = 'total'", (amount,))
    conn.commit()
    conn.close()
