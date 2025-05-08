
# Instruções de Integração do Módulo de Avaliação Mental

Este documento fornece instruções detalhadas para integrar o novo módulo de avaliação mental ao seu aplicativo Sintonia existente.

## 1. Configuração do Banco de Dados

### 1.1 Criar Tabelas no Supabase

1. Acesse o painel de controle do Supabase
2. Navegue até "SQL Editor"
3. Crie um novo script e cole o conteúdo do arquivo `create_tables.sql`
4. Execute o script para criar as tabelas necessárias:
   - `readiness_assessments`: Armazena dados de avaliação de prontidão
   - `training_sessions`: Armazena dados de sessões de treino

## 2. Configuração do Ambiente

### 2.1 Dependências

Certifique-se de que seu arquivo `requirements.txt` inclua as seguintes dependências:

```
streamlit>=1.22.0
pandas>=1.5.3
numpy>=1.24.3
plotly>=5.14.1
supabase>=1.0.3
```

### 2.2 Configuração de Segredos

Certifique-se de que seu arquivo `.streamlit/secrets.toml` contenha as credenciais do Supabase:

```toml
supabase_url = "sua_url_do_supabase"
supabase_key = "sua_chave_do_supabase"
```

## 3. Integração do Código

### 3.1 Adicionar o Módulo

1. Copie o arquivo `mental_assessment.py` para o diretório do seu projeto
2. Importe o módulo no seu arquivo `app.py` principal:

```python
from mental_assessment import mental_assessment_module
```

### 3.2 Integrar ao Fluxo de Navegação

Adicione o módulo ao seu sistema de navegação existente, como mostrado no arquivo `app_integration.py`.

## 4. Teste e Implantação

1. Teste localmente executando:
   ```
   streamlit run app.py
   ```

2. Verifique se todas as funcionalidades estão operando corretamente:
   - Avaliação de Prontidão
   - Análise Pós-Treino
   - Visualização de Histórico

3. Implante no Render ou na plataforma de sua escolha

## 5. Personalização

Você pode personalizar o módulo conforme necessário:

- Ajustar fórmulas de cálculo em `calculate_readiness_index()` e `calculate_trimp()`
- Modificar a interface do usuário
- Adicionar métricas adicionais

## 6. Suporte

Se encontrar problemas durante a integração, verifique:

1. Conexão com o Supabase
2. Permissões das tabelas
3. Configuração correta dos segredos
4. Dependências instaladas
