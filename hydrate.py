"""
hydrate.py — recover Tweet Content for this dataset.

This dataset ships message IDs and labels, not message text. That is what
X's Developer Agreement permits redistributing, and it is also what keeps
the dataset honest over time: a message its author later deleted simply does
not come back, so your copy stays current with what is actually public.

Two modes:

  --timestamps-only   No network, no credentials, no X account needed.
                      Reconstructs created_at arithmetically from the
                      snowflake ID (IDs issued after 2010-11-04 encode their
                      own creation time to the millisecond). Covers
                      66,803 / 66,890 IDs in this dataset; the 87 older ones
                      predate snowflake and are left blank.

  (default)           Fetches text and engagement metrics from the X API v2.
                      Needs a bearer token with the tweets-lookup scope:
                          export X_BEARER_TOKEN=...
                      Requests 100 IDs per call, honours rate limits, and
                      writes partial progress so it can be resumed.

Between them the two modes reconstruct every field withheld from this
release: text, created_at, lang, conversation_id, ref_type, and the four
engagement counts.

Usage:
    python hydrate.py --timestamps-only              # offline
    python hydrate.py                                # full hydration
    python hydrate.py --in messages.csv --out hydrated.csv

Each mode writes to its own default output (hydrated.csv and
timestamps.csv), so a full run is never mistaken for a resume of an
offline one.

Paths ending in .gz are read and written gzip-compressed, so
`--out hydrated.csv.gz` works if you would rather keep it packed.
"""

import argparse
import csv
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SNOWFLAKE_EPOCH_MS = 1288834974657   # 2010-11-04T01:42:54.657Z
API = "https://api.x.com/2/tweets"
FIELDS = "id,text,created_at,lang,conversation_id,public_metrics,referenced_tweets"
BATCH = 100


def opener(path, mode="rt"):
    return (gzip.open(path, mode, newline="", encoding="utf-8")
            if str(path).endswith(".gz")
            else open(path, mode, newline="", encoding="utf-8"))


def snowflake_time(message_id):
    """created_at from the ID itself. None for pre-snowflake IDs."""
    i = int(message_id)
    if i < 29700859247:          # first snowflake-era ID
        return None
    ms = (i >> 22) + SNOWFLAKE_EPOCH_MS
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z")


def read_ids(path):
    with opener(path) as f:
        return [r["message_id"] for r in csv.DictReader(f) if r.get("message_id")]


def fetch(ids, token):
    q = urllib.parse.urlencode({"ids": ",".join(ids), "tweet.fields": FIELDS})
    req = urllib.request.Request(f"{API}?{q}",
                                 headers={"Authorization": f"Bearer {token}"})
    while True:
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                reset = e.headers.get("x-rate-limit-reset")
                wait = max(5, int(reset) - int(time.time())) if reset else 60
                print(f"  rate limited; sleeping {wait}s", flush=True)
                time.sleep(wait)
                continue
            if e.code in (500, 502, 503, 504):
                time.sleep(5)
                continue
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="messages.csv")
    ap.add_argument("--out", dest="out", default=None,
                    help="default: hydrated.csv, or timestamps.csv "
                         "with --timestamps-only; .gz paths are compressed")
    ap.add_argument("--timestamps-only", action="store_true")
    a = ap.parse_args()

    # Distinct defaults per mode: sharing one would let a timestamps file be
    # read back as hydration progress, and every id would look already done.
    if a.out is None:
        a.out = "timestamps.csv" if a.timestamps_only else "hydrated.csv"

    if not Path(a.inp).exists():
        sys.exit(f"not found: {a.inp}")
    ids = read_ids(a.inp)
    print(f"{len(ids)} message ids from {a.inp}")

    # ---------------- offline mode ----------------
    if a.timestamps_only:
        n_ok = 0
        with opener(a.out, "wt") as f:
            w = csv.writer(f)
            w.writerow(["message_id", "created_at"])
            for i in ids:
                ts = snowflake_time(i)
                n_ok += ts is not None
                w.writerow([i, ts or ""])
        print(f"derived {n_ok}/{len(ids)} timestamps offline "
              f"({len(ids) - n_ok} pre-snowflake) -> {a.out}")
        return

    # ---------------- API mode ----------------
    token = os.getenv("X_BEARER_TOKEN", "").strip()
    if not token:
        sys.exit("X_BEARER_TOKEN not set.\n"
                 "Either export a bearer token, or run with --timestamps-only "
                 "for the offline subset.")

    cols = ["message_id", "text", "created_at", "lang", "conversation_id",
            "ref_type", "like_count", "retweet_count", "reply_count",
            "impression_count"]

    done = set()
    if Path(a.out).exists():
        with opener(a.out) as f:
            r = csv.DictReader(f)
            if r.fieldnames != cols:
                sys.exit(f"{a.out} exists but is not a hydration file "
                         f"(header: {r.fieldnames}).\n"
                         "Point --out somewhere else, or delete it.")
            done = {row["message_id"] for row in r}
        print(f"resuming: {len(done)} already hydrated")

    todo = [i for i in ids if i not in done]
    new = not Path(a.out).exists()
    n_got = n_gone = 0
    with opener(a.out, "at") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        for s in range(0, len(todo), BATCH):
            batch = todo[s:s + BATCH]
            payload = fetch(batch, token)
            for t in payload.get("data", []):
                m = t.get("public_metrics", {})
                ref = t.get("referenced_tweets") or []
                w.writerow({
                    "message_id": t["id"], "text": t.get("text", ""),
                    "created_at": t.get("created_at", ""),
                    "lang": t.get("lang", ""),
                    "conversation_id": t.get("conversation_id", ""),
                    "ref_type": ref[0].get("type", "") if ref else "original",
                    "like_count": m.get("like_count", 0),
                    "retweet_count": m.get("retweet_count", 0),
                    "reply_count": m.get("reply_count", 0),
                    "impression_count": m.get("impression_count", 0),
                })
                n_got += 1
            n_gone += len(payload.get("errors", []))
            f.flush()
            print(f"  {min(s + BATCH, len(todo))}/{len(todo)} "
                  f"(recovered {n_got}, unavailable {n_gone})", flush=True)

    print(f"\nhydrated {n_got}; {n_gone} unavailable (deleted, suspended, or "
          f"protected since collection) -> {a.out}")
    print("Join back to the dataset on message_id.")


if __name__ == "__main__":
    main()
