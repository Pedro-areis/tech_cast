# Tarefas

Backlog do TechCast em fases. Cada tarefa segue o ciclo do `.claude/CLAUDE.md` e só avança com validação. Requisitos (RFxx) em [PROJECT.md](PROJECT.md); custos e limites em [FEASIBILITY.md](FEASIBILITY.md).

Status: ⬜ não iniciada · 🔄 em andamento · ✅ concluída

## Estado atual

- **Atualizado em:** 2026-11-09
- **Última sessão:** primeira tarefa da Fase 1 feita (feeds RSS, D6). `uv` reinstalado no WSL com o instalador da Astral (`curl -LsSf https://astral.sh/uv/install.sh | sh`, fica em `~/.local/bin`; o `pipx` não existe mais). Criados `spikes/feeds_candidates.toml` (25 candidatos) e `spikes/rss_probe.py`; grupo de dependências `spikes` (`httpx`, `feedparser`) no `pyproject.toml`. Rodar: `uv run --group spikes python spikes/rss_probe.py`. Resultado: 24/25 feeds responderam, 537 itens em 7 dias (a hipótese era 60 a 150); vários feeds truncam antes de 7 dias, então o volume real é maior. Canaltech manda o texto inteiro no resumo (média de 3.436 caracteres), Hugging Face vem sem resumo, todos os itens têm data.
- **Em andamento:** nada. Falta registrar o resultado no `FEASIBILITY.md` (último item da Fase 1), junto com o ADR de D6.
- **Bloqueios:** nenhum. D1 a D7 ainda pendentes (D1/D2 resolvidas na Fase 1). Preferência do dono no canal (D3): gosta mais do Spotify, mas quer comparar com o Telegram antes de decidir.
- **Decisões de sessão:**
  - O dono autorizou o agente a criar branches (commits e push continuam com o dono). O `.env` real não existe; copie `.env.example` se quiser mudar algo.
  - Feeds (D6), corte aprovado: **manter** Tecnoblog, Canaltech, Tecmundo, Mobile Time, Convergência Digital, Ars Technica, The Verge, TechCrunch, MIT Technology Review, OpenAI Blog, Cloudflare Blog, The Hacker News, BleepingComputer, The Register. **Cortar** Wired, Tom's Hardware, Google AI Blog, Hugging Face. **Ainda sem decisão** (o dono aprovou só o corte): Olhar Digital, Hacker News front page, Krebs, AWS News Blog, InfoQ e AnandTech (deu timeout; testar de novo). Mistura de português e inglês aprovada.
  - Para a Fase 3: cortar o resumo num tamanho fixo (Canaltech traz o texto inteiro) e lembrar que o volume é maior que o previsto, então o limite de entrada do LLM é o gargalo.
  - O corte final ainda precisa ser conferido quanto a notícia versus review, oferta e opinião; isso sai do roteiro de teste com o Gemini.
- **Próximo passo:** commit da tarefa (sugestão: branch `fase-1-spikes`, com `spikes/`, `pyproject.toml`, `uv.lock` e `docs/TASKS.md`). Depois, o roteiro de teste com o Gemini e a medição de tokens (D1).

## Concluído

- [x] Especificação inicial e análise de viabilidade (`docs/FEASIBILITY.md`)
- [x] Documentos de base: `.claude/CLAUDE.md`, `docs/PROJECT.md`, `docs/TASKS.md`
- [x] D8. Banco de dados: SQLite com SQLAlchemy e Alembic ([ADR 0001](adr/0001-banco-de-dados.md))

## Decisões pendentes

- [ ] D1. Provedor de LLM padrão. Sugestão: Gemini Flash (free tier), Groq como alternativa, Claude só manual e depois de medido. Necessária na Fase 4.
- [ ] D2. Provedor de TTS. Sugestão: escolher pela audição dos testes da Fase 1; proposta inicial Google Chirp 3 HD com Piper de fallback. Necessária na Fase 5.
- [ ] D3. Canal do MVP: Spotify (feed RSS) ou Telegram. Sugestão: Telegram primeiro (sem depender do deploy), RSS para o Spotify em seguida. Necessária na Fase 7.
- [ ] D4. Quem pode pedir episódio manual (RF21): só o admin ou qualquer usuário. Sugestão: só o admin, para proteger cotas. Necessária na Fase 6.
- [ ] D5. Dia e hora do episódio semanal. Sugestão: segunda-feira, 6h, `America/Sao_Paulo`. Necessária na Fase 6.
- [ ] D6. Lista inicial de feeds RSS (pt-BR e inglês). Corte aprovado em 2026-11-09 (ver "Estado atual"); faltam decidir 6 feeds e escrever o ADR. Necessária na Fase 3.
- [ ] D7. Cadastrar cartão no Google Cloud (TTS) e na Oracle (hospedagem). Sugestão: sim, com alerta de orçamento em US$ 1; se não, Piper/edge-tts e outra hospedagem. Necessária nas Fases 5 e 9.

