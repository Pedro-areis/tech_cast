# TechCast: viabilidade técnica e financeira

Pesquisa feita em 2026-11-07. Os limites de free tier mudam com frequência e várias fontes encontradas eram de terceiros e discordavam entre si. **Toda cifra marcada [H] precisa ser confirmada no console do provedor na Fase 1** antes de virar ADR.

Legenda: **[C]** confirmado em fonte oficial · **[H]** fonte de terceiros ou inferência, a verificar.

## Consumo estimado por episódio

| Item | Estimativa | Base |
|---|---|---|
| Notícias coletadas | 60 a 150 itens/semana | ~15 feeds RSS × 5 a 10 itens relevantes |
| Entrada do LLM (curadoria) | ~15 a 30 mil tokens | título + resumo curto por item |
| Saída do LLM (roteiro) | ~4 a 6 mil tokens | 1.500 a 2.250 palavras em pt-BR |
| Chamadas ao LLM | 2 a 4 por episódio | curadoria, roteiro, até 2 novas tentativas |
| Caracteres para o TTS | ~9 a 14 mil por episódio, ~60 mil/mês | 150 palavras/min × 15 min × ~6 caracteres |
| Tamanho do MP3 | ~7 MB (15 min, 64 kbps mono) | |
| Armazenamento/ano | ~400 MB | 52 episódios |

O volume é pequeno. Qualquer free tier razoável comporta, desde que **exista** e seja **compatível com automação**.

## 1. Pesquisa de notícias

| Opção | Custo | Limites | Prós | Contras |
|---|---|---|---|---|
| **Feeds RSS de veículos e blogs oficiais** (recomendada) | Grátis, sem chave | Nenhum, além de boas práticas (cache, `User-Agent`) | Data de publicação e URL vêm no item; fonte rastreável; lista sob nosso controle | Precisamos manter a lista de feeds; só resumo, não o texto completo |
| Hacker News API (complemento) | Grátis | Sem limite documentado relevante [H] | Sinal de relevância (pontos/comentários) | Viés para o público dev em inglês |
| GNews / NewsAPI | Free tier com limites diários e restrição de uso [H] | ~100 requisições/dia [H]; NewsAPI grátis historicamente só para desenvolvimento [H] | Busca por palavra-chave | Cadastro, termos restritivos, cobertura de tech irregular |
| Busca do LLM (Gemini com Google Search grounding) | Free tier com cota diária/mensal [H] | Números conflitantes: 500 a 1.500/dia no Gemini 2.5; ~5.000/mês no Gemini 3 [H] | Acha o que não está nos feeds | Menos controle da fonte e da data; cota pode mudar |

**Recomendação:** RSS como fonte principal, com a interface `NewsSource` permitindo somar Hacker News ou busca do LLM depois. Atende à rastreabilidade (RF05) sem depender de cota de terceiros.

## 2. LLM para curadoria e roteiro

| Opção | Custo | Limites | Prós | Contras |
|---|---|---|---|---|
| **Gemini API, modelo Flash, free tier** (recomendada) | Grátis | Requisições/dia na casa das centenas ou mais [H]; fontes discordam | Contexto grande, bom em pt-BR, saída JSON estruturada | Limites mudam sem aviso; no free tier o Google pode usar os dados para melhorar produtos [H] (aceitável: só notícias públicas) |
| Groq, free tier (Llama 3.3 70B ou similar) | Grátis | ~100 mil tokens/dia para o 70B [H] | Rápido; bom como alternativa | 100 mil tokens/dia é apertado se a entrada crescer; pt-BR um pouco inferior [H] |
| Claude via `claude -p` com a assinatura Pro | Sem custo extra | **Consome o limite da assinatura Pro** [C] | Qualidade alta de texto | Ver seção abaixo |
| API da Anthropic | **Paga**, por token [C] | | Melhor integração | Viola a restrição de custo zero |

### Medição real do Gemini (Fase 1, 2026-11-11 e 12)
Teste em `spikes/gemini_script.py`: 2 chamadas (curadoria e roteiro), API REST com `httpx`, modelo `gemini-3.5-flash`, 18 feeds (419 itens em 7 dias, resumo cortado em 500 caracteres).

