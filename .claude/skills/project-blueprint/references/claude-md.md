# Modelo: .claude/CLAUDE.md

Estrutura sugerida. Preencha com o que é específico do projeto e corte o que não se aplica. Mantenha abaixo de ~150 linhas: este arquivo é carregado em toda sessão.

```markdown
# <Nome do projeto>: instruções para agentes de IA

<Uma ou duas frases: o que o produto faz e o que ele deliberadamente não faz.>

Responda ao usuário em <idioma>.

Leia antes de trabalhar:
- [docs/PROJECT.md](../docs/PROJECT.md): o problema, os requisitos e as definições do domínio.
- [docs/TASKS.md](../docs/TASKS.md): fases, tarefas, decisões pendentes. Atualize ao concluir cada tarefa. Comece a sessão pela seção "Estado atual".

## Troca de bastão
Ao terminar uma tarefa, ou antes de encerrar uma sessão com trabalho pela metade, reescreva a seção "Estado atual" do `docs/TASKS.md` (última sessão, em andamento, bloqueios, próximo passo). Preferências e decisões que o dono do projeto deu só na conversa e ainda não viraram ADR ou regra deste arquivo também entram lá, em "Bloqueios" ou "Próximo passo". Motivo: outra pessoa ou outro agente precisa continuar sem o histórico da conversa.

## Regras de trabalho (definidas pelo dono do projeto)
<Numeradas, cada uma com o motivo. Inclua as preferências padrão do autor da skill, salvo instrução contrária, e qualquer regra que o usuário tenha pedido.>

## Forma de trabalho
<O ciclo de cada etapa: problema → arquivos → solução e alternativas → critérios de aceite → implementação → testes → relatório → aguardar validação. A ordem das fases do TASKS.md.>

## Estrutura e stack
<Pastas principais, stack com versões, padrão de organização que deve ser mantido.>

## Comandos
<Bloco com build, testes, lint e execução local. Se algum ainda não funciona, diga, e diga qual fase resolve.>

## Regras técnicas obrigatórias
<Só as que vieram do diagnóstico ou da especificação. Exemplos do tipo certo:
- Isolamento de dados: o usuário vem do token, nunca de parâmetro; recurso alheio retorna 404.
- Banco: toda mudança de schema é uma migration nova; nunca editar migration aplicada.
- Dinheiro: tipo decimal exato; agregações no banco.
- Segredos só em variáveis de ambiente.
- Testes obrigatórios para o que é crítico, com as ferramentas escolhidas.
- Simplicidade: nada de tecnologia nova sem necessidade demonstrada e aprovação.>

## Deploy (se planejado)
<O que fica para o fim e o que o código deve respeitar desde já para não atrapalhar.>

## Fora do escopo
<O que não implementar sem autorização explícita.>

## ADRs
Registre em `docs/adr/NNNN-titulo-curto.md` com: Contexto, Decisão, Alternativas consideradas (com trade-offs), Consequências e Status. Escreva só depois da aprovação do dono do projeto.
```

## Sinais de um CLAUDE.md ruim
- Regras genéricas que serviriam para qualquer projeto ("escreva código limpo").
- Repetir o que o código já mostra (lista de todas as classes).
- Comandos que não foram testados.
- Regras sem motivo. O agente segue melhor quando entende o porquê.