## ✅ Fase 0: Fundação do projeto

- [x] Projeto `uv` com Python 3.12, `pyproject.toml` e pacote `src/techcast/`
- [x] `ruff` (lint e formatação) e `pytest` configurados, com um teste de exemplo
- [x] `config.py` com `pydantic-settings` e `.env.example`; `.gitignore` com `.env`, banco, áudios e `.claude/settings.local.json`
- [x] Logging estruturado no stdout
- [x] App FastAPI mínima com `GET /health`
- [x] SQLAlchemy + Alembic com SQLite e uma migration inicial vazia
- [x] Atualizar a seção "Comandos" do `CLAUDE.md` com os comandos testados

**Aceite:** `uv sync`, `uv run pytest`, `uv run ruff check .` e `uv run alembic upgrade head` passam numa cópia limpa do repositório; `GET /health` retorna 200.

## 🔄 Fase 1: Testes de viabilidade (scripts descartáveis em `spikes/`)

- [x] Propor a lista inicial de feeds RSS e medir quantos itens por semana cada um gera (D6). Corte aprovado; resultado e ADR pendentes no último item da fase
- [ ] Gerar um roteiro de teste com o Gemini a partir de notícias reais e medir tokens de entrada e saída
- [ ] Confirmar no AI Studio os limites reais do free tier do modelo escolhido
- [ ] Gerar o mesmo trecho de 1 minuto em Google Chirp 3 HD, edge-tts e Piper para audição (D2)
- [ ] (Opcional) Rodar o mesmo roteiro com `claude -p` e medir o consumo com `/usage` antes e depois
- [ ] Levantar os requisitos atuais do Spotify for Creators para feed RSS (e-mail, capa, verificação)
- [ ] Registrar os resultados no `FEASIBILITY.md` e propor ADRs para D1, D2 e D6

**Aceite:** cada [H] crítico do `FEASIBILITY.md` virou [C] ou foi corrigido; você ouviu as amostras de voz e aprovou os ADRs do LLM e do TTS.

## ⬜ Fase 2: Modelo de dados e episódios

- [ ] Modelos `User`, `Episode`, `NewsItem`, `Story`, `EpisodeNewsItem`, `Delivery`, com migration
- [ ] `Episode.period_key` com `UNIQUE` para episódios agendados (RF22)
- [ ] Máquina de estados do episódio com transições válidas e registro do erro e da etapa (RF19)
- [ ] Interfaces `NewsSource`, `LLMProvider`, `TTSProvider`, `AudioStorage`, `Distributor`, com fakes para teste
- [ ] Testes das transições de estado e da restrição de unicidade

**Aceite:** os testes provam que uma transição inválida é rejeitada e que um segundo episódio agendado na mesma semana falha no banco.

## ⬜ Fase 3: Pesquisa de notícias

- [ ] `RssNewsSource` com `httpx` + `feedparser`, lista de feeds configurável (RF08)
- [ ] Normalização: URL canônica, data em UTC, veículo, resumo sem HTML (RF05)
- [ ] Filtro pelo período e descarte de itens sem data (RF04, RF06)
- [ ] Deduplicação por URL canônica e por similaridade de título (RF07)
- [ ] Tolerância a falhas: um feed fora do ar não derruba a coleta; fica registrado em log
- [ ] Testes com feeds gravados em `tests/fixtures/`

**Aceite:** com os fixtures, a coleta retorna só itens do período, sem URLs repetidas, e um feed inválido gera log de aviso sem exceção.

## ⬜ Fase 4: Curadoria e roteiro

