# TechCast: projeto e requisitos

## O problema
- **Acompanhar o setor exige tempo.** As notícias de IA, cloud, segurança, hardware e mercado ficam espalhadas por dezenas de portais, blogs e vídeos. Ler tudo toma horas por semana.
- **O mesmo fato aparece várias vezes.** Um lançamento grande sai em dez veículos com títulos diferentes, e separar o que é novo do que é repetição dá trabalho.
- **Notícia escrita não cabe na rotina.** Deslocamento, almoço e intervalos são momentos em que dá para ouvir, mas não para ler.
- **Especulação se mistura com fato.** Rumores e anúncios confirmados chegam com o mesmo peso, sem indicação da fonte.

## O que o TechCast resolve
- Coleta automaticamente, uma vez por semana, as notícias publicadas no período em fontes confiáveis.
- Usa um LLM para remover duplicatas, escolher o que é relevante e agrupar por categoria.
- Gera um roteiro de 10 a 15 minutos, com introdução, contexto, transições, encerramento e menção às fontes, distinguindo rumor de fato confirmado.
- Converte o roteiro em MP3 e entrega o episódio por um canal (Telegram e/ou feed RSS para o Spotify).
- Guarda roteiro, fontes e status de cada episódio para consulta.

O que ele deliberadamente **não** faz: não personaliza o episódio por usuário, não é um player de streaming, não usa IA para nada além de curadoria e roteiro, e não preenche o episódio com notícias fracas só para atingir a duração.

## Para quem
Uso pessoal do dono do projeto e de alguns amigos (menos de ~20 usuários), no Brasil, em português brasileiro. Sem finalidade comercial.

Objetivo do autor: aprender FastAPI e o ecossistema Python construindo um sistema completo, com arquitetura que permita evoluir.

## Requisitos funcionais
Legenda de status: ✅ implementado · ⚠️ parcial · ❌ ausente

### Usuários
| Requisito | Status |
|---|---|
| RF01. Cadastro com nome, e-mail, destino do canal (ex.: chat ID do Telegram) e data de cadastro | ❌ |
| RF02. Preferências do usuário: canal de entrega e opção de pausar o recebimento | ❌ |
| RF03. Vínculo com o Telegram por link de convite (`/start <token>`), sem o usuário digitar o chat ID | ❌ |

### Pesquisa de notícias
| Requisito | Status |
|---|---|
| RF04. Coletar notícias de um intervalo configurável (padrão: últimos 7 dias) | ❌ |
| RF05. Registrar de cada notícia: título, URL, veículo, data de publicação, resumo, categoria | ❌ |
| RF06. Descartar notícias fora do período ou sem data de publicação | ❌ |
| RF07. Remover duplicatas: mesma URL canônica, títulos muito parecidos e, na curadoria, o mesmo fato em veículos diferentes | ❌ |
| RF08. Lista de fontes configurável, sem alterar código | ❌ |

### Curadoria e roteiro
| Requisito | Status |
|---|---|
| RF09. Selecionar e agrupar as notícias por categoria e relevância | ❌ |
| RF10. Gerar roteiro com introdução, blocos por assunto, transições e encerramento | ❌ |
| RF11. Citar o veículo de cada notícia no texto falado | ❌ |
| RF12. Marcar rumores e especulações como tal | ❌ |
| RF13. Roteiro entre ~1.500 e ~2.250 palavras (10 a 15 min); menos notícias se a semana for fraca | ❌ |
| RF14. Armazenar o roteiro completo e as notícias usadas, recuperáveis depois | ❌ |

### Áudio
| Requisito | Status |
|---|---|
| RF15. Converter o roteiro em MP3 em pt-BR, com voz natural | ❌ |
| RF16. Dividir o texto em partes dentro do limite do provedor e juntar o áudio final | ❌ |
| RF17. Armazenar o MP3 num local acessível para a distribuição | ❌ |