| Etapa | Entrada | Saída | Raciocínio | Tempo |
|---|---|---|---|---|
| Curadoria | 36.145 | 570 | 3.634 | 22 s |
| Roteiro | 6.248 | 3.363 | 10.012 | 82 s |
| **Episódio** | **~42,4 mil** | **~17,6 mil** (com raciocínio) | | |

- **[C]** O JSON saiu válido de primeira nas duas rodadas, o roteiro ficou com ~2.000 palavras (alvo 1.500 a 2.250), com fontes por seção e nenhum id inventado. O consumo de entrada ficou dentro da estimativa de 25 a 40 mil tokens por semana, um pouco acima (~42 mil). Os tokens de raciocínio contam como saída.
- **[C]** O `gemini-2.5-flash` não está disponível para contas novas (404). Modelos listados na conta em 2026-11-11: família 3.x Flash e Flash-Lite, e `gemini-flash-latest`.
- **[C]** Confiabilidade: em 2026-11-11, `gemini-3.8-flash` e `gemini-3.7-flash` não responderam nem a um prompt de uma frase em 100 s; `gemini-3.6-flash` e `gemini-3.5-flash` devolveram 503 ("alta demanda") em várias chamadas, inclusive de 3 mil tokens, então a causa não é o tamanho da entrada. Em 2026-11-12, o `gemini-3.5-flash` não deu nenhum 503. Nenhum 429 apareceu.
- **[H]** O pipeline precisa de nova tentativa com espera e, de preferência, de um segundo modelo de reserva. Só o `gemini-3.5-flash` foi avaliado de ponta a ponta; os modelos lite não foram testados (dispensado pelo dono). 
- **[H]** Limites do free tier (RPM, TPM, RPD): o painel de uso do AI Studio (consultado em 2026-11-12) mostrou apenas o **uso**, não as cotas. Ele registrou, para o `gemini-3.6-flash`, menos de 50 mil tokens de entrada, menos de 20 mil de saída e 2 requisições (modelo mais usado hoje e ontem). Isso é compatível com uma execução completa do spike (2 chamadas, ~42 mil de entrada, ~17,6 mil de saída), mas o spike usou o `gemini-3.5-flash`; a divergência de nome no painel não foi esclarecida. **Evidência prática:** uma requisição de ~36 mil tokens de entrada passou no free tier sem nenhum 429, então o TPM é de pelo menos esse valor. As cotas em si continuam não confirmadas. Para 1 episódio por semana (2 chamadas, ~60 mil tokens), a folga é grande mesmo com as cotas mais baixas citadas por terceiros; a Fase 4 deve tratar 429 como falha com nova tentativa.

### Sobre usar o Claude Pro (sua pergunta)
- **[C]** Pelo artigo atual do Help Center (atualização de 2026-10-07), o `claude -p` e o Agent SDK autenticados com o plano **continuam consumindo os limites da assinatura**. Os créditos mensais de API anunciados valem para Max, Ultra e Team, **não para o Pro**.
- **[C]** Os limites do Pro (janela de 5 horas e limite semanal) são compartilhados entre o claude.ai e o Claude Code. A Anthropic não publica esses limites em tokens, então não dá para calcular os 10% antecipadamente.
- **[H]** Só curadoria + roteiro a partir das notícias já coletadas (~25 a 40 mil tokens por semana) tende a ser uma fração pequena do limite semanal. Se o Claude fizer a **pesquisa na web** sozinho, o consumo pode multiplicar por 5 a 10, porque cada página lida entra no contexto.
- Outros problemas para produção: o login do plano é por OAuth no navegador (ruim num servidor), e a especificação pede para não tratar o Claude Code como serviço de produção.

**Recomendação:** Gemini Flash como provedor padrão, Groq como alternativa. O Claude fica como provedor opcional só para execução manual na sua máquina, e apenas depois de medido com `/usage` antes e depois de uma execução real (tarefa da Fase 1).

## 3. Text-to-Speech (pt-BR)

