import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuração do banco de dados
DATABASE = 'prontidao.db'

def create_tables():
    # Cria as tabelas necessárias no banco de dados se não existirem
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Tabela de usuários (para um sistema real com autenticação)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
        ''')

        # Tabela de avaliações
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            sono INTEGER NOT NULL,
            fadiga INTEGER NOT NULL,
            dor INTEGER NOT NULL,
            estresse INTEGER NOT NULL,
            vigor INTEGER NOT NULL,
            tensao INTEGER NOT NULL,
            apetite INTEGER NOT NULL,
            prontidao INTEGER NOT NULL
        )
        ''')

        # Inserir um usuário admin padrão se não existir
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
            INSERT INTO users (username, email, password, created_at, is_admin)
            VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@example.com', 'password123', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        raise e

def save_assessment(usuario_id, data, sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao):
    # Salva uma nova avaliação no banco de dados
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO assessments (usuario_id, data, sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (usuario_id, data, sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao))

        assessment_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return assessment_id
    except Exception as e:
        print(f"Erro ao salvar avaliação: {e}")
        raise e

def get_historico(usuario_id, dias=30):
    # Busca o histórico de avaliações de um usuário
    try:
        conn = sqlite3.connect(DATABASE)

        # Calcular a data de início
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)

        # Consulta SQL
        query = '''
        SELECT data, sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao
        FROM assessments
        WHERE usuario_id = ? AND date(data) BETWEEN date(?) AND date(?)
        ORDER BY data
        '''

        # Executar a consulta
        df = pd.read_sql_query(
            query, 
            conn, 
            params=(usuario_id, data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d'))
        )

        conn.close()

        # Se houver resultados, calcular o score e ajuste
        if not df.empty:
            df['Data'] = pd.to_datetime(df['data'])
            df['Score'] = df[['sono', 'fadiga', 'dor', 'estresse', 'vigor', 'tensao', 'apetite', 'prontidao']].sum(axis=1)

            # Calcular o ajuste (importando a função aqui para evitar importação circular)
            def ajuste_carga(score_total):
                score_percentual = (score_total / 40) * 100
                if score_percentual >= 90:
                    return 100
                elif score_percentual <= 50:
                    return 50
                else:
                    return score_percentual

            df['Ajuste'] = df['Score'].apply(ajuste_carga)

        return df
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        # Retornar DataFrame vazio em caso de erro
        return pd.DataFrame()
