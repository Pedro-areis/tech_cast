# 0004. Provedor de LLM: Gemini Flash com modelo de reserva

- **Status:** Aceito
- **Data:** 2026-11-17
- **Decisão pendente resolvida:** D1

## Contexto

O LLM faz a curadoria das notícias (chamada 1) e escreve o roteiro em JSON (chamada 2). O `CLAUDE.md` exige custo zero recorrente, saída validada por Pydantic e provedor atrás da interface `LLMProvider`.

Medição da Fase 1 (`spikes/gemini_script.py`, `gemini-3.5-flash`, 18 feeds, 419 itens): ~42,4 mil tokens de entrada e ~17,6 mil de saída (com raciocínio) por episódio. JSON válido de primeira nas duas rodadas, ~2.000 palavras, 77 fontes, tom e pt-BR bons, rumores marcados como rumor. Nenhum 429 apareceu.

Problema: **confiabilidade**. Em 2026-11-11, `gemini-3.8-flash` e `gemini-3.7-flash` não responderam em 100 s, e `3.6` e `3.5` devolveram 503 ("alta demanda"), com uma execução falhando nas 4 tentativas. Em 2026-11-12 não houve nenhum 503. O `gemini-2.5-flash` não está disponível para contas novas. As cotas exatas do free tier não são mostradas no painel do AI Studio (só o uso).

## Decisão

- **Padrão:** Gemini Flash, no free tier, com o `gemini-3.5-flash` como modelo inicial. O nome do modelo vem de variável de ambiente (`LLM_MODEL`).
- **Nova tentativa** com espera crescente em 503 e 429, e limite de tentativas. Esgotadas as tentativas, a etapa falha com erro registrado e o reprocessamento retoma dela.
- **Modelo de reserva configurável** (`LLM_FALLBACK_MODEL`): outro modelo Flash ou, se for preciso, outro provedor (Groq), cada um como implementação de `LLMProvider`.
- **Claude (`claude -p`):** só execução manual na máquina do dono, e só depois de medido. O dono dispensou a medição por ora.
- **SDK:** o spike usou `httpx` direto; a escolha entre `httpx` e o SDK `google-genai` fica para a Fase 4, com ADR próprio.
- **Confirmação na Fase 4:** repetir a medição de confiabilidade em outros dias e horários antes de fixar o modelo padrão e o de reserva.

## Alternativas consideradas

### Gemini Flash sem modelo de reserva
- **Prós:** mais simples.
- **Contras:** um dia de 503 como o de 2026-11-11 atrasa ou derruba o episódio semanal.

### Groq (Llama 3.3 70B ou similar) como padrão
- **Prós:** rápido; free tier.
- **Contras:** ~100 mil tokens/dia é apertado se a entrada crescer; pt-BR um pouco inferior [H]. Fica como reserva.

### Claude via `claude -p` (assinatura Pro)
- **Prós:** qualidade alta de texto.
- **Contras:** consome o limite do Pro de trabalho do dono, que a regra 7 limita a ~10% semanal e não pode ser calculado antecipadamente; login por OAuth no navegador é ruim num servidor.

### API paga da Anthropic
- **Contras:** viola o custo zero. Descartada.

## Consequências

- **Positivas:** custo zero; qualidade de roteiro já validada; a troca de modelo ou provedor exige só uma implementação e variáveis de ambiente.
- **Negativas:** limites do free tier podem mudar sem aviso; o Google pode usar os dados do free tier para melhorar produtos (aceitável: só notícias públicas); a curadoria favorece notícia geral, e o ajuste de prompt para pautas técnicas e de cultura tech fica para a Fase 4.
- **A confirmar:** modelo estável e cotas reais (hoje [H] no `FEASIBILITY.md`).
