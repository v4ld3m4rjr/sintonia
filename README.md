# Sintonia - Análise de Treino

Este aplicativo oferece duas funcionalidades principais:

1. **Avaliação de Prontidão (Sintonia)**: Avalia a prontidão para treino com base em diversos fatores como sono, fadiga, etc.
2. **Análise Pós-Treino**: Nova funcionalidade que analisa a relação entre recuperação e carga de treino.

## Instruções de Instalação

### 1. Configuração do Banco de Dados

Antes de executar o aplicativo, você precisa configurar as tabelas no Supabase:

1. Faça login no seu painel do Supabase
2. Vá para a seção "SQL Editor"
3. Crie um novo script e cole o conteúdo do arquivo `create_tables.sql`
4. Execute o script para criar as novas tabelas

### 2. Configuração do Aplicativo

1. Faça upload do arquivo `app.py` para seu repositório GitHub
2. Certifique-se de que o arquivo `.streamlit/secrets.toml` contém suas credenciais do Supabase:

```toml
SUPABASE_URL = "sua_url_do_supabase"
SUPABASE_KEY = "sua_chave_do_supabase"
```

3. Implante o aplicativo no Render ou na plataforma de sua preferência

## Funcionalidades

### Avaliação de Prontidão (Sintonia)
- Questionário de prontidão para treino
- Cálculo de ajuste de carga com base na prontidão
- Visualização de histórico de avaliações

### Análise Pós-Treino (Nova)
- Registro de dados de recuperação (PSR, sono, etc.)
- Registro de dados de treino (PSE, duração, tipo)
- Cálculo da razão entre carga e recuperação
- Visualização de tendências ao longo do tempo
- Recomendações baseadas em evidências científicas

## Referências Científicas

- Laurent et al. (2011): Validação da escala PSR
- Mah et al. (2011): Importância do sono para atletas
- Fullagar et al. (2015): Impacto da qualidade do sono na recuperação
- Saw et al. (2016): Monitoramento de bem-estar em atletas
- Foster et al. (2001): Método PSE para quantificar carga de treino
- Impellizzeri et al. (2004): Impacto de diferentes tipos de treino
- McLean et al. (2010) e Hooper et al. (1995): Índices de bem-estar
- Gabbett (2016) e Halson (2014): Equilíbrio entre estresse e recuperação