- [ ] Implementar o `LLMProvider` escolhido em D1, com chave por variável de ambiente
- [ ] Prompt de curadoria: agrupar duplicatas em pautas, escolher por relevância, categorizar (RF09)
- [ ] Prompt de roteiro: estrutura, transições, citação dos veículos, marcação de rumores, sem copiar trechos das matérias (RF10 a RF12)
- [ ] Saída em JSON validada por Pydantic, com até 2 novas tentativas
- [ ] Validação: tamanho entre ~1.500 e ~2.250 palavras e pelo menos uma fonte por pauta (RF13)
- [ ] Persistir roteiro, pautas e o vínculo com as notícias (RF14)
- [ ] Testes com respostas do LLM gravadas, incluindo uma resposta inválida

**Aceite:** um roteiro gerado de verdade (teste `live`) tem as seções esperadas e cita fontes; nos testes, uma resposta inválida dispara nova tentativa e, depois do limite, marca o episódio como `failed` em `scripting`.

## ⬜ Fase 5: Geração de áudio

- [ ] Implementar o `TTSProvider` escolhido em D2 e o fallback, se aprovado
- [ ] Dividir o roteiro em partes dentro do limite do provedor, sem cortar frases (RF16)
- [ ] Juntar as partes com `ffmpeg` num MP3 mono de 64 a 96 kbps
- [ ] `LocalAudioStorage` com a pasta configurável (RF17)
- [ ] Testes da divisão do texto e da montagem com um TTS falso

**Aceite:** um roteiro de 2.000 palavras vira um MP3 único de 12 a 15 min e com menos de 10 MB, e o arquivo aparece no armazenamento ligado ao episódio.

## ⬜ Fase 6: Pipeline e agendamento

- [ ] Pipeline que executa as etapas em ordem e grava o status antes e depois de cada uma
- [ ] Reprocessamento a partir da etapa que falhou (RF20)
- [ ] Agendamento semanal com APScheduler no dia e hora de D5 (RF18)
- [ ] Execução manual pela linha de comando e por função reutilizável pela web (RF21)
- [ ] Proteção contra execução simultânea do mesmo episódio
- [ ] Testes de ponta a ponta com todos os provedores falsos, incluindo falha no meio

**Aceite:** com provedores falsos, um episódio vai de `pending` a `published`; uma falha forçada no TTS deixa `failed/synthesizing`, e o reprocessamento termina sem chamar de novo a pesquisa e o LLM.

## ⬜ Fase 7: Distribuição

- [ ] `TelegramDistributor` com `sendAudio`, título e lista de fontes na legenda (se D3 incluir Telegram)
- [ ] Vínculo do chat pelo link `t.me/<bot>?start=<token>` (RF03)
- [ ] `Delivery` por usuário, com status e reenvio do que falhou (RF24)
- [ ] Feed RSS de podcast em `/feed.xml` com capa, `itunes:owner` e enclosures (se D3 incluir Spotify) (RF26)
- [ ] Validação do feed num validador e cadastro no Spotify for Creators
- [ ] Testes da montagem das mensagens e do XML do feed

**Aceite:** o episódio chega no Telegram de pelo menos dois usuários de teste e/ou o feed passa no validador e o episódio aparece no Spotify.

## ⬜ Fase 8: Interface web

- [ ] Página pública de cadastro com Jinja2 + HTMX, com validação dos campos (RF01, RF02, RF27)
- [ ] Histórico de episódios com player de áudio (RF28)
- [ ] Login do admin com senha de variável de ambiente e cookie de sessão
- [ ] Admin: roteiro e fontes de cada episódio (RF29)
- [ ] Admin: status, erro, botão de reprocessar e de episódio manual (RF30)
- [ ] Testes das rotas, incluindo acesso negado ao admin sem login

**Aceite:** um usuário novo se cadastra e recebe o link do bot; sem login, `/admin` redireciona para a página de login; com login, o admin dispara um episódio manual e acompanha o status.

## ⬜ Fase 9: Deploy (extra)

- [ ] `Dockerfile` e `docker-compose.yml` com volumes para o banco e os áudios
- [ ] VM na hospedagem escolhida em D7, com reinício automático (`restart: unless-stopped`)
- [ ] HTTPS para a web e o feed (Caddy ou Cloudflare Tunnel)
- [ ] Backup diário do SQLite
- [ ] Deploy reproduzível documentado (script ou GitHub Actions)
- [ ] Alerta de orçamento nos provedores com cartão

**Aceite:** o servidor reinicia e volta sozinho; o episódio da semana seguinte é gerado e entregue sem nenhuma ação manual.
