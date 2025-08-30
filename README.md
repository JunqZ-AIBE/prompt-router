# 🚀 Prompt Router

Sistema inteligente de otimização e roteamento de prompts para múltiplos LLMs (Claude, OpenAI, Cursor).

## 📋 Visão Geral

O **Prompt Router** é uma ferramenta desenvolvida para otimizar e rotear prompts automaticamente para diferentes Large Language Models (LLMs), aplicando as melhores práticas específicas de cada modelo e formatando adequadamente para máxima eficiência.

### 🎯 Funcionalidades Principais

- **Otimização Inteligente**: Aplica otimizações específicas baseadas no LLM de destino
- **Roteamento Automático**: Determina automaticamente o melhor LLM para cada tipo de prompt
- **Templates Personalizados**: Usa templates otimizados para Claude, OpenAI e Cursor
- **Multi-Output**: Suporte para múltiplos formatos de saída
- **Extensível**: Arquitetura modular para fácil expansão

## 🏗️ Estrutura do Projeto

```
PromptRouter/
├── main.py                 # Ponto de entrada principal
├── requirements.txt        # Dependências do projeto
├── .env                   # Configurações de ambiente
├── README.md              # Documentação (este arquivo)
│
├── config/                # Configurações centralizadas
│   ├── __init__.py
│   └── settings.py        # Classe Settings com todas as configurações
│
├── chains/                # Módulos principais de processamento
│   ├── __init__.py
│   ├── prompt_optimizer.py    # Otimizador de prompts
│   ├── llm_router.py         # Roteador de LLMs
│   └── api_client.py         # Cliente de APIs (placeholder)
│
├── templates/             # Templates para diferentes LLMs
│   ├── claude_template.txt    # Template otimizado para Claude
│   ├── openai_template.txt    # Template otimizado para OpenAI
│   ├── cursor_template.txt    # Template otimizado para Cursor
│   └── universal_template.txt # Template universal
│
├── utils/                 # Utilitários e ferramentas auxiliares
│   ├── __init__.py
│   └── logger.py          # Sistema de logging
│
└── logs/                  # Arquivos de log (gerado automaticamente)
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 2. Instalação de Dependências

```bash
# Clone ou baixe o projeto
cd PromptRouter

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Ambiente

1. Copie o arquivo `.env` e configure suas chaves de API:

```bash
# Edite o arquivo .env e configure suas chaves
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
CURSOR_API_KEY=sua_chave_cursor_aqui
```

2. Pelo menos uma chave de API deve ser configurada para usar o sistema.

## 💻 Como Usar

### Uso Básico via Linha de Comando

```bash
# Exemplo básico - prompt simples
python main.py --input "Explique o conceito de machine learning"

# Otimizar prompt para Claude especificamente
python main.py --input "Analise os prós e contras da IA" --target claude --optimize

# Roteamento automático com otimização
python main.py --input "Crie uma função Python para calcular fibonacci" --optimize

# Usar template específico para OpenAI
python main.py --input "Escreva um texto criativo sobre o futuro" --target openai --optimize
```

### Opções de Linha de Comando

- `--input, -i`: Prompt de entrada (obrigatório)
- `--target, -t`: LLM de destino (`claude`, `openai`, `cursor`, `universal`)
- `--optimize, -o`: Aplica otimização ao prompt
- `--send, -s`: Envio direto para LLM (funcionalidade futura)

### Exemplos de Saída

```
🚀 Iniciando Prompt Router v1.0.0
📝 Prompt de entrada: Explique machine learning de forma simples...
🎯 Destino: claude
🔧 Otimizando prompt...
🔄 Roteando prompt...

============================================================
📤 PROMPT OTIMIZADO E ROTEADO:
============================================================
<instructions>
Explique machine learning de forma simples para iniciantes
</instructions>

<thinking>
Vou analisar cuidadosamente esta solicitação e fornecer uma resposta detalhada e útil.
</thinking>

Por favor, processe esta solicitação aplicando seu melhor raciocínio e conhecimento.

============================================================
ℹ️  Informações do roteamento:
   - LLM de destino: claude
   - Template usado: claude_template
   - Timestamp: 2025-08-30 11:52:15
```

