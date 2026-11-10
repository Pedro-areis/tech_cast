"""Spike (disposable): measure each candidate RSS feed over the last 7 days.

Run: uv run --group spikes python spikes/rss_probe.py
"""

import re
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import feedparser
import httpx

HERE = Path(__file__).parent
DAYS = 7
HEADERS = {"User-Agent": "TechCastSpike/0.1 (personal podcast project)"}
TAG_RE = re.compile(r"<[^>]+>")


def entry_date(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=UTC)


def probe(client: httpx.Client, feed: dict, cutoff: datetime) -> dict:
    row = {"name": feed["name"], "lang": feed["lang"], "category": feed["category"]}
    try:
        resp = client.get(feed["url"])
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        return row | {"error": f"{type(exc).__name__} {getattr(getattr(exc, 'response', None), 'status_code', '')}".strip()}
    parsed = feedparser.parse(resp.content)
    entries = parsed.entries
    if not entries:
        return row | {"error": "no entries (invalid XML?)"}
    dated = [(e, entry_date(e)) for e in entries]
    recent = [e for e, d in dated if d and d >= cutoff]
    summaries = [len(TAG_RE.sub("", e.get("summary", ""))) for e in recent]
    return row | {
        "total": len(entries),
        "recent": len(recent),
        "no_date": sum(1 for _, d in dated if d is None),
        "avg_summary": round(sum(summaries) / len(summaries)) if summaries else 0,
        "oldest": min((d for _, d in dated if d), default=None),
    }


def main() -> None:
    feeds = tomllib.loads((HERE / "feeds_candidates.toml").read_text())["feed"]
    cutoff = datetime.now(UTC) - timedelta(days=DAYS)
    rows = []
    with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        for feed in feeds:
            rows.append(probe(client, feed, cutoff))

    print(f"{'feed':28} {'lang':4} {'cat':10} {'7d':>4} {'in feed':>7} {'nodate':>6} {'avg sum':>7}  note")
    for r in rows:
        if "error" in r:
            print(f"{r['name']:28} {r['lang']:4} {r['category']:10} {'-':>4} {'-':>7} {'-':>6} {'-':>7}  ERROR {r['error']}")
            continue
        note = ""
        if r["oldest"] and r["oldest"] > cutoff:
            note = "feed window < 7d (count is a lower bound)"
        print(
            f"{r['name']:28} {r['lang']:4} {r['category']:10} {r['recent']:>4} {r['total']:>7} "
            f"{r['no_date']:>6} {r['avg_summary']:>7}  {note}"
        )
    ok = [r for r in rows if "error" not in r]
    print(f"\nOK: {len(ok)}/{len(rows)} feeds; total items in 7d: {sum(r['recent'] for r in ok)}")


if __name__ == "__main__":
    main()
