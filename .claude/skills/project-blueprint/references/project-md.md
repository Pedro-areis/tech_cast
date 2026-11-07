# Modelo: docs/PROJECT.md

Este é o documento de produto: o que construir e por quê. Escreva para alguém que nunca viu o projeto.

```markdown
# <Nome>: projeto e requisitos

## O problema
<As dores concretas de quem vai usar o produto. Duas a quatro, com exemplos reais. É a seção mais importante: ela decide o que entra no escopo.>

## O que <Nome> resolve
<Como o produto responde a cada dor. Inclua o que ele deliberadamente não faz e por quê.>

## Para quem
<Público, contexto (país, moeda, idioma) e, se houver, objetivos do autor (ex.: aprendizado).>

## Requisitos funcionais
Legenda de status: ✅ implementado · ⚠️ parcial · ❌ ausente
<Tabelas agrupadas por área: Requisito | Status. Num projeto existente, o status vem do diagnóstico, com o motivo curto. Num projeto novo, todos começam em ❌ ou a coluna é omitida.>

## Requisitos não funcionais
<Segurança, consistência, usabilidade, desempenho, qualidade, portabilidade. Só os que valem para este projeto, cada um em uma linha concreta.>

## Definições do domínio
<Termos e indicadores que precisam de definição única (ex.: saldo, fluxo de caixa, taxa de conversão). Tabela: Termo | Definição | Situação (Proposta / Aprovada). Uma definição só muda com ADR.>

## Fora do escopo
<Agora (não fazer) e Visão futura (só com autorização explícita).>
```

Inclua "Definições do domínio" sempre que o produto calcular números que o usuário vai ler. Definições ambíguas geram relatórios que ninguém consegue verificar.
