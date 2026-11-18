"""Spike (disposable): curation + script with Gemini over real RSS items, measuring tokens.

Two calls, like the future pipeline:
  1. curation: all items -> chosen stories (item ids only)
  2. script:   chosen stories -> podcast script JSON

Run: uv run --group spikes python spikes/gemini_script.py [--model gemini-3.8-flash]
Reads GEMINI_API_KEY from the environment or from .env. Output goes to spikes/out/.
"""

import argparse
import json
import os
import re
import time
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import feedparser
import httpx
from pydantic import BaseModel, Field

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = HERE / "out"
DAYS = 7
SUMMARY_CHARS = 500
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
HEADERS = {"User-Agent": "TechCastSpike/0.1 (personal podcast project)"}
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

# 9 BR + 9 foreign feeds (chosen 2026-11-12; supersedes the 2026-11-09 cut for the spike).
KEEP = {
    "Tecnoblog", "Canaltech", "Tecmundo", "Olhar Digital", "Adrenaline", "Mobile Time",
    "Convergência Digital", "Meio Bit", "Núcleo",
    "The Verge", "TechCrunch", "Ars Technica", "Engadget", "MIT Technology Review",
    "BleepingComputer", "BBC Technology", "The Register", "InfoQ",
}  # fmt: skip


# ---------- Pydantic models for the LLM output ----------
class Story(BaseModel):
    title: str
    category: str
    item_ids: list[int] = Field(min_length=1)


class Curation(BaseModel):
    stories: list[Story] = Field(min_length=1)


class Section(BaseModel):
    heading: str
    text: str
    source_item_ids: list[int] = Field(min_length=1)


class Script(BaseModel):
    title: str
    sections: list[Section] = Field(min_length=1)


# ---------- .env and collection ----------
def load_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def clean(text: str) -> str:
    return SPACE_RE.sub(" ", TAG_RE.sub(" ", text)).strip()


def collect() -> list[dict]:
    feeds = [f for f in tomllib.loads((HERE / "feeds_candidates.toml").read_text())["feed"]]
    feeds = [f for f in feeds if f["name"] in KEEP]
    cutoff = datetime.now(UTC) - timedelta(days=DAYS)
    items, seen = [], set()
    with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        for feed in feeds:
            try:
                resp = client.get(feed["url"])
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                print(f"  aviso: {feed['name']} falhou ({type(exc).__name__})")
                continue
            for e in feedparser.parse(resp.content).entries:
                parsed = e.get("published_parsed") or e.get("updated_parsed")
                link = e.get("link")
                if not parsed or not link or link in seen:
                    continue
                date = datetime(*parsed[:6], tzinfo=UTC)
                if date < cutoff:
                    continue
                seen.add(link)
                items.append(
                    {
                        "outlet": feed["name"],
                        "lang": feed["lang"],
                        "title": clean(e.get("title", "")),
                        "url": link,
                        "date": date.date().isoformat(),
                        "summary": clean(e.get("summary", ""))[:SUMMARY_CHARS],
                    }
                )
    for i, item in enumerate(items, start=1):
        item["id"] = i
    return items


# ---------- Gemini ----------
def call_gemini(client: httpx.Client, model: str, key: str, prompt: str, label: str) -> dict:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
    }
    start = time.monotonic()
    for attempt in range(1, 5):
        try:
            resp = client.post(API.format(model=model), headers={"x-goog-api-key": key}, json=body)
        except httpx.TimeoutException:
            print(f"  [{label}] tentativa {attempt}: timeout")
            continue
        if resp.status_code in (429, 500, 503):
            print(f"  [{label}] tentativa {attempt}: HTTP {resp.status_code}, aguardando")
            time.sleep(15 * attempt)
            continue
        break
    else:
        raise SystemExit(f"{label}: sem resposta depois de 4 tentativas")
    elapsed = time.monotonic() - start
    (OUT / f"{label}_raw.json").write_text(resp.text)
    if resp.status_code != 200:
        print(f"  ERRO {resp.status_code} em {label}: {resp.text[:600]}")
        raise SystemExit(1)
    data = resp.json()
    usage = data.get("usageMetadata", {})
    print(
        f"  [{label}] {elapsed:.1f}s | entrada {usage.get('promptTokenCount')} | "
        f"saída {usage.get('candidatesTokenCount')} | "
        f"raciocínio {usage.get('thoughtsTokenCount', 0)} | "
        f"total {usage.get('totalTokenCount')}"
    )
    candidate = data["candidates"][0]
    if candidate.get("finishReason") not in (None, "STOP"):
        print(f"  atenção: finishReason={candidate['finishReason']}")
    text = "".join(p.get("text", "") for p in candidate["content"]["parts"])
    return {"text": text, "usage": usage, "seconds": elapsed}


