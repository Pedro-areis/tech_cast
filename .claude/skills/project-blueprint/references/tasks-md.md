# Modelo: docs/TASKS.md

Este formato é lido pela skill `backlog-page`. Mantenha as convenções marcadas como **formato** para a página continuar funcionando.

```markdown
# Tarefas

<Uma ou duas linhas: como usar o arquivo e a referência ao PROJECT.md.>

Status: ⬜ não iniciada · 🔄 em andamento · ✅ concluída

## Estado atual

- **Atualizado em:** <AAAA-MM-DD>
- **Última sessão:** <o que foi feito, em uma ou duas linhas, com branch ou PR>
- **Em andamento:** <tarefa e fase, e o que falta nela; "nada" se a última tarefa terminou>
- **Bloqueios:** <decisão, acesso ou problema que impede avançar; "nenhum" se não houver>
- **Próximo passo:** <a próxima ação concreta, para quem pegar o projeto agora>

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
- **Formato:** as seções sem emoji (Estado atual, Concluído, Decisões pendentes) ficam antes das fases.
- **Estado atual** é a troca de bastão: quem abrir o projeto sem o histórico da conversa deve saber, só por ela, onde o trabalho parou e o que fazer em seguida. Reescreva a seção inteira (não acumule histórico; o histórico é o git) ao fim de cada tarefa ou sessão. No projeto novo, preencha com o resultado do blueprint e "Próximo passo: aprovar a Fase 0 e as decisões pendentes".
- Uma fase deve caber em poucos PRs. Se tiver mais de ~8 tarefas, divida.
- Ordem das fases: primeiro o que destrava a verificação (build, ambiente, testes), depois o que reduz risco (segurança, integridade de dados), depois funcionalidades, por fim acabamento e deploy.
- Ao concluir uma tarefa, marque `[x]` e anote o PR. Ao concluir a fase, troque o emoji para ✅.
