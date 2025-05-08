
# Sintonia - Diagnóstico de Conexão

Este aplicativo de diagnóstico ajuda a verificar a conexão com o Supabase e testar operações de usuário.

## Como usar

1. **Teste de Conexão**
   - Verifica se o aplicativo consegue se conectar ao Supabase
   - Mostra informações sobre as credenciais encontradas

2. **Teste de Login**
   - Permite testar credenciais de login
   - Mostra a resposta completa do Supabase para diagnóstico

3. **Usuários Cadastrados**
   - Lista todos os usuários no banco de dados
   - Útil para verificar se os registros estão sendo salvos

4. **Criar Usuário de Teste**
   - Permite criar um usuário de teste rapidamente
   - Mostra a resposta completa da operação

## Configuração

Certifique-se de que as credenciais do Supabase estão configuradas:

- No Render: Adicione as variáveis de ambiente `SUPABASE_URL` e `SUPABASE_KEY`
- Localmente: Edite o arquivo `.streamlit/secrets.toml`
