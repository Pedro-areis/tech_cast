# TechCast: instruções para agentes de IA

O TechCast gera, toda semana, um podcast em português brasileiro com as principais notícias de tecnologia: coleta notícias, usa um LLM para curadoria e roteiro, converte em áudio com TTS e distribui o episódio. Ele **não** é uma plataforma de streaming, não personaliza episódios por usuário e não usa IA fora das etapas de curadoria e roteiro.

Responda ao usuário em português brasileiro.

Leia antes de trabalhar:
- [docs/PROJECT.md](../docs/PROJECT.md): problema, requisitos e definições do domínio.
- [docs/TASKS.md](../docs/TASKS.md): fases, tarefas e decisões pendentes. Atualize ao concluir cada tarefa. Comece a sessão pela seção "Estado atual".
  - Se a pasta `backlog-page/` existir (é local e ignorada pelo git), rode `node backlog-page/build-backlog.mjs` depois de alterar o TASKS.md. O comando regenera a página visual do backlog. A página é derivada: nunca edite o HTML à mão. No WSL deste projeto, o Node é o do Windows: `"/mnt/c/Program Files/nodejs/node.exe"`.
- [docs/FEASIBILITY.md](../docs/FEASIBILITY.md): análise de custo e limites de cada provedor externo. Consulte antes de mexer em qualquer integração.

## Troca de bastão
Ao terminar uma tarefa, ou antes de encerrar uma sessão com trabalho pela metade, reescreva a seção "Estado atual" do `docs/TASKS.md` (última sessão, em andamento, bloqueios, próximo passo). Preferências e decisões que o dono do projeto deu só na conversa e ainda não viraram ADR ou regra deste arquivo também entram lá. Motivo: outra pessoa ou outro agente precisa continuar sem o histórico da conversa.

## Regras de trabalho (definidas pelo dono do projeto)
1. **Explique o FastAPI e o ecossistema Python em profundidade.** O dono do projeto nunca trabalhou com FastAPI. Ao introduzir um conceito novo (injeção de dependências com `Depends`, modelos Pydantic, sessões do SQLAlchemy, migrations do Alembic, `async`/`await`, lifespan), explique o que é, por que foi usado e como se encaixa no resto. Ele quer entender o código, não só recebê-lo.
2. **Nomes no código em inglês** (variáveis, classes, rotas, tabelas). Textos de interface, roteiros e mensagens ao usuário em português brasileiro.
3. **Git é feito pelo dono do projeto.** O agente não commita, não faz push e não abre PRs, nem cria branches. Motivo: o dono quer praticar git. Quando um ponto de commit fizer sentido (fim de tarefa, mudança coesa e testada), avise e sugira: a branch (uma por tarefa ou fase, nunca direto na `main`), os arquivos a incluir e uma mensagem de commit. Comandos de leitura (`git status`, `git diff`, `git log`) estão liberados.
4. **Toda mudança vem com o porquê.** Decisões de arquitetura são consultadas antes de implementar.
5. **Na dúvida, pergunte e apresente trade-offs.** Decisões aprovadas viram ADRs em `docs/adr/`.
6. **Custo zero recorrente.** Nenhuma integração nova sem verificar o preço e os limites do plano gratuito e registrar em `docs/FEASIBILITY.md`. Não presuma que um serviço é gratuito.
7. **Limite do Claude Pro.** A conta Claude Pro do dono é de trabalho. Se alguma etapa automática for usar o Claude (via `claude -p`), ela não pode passar de ~10% do limite semanal do plano. Meça e informe antes de adotar.

## Forma de trabalho
Cada tarefa segue o ciclo: problema → arquivos afetados → solução e alternativas → critérios de aceite → implementação → testes → relatório → **aguardar validação** antes da próxima.

Siga a ordem das fases do `docs/TASKS.md`. Tarefas pequenas, testáveis e independentes. Não comece uma fase sem a anterior aceita.

## Estrutura e stack
Stack aprovada: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, SQLite, Jinja2 + HTMX, APScheduler, `uv`, `ruff`, `pytest`. Versões exatas ficam no `pyproject.toml` (Fase 0).