def curation_prompt(items: list[dict]) -> str:
    lines = [
        f"[{i['id']}] ({i['outlet']}, {i['date']}) {i['title']} :: {i['summary']}" for i in items
    ]
    return (
        "Você é o curador de um podcast semanal de notícias de tecnologia em português do Brasil.\n"
        "Abaixo estão as notícias da última semana, uma por linha, com [id].\n"
        "Tarefa: agrupe notícias sobre o mesmo fato em uma pauta, descarte reviews, ofertas e "
        "opinião, e escolha de 8 a 12 pautas de maior relevância para um público brasileiro "
        "interessado em tecnologia. Dê a cada pauta um título curto em português e uma categoria "
        "(ia, seguranca, mobile, negocios, infraestrutura, produtos ou outra).\n"
        'Responda só JSON: {"stories":[{"title":str,"category":str,"item_ids":[int]}]}. '
        "Use apenas ids que existem na lista.\n\n" + "\n".join(lines)
    )


def script_prompt(stories: list[Story], by_id: dict[int, dict]) -> str:
    blocks = []
    for s in stories:
        src = "\n".join(
            f"  - [{i}] {by_id[i]['outlet']} ({by_id[i]['date']}): {by_id[i]['title']} :: "
            f"{by_id[i]['summary']}"
            for i in s.item_ids
            if i in by_id
        )
        blocks.append(f"PAUTA: {s.title} ({s.category})\n{src}")
    return (
        "Você é roteirista de um podcast semanal de notícias de tecnologia em português do Brasil, "
        "com um único apresentador, tom conversado e claro.\n"
        "Escreva o roteiro do episódio com base APENAS nas pautas abaixo. Regras:\n"
        "- Entre 1.800 e 2.100 palavras no total, em texto corrido para ser lido em voz alta "
        "(sem listas, sem markdown, sem emojis).\n"
        "- Seções: abertura, uma seção por pauta (ou por grupo de pautas da mesma categoria), "
        "com transições naturais, e encerramento.\n"
        "- Cite o veículo de cada informação (ex.: 'segundo o Tecnoblog').\n"
        "- Marque rumores e informações não confirmadas como tal. Não invente fatos além dos "
        "resumos e não copie trechos literais.\n"
        "- Em cada seção, liste em source_item_ids os ids [n] das notícias usadas "
        "(a abertura e o encerramento podem repetir ids de pautas que resumem).\n"
        'Responda só JSON: {"title":str,"sections":[{"heading":str,"text":str,'
        '"source_item_ids":[int]}]}.\n\n' + "\n\n".join(blocks)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gemini-3.8-flash")
    model = parser.parse_args().model
    load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY ausente (.env ou ambiente)")
    OUT.mkdir(exist_ok=True)

    print(f"Modelo: {model}\n1) Coleta")
    items = collect()
    by_id = {i["id"]: i for i in items}
    print(f"  {len(items)} itens nos últimos {DAYS} dias (resumo cortado em {SUMMARY_CHARS} chars)")
    (OUT / "items.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))

    with httpx.Client(timeout=180) as client:
        print("2) Curadoria")
        cur_call = call_gemini(client, model, key, curation_prompt(items), "curation")
        curation = Curation.model_validate_json(cur_call["text"])
        valid_stories = []
        for s in curation.stories:
            s.item_ids = [i for i in s.item_ids if i in by_id]
            if s.item_ids:
                valid_stories.append(s)
        print(f"  {len(valid_stories)} pautas (de {len(curation.stories)} devolvidas)")

        print("3) Roteiro")
        scr_call = call_gemini(client, model, key, script_prompt(valid_stories, by_id), "script")
        script = Script.model_validate_json(scr_call["text"])

    words = sum(len(s.text.split()) for s in script.sections)
    bad_ids = {i for s in script.sections for i in s.source_item_ids if i not in by_id}
    sources = {i for s in script.sections for i in s.source_item_ids if i in by_id}
    (OUT / "script.txt").write_text(
        f"{script.title}\n\n"
        + "\n\n".join(
            f"## {s.heading}\n{s.text}\nFontes: {s.source_item_ids}" for s in script.sections
        )
        + "\n\nFONTES\n"
        + "\n".join(
            f"[{i}] {by_id[i]['outlet']} {by_id[i]['date']} {by_id[i]['url']}"
            for i in sorted(sources)
        )
    )

    total_in = cur_call["usage"].get("promptTokenCount", 0) + scr_call["usage"].get(
        "promptTokenCount", 0
    )
    total_out = sum(
        c["usage"].get("candidatesTokenCount", 0) + c["usage"].get("thoughtsTokenCount", 0)
        for c in (cur_call, scr_call)
    )
    print("\nResumo")
    print(f"  palavras do roteiro: {words} (alvo 1.500 a 2.250)")
    print(
        f"  seções: {len(script.sections)} | fontes distintas: {len(sources)} | "
        f"ids inválidos: {sorted(bad_ids)}"
    )
    print(f"  tokens por episódio: entrada {total_in} | saída (+raciocínio) {total_out}")
    print(f"  roteiro salvo em {OUT / 'script.txt'}")


if __name__ == "__main__":
    main()
