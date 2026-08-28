# CLAUDE.md

Personal budgeting app: two front-ends (Flask web + argparse CLI) over one SQLite database.

## Layout

| File | Purpose |
|---|---|
| `app.py` | Flask web app. Runs on port 9901, `debug=True`. Password-gated via `@app.before_request`. Renders `templates/index.html` / `templates/login.html`. |
| `main.py` | CLI with the same operations (`python main.py <command>`). `overview`/`o` is the default. |
| `functions.py` | Shared data layer. Every function opens and closes its own `sqlite3` connection. |
| `budget.db` | SQLite database (committed to the repo). |
| `templates/` | `index.html` (single-page dashboard + all forms), `login.html`. |
| `requirements.txt` | `flask`, `gunicorn`. |

## Environment variables

- `DB_PATH` — database path (default `budget.db`)
- `BUDGET_PASSWORD` — web login password (default `changeme`)

## Data model (`budget.db`)

| Table | Columns | Notes |
|---|---|---|
| `accounts` | id, name, total | Single row with `name = 'total'`. This is the real account balance. |
| `buckets` | id, name, total, check_percentage | Envelope-style categories. `check_percentage` is stored per bucket but nothing auto-splits deposits by it yet. |
| `transactions` | id, name, amount, bucket_id → buckets(id) | Spending log only. |
| `deposits` | id, amount, label | Deposit log. |
| `unbucketed` | total (VIEW) | Computed: `accounts.total` − `SUM(buckets.total)`. |

## Operations

Each exists as a web route in `app.py` and (mostly) a CLI subcommand in `main.py`, both calling into `functions.py`:

- `add_transaction(name, amount, bucket=None)` — inserts a transaction row. `bucket` may be a name or an int id.
- `add_deposit(amount, label=None)` — inserts a deposit **and** adds the amount to `accounts.total`.
- `add_bucket(name, check_percentage=0.0)` — creates a bucket at total 0.
- `add_to_bucket(bucket, amount)` — adds to a bucket's `total`.
- `move_between_buckets(from_bucket, to_bucket, amount)` — moves between bucket totals.
- `set_bucket_percentage(bucket, percentage)` — sets `check_percentage`.
- `set_total(amount)` — directly overwrites `accounts.total`.
- `dump_bucket(name)` — sets a bucket's total to 0.
- `delete_bucket(name)` — nulls `bucket_id` on its transactions, then deletes the bucket.

CLI has no subcommand for `move-between-buckets`, `dump-bucket`, or `set-percentage` parity is partial — the web app is the fuller interface.

## Behavior notes / rough edges

- **Money is stored as SQLite `REAL`** (float) — rounding drift is possible.
- **Transactions are log-only.** Adding a transaction never changes `accounts.total` or any bucket total. Only deposits move `accounts.total`; only the explicit bucket operations move bucket totals.
- `add_to_bucket` / `move_between_buckets` do **not** verify the bucket exists — a bad name silently no-ops (or writes to `id = NULL`).
- `app.secret_key` is hardcoded (`"budget-secret-key"`); default password is `changeme`.
- Web app runs with `debug=True`.
- No test suite.

## Running

```
# Web
python app.py                 # http://localhost:9901
# or: gunicorn app:app

# CLI
python main.py overview       # dump all tables + computed unbucketed
python main.py add-deposit 1000 --label Paycheck
python main.py add-bucket rent --check-percentage 30
```
