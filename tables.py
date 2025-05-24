"""
Módulo de tabelas para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo contém funções para criação e manipulação de tabelas.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Union, Tuple

def create_data_table(
    data: pd.DataFrame,
    columns: List[str] = None,
    column_names: Dict[str, str] = None,
    formatters: Dict[str, callable] = None,
    sort_by: str = None,
    ascending: bool = False,
    page_size: int = 10,
    height: str = "400px",
    width: str = "100%",
    filters: Dict[str, List[Any]] = None,
    highlight_max: List[str] = None,
    highlight_min: List[str] = None,
    conditional_formatting: Dict[str, Dict[str, Any]] = None,
    show_pagination: bool = True,
    show_search: bool = True,
    show_export: bool = True,
    key: str = None
) -> None:
    """
    Cria uma tabela de dados interativa com várias opções de formatação e filtragem.
    
    Args:
        data: DataFrame com os dados
        columns: Lista de colunas a serem exibidas (None = todas)
        column_names: Dicionário para renomear colunas {nome_original: nome_exibição}
        formatters: Dicionário de funções para formatar valores {coluna: função}
        sort_by: Coluna para ordenação inicial
        ascending: Ordem ascendente (True) ou descendente (False)
        page_size: Número de linhas por página
        height: Altura da tabela (CSS)
        width: Largura da tabela (CSS)
        filters: Dicionário de filtros {coluna: [valores]}
        highlight_max: Lista de colunas para destacar valores máximos
        highlight_min: Lista de colunas para destacar valores mínimos
        conditional_formatting: Formatação condicional {coluna: {condição: estilo}}
        show_pagination: Exibir controles de paginação
        show_search: Exibir campo de busca
        show_export: Exibir botão de exportação
        key: Chave única para o componente
    """
    # Cria uma cópia do DataFrame para não modificar o original
    df = data.copy()
    
    # Filtra as colunas se especificado
    if columns is not None:
        df = df[columns]
    
    # Renomeia as colunas se especificado
    if column_names is not None:
        df = df.rename(columns=column_names)
    
    # Aplica formatadores se especificados
    if formatters is not None:
        for col, formatter in formatters.items():
            if col in df.columns:
                df[col] = df[col].apply(formatter)
    
    # Aplica filtros se especificados
    if filters is not None:
        for col, values in filters.items():
            if col in df.columns:
                df = df[df[col].isin(values)]
    
    # Ordena os dados se especificado
    if sort_by is not None and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # Prepara a paginação
    if show_pagination:
        total_pages = max(1, (len(df) + page_size - 1) // page_size)
        page_number = st.session_state.get(f"page_{key}", 0)
        
        # Garante que o número da página é válido
        page_number = max(0, min(page_number, total_pages - 1))
        
        # Atualiza o estado da sessão
        st.session_state[f"page_{key}"] = page_number
        
        # Filtra os dados para a página atual
        start_idx = page_number * page_size
        end_idx = min(start_idx + page_size, len(df))
        df_page = df.iloc[start_idx:end_idx]
    else:
        df_page = df
    
    # Prepara a tabela
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_page.columns),
            fill_color='#1E88E5',
            align='left',
            font=dict(color='white', size=14)
        ),
        cells=dict(
            values=[df_page[col] for col in df_page.columns],
            fill_color='white',
            align='left',
            font=dict(color='#424242', size=12),
            height=30
        )
    )])
    
    # Aplica formatação condicional
    if conditional_formatting is not None:
        for col, conditions in conditional_formatting.items():
            if col in df_page.columns:
                col_idx = list(df_page.columns).index(col)
                for condition, style in conditions.items():
                    # Avalia a condição para cada valor na coluna
                    mask = df_page[col].apply(lambda x: eval(condition, {"x": x}))
                    
                    # Aplica o estilo onde a condição é verdadeira
                    if 'fill_color' in style:
                        fig.update_traces(cells=dict(
                            fill_color=[[style['fill_color'] if mask.iloc[i] else 'white' for i in range(len(df_page))] if j == col_idx else None for j in range(len(df_page.columns))]
                        ))
                    
                    if 'font_color' in style:
                        fig.update_traces(cells=dict(
                            font=dict(color=[[style['font_color'] if mask.iloc[i] else '#424242' for i in range(len(df_page))] if j == col_idx else None for j in range(len(df_page.columns))])
                        ))
    
    # Destaca valores máximos
    if highlight_max is not None:
        for col in highlight_max:
            if col in df_page.columns:
                col_idx = list(df_page.columns).index(col)
                max_val = df_page[col].max()
                
                # Cria máscara para valores máximos
                mask = df_page[col] == max_val
                
                # Aplica destaque
                fig.update_traces(cells=dict(
                    fill_color=[[('#4CAF50' if mask.iloc[i] else 'white') for i in range(len(df_page))] if j == col_idx else None for j in range(len(df_page.columns))]
                ))
    
    # Destaca valores mínimos
    if highlight_min is not None:
        for col in highlight_min:
            if col in df_page.columns:
                col_idx = list(df_page.columns).index(col)
                min_val = df_page[col].min()
                
                # Cria máscara para valores mínimos
                mask = df_page[col] == min_val
                
                # Aplica destaque
                fig.update_traces(cells=dict(
                    fill_color=[[('#F44336' if mask.iloc[i] else 'white') for i in range(len(df_page))] if j == col_idx else None for j in range(len(df_page.columns))]
                ))
    
    # Configura o layout da tabela
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        width=800
    )
    
    # Exibe a tabela
    st.plotly_chart(fig, use_container_width=True)
    
    # Exibe controles de paginação
    if show_pagination and total_pages > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
        
        with col1:
            if st.button("⏮️ Primeira", key=f"first_{key}"):
                st.session_state[f"page_{key}"] = 0
                st.experimental_rerun()
        
        with col2:
            if st.button("⏪ Anterior", key=f"prev_{key}"):
                st.session_state[f"page_{key}"] = max(0, page_number - 1)
                st.experimental_rerun()
        
        with col3:
            st.write(f"Página {page_number + 1} de {total_pages} ({len(df)} registros)")
        
        with col4:
            if st.button("⏩ Próxima", key=f"next_{key}"):
                st.session_state[f"page_{key}"] = min(total_pages - 1, page_number + 1)
                st.experimental_rerun()
        
        with col5:
            if st.button("⏭️ Última", key=f"last_{key}"):
                st.session_state[f"page_{key}"] = total_pages - 1
                st.experimental_rerun()
    
    # Exibe campo de busca
    if show_search:
        search_term = st.text_input("Buscar", key=f"search_{key}")
        if search_term:
            # Busca em todas as colunas
            mask = np.column_stack([df[col].astype(str).str.contains(search_term, case=False, na=False) for col in df.columns])
            filtered_df = df[mask.any(axis=1)]
            
            # Exibe resultados da busca
            st.write(f"Encontrados {len(filtered_df)} resultados para '{search_term}'")
            
            # Cria nova tabela com resultados filtrados
            create_data_table(
                filtered_df,
                column_names=column_names,
                formatters=formatters,
                sort_by=sort_by,
                ascending=ascending,
                page_size=page_size,
                height=height,
                width=width,
                highlight_max=highlight_max,
                highlight_min=highlight_min,
                conditional_formatting=conditional_formatting,
                show_pagination=show_pagination,
                show_search=False,  # Evita recursão
                show_export=show_export,
                key=f"search_results_{key}"
            )
    
    # Exibe botão de exportação
    if show_export:
        export_format = st.selectbox(
            "Formato de exportação",
            options=["CSV", "Excel", "JSON"],
            key=f"export_format_{key}"
        )
        
        if st.button("Exportar dados", key=f"export_{key}"):
            if export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name=f"dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"download_csv_{key}"
                )
            elif export_format == "Excel":
                excel_file = df.to_excel(index=False)
                st.download_button(
                    label="Baixar Excel",
                    data=excel_file,
                    file_name=f"dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_excel_{key}"
                )
            elif export_format == "JSON":
                json = df.to_json(orient="records")
                st.download_button(
                    label="Baixar JSON",
                    data=json,
                    file_name=f"dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"download_json_{key}"
                )

def create_readiness_table(data: pd.DataFrame, show_details: bool = True) -> None:
    """
    Cria uma tabela específica para dados de prontidão.
    
    Args:
        data: DataFrame com dados de prontidão
        show_details: Exibir colunas detalhadas ou apenas resumo
    """
    if data is None or data.empty:
        st.info("Não há dados de prontidão disponíveis.")
        return
    
    # Define as colunas a serem exibidas
    if show_details:
        columns = [
            'date', 'score', 'sleep_quality', 'sleep_duration', 'stress',
            'fatigue', 'muscle_soreness', 'energy', 'motivation',
            'nutrition', 'hydration'
        ]
    else:
        columns = ['date', 'score']
    
    # Define nomes amigáveis para as colunas
    column_names = {
        'date': 'Data',
        'score': 'Prontidão',
        'sleep_quality': 'Qualidade do Sono',
        'sleep_duration': 'Duração do Sono (h)',
        'stress': 'Estresse',
        'fatigue': 'Fadiga',
        'muscle_soreness': 'Dor Muscular',
        'energy': 'Energia',
        'motivation': 'Motivação',
        'nutrition': 'Nutrição',
        'hydration': 'Hidratação'
    }
    
    # Define formatadores para as colunas
    formatters = {
        'date': lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime, pd.Timestamp)) else x,
        'score': lambda x: f"{x}/100"
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'score': {
            'x < 20': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x >= 20 and x < 40': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= 40 and x < 60': {'fill_color': '#FFF9C4'},  # Amarelo muito claro
            'x >= 60 and x < 80': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 80': {'fill_color': '#C8E6C9'}   # Verde mais claro
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=data,
        columns=columns,
        column_names=column_names,
        formatters=formatters,
        sort_by='date',
        ascending=False,
        conditional_formatting=conditional_formatting,
        highlight_max=['score'],
        highlight_min=None,
        key="readiness_table"
    )

def create_training_table(data: pd.DataFrame, show_details: bool = True) -> None:
    """
    Cria uma tabela específica para dados de treino.
    
    Args:
        data: DataFrame com dados de treino
        show_details: Exibir colunas detalhadas ou apenas resumo
    """
    if data is None or data.empty:
        st.info("Não há dados de treino disponíveis.")
        return
    
    # Define as colunas a serem exibidas
    if show_details:
        columns = [
            'date', 'type', 'duration', 'rpe', 'trimp', 'tss',
            'post_feeling', 'notes'
        ]
    else:
        columns = ['date', 'type', 'duration', 'rpe', 'trimp']
    
    # Define nomes amigáveis para as colunas
    column_names = {
        'date': 'Data',
        'type': 'Tipo',
        'duration': 'Duração (min)',
        'rpe': 'RPE (0-10)',
        'trimp': 'TRIMP',
        'tss': 'TSS',
        'post_feeling': 'Sensação Pós-Treino',
        'notes': 'Observações'
    }
    
    # Define formatadores para as colunas
    formatters = {
        'date': lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime, pd.Timestamp)) else x,
        'post_feeling': lambda x: ['Muito ruim', 'Ruim', 'Normal', 'Bom', 'Excelente'][x-1] if isinstance(x, (int, float)) and 1 <= x <= 5 else x
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'rpe': {
            'x <= 2': {'fill_color': '#E3F2FD'},  # Azul muito claro
            'x > 2 and x <= 4': {'fill_color': '#BBDEFB'},  # Azul claro
            'x > 4 and x <= 6': {'fill_color': '#90CAF9'},  # Azul médio
            'x > 6 and x <= 8': {'fill_color': '#64B5F6'},  # Azul mais escuro
            'x > 8': {'fill_color': '#42A5F5'}   # Azul escuro
        },
        'trimp': {
            'x < 50': {'fill_color': '#E3F2FD'},  # Azul muito claro
            'x >= 50 and x < 100': {'fill_color': '#BBDEFB'},  # Azul claro
            'x >= 100 and x < 200': {'fill_color': '#90CAF9'},  # Azul médio
            'x >= 200 and x < 300': {'fill_color': '#64B5F6'},  # Azul mais escuro
            'x >= 300': {'fill_color': '#42A5F5'}   # Azul escuro
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=data,
        columns=columns,
        column_names=column_names,
        formatters=formatters,
        sort_by='date',
        ascending=False,
        conditional_formatting=conditional_formatting,
        highlight_max=['trimp'],
        highlight_min=None,
        key="training_table"
    )

def create_psychological_table(data: pd.DataFrame, show_details: bool = True) -> None:
    """
    Cria uma tabela específica para dados psicológicos.
    
    Args:
        data: DataFrame com dados psicológicos
        show_details: Exibir colunas detalhadas ou apenas resumo
    """
    if data is None or data.empty:
        st.info("Não há dados psicológicos disponíveis.")
        return
    
    # Define as colunas a serem exibidas
    if show_details:
        columns = [
            'date', 'dass_score', 'dass_depression', 'dass_anxiety',
            'dass_stress', 'mood', 'sleep_quality', 'life_stress', 'notes'
        ]
    else:
        columns = ['date', 'dass_score', 'mood']
    
    # Define nomes amigáveis para as colunas
    column_names = {
        'date': 'Data',
        'dass_score': 'Score DASS',
        'dass_depression': 'Depressão',
        'dass_anxiety': 'Ansiedade',
        'dass_stress': 'Estresse',
        'mood': 'Humor',
        'sleep_quality': 'Qualidade do Sono',
        'life_stress': 'Estresse da Vida',
        'notes': 'Observações'
    }
    
    # Define formatadores para as colunas
    formatters = {
        'date': lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime, pd.Timestamp)) else x,
        'dass_score': lambda x: f"{x}/100",
        'mood': lambda x: ['Muito ruim', 'Ruim', 'Neutro', 'Bom', 'Excelente'][x-1] if isinstance(x, (int, float)) and 1 <= x <= 5 else x,
        'dass_depression': lambda x: ['Nenhum', 'Leve', 'Moderado', 'Severo'][x] if isinstance(x, (int, float)) and 0 <= x <= 3 else x,
        'dass_anxiety': lambda x: ['Nenhum', 'Leve', 'Moderado', 'Severo'][x] if isinstance(x, (int, float)) and 0 <= x <= 3 else x,
        'dass_stress': lambda x: ['Nenhum', 'Leve', 'Moderado', 'Severo'][x] if isinstance(x, (int, float)) and 0 <= x <= 3 else x
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'dass_score': {
            'x < 20': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x >= 20 and x < 40': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= 40 and x < 60': {'fill_color': '#FFF9C4'},  # Amarelo muito claro
            'x >= 60 and x < 80': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 80': {'fill_color': '#C8E6C9'}   # Verde mais claro
        },
        'mood': {
            'x == 1': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x == 2': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x == 3': {'fill_color': '#FFF9C4'},  # Amarelo muito claro
            'x == 4': {'fill_color': '#DCEDC8'},  # Verde claro
            'x == 5': {'fill_color': '#C8E6C9'}   # Verde mais claro
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=data,
        columns=columns,
        column_names=column_names,
        formatters=formatters,
        sort_by='date',
        ascending=False,
        conditional_formatting=conditional_formatting,
        highlight_max=['dass_score'],
        highlight_min=None,
        key="psychological_table"
    )

def create_metrics_table(data: pd.DataFrame) -> None:
    """
    Cria uma tabela específica para métricas avançadas.
    
    Args:
        data: DataFrame com métricas avançadas
    """
    if data is None or data.empty:
        st.info("Não há dados de métricas avançadas disponíveis.")
        return
    
    # Define as colunas a serem exibidas
    columns = [
        'date', 'tss', 'ctl', 'atl', 'tsb', 'monotony', 'strain',
        'readiness_tsb', 'volume_reduction'
    ]
    
    # Define nomes amigáveis para as colunas
    column_names = {
        'date': 'Data',
        'tss': 'TSS',
        'ctl': 'CTL',
        'atl': 'ATL',
        'tsb': 'TSB',
        'monotony': 'Monotonia',
        'strain': 'Strain',
        'readiness_tsb': 'Prontidão (TSB)',
        'volume_reduction': 'Redução de Volume (%)'
    }
    
    # Define formatadores para as colunas
    formatters = {
        'date': lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime, pd.Timestamp)) else x,
        'ctl': lambda x: f"{x:.1f}",
        'atl': lambda x: f"{x:.1f}",
        'tsb': lambda x: f"{x:.1f}",
        'monotony': lambda x: f"{x:.2f}",
        'strain': lambda x: f"{x:.0f}",
        'readiness_tsb': lambda x: f"{x}/100",
        'volume_reduction': lambda x: f"{x:.0f}%"
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'tsb': {
            'x < -30': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x >= -30 and x < -10': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= -10 and x < 10': {'fill_color': '#FFF9C4'},  # Amarelo muito claro
            'x >= 10 and x < 30': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 30': {'fill_color': '#C8E6C9'}   # Verde mais claro
        },
        'readiness_tsb': {
            'x < 20': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x >= 20 and x < 40': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= 40 and x < 60': {'fill_color': '#FFF9C4'},  # Amarelo muito claro
            'x >= 60 and x < 80': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 80': {'fill_color': '#C8E6C9'}   # Verde mais claro
        },
        'monotony': {
            'x < 1.0': {'fill_color': '#C8E6C9'},  # Verde mais claro
            'x >= 1.0 and x < 1.5': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 1.5 and x < 2.0': {'fill_color': '#FFF9C4'},  # Amarelo muito claro
            'x >= 2.0 and x < 2.5': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= 2.5': {'fill_color': '#FFCDD2'}   # Vermelho claro
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=data,
        columns=columns,
        column_names=column_names,
        formatters=formatters,
        sort_by='date',
        ascending=False,
        conditional_formatting=conditional_formatting,
        highlight_max=None,
        highlight_min=None,
        key="metrics_table"
    )

def create_correlation_table(data: pd.DataFrame, method: str = 'pearson') -> None:
    """
    Cria uma tabela de correlação entre variáveis.
    
    Args:
        data: DataFrame com os dados
        method: Método de correlação ('pearson' ou 'spearman')
    """
    if data is None or data.empty:
        st.info("Não há dados suficientes para análise de correlação.")
        return
    
    # Remove colunas não numéricas
    numeric_cols = data.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) < 2:
        st.info("São necessárias pelo menos duas variáveis numéricas para análise de correlação.")
        return
    
    # Calcula a matriz de correlação
    corr_matrix = data[numeric_cols].corr(method=method)
    
    # Formata a matriz para exibição
    corr_df = corr_matrix.reset_index()
    corr_df = corr_df.rename(columns={'index': 'Variável'})
    
    # Define formatadores para as colunas
    formatters = {col: lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x for col in corr_df.columns}
    formatters['Variável'] = lambda x: x  # Não formata a coluna de nomes
    
    # Define formatação condicional para valores de correlação
    conditional_formatting = {}
    for col in corr_df.columns:
        if col != 'Variável':
            conditional_formatting[col] = {
                'x <= -0.7': {'fill_color': '#EF9A9A'},  # Vermelho forte negativo
                'x > -0.7 and x <= -0.5': {'fill_color': '#FFCDD2'},  # Vermelho médio negativo
                'x > -0.5 and x <= -0.3': {'fill_color': '#FFEBEE'},  # Vermelho fraco negativo
                'x > -0.3 and x < 0.3': {'fill_color': '#F5F5F5'},  # Neutro
                'x >= 0.3 and x < 0.5': {'fill_color': '#E8F5E9'},  # Verde fraco positivo
                'x >= 0.5 and x < 0.7': {'fill_color': '#C8E6C9'},  # Verde médio positivo
                'x >= 0.7': {'fill_color': '#A5D6A7'}   # Verde forte positivo
            }
    
    # Cria a tabela
    create_data_table(
        data=corr_df,
        formatters=formatters,
        conditional_formatting=conditional_formatting,
        show_pagination=False,
        show_search=False,
        key="correlation_table"
    )

def create_summary_table(data: Dict[str, Any]) -> None:
    """
    Cria uma tabela de resumo com estatísticas.
    
    Args:
        data: Dicionário com estatísticas resumidas
    """
    if not data:
        st.info("Não há dados disponíveis para resumo.")
        return
    
    # Converte o dicionário para DataFrame
    df = pd.DataFrame(list(data.items()), columns=['Métrica', 'Valor'])
    
    # Cria a tabela
    create_data_table(
        data=df,
        show_pagination=False,
        show_search=False,
        show_export=False,
        key="summary_table"
    )

def create_goals_table(data: pd.DataFrame) -> None:
    """
    Cria uma tabela específica para metas.
    
    Args:
        data: DataFrame com dados de metas
    """
    if data is None or data.empty:
        st.info("Não há metas definidas.")
        return
    
    # Define as colunas a serem exibidas
    columns = [
        'type', 'metric', 'target_value', 'current_value', 'progress',
        'target_date', 'days_remaining', 'status'
    ]
    
    # Define nomes amigáveis para as colunas
    column_names = {
        'type': 'Tipo',
        'metric': 'Métrica',
        'target_value': 'Valor Alvo',
        'current_value': 'Valor Atual',
        'progress': 'Progresso',
        'target_date': 'Data Alvo',
        'days_remaining': 'Dias Restantes',
        'status': 'Status'
    }
    
    # Define formatadores para as colunas
    formatters = {
        'target_date': lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime, pd.Timestamp)) else x,
        'progress': lambda x: f"{x:.0f}%",
        'days_remaining': lambda x: f"{x} dias",
        'status': lambda x: {
            'active': '🟢 Ativa',
            'completed': '✅ Concluída',
            'expired': '⏱️ Expirada',
            'cancelled': '❌ Cancelada'
        }.get(x, x)
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'progress': {
            'x < 25': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x >= 25 and x < 50': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= 50 and x < 75': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 75': {'fill_color': '#C8E6C9'}   # Verde mais claro
        },
        'days_remaining': {
            'x < 0': {'fill_color': '#FFCDD2'},  # Vermelho claro
            'x >= 0 and x < 7': {'fill_color': '#FFECB3'},  # Amarelo claro
            'x >= 7 and x < 30': {'fill_color': '#DCEDC8'},  # Verde claro
            'x >= 30': {'fill_color': '#C8E6C9'}   # Verde mais claro
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=data,
        columns=columns,
        column_names=column_names,
        formatters=formatters,
        sort_by='target_date',
        ascending=True,
        conditional_formatting=conditional_formatting,
        key="goals_table"
    )

def create_comparison_table(data1: pd.DataFrame, data2: pd.DataFrame, label1: str, label2: str) -> None:
    """
    Cria uma tabela de comparação entre dois conjuntos de dados.
    
    Args:
        data1: Primeiro DataFrame
        data2: Segundo DataFrame
        label1: Rótulo para o primeiro DataFrame
        label2: Rótulo para o segundo DataFrame
    """
    if data1 is None or data1.empty or data2 is None or data2.empty:
        st.info("Não há dados suficientes para comparação.")
        return
    
    # Calcula estatísticas para cada DataFrame
    stats1 = data1.describe().T
    stats2 = data2.describe().T
    
    # Mescla as estatísticas
    stats = pd.DataFrame({
        'Variável': stats1.index,
        f'{label1} (Média)': stats1['mean'],
        f'{label2} (Média)': stats2['mean'],
        'Diferença (%)': (stats2['mean'] - stats1['mean']) / stats1['mean'] * 100,
        f'{label1} (Mín)': stats1['min'],
        f'{label2} (Mín)': stats2['min'],
        f'{label1} (Máx)': stats1['max'],
        f'{label2} (Máx)': stats2['max']
    })
    
    # Define formatadores para as colunas
    formatters = {
        f'{label1} (Média)': lambda x: f"{x:.2f}",
        f'{label2} (Média)': lambda x: f"{x:.2f}",
        'Diferença (%)': lambda x: f"{x:+.1f}%",
        f'{label1} (Mín)': lambda x: f"{x:.2f}",
        f'{label2} (Mín)': lambda x: f"{x:.2f}",
        f'{label1} (Máx)': lambda x: f"{x:.2f}",
        f'{label2} (Máx)': lambda x: f"{x:.2f}"
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'Diferença (%)': {
            'x <= -20': {'fill_color': '#FFCDD2'},  # Vermelho claro (piora significativa)
            'x > -20 and x <= -5': {'fill_color': '#FFECB3'},  # Amarelo claro (piora moderada)
            'x > -5 and x < 5': {'fill_color': '#F5F5F5'},  # Neutro
            'x >= 5 and x < 20': {'fill_color': '#DCEDC8'},  # Verde claro (melhora moderada)
            'x >= 20': {'fill_color': '#C8E6C9'}   # Verde mais claro (melhora significativa)
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=stats,
        formatters=formatters,
        conditional_formatting=conditional_formatting,
        show_pagination=False,
        key="comparison_table"
    )

def create_heatmap_table(data: pd.DataFrame, x_col: str, y_col: str, value_col: str) -> None:
    """
    Cria uma tabela de mapa de calor.
    
    Args:
        data: DataFrame com os dados
        x_col: Coluna para o eixo X
        y_col: Coluna para o eixo Y
        value_col: Coluna para os valores
    """
    if data is None or data.empty:
        st.info("Não há dados suficientes para criar o mapa de calor.")
        return
    
    # Cria a tabela pivô
    pivot = pd.pivot_table(
        data,
        values=value_col,
        index=y_col,
        columns=x_col,
        aggfunc='mean'
    )
    
    # Cria a figura
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Viridis',
        showscale=True
    ))
    
    # Configura o layout
    fig.update_layout(
        title=f'Mapa de Calor: {value_col} por {y_col} e {x_col}',
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=500,
        width=800
    )
    
    # Exibe a figura
    st.plotly_chart(fig, use_container_width=True)

def create_calendar_table(data: pd.DataFrame, date_col: str, value_col: str, title: str = None) -> None:
    """
    Cria uma tabela de calendário com valores codificados por cor.
    
    Args:
        data: DataFrame com os dados
        date_col: Coluna de data
        value_col: Coluna de valor
        title: Título do calendário
    """
    if data is None or data.empty:
        st.info("Não há dados suficientes para criar o calendário.")
        return
    
    # Garante que a coluna de data está no formato correto
    data[date_col] = pd.to_datetime(data[date_col])
    
    # Extrai ano, mês e dia
    data['year'] = data[date_col].dt.year
    data['month'] = data[date_col].dt.month
    data['day'] = data[date_col].dt.day
    
    # Obtém o intervalo de datas
    min_date = data[date_col].min()
    max_date = data[date_col].max()
    
    # Calcula o número de meses no intervalo
    num_months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month + 1
    
    # Limita a 12 meses para não sobrecarregar a visualização
    if num_months > 12:
        st.warning(f"O intervalo de datas é muito grande ({num_months} meses). Exibindo apenas os últimos 12 meses.")
        min_date = max_date - pd.DateOffset(months=11)
        data = data[data[date_col] >= min_date]
    
    # Cria um DataFrame com todas as datas no intervalo
    all_dates = pd.date_range(start=min_date.replace(day=1), end=max_date, freq='D')
    all_dates_df = pd.DataFrame({
        date_col: all_dates,
        'year': all_dates.year,
        'month': all_dates.month,
        'day': all_dates.day
    })
    
    # Mescla com os dados originais
    merged = all_dates_df.merge(
        data[[date_col, value_col]],
        on=date_col,
        how='left'
    )
    
    # Agrupa por ano e mês
    months = merged.groupby(['year', 'month'])
    
    # Cria um calendário para cada mês
    for (year, month), group in months:
        month_name = pd.Timestamp(year=year, month=month, day=1).strftime('%B %Y')
        
        # Cria uma matriz para o mês (6 semanas x 7 dias)
        month_matrix = np.full((6, 7), np.nan)
        
        # Obtém o primeiro dia do mês
        first_day = pd.Timestamp(year=year, month=month, day=1)
        
        # Obtém o dia da semana do primeiro dia (0 = segunda, 6 = domingo)
        first_weekday = first_day.weekday()
        
        # Ajusta para domingo como primeiro dia da semana
        first_weekday = (first_weekday + 1) % 7
        
        # Preenche a matriz com os dias do mês
        for i, row in group.iterrows():
            day = row['day']
            week = (day + first_weekday - 1) // 7
            weekday = (day + first_weekday - 1) % 7
            
            if week < 6:  # Garante que não ultrapassa as 6 semanas
                month_matrix[week, weekday] = row[value_col]
        
        # Cria a figura
        fig = go.Figure(data=go.Heatmap(
            z=month_matrix,
            x=['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
            y=[f'Semana {i+1}' for i in range(6)],
            colorscale='Viridis',
            showscale=True,
            text=[[str(i * 7 + j + 1 - first_weekday) if not np.isnan(month_matrix[i, j]) and 
                  (i * 7 + j + 1 - first_weekday > 0) and 
                  (i * 7 + j + 1 - first_weekday <= pd.Timestamp(year=year, month=month, day=1).days_in_month) 
                  else '' for j in range(7)] for i in range(6)],
            hovertemplate='Dia: %{text}<br>Valor: %{z}<extra></extra>'
        ))
        
        # Configura o layout
        fig.update_layout(
            title=f'{month_name}',
            height=300,
            width=600,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Exibe a figura
        st.plotly_chart(fig, use_container_width=True)

def create_variable_selection_table(available_variables: Dict[str, List[str]], selected_variables: List[str] = None) -> None:
    """
    Cria uma tabela para seleção de variáveis.
    
    Args:
        available_variables: Dicionário com variáveis disponíveis por categoria
        selected_variables: Lista de variáveis já selecionadas
    """
    if not available_variables:
        st.info("Não há variáveis disponíveis para seleção.")
        return
    
    if selected_variables is None:
        selected_variables = []
    
    # Cria uma lista de todas as variáveis
    all_variables = []
    for category, vars in available_variables.items():
        for var in vars:
            all_variables.append({
                'Categoria': category,
                'Variável': var,
                'Selecionada': var in selected_variables
            })
    
    # Converte para DataFrame
    df = pd.DataFrame(all_variables)
    
    # Define formatadores para as colunas
    formatters = {
        'Selecionada': lambda x: '✅' if x else '❌'
    }
    
    # Define formatação condicional
    conditional_formatting = {
        'Selecionada': {
            'x == True': {'fill_color': '#C8E6C9'},  # Verde claro
            'x == False': {'fill_color': '#FFFFFF'}  # Branco
        }
    }
    
    # Cria a tabela
    create_data_table(
        data=df,
        formatters=formatters,
        conditional_formatting=conditional_formatting,
        sort_by='Categoria',
        ascending=True,
        key="variable_selection_table"
    )
