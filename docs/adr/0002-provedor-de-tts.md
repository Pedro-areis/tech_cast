# 0002. Provedor de TTS: edge-tts (voz Thalita) com Piper de fallback

- **Status:** Proposto (aguardando a leitura do dono)
- **Data:** 2026-11-17
- **Decisão pendente resolvida:** D2

## Contexto

O TechCast converte o roteiro (~2.000 palavras, ~14 min) em MP3 em português brasileiro. O `CLAUDE.md` exige custo zero recorrente e provedores atrás da interface `TTSProvider`.

A Fase 1 gerou o mesmo trecho de 1 minuto em 3 vozes do edge-tts e 3 do Piper (`spikes/tts_voices.py`). O dono ouviu as amostras e preferiu a **Thalita** (`pt-BR-ThalitaMultilingualNeural`, edge-tts). O Google Chirp 3 HD não foi testado, porque exige cartão no Google Cloud (D7), que o dono deixou para depois.

## Decisão

- **Padrão:** edge-tts com a voz `pt-BR-ThalitaMultilingualNeural`.
- **Fallback:** Piper (local, sem rede nem cota). A voz Piper de reserva é escolhida na Fase 5.
- Ambos entram como implementações de `TTSProvider`. A escolha vem de uma variável de ambiente (por exemplo `TTS_PROVIDER=edge|piper`), e trocar de provedor não mexe no resto do código.
- O texto é dividido em partes e o áudio é juntado com `ffmpeg`. Cada chamada tem limite de tempo e nova tentativa.
- Se o edge-tts falhar depois das tentativas, o pipeline usa o Piper e registra o fato no log e no episódio.

## Alternativas consideradas

### Google Cloud TTS (Chirp 3 HD)
- **Prós:** muito natural; API oficial; uso estimado ~6% do 1 milhão de caracteres/mês gratuito.
- **Contras:** exige conta de faturamento com cartão (acima do limite, cobra). Não foi ouvido na Fase 1.
- **Situação:** continua possível como nova implementação se o dono cadastrar o cartão (D7).

### Somente Piper
- **Prós:** sem dependência externa, sem cota, licença aberta.
- **Contras:** qualidade inferior em pt-BR; o dono preferiu a Thalita. Ocupa CPU do servidor.

### Gemini TTS
- **Contras:** fora do free tier. Descartado.

## Consequências

- **Positivas:** custo zero, sem cartão, voz aprovada pelo dono, fallback que nunca falha por cota.
- **Negativas:** o edge-tts é um cliente **não oficial** do serviço do Microsoft Edge. Pode ser bloqueado ou mudar sem aviso, e os termos de uso são incertos. O tempo varia muito (12 a 38 s por minuto de áudio), então um episódio pode levar de 3 a 9 min.
- **A medir na Fase 5:** limite de texto por chamada e estabilidade em ~14 min de áudio.
- **Revisão:** se o edge-tts for bloqueado, o Piper assume ou o dono decide sobre o cartão (D7) para usar o Chirp 3 HD.
