# 0001. Banco de dados: SQLite com SQLAlchemy e Alembic

- **Status:** Aceito
- **Data:** 2026-11-07
- **Decisão pendente resolvida:** D8

## Contexto

O TechCast precisa guardar usuários, episódios, notícias, pautas do roteiro e entregas. Os dados são relacionais: um episódio tem várias notícias, uma notícia pode aparecer em mais de um episódio (`EpisodeNewsItem`), e cada usuário tem uma entrega (`Delivery`) por episódio.

O `CLAUDE.md` exige do banco:

- restrição `UNIQUE` no `period_key` do episódio agendado, para a segunda execução do agendador na mesma semana falhar no próprio banco;
- status gravado de forma confiável antes e depois de cada etapa do pipeline, com transações;
- toda mudança de schema numa migration versionada;
- testes sem depender de serviços externos;
- custo zero recorrente.

O volume é pequeno: um episódio por semana, poucos usuários, um único servidor e um único processo escrevendo de cada vez.

O dono do projeto perguntou se um banco NoSQL faria sentido e pediu um comparativo antes de decidir.

## Decisão

Usar **SQLite** como banco, acessado pelo **SQLAlchemy 2** (ORM) e versionado pelo **Alembic** (migrations).

- O endereço do banco vem da variável de ambiente `DATABASE_URL`, por exemplo `sqlite:///./data/techcast.db`. A pasta `data/` fica fora do git e, no deploy, vira um volume do Docker.
- O modo WAL do SQLite fica ativado, para a interface web ler enquanto o pipeline grava.
- O roteiro gerado pelo LLM, que tem formato de documento, fica numa coluna `JSON`.
- Os testes usam SQLite em memória (`sqlite://`), criado e descartado a cada teste.
- O código não usa recursos exclusivos do SQLite, para a migração ao PostgreSQL continuar sendo só uma troca de `DATABASE_URL`.

## Alternativas consideradas

### PostgreSQL

- **Prós:** muitas escritas simultâneas, vários processos ou servidores; mesma stack (SQLAlchemy + Alembic); prática com um banco de servidor muito usado no mercado.
- **Contras:** mais um serviço para instalar e operar (Docker já na Fase 0, usuário e senha); os testes precisariam de um Postgres rodando; num serviço gerenciado, o preço e os limites do plano gratuito teriam de ser verificados. A capacidade extra não seria usada no volume atual.
- **Situação:** é a evolução natural, já prevista como visão futura no `PROJECT.md`.

### MongoDB (NoSQL)

- **Prós:** documentos flexíveis, sem esquema fixo; bom para volumes muito grandes e estruturas que mudam com frequência.
- **Contras:** os dados do projeto são relacionais, o que obrigaria a duplicar dados nos documentos ou juntar coleções com `$lookup`; transações só com *replica set*; sem migrations; incompatível com o SQLAlchemy e o Alembic da stack aprovada, que teriam de ser trocados por outra biblioteca (Beanie/Motor); mais um serviço para operar, ou o Atlas, com limites a verificar. O único dado com formato de documento (o roteiro) cabe numa coluna `JSON`.

### Arquivos JSON

- **Prós:** nenhuma dependência; fácil de abrir e ler.
- **Contras:** sem transações, sem `UNIQUE`, sem consultas; uma falha no meio da gravação pode corromper o arquivo; escritas concorrentes sobrescrevem dados. Não atende às regras do `CLAUDE.md`.

## Consequências

- **Positivas:** nenhuma instalação nem servidor de banco; custo zero; backup é copiar um arquivo; testes rápidos e isolados; `UNIQUE`, chaves estrangeiras e transações nativas.
- **Negativas:** uma escrita por vez. Se no futuro houver vários processos ou servidores escrevendo ao mesmo tempo, será preciso migrar para o PostgreSQL. O SQLite tem limitações no `ALTER TABLE`; o Alembic contorna isso com o modo *batch* (`render_as_batch=True`), que precisa estar ligado desde a configuração inicial.
- **Neutras:** o arquivo do banco não pode ficar numa pasta sincronizada (OneDrive, Dropbox), porque a sincronização durante o uso pode corrompê-lo. Por isso o projeto foi movido para dentro do WSL.
