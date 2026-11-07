---
name: backlog-page
description: Cria uma página HTML visual do backlog de um projeto, gerada a partir do docs/TASKS.md, com progresso por fase, checklist, critérios de aceite e decisões pendentes, mais um script Node sem dependências para regenerá-la sempre que o TASKS.md mudar. Use quando o usuário quiser acompanhar o backlog, o progresso das fases ou as tarefas de forma visual, pedir uma página ou um painel do TASKS.md, ou disser que prefere ver o andamento do projeto numa página em vez do markdown. Também use para atualizar ou consertar uma página de backlog que já existe.
---

# Backlog Page

Gera uma visualização do `docs/TASKS.md` em HTML. A ideia central é uma **única fonte da verdade**: o markdown é editado e versionado, e a página é derivada dele por um script. Assim as duas versões nunca divergem. Por isso a página nunca é editada à mão.

## Passo 1: conferir o TASKS.md

- Procure `docs/TASKS.md`. Se o arquivo estiver em outro lugar, use `--source` no script.
- Confira se ele segue o formato que o script entende (detalhes em [references/tasks-format.md](references/tasks-format.md)):
  - Fases como títulos `##` que começam com ⬜, 🔄 ou ✅.
  - Tarefas em `- [ ]` ou `- [x]`.
  - Critério de aceite numa linha `**Aceite:**`.
  - Opcional, mas recomendado: uma seção `## Estado atual` (sem emoji) para a troca de bastão. Ela aparece no topo da coluna lateral, em destaque. Se não existir, sugira ao usuário criá-la (o modelo está na skill `project-blueprint`), sem criá-la por conta própria.
- Se o formato for diferente, **não reescreva o TASKS.md por conta própria**. Mostre ao usuário a diferença e pergunte se ele prefere ajustar o arquivo ao formato ou se você deve adaptar o parser do script. O TASKS.md é dele, e mudar a estrutura afeta como ele trabalha.
- Se não existir TASKS.md, sugira criá-lo (a skill `project-blueprint` gera um no formato certo).

## Passo 2: instalar o gerador no projeto

1. Escolha a pasta. O padrão é `backlog-page/` na raiz do projeto. Se o usuário já tem uma pasta para isso, use a dele.
2. Copie [scripts/build-backlog.mjs](scripts/build-backlog.mjs) para essa pasta. O script resolve os caminhos a partir da própria localização, então ele precisa estar uma pasta abaixo da raiz, ou receber `--source` e `--out`.
3. **Versionar ou não:** o padrão recomendado é ignorar a pasta no git (`backlog-page/` no `.gitignore`). A página é derivada; versioná-la só gera diffs barulhentos. Se o usuário quiser compartilhar o gerador com outras pessoas, a alternativa é versionar só o script e ignorar o `backlog.html`. Pergunte se não ficar claro.
4. Rode o script na raiz do projeto:
   ```bash
   node backlog-page/build-backlog.mjs --name "Nome do Projeto"
   ```
   Sem `--name`, ele usa o nome da pasta do projeto ("web-wallet" vira "Web Wallet"). Requer Node 18 ou mais recente.

## Passo 3: verificar

Abra `backlog-page/backlog.html` num navegador (o painel de navegador, se houver) e confira:
- Os números do resumo batem com o TASKS.md (tarefas concluídas, fases concluídas, fase atual, decisões pendentes).
- Se o TASKS.md tiver "Estado atual", ele aparece primeiro na coluna lateral.
- Todas as fases aparecem, com as tarefas e o critério de aceite.
- A página não rola na horizontal numa janela estreita.

Prefira ler o texto da página a tirar screenshots.

## Passo 4: manter a página atualizada

Se o projeto tiver um `CLAUDE.md`, proponha acrescentar esta orientação junto da referência ao TASKS.md:

> Se a pasta `backlog-page/` existir (é local e ignorada pelo git), rode `node backlog-page/build-backlog.mjs` depois de alterar o TASKS.md. O comando regenera a página visual do backlog. A página é derivada: nunca edite o HTML à mão.

Por que a frase "se a pasta existir": a pasta é local. Em outra máquina, ou numa sessão na nuvem, ela não existe, e o agente não deve falhar nem recriá-la sem pedido.

## Personalizar

O visual (cores, fontes, layout) está no CSS dentro do script, com as cores definidas como variáveis no `:root`. A página segue o tema claro ou escuro do sistema. Ajustes de visual são feitos no script, nunca no HTML gerado.

## Ao terminar

Diga ao usuário:
- Onde ficaram o script e a página.
- O comando para regenerar.
- Se a pasta foi ignorada no git.
- Se o CLAUDE.md recebeu a orientação.