## 🧩 Componentes Principais

### 1. PromptOptimizer (`chains/prompt_optimizer.py`)

Responsável por otimizar prompts baseado no LLM de destino:

- **Otimizações Gerais**: Remove espaços extras, normaliza formatação
- **Otimizações Específicas**:
  - **Claude**: Estruturas XML, thinking tags
  - **OpenAI**: Prompts diretos, role context
  - **Cursor**: Contexto de programação
  - **Universal**: Formatação compatível com todos

### 2. LLMRouter (`chains/llm_router.py`)

Gerencia o roteamento inteligente:

- **Detecção Automática**: Analisa conteúdo para escolher melhor LLM
- **Templates**: Aplica templates específicos
- **Metadados**: Gera informações sobre complexidade e linguagem

### 3. Settings (`config/settings.py`)

Configuração centralizada:

- Carregamento de variáveis de ambiente
- Configurações específicas por LLM
- Validação de configurações

### 4. Templates (`templates/`)

Templates otimizados para cada LLM:

- **claude_template.txt**: Estrutura XML, thinking tags
- **openai_template.txt**: System/User format, instruções claras
- **cursor_template.txt**: Foco em desenvolvimento
- **universal_template.txt**: Compatível com qualquer LLM

## 📊 Roadmap de Desenvolvimento

### ✅ Fase 1: MVP (Concluída)
- [x] Estrutura base do projeto
- [x] Sistema de otimização de prompts
- [x] Roteamento inteligente
- [x] Templates para diferentes LLMs
- [x] Sistema de logging
- [x] Interface de linha de comando

### 🚧 Fase 2: Multi-Output (Em Desenvolvimento)
- [ ] Múltiplos formatos de saída (JSON, Markdown, Plain Text)
- [ ] Comparação de respostas entre LLMs
- [ ] Metrics de performance
- [ ] Cache de prompts otimizados

### 🔄 Fase 3: Envio Direto (Planejado)
- [ ] Integração com API Anthropic (Claude)
- [ ] Integração com API OpenAI
- [ ] Integração com Cursor (quando disponível)
- [ ] Retry automático e error handling
- [ ] Rate limiting inteligente

### 🌐 Fase 4: Interface Web (Futuro)
- [ ] Interface web intuitiva
- [ ] Dashboard de analytics
- [ ] Histórico de prompts
- [ ] Compartilhamento de templates
- [ ] API REST para integração

## 🔧 Desenvolvimento

### Estrutura de Classes Principais

```python
# Otimizador de prompts
optimizer = PromptOptimizer(settings)
optimized_prompt = optimizer.optimize("seu prompt", target_llm="claude")

# Roteador de LLMs  
router = LLMRouter(settings)
result = router.route_prompt(optimized_prompt, target="auto")

# Cliente de API (placeholder)
client = APIClient(settings)
response = await client.send_prompt(prompt, "claude")
```

### Adicionando Novos LLMs

1. **Adicione configurações** em `config/settings.py`
2. **Crie template** em `templates/novo_llm_template.txt`
3. **Implemente otimizações** em `chains/prompt_optimizer.py`
4. **Adicione roteamento** em `chains/llm_router.py`

### Executando Testes

```bash
# Quando implementado
pytest tests/ -v
```

## 📝 Logs e Debugging

O sistema gera logs automáticos em `logs/prompt_router_YYYYMMDD.log`:

```
2025-08-30 11:52:15 | prompt_router | INFO | PromptOptimizer inicializado  
2025-08-30 11:52:15 | prompt_router | INFO | LLMRouter inicializado
2025-08-30 11:52:16 | prompt_router | INFO | Iniciando otimização para claude
2025-08-30 11:52:16 | prompt_router | DEBUG | Aplicando otimizações para Claude
```

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙋‍♂️ Suporte

Para dúvidas, problemas ou sugestões:

- Abra uma issue no repositório
- Consulte os logs em `logs/` para debugging
- Verifique a configuração do `.env`

---

**Desenvolvido com ❤️ para otimizar sua experiência com LLMs**

*Última atualização: 30/08/2025 - v1.0.0 MVP*