| Opção | Custo | Limites | Prós | Contras |
|---|---|---|---|---|
| **Google Cloud TTS, vozes Chirp 3 HD** (recomendada, sujeita a teste de audição) | Grátis até o limite | 1 milhão de caracteres/mês em Chirp 3 HD; 4 milhões em Standard [H] | Muito natural; uso estimado ~6% do limite | **Exige conta de faturamento com cartão**: acima do limite, cobra. Mitigar com alerta de orçamento e limite de cota |
| edge-tts (vozes neurais do Microsoft Edge) | Grátis | Sem limite publicado | Vozes pt-BR boas (Francisca, Antonio, Thalita) | API não oficial: pode parar a qualquer momento; termos de uso incertos [H] |
| Piper (local, open-source) | Grátis | Só CPU do servidor | Sem dependência externa nem cartão; licença aberta das vozes | Qualidade inferior em pt-BR [H]; ocupa CPU do servidor |
| Gemini TTS | Fora do free tier [H] | | | Pago |

**Recomendação:** decidir pela audição. A Fase 1 gera o mesmo trecho de roteiro nos três (Google Chirp 3 HD, edge-tts, Piper) e você escolhe. Proposta inicial: Google como padrão, Piper como fallback que nunca falha por cota. Se você não quiser cadastrar cartão no Google Cloud, Piper ou edge-tts.

### Audição de vozes (Fase 1, 2026-11-12)
Teste em `spikes/tts_voices.py`: o mesmo trecho de 182 palavras (~1 min) do roteiro de teste, em 3 vozes do edge-tts e 3 do Piper (`faber`, `cadu`, `jeff`, todas `medium`). O Chirp 3 HD **não foi testado**: depende do cartão no Google Cloud (D7) e o dono o deixou para depois.

| Voz | Tempo para gerar 1 min | Arquivo |
|---|---|---|
| edge-tts Francisca | 12,5 s | MP3, 382 KB |
| edge-tts Antonio | 31,7 s | MP3, 404 KB |
| **edge-tts Thalita (Multilingual)** | 38,3 s | MP3, 380 KB |
| Piper faber / cadu / jeff | ~4 s cada | WAV, ~2,7 MB (precisa de `ffmpeg` para virar MP3) |

- **[C]** O dono ouviu as amostras e **preferiu a voz Thalita (`pt-BR-ThalitaMultilingualNeural`, edge-tts)**.
- **[C]** Tempo do edge-tts varia muito (12 a 38 s por minuto de áudio, depende da rede e do serviço). Um episódio de ~14 min pode levar de 3 a 9 min. Aceitável para uma geração semanal, mas precisa de nova tentativa e de limite de tempo.
- **[H]** Risco do edge-tts: cliente não oficial do serviço do Microsoft Edge; pode ser bloqueado ou mudar sem aviso, e os termos de uso são incertos. Mitigação: o `TTSProvider` isola a escolha, e o **Piper fica como fallback** sem cota nem rede. O limite de tamanho de texto por chamada e a estabilidade em 14 min de áudio ainda não foram medidos (Fase 5).
- **[H]** Piper não foi escolhido pelo dono; só serve de reserva. Qual voz Piper usar como reserva fica para a Fase 5, se o fallback for aprovado.
- **Proposta para o ADR de D2:** edge-tts com a voz Thalita como padrão, Piper como fallback. Chirp 3 HD segue como opção se o dono decidir cadastrar o cartão (D7). Falta o ADR, que só é escrito depois da aprovação do dono.


Em qualquer opção, o texto é dividido em partes (o Google aceita ~5.000 bytes por requisição [H]) e o áudio é juntado com `ffmpeg`.

## 4. Distribuição: Spotify e Telegram

### Spotify: a burocracia
- **[H]** O Spotify **não tem API pública de upload** de episódios. Há duas formas de publicar:
  1. **Upload manual** no Spotify for Creators. Não automatizável, então não atende ao RF23.
  2. **Feed RSS próprio:** o TechCast publica um `feed.xml` de podcast, você envia a URL **uma vez** no Spotify for Creators, e depois o Spotify lê o feed periodicamente e pega os episódios novos sozinho. **Esse é o caminho viável.**
