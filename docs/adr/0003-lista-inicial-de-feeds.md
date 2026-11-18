# 0003. Lista inicial de feeds RSS: 18 feeds, 9 brasileiros e 9 estrangeiros

- **Status:** Proposto (aguardando a leitura do dono)
- **Data:** 2026-11-17
- **Decisão pendente resolvida:** D6

## Contexto

A pesquisa de notícias usa feeds RSS (ver `FEASIBILITY.md`, seção 1). A Fase 1 mediu quantos itens cada feed gera por semana (`spikes/`) e rodou a curadoria sobre eles: 18 feeds, 419 itens em 7 dias (245 em português e 174 em inglês). O podcast deve ser técnico o bastante para quem trabalha na área, mas leve; pautas de cultura e entretenimento tech (GTA 6, caso Nvidia) são bem-vindas.

## Decisão

Lista inicial de **18 feeds**, configurável (não fixa no código):

- **Brasileiros (9):** Tecnoblog, Canaltech, Tecmundo, Olhar Digital, Adrenaline, Mobile Time, Convergência Digital, Meio Bit, Núcleo.
- **Estrangeiros (9):** The Verge, TechCrunch, Ars Technica, Engadget, MIT Technology Review, BleepingComputer, BBC Technology, The Register, InfoQ.
- **Reserva (não coletados hoje):** NYT Technology, The Guardian, Showmetech, Folha Tec.
- **Fora:** Wired, Tom's Hardware, Google AI Blog, Hugging Face, OpenAI Blog, Cloudflare Blog, The Hacker News, Hacker News (página inicial), Krebs, AWS News Blog, AnandTech.

Regras para a Fase 3: o resumo é cortado num tamanho fixo (500 caracteres no spike, porque o Canaltech traz o texto inteiro); um feed fora do ar não derruba a coleta.

## Alternativas consideradas

- **Lista menor (14 feeds, primeira rodada):** menos tokens de entrada (~35,7 mil na curadoria contra ~36,1 mil), mas menos variedade; InfoQ e outros foram acrescentados para dar mais pauta técnica.
- **Lista maior:** mais itens, porém o limite de entrada do LLM é o gargalo e o ganho de variedade é pequeno.
- **Só veículos brasileiros ou só estrangeiros:** perde cobertura. A mistura equilibrada deu 42 itens em português e 35 em inglês nas pautas escolhidas.

## Consequências

- **Positivas:** mistura equilibrada de português e inglês; custo zero e sem chave de API; fonte, data e URL rastreáveis (RF05).
- **Negativas:** a curadoria ainda favorece notícia geral; nenhuma pauta saiu do InfoQ nem foi de desenvolvimento ou arquitetura. O ajuste de prompt para 1 a 2 pautas técnicas e 1 a 2 de cultura tech por episódio fica para a Fase 4.
- **Manutenção:** feeds mudam de endereço ou saem do ar; a lista fica em configuração e pode ser revisada sem alterar código.
