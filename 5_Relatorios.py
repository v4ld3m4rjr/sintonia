"""
Módulo de Relatórios para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo permite ao atleta gerar relatórios detalhados e exportar dados.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from PIL import Image
from io import BytesIO
from fpdf import FPDF

# Adiciona os diretórios ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os módulos de utilidades
from utils.auth import check_authentication
from utils.database import (
    get_readiness_data, get_training_data, get_psychological_data
)
from utils.helpers import format_date, get_date_range, get_date_labels
from utils.training_load import (
    calculate_tss_from_rpe, calculate_ctl, calculate_atl, calculate_tsb,
    calculate_monotony, calculate_strain, calculate_readiness_from_tsb
)
from utils.scale_descriptions import (
    get_scale_description, get_readiness_score_description, get_tsb_description,
    get_ctl_description, get_monotony_description, get_strain_description
)

# Importa os componentes reutilizáveis
from components.cards import metric_card, info_card
from components.charts import (
    create_trend_chart, create_bar_chart, create_pie_chart, create_radar_chart,
    create_heatmap, create_tss_ctl_atl_chart, create_monotony_strain_chart
)
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Relatórios - Sistema de Monitoramento do Atleta",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("📄 Relatórios")
create_breadcrumbs(["Dashboard", "Relatórios"])

# Função para preparar todos os dados
def prepare_all_data(start_date, end_date):
    """
    Prepara todos os dados (prontidão, treino, psicológico) para o período selecionado.
    
    Args:
        start_date (date): Data de início
        end_date (date): Data de fim
    
    Returns:
        dict: Dicionário contendo DataFrames para cada tipo de dado
    """
    days = (end_date - start_date).days + 1
    user_id = st.session_state.user_id
    
    all_data = {}
    
    # Dados de Prontidão (Questionário)
    readiness_data = get_readiness_data(user_id, days)
    df_readiness = None
    if readiness_data:
        df_readiness = pd.DataFrame(readiness_data)
        df_readiness["date"] = pd.to_datetime(df_readiness["date"])
        df_readiness["date_only"] = df_readiness["date"].dt.date
        df_readiness = df_readiness[(df_readiness["date_only"] >= start_date) & (df_readiness["date_only"] <= end_date)]
        if not df_readiness.empty:
            all_data["readiness"] = df_readiness.sort_values("date_only")
    
    # Dados de Treino
    training_data = get_training_data(user_id, days)
    df_training = None
    if training_data:
        df_training = pd.DataFrame(training_data)
        df_training["date"] = pd.to_datetime(df_training["date"])
        df_training["date_only"] = df_training["date"].dt.date
        df_training = df_training[(df_training["date_only"] >= start_date) & (df_training["date_only"] <= end_date)]
        if not df_training.empty:
            # Calcula TSS
            df_training["tss"] = df_training.apply(
                lambda row: calculate_tss_from_rpe(row["duration"], row["rpe"]),
                axis=1
            )
            all_data["training"] = df_training.sort_values("date_only")
    
    # Dados Psicológicos
    psychological_data = get_psychological_data(user_id, days)
    df_psychological = None
    if psychological_data:
        df_psychological = pd.DataFrame(psychological_data)
        df_psychological["date"] = pd.to_datetime(df_psychological["date"])
        df_psychological["date_only"] = df_psychological["date"].dt.date
        df_psychological = df_psychological[(df_psychological["date_only"] >= start_date) & (df_psychological["date_only"] <= end_date)]
        if not df_psychological.empty:
            all_data["psychological"] = df_psychological.sort_values("date_only")
    
    # Dados de Carga Avançada (calculados a partir do treino)
    if "training" in all_data:
        df_train_agg = df_training.groupby("date_only").agg({
            "tss": "sum"
        }).reset_index()
        
        # Cria um DataFrame com todas as datas no período
        date_range = [start_date + timedelta(days=i) for i in range(days)]
        df_dates = pd.DataFrame({"date_only": date_range})
        
        # Mescla com os dados diários
        df_all = df_dates.merge(df_train_agg, on="date_only", how="left")
        df_all = df_all.fillna(0)
        
        # Calcula CTL, ATL, TSB
        df_all["ctl"] = df_all["tss"].ewm(span=42, adjust=False).mean()
        df_all["atl"] = df_all["tss"].ewm(span=7, adjust=False).mean()
        df_all["tsb"] = df_all["ctl"] - df_all["atl"]
        
        # Calcula monotonia e strain
        monotony_values = []
        strain_values = []
        for i in range(len(df_all)):
            if i < 6:
                monotony_values.append(np.nan)
                strain_values.append(np.nan)
            else:
                window = df_all.iloc[i-6:i+1]
                mean_load = window["tss"].mean()
                std_load = window["tss"].std()
                monotony = mean_load / std_load if std_load > 0 else 0
                monotony_values.append(monotony)
                weekly_load = window["tss"].sum()
                strain = weekly_load * monotony
                strain_values.append(strain)
        
        df_all["monotony"] = monotony_values
        df_all["strain"] = strain_values
        df_all["readiness_tsb"] = df_all["tsb"].apply(calculate_readiness_from_tsb)
        
        all_data["load"] = df_all
    
    return all_data

# Função para gerar o relatório em PDF
class PDF(FPDF):
    def header(self):
        # Logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "logo_sintonia.png")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        # Arial bold 15
        self.set_font("Arial", "B", 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, "Relatório de Monitoramento", 0, 0, "C")
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font("Arial", "I", 8)
        # Page number
        self.cell(0, 10, "Página " + str(self.page_no()) + "/{nb}", 0, 0, "C")

    def chapter_title(self, title):
        # Arial 12
        self.set_font("Arial", "B", 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, title, 0, 1, "L", 1)
        # Line break
        self.ln(4)

    def chapter_body(self, body):
        # Times 12
        self.set_font("Times", "", 12)
        # Output justified text
        self.multi_cell(0, 5, body)
        # Line break
        self.ln()

    def add_dataframe(self, df):
        # Define column widths
        col_widths = [self.w / (len(df.columns) + 1)] * len(df.columns)
        line_height = self.font_size * 2.5
        
        # Header
        self.set_font("Arial", "B", 10)
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], line_height, col, border=1)
        self.ln(line_height)
        
        # Data
        self.set_font("Arial", "", 10)
        for index, row in df.iterrows():
            for i, item in enumerate(row):
                self.cell(col_widths[i], line_height, str(item), border=1)
            self.ln(line_height)
        self.ln()

    def add_plot(self, fig, title):
        # Save plot to a temporary file
        img_bytes = fig.to_image(format="png")
        img_path = f"/tmp/{title.replace(" ", "_")}.png"
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        
        # Add image to PDF
        self.image(img_path, x=None, y=None, w=self.w - 20)
        os.remove(img_path) # Clean up temporary file
        self.ln(5)

def generate_pdf_report(data, start_date, end_date):
    """Gera o relatório em formato PDF."""
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Times", "", 12)
    
    pdf.chapter_title(f"Relatório do Período: {start_date.strftime("%d/%m/%Y")} a {end_date.strftime("%d/%m/%Y")}")
    
    # Resumo Geral
    pdf.chapter_title("Resumo Geral")
    # Adicionar métricas gerais aqui (ex: média de prontidão, TRIMP total, etc.)
    # ... (implementar cálculo de métricas gerais)
    pdf.chapter_body("Este resumo apresenta as principais métricas do período selecionado.")
    
    # Seção de Prontidão (Questionário)
    if "readiness" in data:
        pdf.add_page()
        pdf.chapter_title("Prontidão (Questionário)")
        df = data["readiness"]
        df["date_formatted"] = df["date_only"].apply(lambda x: x.strftime("%d/%m"))
        fig = create_trend_chart(df, "date_formatted", "score", title="Evolução da Prontidão", color="#4CAF50", range_y=[0, 100])
        pdf.add_plot(fig, "Evolucao_Prontidao")
        pdf.add_dataframe(df[["date_only", "score", "sleep_quality", "stress", "fatigue", "muscle_soreness"]].head())
    
    # Seção de Treino
    if "training" in data:
        pdf.add_page()
        pdf.chapter_title("Treino")
        df = data["training"]
        df["date_formatted"] = df["date_only"].apply(lambda x: x.strftime("%d/%m"))
        fig = create_trend_chart(df, "date_formatted", "trimp", title="Evolução do TRIMP", color="#FF9800")
        pdf.add_plot(fig, "Evolucao_TRIMP")
        pdf.add_dataframe(df[["date_only", "type", "duration", "rpe", "trimp", "tss"]].head())
    
    # Seção de Carga Avançada
    if "load" in data:
        pdf.add_page()
        pdf.chapter_title("Carga de Treino Avançada")
        df = data["load"]
        df["date_formatted"] = df["date_only"].apply(lambda x: x.strftime("%d/%m"))
        fig = create_tss_ctl_atl_chart(df)
        pdf.add_plot(fig, "TSS_CTL_ATL")
        fig = create_monotony_strain_chart(df)
        pdf.add_plot(fig, "Monotonia_Strain")
        pdf.add_dataframe(df[["date_only", "tss", "ctl", "atl", "tsb", "monotony", "strain"]].head())
    
    # Seção Psicológica
    if "psychological" in data:
        pdf.add_page()
        pdf.chapter_title("Psicológico")
        df = data["psychological"]
        df["date_formatted"] = df["date_only"].apply(lambda x: x.strftime("%d/%m"))
        fig = create_trend_chart(df, "date_formatted", "dass_score", title="Evolução do Score DASS", color="#9C27B0", range_y=[0, 100])
        pdf.add_plot(fig, "Evolucao_DASS")
        pdf.add_dataframe(df[["date_only", "dass_score", "dass_anxiety", "dass_depression", "dass_stress", "mood"]].head())
    
    # Salva o PDF em memória
    pdf_output = pdf.output(dest="S").encode("latin-1")
    return pdf_output

# Função para converter DataFrame para CSV em memória
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# Função principal
def main():
    """Função principal que controla o fluxo da página."""
    # Adiciona o logo na barra lateral
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "logo_sintonia.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.sidebar.image(logo, width=200)
    
    create_section_header(
        "Gerar Relatório", 
        "Selecione o período e os dados que deseja incluir no relatório.",
        "⚙️"
    )
    
    # Seleção de período
    today = datetime.now().date()
    default_start = today - timedelta(days=29)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data de Início", default_start)
    with col2:
        end_date = st.date_input("Data de Fim", today)
    
    if start_date > end_date:
        st.error("Erro: A data de início não pode ser posterior à data de fim.")
        return
    
    # Seleção de dados a incluir
    st.markdown("**Selecione os dados a incluir:**")
    include_readiness = st.checkbox("Prontidão (Questionário)", value=True)
    include_training = st.checkbox("Treino", value=True)
    include_load = st.checkbox("Carga de Treino Avançada", value=True)
    include_psychological = st.checkbox("Psicológico", value=True)
    
    # Botão para gerar relatório
    if st.button("Gerar Relatório", use_container_width=True):
        with st.spinner("Gerando relatório..."):
            # Prepara os dados
            all_data = prepare_all_data(start_date, end_date)
            
            if not all_data:
                st.warning("Não há dados disponíveis para o período selecionado.")
                return
            
            # Filtra os dados com base na seleção do usuário
            report_data = {}
            if include_readiness and "readiness" in all_data: report_data["readiness"] = all_data["readiness"]
            if include_training and "training" in all_data: report_data["training"] = all_data["training"]
            if include_load and "load" in all_data: report_data["load"] = all_data["load"]
            if include_psychological and "psychological" in all_data: report_data["psychological"] = all_data["psychological"]
            
            if not report_data:
                st.warning("Não há dados selecionados disponíveis para o período.")
                return
            
            st.success("Relatório gerado com sucesso!")
            
            # Opções de download
            st.subheader("Download do Relatório")
            
            col1, col2 = st.columns(2)
            
            # Download PDF
            with col1:
                try:
                    pdf_bytes = generate_pdf_report(report_data, start_date, end_date)
                    st.download_button(
                        label="Download Relatório PDF",
                        data=pdf_bytes,
                        file_name=f"relatorio_sintonia_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")
            
            # Download CSV (combinado)
            with col2:
                # Combina todos os DataFrames selecionados
                combined_df = None
                dfs_to_combine = []
                
                if "readiness" in report_data: dfs_to_combine.append(report_data["readiness"].add_prefix("readiness_"))
                if "training" in report_data: dfs_to_combine.append(report_data["training"].add_prefix("training_"))
                if "load" in report_data: dfs_to_combine.append(report_data["load"].add_prefix("load_"))
                if "psychological" in report_data: dfs_to_combine.append(report_data["psychological"].add_prefix("psych_"))
                
                # Usa a coluna de data como chave para merge
                date_col_map = {
                    "readiness": "readiness_date_only",
                    "training": "training_date_only",
                    "load": "load_date_only",
                    "psychological": "psych_date_only"
                }
                
                if dfs_to_combine:
                    combined_df = dfs_to_combine[0]
                    date_key = date_col_map[list(report_data.keys())[0]]
                    
                    for i in range(1, len(dfs_to_combine)):
                        df_to_merge = dfs_to_combine[i]
                        merge_key = date_col_map[list(report_data.keys())[i]]
                        combined_df = pd.merge(combined_df, df_to_merge, left_on=date_key, right_on=merge_key, how="outer")
                        # Remove a coluna de data duplicada
                        if date_key != merge_key:
                            combined_df = combined_df.drop(columns=[merge_key])
                    
                    # Ordena por data
                    combined_df = combined_df.sort_values(by=date_key)
                    
                    csv_bytes = convert_df_to_csv(combined_df)
                    st.download_button(
                        label="Download Dados CSV",
                        data=csv_bytes,
                        file_name=f"dados_sintonia_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("Nenhum dado selecionado para exportar como CSV.")

# Executa a função principal
if __name__ == "__main__":
    main()
