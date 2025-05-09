# Sistema de Monitoramento do Atleta

## Descrição
Sistema integrado de monitoramento de atletas com três módulos principais:

1. **Avaliação de Prontidão**
   - Avaliação da prontidão física (Hooper Index, TQR, NPRS)
   - Cálculo estatístico dos últimos 7 dias
   - Análise de tendências e recomendações

2. **Avaliação do Estado de Treino**
   - Avaliação de cargas de treino (TRIMP)
   - Análise de risco de lesões
   - Monitoramento de cargas agudas e crônicas (ACWR)

3. **Avaliação Psicoemocional**
   - Avaliação de ansiedade (DASS-21)
   - Avaliação de estresse (PSS-10)
   - Avaliação de estilo de vida (FANTASTIC)

## Instrumentos Validados
Todos os instrumentos utilizados são validados cientificamente:
- **Hooper Index**: Avalia fadiga, estresse, dor muscular e qualidade do sono
- **TQR (Total Quality Recovery)**: Avalia a percepção global de recuperação
- **NPRS (Numeric Pain Rating Scale)**: Avalia a intensidade da dor musculoesquelética
- **TRIMP (Training Impulse)**: Quantifica a carga de treino
- **ACWR (Acute:Chronic Workload Ratio)**: Relação entre carga aguda e crônica
- **DASS-21 (Depression Anxiety Stress Scale)**: Avalia ansiedade
- **PSS-10 (Perceived Stress Scale)**: Avalia a percepção de estresse
- **FANTASTIC (Lifestyle Assessment)**: Avalia estilo de vida

## Instruções para Instalação

### Pré-requisitos
- Conta no [Supabase](https://supabase.com/) (banco de dados)
- Conta no [Render](https://render.com/) (hospedagem)
- [GitHub](https://github.com/) para armazenar o código

### Passo 1: Configurar o Banco de Dados
1. Faça login no Supabase
2. Crie um novo projeto
3. Copie as credenciais (URL e chave de API) para usar posteriormente
4. Vá até a seção "SQL Editor"
5. Copie e cole o conteúdo do arquivo `schema_update.sql` 
6. Execute o script para criar/modificar as tabelas necessárias

### Passo 2: Preparar o Código
1. Crie um repositório no GitHub
2. Faça upload dos seguintes arquivos:
   - `app.py`
   - `readiness_assessment.py`
   - `training_assessment.py`
   - `psychological_assessment.py`
   - `requirements.txt`
   - `logo.png` (sua logomarca)

### Passo 3: Implantar no Render
1. Faça login no Render
2. Clique em "New" e escolha "Web Service"
3. Conecte ao seu repositório GitHub
4. Configure os seguintes detalhes:
   - Nome do serviço: "sistema-monitoramento-atleta" (ou outro nome de sua escolha)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py`
5. Adicione as variáveis de ambiente:
   - `SUPABASE_URL`: URL do seu projeto Supabase
   - `SUPABASE_KEY`: Chave de API do seu projeto Supabase
6. Clique em "Create Web Service"

### Passo 4: Acessar o Aplicativo
Após a implantação, o Render fornecerá um URL para acessar o aplicativo. 
Você pode compartilhar este URL com seus usuários.

## Uso do Aplicativo

### Registro e Login
Os usuários precisam criar uma conta para utilizar o aplicativo:
1. Preencha os campos de registro (nome, email, senha, etc.)
2. Após o registro, faça login com email e senha

### Avaliação de Prontidão
1. Responda às perguntas do Hooper Index (fadiga, estresse, dor, sono)
2. Informe sua recuperação percebida (TQR)
3. Indique seu nível de dor atual (NPRS)
4. Veja sua prontidão para o treino e as recomendações

### Estado de Treino
1. Registre os detalhes do seu treino (duração, intensidade)
2. Veja o cálculo do TRIMP e avaliação de risco de lesão
3. Acompanhe tendências e métricas avançadas (ACWR, monotonia, strain)

### Avaliação Psicoemocional
1. Complete os questionários de ansiedade, estresse e estilo de vida
2. Veja seus scores e recomendações para cada área
3. Acompanhe correlações e tendências ao longo do tempo

### Dashboard
Visualize todas as suas métricas de forma integrada em um único painel.

## Manutenção

### Atualizações
Para atualizar o aplicativo, basta fazer push das alterações no GitHub. 
O Render irá automaticamente implantar as atualizações.

### Backup do Banco de Dados
Recomenda-se fazer backups regulares do banco de dados no Supabase.

## Suporte
Para problemas técnicos ou dúvidas, entre em contato com o desenvolvedor.