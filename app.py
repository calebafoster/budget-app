import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functions import DB_PATH
from functions import (
    add_transaction, add_deposit, add_bucket, add_to_bucket,
    move_between_buckets, set_bucket_percentage, set_total, dump_bucket, delete_bucket
)

app = Flask(__name__)
app.secret_key = "budget-secret-key"

PASSWORD = os.environ.get("BUDGET_PASSWORD", "changeme")


@app.before_request
def require_login():
    if request.endpoint not in ("login",) and not session.get("authed"):
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["authed"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Wrong password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def get_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT total FROM accounts WHERE name = 'total'")
    account_total = cur.fetchone()[0]
    cur.execute("SELECT id, name, total, check_percentage FROM buckets ORDER BY name")
    buckets = cur.fetchall()
    cur.execute("SELECT total FROM unbucketed")
    unbucketed = cur.fetchone()[0]
    cur.execute("""
        SELECT t.id, t.name, t.amount, b.name
        FROM transactions t LEFT JOIN buckets b ON t.bucket_id = b.id
        ORDER BY t.id DESC LIMIT 30
    """)
    transactions = cur.fetchall()
    cur.execute("SELECT id, amount, label FROM deposits ORDER BY id DESC LIMIT 20")
    deposits = cur.fetchall()
    conn.close()
    return dict(account_total=account_total, buckets=buckets,
                unbucketed=unbucketed, transactions=transactions, deposits=deposits)


@app.route("/")
def index():
    return render_template("index.html", **get_data())


@app.route("/add-transaction", methods=["POST"])
def add_transaction_route():
    name = request.form["name"]
    amount = float(request.form["amount"])
    bucket = request.form.get("bucket") or None
    if bucket and bucket.isdigit():
        bucket = int(bucket)
    add_transaction(name, amount, bucket)
    flash(f'Transaction "{name}" ${amount:.2f} added.')
    return redirect(url_for("index"))


@app.route("/add-deposit", methods=["POST"])
def add_deposit_route():
    amount = float(request.form["amount"])
    label = request.form.get("label") or None
    add_deposit(amount, label)
    flash(f"Deposit ${amount:.2f} added.")
    return redirect(url_for("index"))


@app.route("/add-to-bucket", methods=["POST"])
def add_to_bucket_route():
    bucket = request.form["bucket"]
    amount = float(request.form["amount"])
    add_to_bucket(bucket, amount)
    flash(f"Added ${amount:.2f} to {bucket}.")
    return redirect(url_for("index"))


@app.route("/move-between-buckets", methods=["POST"])
def move_between_buckets_route():
    from_bucket = request.form["from_bucket"]
    to_bucket = request.form["to_bucket"]
    amount = float(request.form["amount"])
    move_between_buckets(from_bucket, to_bucket, amount)
    flash(f"Moved ${amount:.2f} from {from_bucket} to {to_bucket}.")
    return redirect(url_for("index"))


@app.route("/add-bucket", methods=["POST"])
def add_bucket_route():
    name = request.form["name"]
    pct = float(request.form.get("check_percentage") or 0)
    add_bucket(name, pct)
    flash(f'Bucket "{name}" created.')
    return redirect(url_for("index"))


@app.route("/set-percentage", methods=["POST"])
def set_percentage_route():
    bucket = request.form["bucket"]
    pct = float(request.form["percentage"])
    set_bucket_percentage(bucket, pct)
    flash(f'Set {bucket} percentage to {pct}%.')
    return redirect(url_for("index"))


@app.route("/set-total", methods=["POST"])
def set_total_route():
    amount = float(request.form["amount"])
    set_total(amount)
    flash(f"Account total set to ${amount:.2f}.")
    return redirect(url_for("index"))


@app.route("/dump-bucket", methods=["POST"])
def dump_bucket_route():
    bucket = request.form["bucket"]
    dump_bucket(bucket)
    flash(f'Bucket "{bucket}" cleared.')
    return redirect(url_for("index"))


@app.route("/delete-bucket", methods=["POST"])
def delete_bucket_route():
    bucket = request.form["bucket"]
    delete_bucket(bucket)
    flash(f'Bucket "{bucket}" deleted.')
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9901, debug=True)
