# CrUISE‑AC: Aprimorando a Integração de Conhecimento em Pipelines de User Stories com RAG e LLMs

## Proposta
O **RAG-UserStories** é uma evolução do *CrUISE‑AC* que utiliza **Large Language Models (LLMs)** combinados com **RAG (Retrieval-Augmented Generation)** para otimizar a geração e avaliação de critérios de aceite (*acceptance criteria*) em histórias de usuário (*user stories*).

A solução integra múltiplas fontes internas de conhecimento — *issues*, *pull requests*, *releases* e documentação — para melhorar a fase de *matching* e automatizar a avaliação, que no artigo original era feita manualmente. Com isso, aumenta-se a relevância dos critérios gerados, reduz-se o esforço humano e torna-se o processo mais escalável e personalizado para o contexto do projeto.


## Arquitetura
O sistema é dividido em 4 módulos principais:

### 1. Coleta e Indexação de Conhecimento
- Extrai dados de issues, pull requests, releases e documentação do repositório.
- Normaliza e organiza essas informações para uso posterior.

### 2. Construção do Repositório Vetorial
- Processa os dados coletados e gera embeddings semânticos.
- Armazena no banco vetorial.

### 3. Matching com RAG
- Recebe uma *user story* como consulta.
- Recupera dados relevantes do repositório vetorial.
- Usa LLM para gerar critérios de aceite com base no contexto recuperado.

### 4. Avaliação Automática com LLM
- Recebe critérios gerados e a *user story*.
- Aplica prompt estruturado para validar:
  - Completude
  - Viabilidade
  - Clareza e validação
- Retorna os critérios aprovados, com justificativa.


## Tecnologias e Ferramentas
- **Python** (código)
- **OpenAI API** (LLM)
- **RAG** (Retrieval-Augmented Generation)

## Equipe
- Ana Laura Albuquerque
- Alysson Ramos
- Lucas Torres
- Shellyda Barbosa
- Thaís Neves

## Resources
- [Paper Original do CrUISE‑AC](https://arxiv.org/abs/2501.15181)
- [Documentação do RAG](https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.RagPipeline)
- [Documentação OpenAI API](https://platform.openai.com/docs/)


