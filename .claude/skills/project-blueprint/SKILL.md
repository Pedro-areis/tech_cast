---
name: project-blueprint
description: Diagnostica um repositório existente (ou parte de uma especificação, num projeto novo) e gera os documentos de base para desenvolver com agentes de IA. Gera o .claude/CLAUDE.md com as regras do projeto, o docs/PROJECT.md (problema, requisitos, indicadores), o docs/TASKS.md (fases, tarefas, critérios de aceite) e o docs/DIAGNOSIS.md. Entrega um relatório com o plano de implementação e os trade-offs, e para para aprovação antes de qualquer código. Use sempre que o usuário enviar especificações ou requisitos de um projeto e pedir diagnóstico, auditoria, plano de refatoração, plano de implementação, "organizar o projeto para trabalhar com IA", criar CLAUDE.md, PROJECT.md ou TASKS.md, ou começar um projeto novo de forma estruturada, mesmo que não cite esta skill pelo nome.
---

# Project Blueprint

Transforma "aqui está a especificação e o repositório" em um ponto de partida confiável para desenvolver com agentes:

1. Um diagnóstico baseado em evidência.
2. Os documentos que dão contexto a toda sessão futura.
3. Um plano em fases que o dono do projeto aprova antes de qualquer código.

O valor desta skill está na **investigação**, não nos templates. Um CLAUDE.md genérico, que serviria para qualquer projeto, não ajuda ninguém. Cada linha gerada deve vir do que você encontrou neste repositório e nesta especificação.

## Regra central: nada de implementação

Esta skill produz diagnóstico, documentos e plano. **Não altere código da aplicação, dependências ou configuração**, mesmo que a correção pareça óbvia.

Motivo: o dono do projeto precisa ver o quadro completo e decidir a ordem e o escopo. Mudanças misturadas ao diagnóstico tiram dele essa decisão e tornam o plano difícil de revisar. O que você pode criar são os documentos listados em "Saídas".

## Passo 1: entender o pedido

- Leia a especificação do usuário (texto colado, arquivo ou link) e anote: o problema que o produto resolve, para quem, os requisitos, o que está fora do escopo, a stack desejada e as restrições.
- Descubra o modo:
  - **Projeto existente:** o repositório tem código. Faça o diagnóstico completo (Passo 2A).
  - **Projeto novo:** não há código, ou só um esqueleto. Planeje a partir da especificação (Passo 2B).
- Se faltar algo que muda o plano (ex.: a stack não foi definida num projeto novo), pergunte antes de seguir. Lacunas menores viram "decisões pendentes" no relatório.
- Verifique se já existem `CLAUDE.md`, `.claude/CLAUDE.md`, `docs/PROJECT.md`, `docs/TASKS.md` ou documentação equivalente. Se existirem, leia tudo e **atualize em vez de sobrescrever**. Diga o que mudou e por quê.

## Passo 2A: diagnóstico de projeto existente

Investigue o estado real. Não presuma que o README ou a documentação estão corretos.

Cubra:
- Estrutura de pastas, módulos e organização arquitetural.
- Tecnologias, versões, dependências e ferramentas de build.
- Modelo de dados: entidades, relacionamentos, migrations e se o schema bate com o código.
- Endpoints, fluxos e regras de negócio implementados.
- Autenticação, autorização e isolamento de dados por usuário, se houver usuários.
- Estado do frontend: o que está integrado, o que está mockado, responsividade e acessibilidade.
- Testes existentes e lacunas críticas.
- Configuração local, segredos, variáveis de ambiente, build e CI.
- Estado do git: branches com trabalho fora da branch principal, arquivos de ferramentas soltos, `.gitignore`.
- Duplicação, acoplamento, nomes inconsistentes e débitos técnicos.

**Execute o que for seguro executar:** build, testes, lint e type-check. Rodar comandos revela problemas que a leitura não mostra, como um build que nem compila.

**Comprove os achados críticos quando der.** Para falhas de segurança ou de integridade de dados, a melhor evidência é reproduzir o problema. Faça isso sem tocar no repositório:
- Use uma cópia temporária no diretório de rascunho e um banco descartável (ex.: um container Docker numa porta alternativa).
- Use usuários de teste criados na hora. Nunca use credenciais reais.
- Limpe tudo ao terminar (pare containers e processos) e informe o que foi feito.

Leia [references/investigation-checklist.md](references/investigation-checklist.md) para a lista detalhada do que verificar e como comprovar.

**Classifique cada achado:**
- **[C] Comprovado:** executado, ou inequívoco no código.
- **[H] Hipótese:** plausível, mas ainda não verificado.

Não afirme que algo está ausente sem procurar nos arquivos e fluxos pertinentes. Essa classificação permite ao dono do projeto confiar no relatório e saber o que ainda precisa ser checado.

## Passo 2B: planejamento de projeto novo

