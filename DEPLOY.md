# Instruções de Deploy no Streamlit Cloud

1. **Preparação**
   - Todos os arquivos devem estar em um repositório GitHub
   - Estrutura necessária:
     ```
     ├── app.py
     ├── readiness_assessment.py
     ├── training_assessment.py
     ├── psychological_assessment.py
     ├── requirements.txt
     ├── config.toml
     └── .gitignore
     ```

2. **Configuração no Streamlit Cloud**
   - Acesse: https://share.streamlit.io
   - Conecte com seu GitHub
   - Selecione o repositório
   - Configure as seguintes variáveis secretas:
     - SUPABASE_URL
     - SUPABASE_KEY

3. **Deploy**
   - Selecione a branch principal
   - Configure o arquivo principal como: app.py
   - Python version: 3.9
   - Clique em "Deploy!"

4. **Monitoramento**
   - Verifique os logs para garantir que tudo está funcionando
   - Teste todas as funcionalidades após o deploy
   - Configure o domínio personalizado se necessário

5. **Manutenção**
   - Atualizações são automáticas a cada commit
   - Monitore o uso de recursos
   - Faça backup regular dos dados do Supabase

6. **Segurança**
   - Nunca commit arquivos secrets.toml com credenciais
   - Use .gitignore para arquivos sensíveis
   - Mantenha as dependências atualizadas

7. **Otimização**
   - Use st.cache para funções pesadas
   - Otimize consultas ao Supabase
   - Minimize o uso de recursos externos

8. **Troubleshooting**
   - Verifique os logs do Streamlit
   - Teste localmente antes do deploy
   - Mantenha um ambiente de staging