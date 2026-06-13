# Agentic Ecommerce Analytics

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Agentic_AI-1C3C3C?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent_State-0F172A?style=for-the-badge)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi_Agent-6D28D9?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Local_Stack-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_Search-DC244C?style=for-the-badge)
![Postgres](https://img.shields.io/badge/Postgres-Ledger-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Chainlit](https://img.shields.io/badge/Chainlit-Chat_UI-111827?style=for-the-badge)
![DeepEval](https://img.shields.io/badge/DeepEval-Agent_Evals-F97316?style=for-the-badge)

[Read this README in English](README.md)

Projeto de AI Data Engineering que combina analytics estruturado, busca vetorial e uma interface agentic para responder perguntas de e-commerce.

## Arquitetura

```text
+------------------+     +------------------+     +------------------+
|  DATA GENERATION |     |   AI / LLM       |     |   INTERFACE      |
|  ShadowTraffic   |     |   Claude         |     |   Chainlit       |
+--------+---------+     |   LlamaIndex     |     +--------+---------+
         |               |   LangChain      |              |
         v               |   CrewAI         |              v
+------------------+     +--------+---------+     +------------------+
|  STORAGE         |              |               |   QUALITY        |
|  Postgres        |              v               |   DeepEval       |
|  (The Ledger)    |     +------------------+     |   LangFuse       |
|  Qdrant          |<--->|   MCP Protocol   |     +------------------+
|  (The Memory)    |     +------------------+
+------------------+
```

O sistema usa dois stores complementares:

- **Ledger:** Postgres para métricas exatas de negócio, como receita, pedidos, produtos, meios de pagamento e segmentos de clientes.
- **Memory:** Qdrant para busca semântica em reviews, reclamações, sentimento e temas recorrentes da experiência do cliente.

## O Que O Projeto Faz

- Gera dados sintéticos de e-commerce com ShadowTraffic.
- Armazena clientes, produtos e pedidos no Postgres.
- Escreve reviews de clientes em arquivos JSONL.
- Valida entidades de e-commerce com modelos Pydantic.
- Executa queries de negócio contra o banco relacional.
- Gera embeddings dos comentários com FastEmbed e indexa no Qdrant.
- Expõe duas tools com LangChain: uma para analytics SQL e outra para busca semântica.
- Usa o ShopAgent para rotear perguntas para a tool correta.
- Adiciona um workflow CrewAI com papéis separados para análise de receita, pesquisa da voz do cliente e síntese executiva.
- Inclui casos de avaliação para perguntas SQL-only, semantic-only e híbridas.
- Fornece uma interface Chainlit para exploração interativa.

## Destaques Da Stack

Este projeto foi pensado para demonstrar habilidades práticas de AI Engineer além de um chatbot básico.

| Ferramenta | Como é usada | Por que importa |
|------------|--------------|-----------------|
| **LangChain / LangGraph** | Constrói o ShopAgent, define tool calling, gerencia execução do agente e mantém estado de conversa com memória por thread. | Demonstra orquestração de agentes, uso de tools, gerenciamento de estado e padrões de aplicações LLM mais próximas de produção. |
| **Seleção de Tools** | O agente escolhe entre analytics SQL e busca semântica a partir da pergunta do usuário. Perguntas numéricas vão para o Ledger, perguntas qualitativas vão para Memory e perguntas híbridas podem usar ambos. | Demonstra lógica de roteamento, design de tools, descrições de tools e acesso controlado a sistemas externos. |
| **CrewAI** | Adiciona um workflow multi-agent com Revenue Analyst, Customer Voice Researcher e Executive Advisor. | Mostra como decompor tarefas complexas de IA em agentes especializados com responsabilidades claras. |
| **Docker Compose** | Executa Postgres, Qdrant e ShadowTraffic localmente como uma plataforma de dados reprodutível. | Demonstra conhecimento de infraestrutura, ambiente local de desenvolvimento e orquestração de serviços. |
| **Postgres** | Armazena entidades estruturadas do e-commerce e responde perguntas de negócio exatas. | Cobre modelagem relacional, SQL analytics, joins, agregações e acesso determinístico a dados. |
| **Qdrant** | Armazena reviews vetorizadas para busca semântica sobre feedback de clientes. | Demonstra vector databases, retrieval, similarity search e arquitetura no estilo RAG. |
| **FastEmbed** | Gera embeddings locais dos reviews antes de indexar no Qdrant. | Mantém a busca semântica reprodutível sem depender de uma API externa de embeddings. |
| **Pydantic** | Define modelos de domínio tipados e constraints de validação. | Mostra validação de schema, contratos de dados e structured outputs mais seguros. |
| **DeepEval / pytest** | Valida casos de roteamento para perguntas SQL-only, memory-only e híbridas. | Adiciona disciplina de avaliação ao comportamento do agente, em vez de depender apenas de testes manuais. |
| **Chainlit** | Fornece uma interface de chat para interagir com o agente analítico. | Demonstra uma superfície de uso final para aplicações LLM. |

## Padrões De AI Engineering

- **Arquitetura dual-store:** Postgres lida com métricas exatas, enquanto Qdrant lida com significado e sentimento do cliente.
- **Agentes tool-aware:** as tools são descritas de forma intencional para que o LLM escolha a fonte de dados correta.
- **Retrieval híbrido:** perguntas complexas podem combinar resultados SQL com evidências semânticas vindas dos reviews.
- **Decomposição multi-agent:** CrewAI separa análise quantitativa, pesquisa qualitativa e síntese executiva.
- **Mentalidade evaluation-first:** o comportamento de roteamento é representado como casos de teste para avaliação sistemática.
- **Infraestrutura local-first:** Docker Compose torna a stack reprodutível sem depender de serviços gerenciados externos.

## Demo

Um frontend simples para visualizar o workflow agentic de analytics de e-commerce.

![Agentic Ecommerce Analytics dashboard](docs/assets/dashboard-screenshot.png)

## Estrutura Do Projeto

```text
infra/
  docker-compose.yml        Postgres, Qdrant e ShadowTraffic locais
  init.sql                  Schema relacional do e-commerce
  shadowtraffic.json        Configuração de geração de dados sintéticos
  license.env.example       Template de licença do ShadowTraffic

src/
  domain/                   Modelos Pydantic e demo de validação
  analysis/                 Análise estruturada com LLM e queries SQL de negócio
  retrieval/                Ingestão de reviews e busca semântica
  agent/                    Tools LangChain e factory do ShopAgent
  crew/                     Workflow multi-agent com CrewAI
  evaluation/               Casos de roteamento e runner DeepEval
  demos/                    Scripts de comparação arquitetural
  app/                      Interface Chainlit

frontend/
  index.html                Mockup estático do dashboard

docs/
  architecture.md           Design do sistema e fluxo de dados
  learning-notes.md         Notas pessoais de implementação
  multi-agent-design.md     Design do crew e notas de avaliação
```

## Setup

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crie os arquivos de ambiente locais:

```bash
copy .env.example .env
copy infra\license.env.example infra\license.env
```

Preencha:

- `ANTHROPIC_API_KEY` em `.env`
- campos de licença do ShadowTraffic em `infra/license.env`

Suba os serviços locais e gere os dados:

```bash
cd infra
docker compose up
```

Os reviews gerados são escritos em `infra/data/reviews/`. Esse diretório é ignorado pelo Git.

## Comandos Comuns

A partir da raiz do projeto:

```bash
python src/domain/validation_demo.py
python src/analysis/ledger_queries.py
python src/retrieval/ingest_reviews.py
python src/retrieval/semantic_search.py
python src/agent/shopagent.py
python src/crew/ecommerce_intelligence_crew.py
python src/demos/compare_single_agent_vs_crew.py
python -m pytest tests
chainlit run src/app/chainlit_app.py --port 8000
```

Execute as checagens opcionais de roteamento com DeepEval:

```bash
python src/evaluation/deepeval_routing.py
```

Se o Docker Compose criar um nome diferente para o container do Postgres, sobrescreva:

```bash
set SHOPAGENT_POSTGRES_CONTAINER=infra-postgres-1
```
