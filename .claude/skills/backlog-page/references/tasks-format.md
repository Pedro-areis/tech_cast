# Formato do TASKS.md que o script entende

O parser é simples de propósito. Ele reconhece só estes elementos:

| Elemento | Sintaxe | Como aparece na página |
|---|---|---|
| Título do documento | `# Título` (primeira linha `#`) | Título da página |
| Seção comum | `## Nome` sem emoji | Coluna lateral. "Decisões pendentes" ganha destaque; "Concluído" vem em seguida |
| Fase | `## ⬜ Fase N: nome`, `## 🔄 …` ou `## ✅ …` | Cartão com status, barra de progresso e checklist |
| Tarefa | `- [ ] texto` ou `- [x] texto` | Item de checklist |
| Item comum | `- texto` | Lista com marcadores |
| Critério de aceite | linha começando com `**Aceite:**` | Faixa destacada no cartão da fase |
| Outro parágrafo | qualquer outra linha | Nota em texto menor |

Formatação inline reconhecida: `` `código` ``, `**negrito**` e `[texto](link)`. Links `http(s)` viram links; links relativos aparecem só como texto destacado, porque a página não fica no mesmo lugar que os arquivos referenciados.

O resumo do topo calcula:
- **Tarefas concluídas:** soma das tarefas `[x]` de todas as fases sobre o total de tarefas das fases. Seções comuns não entram.
- **Fases concluídas:** fases com ✅.
- **Fase atual:** a primeira com 🔄 ou, se não houver, a primeira com ⬜. O texto antes de `:` vira o destaque, e o texto depois vira a legenda.
- **Decisões pendentes:** tarefas `[ ]` da seção cujo título contém "decis".

Se o projeto precisar de outro formato (ex.: subtarefas aninhadas, responsáveis, datas), adapte as funções `parse` e `render` do script e atualize esta tabela.
