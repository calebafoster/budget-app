import argparse
from functions import *

parser = argparse.ArgumentParser(description="Budget app")
subparsers = parser.add_subparsers(dest="command")

subparsers.add_parser("overview", aliases=["o"], help="Print db overview")

t = subparsers.add_parser("add-transaction", aliases=["t"], help="Add a transaction")
t.add_argument("name")
t.add_argument("amount", type=float)
t.add_argument("--bucket", "-b", default=None, help="Bucket name or id")

b = subparsers.add_parser("add-bucket", aliases=["b"], help="Add a bucket")
b.add_argument("name")
b.add_argument("--check-percentage", "-p", type=float, default=0.0)

d = subparsers.add_parser("add-deposit", aliases=["d"], help="Add a deposit")
d.add_argument("amount", type=float)
d.add_argument("--label", "-l", default=None)

p = subparsers.add_parser("set-percentage", aliases=["p"], help="Set a bucket's check percentage")
p.add_argument("bucket")
p.add_argument("percentage", type=float)

a = subparsers.add_parser("add-to-bucket", aliases=["a"], help="Add an amount to a bucket")
a.add_argument("bucket", help="Bucket name or id")
a.add_argument("amount", type=float)

s = subparsers.add_parser("set-total", help="Directly set the account total")
s.add_argument("amount", type=float)

args = parser.parse_args()

if args.command in ("overview", "o", None):
    overview()
elif args.command in ("add-transaction", "t"):
    bucket = int(args.bucket) if args.bucket and args.bucket.isdigit() else args.bucket
    add_transaction(args.name, args.amount, bucket)
elif args.command in ("add-bucket", "b"):
    add_bucket(args.name, args.check_percentage)
elif args.command in ("add-deposit", "d"):
    add_deposit(args.amount, args.label)
elif args.command in ("set-percentage", "p"):
    set_bucket_percentage(args.bucket, args.percentage)
elif args.command in ("add-to-bucket", "a"):
    bucket = int(args.bucket) if args.bucket.isdigit() else args.bucket
    add_to_bucket(bucket, args.amount)
elif args.command == "set-total":
    set_total(args.amount)
