# Sintonia

Este repositório contém um app em Streamlit para avaliar:
- **Readiness**: baseado em Hooper Index, TQR e NPRS  
- **Estado de Treino**: cálculo de TRIMP (método S-RPE) e risco de lesão  
- **Avaliação Psicoemocional**: DASS-21, PSS-10 e FANTASTIC

## Pré-requisitos

- Python 3.8+  
- Conta e projeto no Supabase  
- Streamlit secrets configurado com `SUPABASE_URL` e `SUPABASE_KEY`

## Estrutura do Repositório

```
.
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/sintonia.git
   cd sintonia
   ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv env
   source env/bin/activate      # Linux/macOS
   env\Scripts\activate       # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure as credenciais no Streamlit:
   Crie o arquivo `~/.streamlit/secrets.toml` com:
   ```toml
   SUPABASE_URL = "sua_supabase_url"
   SUPABASE_KEY = "sua_supabase_key"
   ```
