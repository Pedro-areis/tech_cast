# Modelo: relatório de diagnóstico (conversa e docs/DIAGNOSIS.md)

O mesmo conteúdo serve para a resposta na conversa e para o `docs/DIAGNOSIS.md` (em projeto existente). No arquivo, inclua no topo a data, a branch e o commit analisados.

Abra com uma linha sobre **como** a análise foi feita: o que foi lido, o que foi executado e o que foi limpo depois. Mostre a legenda **[C] comprovado · [H] hipótese**.

## Seções

1. **Estado atual:** o que o sistema faz, como está organizado, a stack real (tabela) e o modelo de dados.
2. **Inventário de funcionalidades:** tabela Funcionalidade | Backend | Frontend (ou equivalente), com status e o motivo curto.
3. **Avaliação arquitetural:** pontos positivos primeiro (o que deve ser mantido), depois os problemas, agrupados (build e banco, regras de negócio, qualidade de código, frontend), cada um com [C] ou [H].
4. **Segurança:** tabela # | Severidade | Achado | Evidência. Severidades: Crítica, Alta, Média, Baixa. Na evidência, conte o que foi feito e o que aconteceu (ex.: "alice trocou a senha de bob e o login de bob falhou").
5. **Testes:** o que existe, se roda, lacunas prioritárias e ferramentas propostas.
6. **Proposta de refatoração (ou de arquitetura, em projeto novo):** mudanças numeradas com justificativa. Destaque decisões de modelagem com a recomendação e a alternativa.
7. **Stack:** confirmar ou propor mudanças. Tabela Ajuste | Por quê | Custo. Liste também o que **não** recomenda agora e por quê.
8. **Plano priorizado:** tabela Fase | Escopo | Prioridade | Risco | Esforço (P ≈ até 1 dia, M ≈ 2 a 4 dias, G ≈ uma semana ou mais).
9. **Critérios de aceite:** por fase, condições objetivas e verificáveis por comando ou teste.
10. **Decisões pendentes:** numeradas, cada uma com a sua sugestão e em que fase precisa estar decidida.

## Estilo
- Frases curtas e diretas. Nomes de arquivos, comandos e endpoints em `código`.
- Separe fato de hipótese. Não exagere severidade.
- Termine pedindo a aprovação da primeira fase.
