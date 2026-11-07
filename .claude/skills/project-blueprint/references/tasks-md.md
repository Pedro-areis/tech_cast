# Modelo: docs/TASKS.md

Este formato é lido pela skill `backlog-page`. Mantenha as convenções marcadas como **formato** para a página continuar funcionando.

```markdown
# Tarefas

<Uma ou duas linhas: como usar o arquivo e a referência ao PROJECT.md.>

Status: ⬜ não iniciada · 🔄 em andamento · ✅ concluída

## Concluído

- [x] <O que já foi feito antes das fases, ex.: diagnóstico, documentação inicial>

## Decisões pendentes

- [ ] <Decisão>. <Sugestão>. Necessária na Fase N.

## ⬜ Fase 0: <nome curto>

- [ ] <Tarefa pequena e verificável>
- [ ] <Tarefa>

**Aceite:** <condições objetivas que provam que a fase terminou>
```

## Convenções de formato
- **Formato:** cada fase é um título `##` que começa com o emoji de status (⬜, 🔄 ou ✅), seguido de "Fase N: nome".
- **Formato:** as tarefas são `- [ ]` ou `- [x]`, uma por linha.
- **Formato:** o critério de aceite é uma linha que começa com `**Aceite:**`.
- **Formato:** as seções sem emoji (Concluído, Decisões pendentes) ficam antes das fases.
- Uma fase deve caber em poucos PRs. Se tiver mais de ~8 tarefas, divida.
- Ordem das fases: primeiro o que destrava a verificação (build, ambiente, testes), depois o que reduz risco (segurança, integridade de dados), depois funcionalidades, por fim acabamento e deploy.
- Ao concluir uma tarefa, marque `[x]` e anote o PR. Ao concluir a fase, troque o emoji para ✅.
