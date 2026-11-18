"""Spike D2: gera o mesmo trecho (~1 min) em edge-tts e Piper para audição.

Rodar: uv run --group spikes python -u spikes/tts_voices.py
Saída em spikes/out/tts/ (ignorada pelo git). O Chirp 3 HD fica para depois (exige cartão, D7).
"""

import asyncio
import re
import subprocess
import sys
import time
from pathlib import Path

import edge_tts
import httpx

ROOT = Path(__file__).parent
OUT = ROOT / "out" / "tts"
MODELS = ROOT / "out" / "piper_models"
SCRIPT = ROOT / "out" / "script.txt"
TARGET_WORDS = 170  # ~1 minuto de fala

EDGE_VOICES = ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", "pt-BR-ThalitaMultilingualNeural"]
PIPER_VOICES = {  # nome -> caminho no repositório rhasspy/piper-voices
    "faber-medium": "pt/pt_BR/faber/medium/pt_BR-faber-medium",
    "cadu-medium": "pt/pt_BR/cadu/medium/pt_BR-cadu-medium",
    "jeff-medium": "pt/pt_BR/jeff/medium/pt_BR-jeff-medium",
}
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"


def build_excerpt() -> str:
    """Pega parágrafos do roteiro (sem títulos e sem 'Fontes:') até ~170 palavras."""
    paragraphs = [
        p.strip()
        for p in SCRIPT.read_text(encoding="utf-8").splitlines()
        if p.strip() and not p.startswith(("#", "Fontes:", "Podcast Tech"))
    ]
    excerpt, count = [], 0
    for sentence in re.split(r"(?<=[.!?])\s+", " ".join(paragraphs)):
        n = len(sentence.split())
        if count + n > TARGET_WORDS + 20 and count >= TARGET_WORDS - 30:
            break
        excerpt.append(sentence)
        count += n
    return " ".join(excerpt)


async def run_edge(text: str) -> None:
    for voice in EDGE_VOICES:
        path = OUT / f"edge_{voice}.mp3"
        start = time.perf_counter()
        try:
            await edge_tts.Communicate(text, voice).save(str(path))
            elapsed, kb = time.perf_counter() - start, path.stat().st_size / 1024
            print(f"edge {voice}: {elapsed:.1f}s, {kb:.0f} KB")
        except Exception as exc:  # spike: só queremos ver o erro
            print(f"edge {voice}: FALHOU ({type(exc).__name__}: {exc})")


def download(url: str, dest: Path) -> None:
    if dest.exists():
        return
    with httpx.stream("GET", url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)


def run_piper(text: str) -> None:
    MODELS.mkdir(parents=True, exist_ok=True)
    for name, remote in PIPER_VOICES.items():
        model = MODELS / f"{name}.onnx"
        try:
            download(f"{HF}{remote}.onnx", model)
            download(f"{HF}{remote}.onnx.json", MODELS / f"{name}.onnx.json")
        except Exception as exc:
            print(f"piper {name}: download FALHOU ({exc})")
            continue
        path = OUT / f"piper_{name}.wav"
        start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, "-m", "piper", "-m", str(model), "-f", str(path)],
            input=text.encode(),
            capture_output=True,
        )
        if proc.returncode != 0:
            print(f"piper {name}: FALHOU {proc.stderr.decode()[-300:]}")
            continue
        print(
            f"piper {name}: {time.perf_counter() - start:.1f}s, {path.stat().st_size / 1024:.0f} KB"
        )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    text = build_excerpt()
    (OUT / "excerpt.txt").write_text(text, encoding="utf-8")
    print(f"trecho: {len(text.split())} palavras, {len(text)} caracteres")
    asyncio.run(run_edge(text))
    run_piper(text)


if __name__ == "__main__":
    main()
