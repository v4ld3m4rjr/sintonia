
# Instruções para Integração da Avaliação Mental no Sintonia

## Arquivos Fornecidos
1. `mental_assessment.py` - Módulo completo de avaliação mental adaptado para Streamlit
2. `app_integration.py` - Código de exemplo para integrar no seu app.py existente

## Passos para Integração

### 1. Configuração do Supabase

Crie uma nova tabela no seu projeto Supabase chamada `mental_assessments` com a seguinte estrutura:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | uuid | Chave primária (gerada automaticamente) |
| user_id | uuid | ID do usuário (referência à tabela de usuários) |
| assessment_type | text | Tipo de avaliação (anxiety, stress, mental_fatigue) |
| score | integer | Pontuação total da avaliação |
| interpretation | text | Interpretação do resultado (ex: "Leve", "Moderado") |
| date | timestamp with timezone | Data e hora da avaliação |

### 2. Configuração do Ambiente

Certifique-se de que seu arquivo `.env` contém as credenciais do Supabase:

```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

### 3. Instalação de Dependências

Certifique-se de que todas as dependências necessárias estão instaladas:

```bash
pip install streamlit pandas numpy matplotlib supabase python-dotenv
```

### 4. Integração no GitHub

1. Adicione o arquivo `mental_assessment.py` ao seu repositório
2. Modifique seu arquivo `app.py` existente para incluir a nova funcionalidade de avaliação mental, seguindo o exemplo em `app_integration.py`

### 5. Deploy no Render

1. Faça commit e push das alterações para o GitHub
2. O Render deve detectar automaticamente as alterações e iniciar um novo deploy
3. Certifique-se de que as variáveis de ambiente (SUPABASE_URL e SUPABASE_KEY) estão configuradas no Render

## Estrutura do Menu

A nova opção "Avaliação Mental" deve aparecer no menu principal do aplicativo, junto com as opções existentes de "Avaliação de Prontidão" e "Avaliação TRIMP".

## Funcionalidades Implementadas

1. **Três questionários validados:**
   - Ansiedade (GAD-7)
   - Estresse (PSS-10)
   - Fadiga Mental (MFS)

2. **Para cada avaliação:**
   - Questionário interativo
   - Cálculo automático da pontuação
   - Interpretação dos resultados
   - Recomendações personalizadas
   - Visualização gráfica dos resultados

3. **Histórico de avaliações:**
   - Tabela com todas as avaliações anteriores
   - Gráficos de progresso ao longo do tempo
   - Filtragem por tipo de avaliação