### Episódios e agendamento
| Requisito | Status |
|---|---|
| RF18. Gerar o episódio automaticamente no dia e hora configurados | ❌ |
| RF19. Status por etapa: `pending → researching → scripting → synthesizing → distributing → published`, ou `failed` com a etapa e o erro | ❌ |
| RF20. Reprocessar um episódio com falha a partir da etapa que falhou | ❌ |
| RF21. Solicitar manualmente um novo episódio | ❌ |
| RF22. Nunca gerar dois episódios agendados para a mesma semana | ❌ |

### Distribuição
| Requisito | Status |
|---|---|
| RF23. Enviar o episódio aos usuários ativos por pelo menos um canal | ❌ |
| RF24. Registrar o status de entrega por usuário e reenviar o que falhou | ❌ |
| RF25. Adicionar um canal novo sem alterar o pipeline (interface `Distributor`) | ❌ |
| RF26. (Se o Spotify for escolhido) publicar um feed RSS de podcast válido | ❌ |

### Interface web
| Requisito | Status |
|---|---|
| RF27. Página pública de cadastro | ❌ |
| RF28. Histórico de episódios com player de áudio | ❌ |
| RF29. Admin: ver roteiros e fontes de cada episódio | ❌ |
| RF30. Admin: ver o status do processamento e disparar reprocessamento ou episódio manual | ❌ |

## Requisitos não funcionais
- **Custo:** zero de custo recorrente. Cada provedor tem o limite gratuito documentado em `docs/FEASIBILITY.md`, e o uso estimado fica abaixo de 20% desse limite.
- **Claude Pro:** se usado, no máximo ~10% do limite semanal da conta do dono.
- **Confiabilidade:** um episódio por semana, sem duplicata; falha numa etapa não perde as anteriores.
- **Desacoplamento:** cada provedor externo atrás de uma interface; troca por configuração.
- **Rastreabilidade:** cada episódio lista as notícias (URL, veículo, data) que o fundamentaram.
- **Segurança:** segredos só no ambiente; área admin protegida por senha; dados pessoais fora de páginas públicas e logs.
- **Observabilidade:** logs estruturados no stdout com ID do episódio e etapa; status e erro visíveis no admin.
- **Qualidade do áudio:** MP3 mono, 64 a 96 kbps, 44,1 ou 24 kHz. Um episódio de 15 min fica abaixo de 10 MB (cabe no limite de 50 MB do Telegram).
- **Qualidade de código:** `ruff` sem erros, testes do pipeline e das regras de domínio sem chamar APIs reais.
- **Portabilidade:** roda localmente e em container com as mesmas variáveis de ambiente.

## Definições do domínio
| Termo | Definição | Situação |
|---|---|---|
| Período do episódio | Intervalo `[início, fim)` de datas de publicação consideradas. Para o agendado: os 7 dias anteriores ao horário da execução, em `America/Sao_Paulo` | Proposta |
| Chave do episódio | Semana ISO do fim do período (ex.: `2026-W45`) para episódios agendados. Episódios manuais não têm chave e não bloqueiam o agendado | Proposta |
| Notícia (news item) | Um item coletado de uma fonte, com URL canônica única | Proposta |
| URL canônica | URL sem parâmetros de rastreamento (`utm_*`, `ref`, fragmento), em minúsculas no host | Proposta |
| Duplicata | Mesma URL canônica, ou mesmo fato reportado por veículos diferentes (decidido na curadoria pelo LLM, que agrupa os itens numa única pauta) | Proposta |
| Pauta (story) | Um fato tratado no roteiro, ligado a uma ou mais notícias de origem | Proposta |
| Duração estimada | Palavras do roteiro ÷ 150 palavras por minuto | Proposta |
| Episódio publicado | Áudio gerado e entrega tentada para todos os usuários ativos (entregas individuais podem falhar) | Proposta |

## Fora do escopo
**Agora (não fazer):** monetização, plataforma de streaming própria, permissões além de "admin ou não", personalização por usuário, app mobile, episódios diários, vídeo, treino de modelos, IA nas etapas de áudio e distribuição.

**Visão futura (só com autorização explícita):** WhatsApp e e-mail como canais, escolha de categorias por usuário, mais de um apresentador (diálogo), Postgres no lugar do SQLite.
