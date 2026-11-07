# Checklist de investigação (projeto existente)

Use como roteiro, não como formulário. Pule o que não se aplica à stack e aprofunde onde encontrar problemas.

## 1. Mapa do repositório
- `git ls-files` para ver o que está versionado. `git status --ignored` para ver o que está solto no disco.
- Branches locais e remotas: há trabalho que nunca entrou na branch principal (`git log main..outra-branch`)? Há PRs abertos?
- Pastas de ferramentas (IDE, extensões, agentes) versionadas ou soltas.
- READMEs: comparar o que dizem com o que o código faz.

## 2. Build e ambiente
- Rodar o build com as ferramentas do projeto (wrapper do Maven/Gradle, `npm ci`, etc.). Registrar a mensagem exata de erro.
- Versões: linguagem, framework, wrapper. Há versões RC, beta, fora de suporte ou fixadas sem motivo?
- Dependências sem versão, duplicadas ou conflitantes com o gerenciador de versões do framework.
- Configuração: segredos no código ou no README, variáveis de ambiente, perfis, `.env` versionado.
- Como rodar localmente: existe docker-compose? Banco de desenvolvimento? Passo a passo?

## 3. Banco e modelo de dados
- Migrations: ordem, conteúdo e se alguma foi editada depois de aplicada.
- O ORM altera o schema por conta própria (ex.: `ddl-auto=update`) junto com uma ferramenta de migrations?
- Mapeamentos do ORM conferidos contra o schema real: tamanhos, `unique`, cardinalidade, nulidade.
- Restrições do banco (`CHECK`, `NOT NULL`, FKs) contra as validações da API. Uma divergência vira erro 500.
- Valores monetários: tipo decimal exato? Valores derivados guardados (saldo, totais) que podem divergir da fonte?

## 4. Segurança (quando há usuários)
- Para cada endpoint: o usuário vem do token ou de um parâmetro (`userId` na URL ou no corpo)?
- Busca de recurso por id sem conferir o dono (IDOR).
- Endpoints que listam ou alteram dados de todos os usuários.
- Tratamento de erros: os status são corretos (400, 401, 403, 404, 409) ou tudo vira 403/500?
- Validação de entrada: e-mail, senha mínima, campos obrigatórios, valores numéricos.
- Token: algoritmo, segredo (força e origem), expiração (cuidado com fuso horário), armazenamento no cliente, logout.
- CORS, documentação de API pública, limite de tentativas no login.

### Como comprovar sem tocar no repositório
1. Copie o projeto para o diretório de rascunho. Se o build original falha, corrija só na cópia o mínimo necessário para compilar e diga o que corrigiu.
2. Suba um banco descartável, por exemplo: `docker run -d --rm --name diag-db -e POSTGRES_PASSWORD=diag -p 55432:5432 postgres:16-alpine`.
3. Rode a aplicação da cópia apontando para esse banco, numa porta alternativa, com um segredo de teste.
4. Crie dois usuários de teste (ex.: alice e bob) e tente, como alice, ler e alterar recursos de bob. Registre os status e as respostas.
5. Pare a aplicação e o container. Confirme que o repositório original continua sem alterações (`git status`).

## 5. Regras de negócio
- Funcionalidades completas, parciais (só backend, só tela, mockadas) e ausentes, conferidas nos dois lados.
- Cálculos (totais, saldos, indicadores): onde são feitos, se são verificáveis e se usam o banco ou a memória.
- Datas: quem define (usuário ou servidor), fuso horário, exibição no frontend (cuidado com datas sem hora interpretadas como UTC).

## 6. Frontend
- Rotas protegidas, logout real, tratamento de 401, origem da URL da API.
- Assets referenciados de forma que funcione no build de produção.
- Estados de carregamento, vazio e erro; feedback ao usuário.
- Responsividade (larguras fixas?) e acessibilidade (labels, contraste, foco).
- Lint e type-check.

## 7. Testes
- O que existe, se roda e se passa.
- Lacunas críticas: autorização, autenticação, regras financeiras ou de negócio, cálculos.
- Ferramentas adequadas (ex.: testes de integração com o banco real via Testcontainers em vez de um banco em memória que não valida migrations).