- Traduza a especificação em requisitos funcionais e não funcionais.
- Se a stack não foi definida, proponha uma com trade-offs (veja "Trade-offs" abaixo). Se foi definida, só aponte riscos concretos.
- Defina a fundação mínima: estrutura de pastas, build, testes, ambiente local e configuração por variáveis de ambiente.
- Não antecipe complexidade (microsserviços, mensageria, cache distribuído) sem uma necessidade demonstrada na especificação.

## Passo 3: gerar os documentos

Crie ou atualize os arquivos abaixo seguindo os modelos em `references/`. Escreva no idioma do usuário. Os modelos são estrutura, não texto pronto: preencha com o que é específico deste projeto e remova seções que não se aplicam.

| Arquivo | Conteúdo | Modelo |
|---|---|---|
| `.claude/CLAUDE.md` | Regras para agentes: forma de trabalho, comandos, convenções e regras técnicas obrigatórias deste projeto | [references/claude-md.md](references/claude-md.md) |
| `docs/PROJECT.md` | Problema, público, requisitos com status, definição dos indicadores e escopo | [references/project-md.md](references/project-md.md) |
| `docs/TASKS.md` | Estado atual (troca de bastão), decisões pendentes, fases com tarefas e critérios de aceite | [references/tasks-md.md](references/tasks-md.md) |
| `docs/DIAGNOSIS.md` | Só em projeto existente: o diagnóstico datado, como registro do ponto de partida | [references/report.md](references/report.md) |

**Por que `.claude/CLAUDE.md`:** o Claude Code lê automaticamente o `CLAUDE.md` da raiz ou de `.claude/` em toda sessão. Um `docs/CLAUDE.md` só seria lido quando o agente abrisse arquivos em `docs/`. Se o projeto já tiver um `CLAUDE.md` na raiz, mantenha-o lá.

**Mantenha o CLAUDE.md curto** (idealmente menos de 150 linhas). Ele é carregado em toda sessão, e regras demais se diluem. Detalhes ficam em `docs/`, com link no CLAUDE.md.

**Versionamento:** recomende versionar os quatro arquivos. Eles dão contexto a qualquer agente, em qualquer máquina, e o histórico mostra como os requisitos mudaram. Se o `.gitignore` ignorar `.claude/` inteiro, sugira ignorar só `.claude/settings.local.json`.

**Git:** não commite nem abra PR por conta própria, a menos que o usuário peça ou que o CLAUDE.md do projeto já autorize. Ao terminar, diga quais arquivos foram criados e pergunte como ele quer versionar.

## Passo 4: relatório e parada

Apresente o relatório na conversa seguindo [references/report.md](references/report.md):
- Estado atual e inventário de funcionalidades.
- Avaliação de arquitetura, segurança e testes.
- Proposta, análise da stack, plano priorizado e critérios de aceite.
- **Decisões pendentes**, cada uma com a sua recomendação.

Depois **pare**. Peça aprovação para a primeira fase e responda às decisões pendentes. Motivo: o plano só vale se o dono do projeto concordar com a ordem e com os trade-offs. Seguir em frente sem isso transforma um plano em uma imposição.

Se o usuário quiser compartilhar o relatório, ofereça publicá-lo como página.

## Trade-offs

Sempre que houver escolha relevante (tecnologia, modelo de dados, estratégia de autenticação, onde calcular algo), apresente:
- As opções reais. Duas ou três bastam.
- Para cada uma: benefício, custo de implementação e de migração, impacto na manutenção e compatibilidade com o que existe.
- A sua recomendação e o motivo.

Não recomende tecnologia só por ser moderna ou popular. Toda mudança precisa resolver um problema identificado. A stack existente é o padrão; trocar exige justificativa concreta.

## Preferências padrão do autor desta skill

Estas regras vieram do uso real e entram no CLAUDE.md gerado, salvo se o usuário disser o contrário. Ao apresentar o resultado, cite-as para que ele possa ajustar.

- Nomes no código (variáveis, classes, rotas, tabelas) em inglês. Textos de interface no idioma dos usuários.
- O agente pode commitar, fazer push e abrir PRs, mas nunca commita direto na branch principal.
- Toda mudança vem com o porquê. Decisões de arquitetura são consultadas antes de implementar.
- Na dúvida, o agente pergunta e apresenta trade-offs. Decisões aprovadas viram ADRs em `docs/adr/`.
- Trabalho incremental: cada etapa tem escopo, critérios de aceite, implementação, testes e relatório, e o agente aguarda validação antes da próxima.
- Deploy e containerização ficam no fim do plano. Até lá, a aplicação só precisa estar pronta para container (configuração por ambiente, logs no stdout).

## Saídas

Ao terminar:
- Os documentos criados ou atualizados.
- O relatório na conversa.
- Uma linha sobre o que foi executado durante o diagnóstico e o que foi limpo depois.
- A seção "Estado atual" do `docs/TASKS.md` preenchida, para que outra pessoa ou outro agente possa continuar sem o histórico da conversa.
- O pedido de aprovação da primeira fase.

O `docs/TASKS.md` segue um formato que a skill `backlog-page` sabe transformar em página visual. Se o usuário gostar de acompanhar o progresso visualmente, mencione essa skill.