- Exigências para o feed [C, ajuda do Spotify e Podcast Delivery Specification v1.10, maio/2025, verificadas em 2026-11-17]:
  - **Áudio:** MP3 (recomendado 128 kbps ou mais), URLs sempre acessíveis, duração máxima de 12 h. Nosso episódio (~15 min) está muito abaixo.
  - **Imagem:** quadrada (1:1), de preferência na maior resolução; JPG, PNG ou GIF de até 3000 × 3000 px (ajuda do Spotify). Define-se por `<itunes:image href>` ou `<image><url>`; pelo menos um dos dois é obrigatório.
  - **Feed:** XML 1.0 em UTF-8, RSS 2.0, sensível a maiúsculas; `&` precisa estar escapado (`&amp;`). Validar no Cast Feed Validator ou Podba.se. Um feed = um podcast.
  - **Canal (obrigatórios):** `title`, `link`, `description`, `itunes:author`, imagem (uma das duas formas). **Recomendados:** `language` (`pt-BR`), `itunes:category` (necessária para as recomendações do Spotify), `itunes:explicit`, `itunes:type` (`episodic`).
  - **Item (obrigatórios):** `guid` estável, `enclosure` (`url`, `type="audio/mpeg"`, `length` em bytes) ou `media:content`, `pubDate` em RFC 2822, `title` e `description`. **Opcionais úteis:** `itunes:duration`, `itunes:episode`, `itunes:season`.
  - **Verificação de dono:** o Spotify usa o e-mail do feed (`<itunes:email>`, dentro de `<itunes:owner>`) para confirmar que o podcast é seu. **O e-mail fica público** para quem abrir o feed. Precisa ser uma caixa que o dono acessa. Mudou o e-mail no feed: o Spotify leva algumas horas para notar (se passar de 4 h, procurar o suporte).
  - **Lembrar:** o Spotify só baixa de novo um áudio ou imagem se o **nome/caminho do arquivo mudar**. Então cada episódio precisa de um nome de arquivo único (ex.: `2026-W47.mp3`), nunca sobrescrever.
  - **Frequência de leitura:** depois de cadastrado, o Spotify consulta o feed várias vezes por hora (respeita `ETag` e `Last-Modified`). Reserve pelo menos 1 h até a mudança chegar aos clientes. O podcast só fica público com pelo menos 1 episódio.
  - **Cadastro (uma vez):** em `creators.spotify.com/switch`, informar a URL do feed. Hosts fora da lista oficial (o nosso) "podem funcionar, sem garantia de suporte". Depois, o Spotify oferece um link de redirecionamento para o host antigo; no nosso caso, não há host antigo e esse passo não se aplica [H, confirmar no cadastro real].
  - A especificação v1.10 é marcada como confidencial pelo Spotify; aqui só resumimos os requisitos, sem copiar o texto.
- **Consequências práticas:**
  - O servidor precisa estar **na internet, com HTTPS, 24 horas por dia**, servindo o feed e os MP3. Isso puxa a Fase de deploy para o caminho crítico.
  - Depois de cadastrado, o podcast fica **público**: qualquer pessoa pode encontrá-lo no Spotify. Não há podcast privado por convite no fluxo de RSS [H].
  - O Spotify não sabe quem são os "usuários cadastrados". Cada um segue o programa no app; não há entrega por usuário nem status de entrega (RF24 não se aplica).
  - Atraso entre publicar no feed e aparecer no app: pelo menos 1 h, na prática algumas horas [C, especificação do Spotify].
  - **E-mail público:** como o `itunes:email` aparece para qualquer um, use um e-mail dedicado ao podcast (não o pessoal nem o de trabalho). Isso respeita a regra de não expor dados pessoais em páginas públicas.
  - O roteiro resume notícias com as próprias palavras e cita as fontes. Ler trechos longos de matérias num podcast público seria um risco de direitos autorais. O prompt deve proibir isso.
  - Bônus: o mesmo feed funciona no Apple Podcasts, Pocket Casts, AntennaPod etc.

### Telegram
- **[C]** Bot API gratuita. `sendAudio` aceita arquivos de até 50 MB; o episódio tem ~7 MB.
- O usuário precisa iniciar a conversa com o bot (`/start`). Com um link de convite com token (`t.me/<bot>?start=<token>`), o bot liga o chat ao cadastro sozinho.
- Funciona sem servidor público: o bot faz requisições de saída (polling), então dá para testar tudo localmente antes do deploy.
- Entrega individual com status por usuário (RF24) e conteúdo privado para o grupo de amigos.