Estrutura planejada (monólito modular, um pacote por responsabilidade):

```
src/techcast/
  config.py          # Settings (pydantic-settings), lidas do ambiente
  db/                # engine, sessão, base dos modelos
  users/             # User Management
  news/              # News Research: NewsSource (interface) + implementações
  content/           # AI Content Generation: LLMProvider (interface), prompts
  audio/             # Audio Generation: TTSProvider (interface), montagem do MP3
  episodes/          # Episode Management: modelos, máquina de estados, pipeline
  distribution/      # Distribution: Distributor (interface) + canais
  scheduler/         # agendamento semanal
  web/               # rotas FastAPI e templates
migrations/          # Alembic
tests/
spikes/              # scripts descartáveis da Fase 1, fora do pacote
docs/
```

Regra de dependência: módulos de domínio não importam `web/`. Integrações externas só são acessadas através das interfaces (`NewsSource`, `LLMProvider`, `TTSProvider`, `AudioStorage`, `Distributor`).

## Comandos
Validados na Fase 0 (o `uv` foi instalado com `pipx install uv`; no WSL fica em `~/.local/bin`).

```bash
uv sync                                   # instalar dependências
uv run pytest                             # testes
uv run ruff check . && uv run ruff format --check .
uv run ruff format .                      # formatar
uv run alembic upgrade head               # aplicar migrations
uv run alembic revision --autogenerate -m "msg"   # nova migration
uv run fastapi dev src/techcast/web/app.py   # servidor de desenvolvimento; GET /health
```

## Regras técnicas obrigatórias
- **Provedores atrás de interfaces.** Trocar Gemini por outro LLM, ou o provedor de TTS, deve exigir só uma nova implementação e uma variável de ambiente.
- **Testes nunca chamam APIs reais.** Use fakes das interfaces e fixtures gravadas (RSS, respostas do LLM). Chamadas reais só em `spikes/` ou em testes marcados `@pytest.mark.live`, fora da suíte padrão.
- **Idempotência do episódio semanal.** Cada episódio agendado tem uma chave única de período (semana ISO, ex.: `2026-W45`) com restrição `UNIQUE` no banco. Uma segunda execução do agendador na mesma semana não cria outro episódio.
- **Status persistido por etapa.** O pipeline grava o status antes e depois de cada etapa (pesquisa, roteiro, áudio, distribuição). Uma falha registra a etapa e o erro, e o reprocessamento retoma da etapa que falhou, sem refazer as anteriores.
- **Rastreabilidade.** Toda notícia usada num roteiro fica ligada ao episódio com URL, veículo e data de publicação. Um roteiro sem fontes é inválido e não segue para o TTS.
- **Saída do LLM é validada.** O roteiro vem em JSON validado por modelo Pydantic. Saída inválida conta como falha da etapa, com novas tentativas limitadas.
- **Banco:** toda mudança de schema é uma migration nova do Alembic. Nunca edite uma migration já aplicada.
- **Segredos só em variáveis de ambiente.** `.env` fica fora do git; `.env.example` lista as variáveis sem valores. Nunca registre tokens ou chaves em log.
- **Dados de usuários:** e-mail e chat ID do Telegram são dados pessoais. Não aparecem em páginas públicas nem em logs.
- **Logs no stdout**, em formato estruturado, com o ID do episódio e a etapa.
- **Simplicidade:** nada de Celery, Redis, filas ou microsserviços sem necessidade demonstrada e aprovada.

## Deploy
Containerização e servidor remoto ficam para a última fase. Até lá, o código só precisa estar pronto para container: configuração por variáveis de ambiente, logs no stdout, caminho do banco e da pasta de áudio configuráveis, nenhum caminho absoluto da máquina local.

## Fora do escopo
Monetização, streaming próprio, permissões complexas, IA em outras etapas, personalização por usuário, app mobile, episódios diários, vídeo, treino de modelos. Não implemente sem autorização explícita.

## ADRs
Registre em `docs/adr/NNNN-titulo-curto.md` com: Contexto, Decisão, Alternativas consideradas (com trade-offs), Consequências e Status. Escreva só depois da aprovação do dono do projeto.
