
# Questionário de Prontidão para Treinamento

Este aplicativo permite que atletas avaliem sua prontidão para treinamento diariamente, ajustando a carga de treinamento com base em fatores como qualidade do sono, dor muscular, fadiga, estresse e outros indicadores importantes.

## Arquivos

- `app.py`: Aplicativo principal
- `test.py`: Aplicativo de teste para verificar a configuração
- `requirements.txt`: Dependências do projeto

## Configuração

### Pré-requisitos

- Python 3.7+
- Conta no Supabase (https://supabase.com)

### Instalação

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as credenciais do Supabase em `.streamlit/secrets.toml` ou nas configurações do Streamlit Cloud

### Banco de Dados

O aplicativo utiliza duas tabelas principais:

1. **users**: Armazena informações dos usuários
2. **assessments**: Armazena as avaliações de prontidão

## Implantação

Para implantar no Streamlit Cloud:

1. Faça upload do código para um repositório GitHub
2. Conecte o repositório ao Streamlit Cloud
3. Configure os segredos (SUPABASE_URL e SUPABASE_KEY)

## Baseado em Evidências Científicas

Este questionário foi desenvolvido com base em pesquisas científicas sobre monitoramento de carga de treinamento, fadiga e recuperação em atletas.
