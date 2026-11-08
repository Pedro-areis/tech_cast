# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.28", "feedparser>=6.0"]
# ///
"""Spike da Fase 1 (D6): mede o volume semanal de cada feed RSS candidato.

Descartável. Roda com: uv run spikes/rss_probe.py
As dependências acima são lidas pelo `uv` (PEP 723), sem mexer no pyproject.toml.
Faz 1 requisição por feed (com User-Agent identificado) e não grava nada em disco.
"""

import re
import statistics
import time
from datetime import UTC, datetime, timedelta

import feedparser
import httpx

USER_AGENT = "TechCastSpike/0.1 (projeto pessoal; teste de viabilidade de RSS)"

# (idioma, veículo, URL). Lista candidata: a medição decide o que sobrevive.
FEEDS = [
    ("pt", "Tecnoblog", "https://tecnoblog.net/feed/"),
    ("pt", "Canaltech", "https://canaltech.com.br/rss/"),
    ("pt", "Olhar Digital", "https://olhardigital.com.br/feed/"),
    ("pt", "TecMundo", "https://rss.tecmundo.com.br/feed"),
    ("pt", "Showmetech", "https://www.showmetech.com.br/feed/"),
    ("pt", "Adrenaline", "https://adrenaline.com.br/feed/"),
    ("pt", "MacMagazine", "https://macmagazine.com.br/feed/"),
    ("pt", "Folha Tec", "https://feeds.folha.uol.com.br/tec/rss091.xml"),
    ("pt", "g1 Tecnologia", "https://g1.globo.com/rss/g1/tecnologia/"),
    ("en", "The Verge", "https://www.theverge.com/rss/index.xml"),
    ("en", "Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("en", "TechCrunch", "https://techcrunch.com/feed/"),
    ("en", "Wired", "https://www.wired.com/feed/rss"),
    ("en", "Engadget", "https://www.engadget.com/rss.xml"),
    ("en", "MIT Technology Review", "https://www.technologyreview.com/feed/"),
    ("en", "BBC Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("en", "The Register", "https://www.theregister.com/headlines.atom"),
    ("en", "Hacker News (front page)", "https://hnrss.org/frontpage"),
    ("en", "OpenAI News", "https://openai.com/news/rss.xml"),
    ("en", "Google Blog", "https://blog.google/rss/"),
    ("en", "GitHub Blog", "https://github.blog/feed/"),
]

TAG_RE = re.compile(r"<[^>]+>")


def entry_datetime(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=UTC)


def probe(client: httpx.Client, lang: str, name: str, url: str, now: datetime) -> dict:
    row = {"lang": lang, "name": name, "url": url, "status": None, "error": None}
    start = time.monotonic()
    try:
        response = client.get(url)
        row["status"] = response.status_code
        row["final_url"] = str(response.url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"[:120]
        return row
    finally:
        row["seconds"] = round(time.monotonic() - start, 1)

    feed = feedparser.parse(response.content)
    entries = feed.entries
    dates = [entry_datetime(e) for e in entries]
    dated = [d for d in dates if d]
    row["total"] = len(entries)
    row["no_date"] = len(entries) - len(dated)
    row["last_7d"] = sum(1 for d in dated if now - d <= timedelta(days=7))
    row["oldest"] = min(dated).date().isoformat() if dated else None
    row["newest"] = max(dated).date().isoformat() if dated else None
    # Se o feed não cobre 7 dias (só guarda os N últimos itens), o "last_7d" é um piso.
    row["covers_7d"] = bool(dated) and min(dated) <= now - timedelta(days=7)
    # Estimativa semanal: itens / dias cobertos * 7.
    if len(dated) >= 2:
        span_days = max((max(dated) - min(dated)).total_seconds() / 86400, 0.1)
        row["per_week_est"] = round(len(dated) / span_days * 7)
    summaries = [len(TAG_RE.sub("", e.get("summary", ""))) for e in entries if e.get("summary")]
    row["summary_chars_median"] = int(statistics.median(summaries)) if summaries else 0
    row["has_link"] = sum(1 for e in entries if e.get("link"))
    return row


def main() -> None:
    now = datetime.now(UTC)
    rows = []
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=20,
    ) as client:
        for lang, name, url in FEEDS:
            rows.append(probe(client, lang, name, url, now))
            time.sleep(1)  # educação com os servidores

    cols = ("lang", "veículo", "http", "itens", "7d", "/sem*", "sem data", "resumo", "cobre 7d")
    header = " ".join(cols) + "  mais antigo"
    print(header)
    print("-" * len(header))
    for r in rows:
        if r.get("error") or "total" not in r:
            print(f"{r['lang']:4} {r['name']:26} {str(r['status']):>4}  ERRO: {r['error']}")
            continue
        print(
            f"{r['lang']:4} {r['name']:26} {r['status']:>4} {r['total']:>5} {r['last_7d']:>4} "
            f"{r.get('per_week_est', '-'):>5} {r['no_date']:>8} {r['summary_chars_median']:>6} "
            f"{'sim' if r['covers_7d'] else 'não':>8} {r['oldest']:>11}"
        )
    print("\n7d = itens publicados nos últimos 7 dias; /sem* = estimativa pelo intervalo do feed;")
    print(
        "resumo = mediana de caracteres do resumo sem HTML;"
        " 'cobre 7d' = o feed alcança 7 dias atrás."
    )
    redirects = [r for r in rows if r.get("final_url") and r["final_url"] != r["url"]]
    for r in redirects:
        print(f"redirect: {r['name']} -> {r['final_url']}")


if __name__ == "__main__":
    main()