| Critério | Spotify (via RSS) | Telegram |
|---|---|---|
| API | Sem API de upload; só RSS | Bot API completa |
| Custo | Grátis (exige servidor público com HTTPS) | Grátis |
| Esforço | Médio: feed válido, capa, verificação, deploy | Baixo |
| Automação | Total, depois do cadastro manual único | Total |
| Consumo pelo usuário | Excelente (app de podcast, velocidade, retomar de onde parou) | Bom (player no chat) |
| Privacidade | Público | Privado |
| Testável localmente | Não (o Spotify precisa alcançar o feed) | Sim |

**Recomendação:** os dois estão registrados como candidatos (decisão D3 no `TASKS.md`). Sugestão: Telegram primeiro, porque fecha o MVP sem depender do deploy, e o feed RSS para o Spotify logo em seguida, aproveitando o mesmo MP3. Como a distribuição fica atrás da interface `Distributor`, a ordem não muda o resto do código.

## 5. Hospedagem (fase final)

| Opção | Custo | Limites | Prós | Contras |
|---|---|---|---|---|
| **Oracle Cloud Always Free, VM Ampere A1** (recomendada) | Grátis | Reduzido em 2026 para 2 OCPUs e 12 GB de RAM no total [H]; 200 GB de disco [H] | Sobra capacidade para FastAPI + SQLite + Piper; disco persistente | Exige cartão no cadastro; erros frequentes de "Out of host capacity" ao criar a VM [H]; Oracle pode mudar os termos de novo |
| GitHub Actions (cron) + GitHub Pages | Grátis para repositório público | Minutos limitados em repositório privado [H] | Zero servidor para manter | Não tem banco nem área admin dinâmica; o cadastro web não funciona |
| Render, Fly.io e similares | Free tiers que dormem ou foram removidos [H] | | | O agendamento não roda com a instância dormindo |

HTTPS para o feed do Spotify: Caddy na VM com um subdomínio gratuito (ex.: DuckDNS) ou Cloudflare Tunnel [H, a escolher na fase de deploy].

## Resumo de custo

| Etapa | Escolha proposta | Custo recorrente | Uso estimado do limite |
|---|---|---|---|
| Pesquisa | RSS | 0 | n/a |
| LLM | Gemini Flash (free) | 0 | < 5% [H] |
| TTS | Google Chirp 3 HD (free) ou Piper | 0 | ~6% [H] / n/a |
| Distribuição | Telegram + RSS | 0 | < 1% |
| Hospedagem | Oracle Always Free | 0 | < 20% |

Riscos principais: (1) free tiers mudarem sem aviso, mitigado pelas interfaces e por um fallback sem cota (Piper, Groq); (2) cobrança acidental no Google Cloud, mitigada com alerta de orçamento e limite de cota; (3) não conseguir capacidade na Oracle, decidido só na fase de deploy.

## Fontes consultadas
- Claude Help Center: [uso do Claude Code com Pro/Max](https://support.claude.com/en/articles/11145838) e [Agent SDK e `claude -p` com o plano](https://support.claude.com/en/articles/15036540)
- Gemini, terceiros: [cometapi](https://www.cometapi.com/gemini-api-free-tier-2026/), [fórum de grounding](https://discuss.ai.google.dev/t/search-grounding-rpd-limit-for-gemini-3-x/187033)
- [Preços do Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech/pricing/?hl=pt-br)
- [Spotify for Creators: importar episódios de outro host](https://support.spotify.com/br-pt/creators/article/importing-your-episodes-from-another-host/) e [feed RSS](https://support.spotify.com/us/creators/article/your-rss-feed/)
- Telegram `sendAudio`, 50 MB: [teloxide-core](https://docs.rs/crate/teloxide-core/latest/source/src/payloads/send_audio.rs)
- Oracle Always Free 2026: [InfoQ](https://infoq.com/news/2026/07/oracle-cloud-free-tier-limits/), [terminalbytes](https://terminalbytes.com/oracle-cloud-free-tier-changes-2026)
- Groq, terceiros: [benchlm.ai](https://benchlm.ai/free-tier/groq)
- [Voz Piper pt_BR faber-medium](https://huggingface.co/Trelis/piper-pt-br-faber-medium)
