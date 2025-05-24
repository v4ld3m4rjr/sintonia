"""
Módulo de estatísticas para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo contém funções para análise estatística e processamento de dados.
"""

import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Funções de estatísticas básicas

def calculate_summary_stats(data, percentiles=None):
    """
    Calcula estatísticas resumidas para uma série de dados.
    
    Args:
        data (array): Série de dados
        percentiles (list): Lista de percentis a calcular (padrão: [25, 50, 75])
    
    Returns:
        dict: Dicionário com estatísticas resumidas
    """
    if percentiles is None:
        percentiles = [25, 50, 75]
    
    # Remove valores ausentes
    data_clean = np.array(data)[~np.isnan(data)]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 1:
        return {
            "count": 0,
            "mean": np.nan,
            "std": np.nan,
            "min": np.nan,
            "max": np.nan,
            "percentiles": {p: np.nan for p in percentiles}
        }
    
    # Calcula estatísticas básicas
    count = len(data_clean)
    mean = np.mean(data_clean)
    std = np.std(data_clean)
    min_val = np.min(data_clean)
    max_val = np.max(data_clean)
    
    # Calcula percentis
    percentile_values = {}
    for p in percentiles:
        percentile_values[p] = np.percentile(data_clean, p)
    
    return {
        "count": count,
        "mean": mean,
        "std": std,
        "min": min_val,
        "max": max_val,
        "percentiles": percentile_values
    }

def calculate_rolling_stats(data, window=7, min_periods=1):
    """
    Calcula estatísticas móveis para uma série temporal.
    
    Args:
        data (array): Série de dados
        window (int): Tamanho da janela (padrão: 7)
        min_periods (int): Número mínimo de observações (padrão: 1)
    
    Returns:
        dict: Dicionário com séries de estatísticas móveis
    """
    # Converte para Series do pandas
    series = pd.Series(data)
    
    # Calcula estatísticas móveis
    rolling = series.rolling(window=window, min_periods=min_periods)
    
    return {
        "mean": rolling.mean().values,
        "std": rolling.std().values,
        "min": rolling.min().values,
        "max": rolling.max().values,
        "median": rolling.median().values
    }

def calculate_ewm_stats(data, span=7, min_periods=1):
    """
    Calcula estatísticas de média móvel exponencial.
    
    Args:
        data (array): Série de dados
        span (int): Período de span (padrão: 7)
        min_periods (int): Número mínimo de observações (padrão: 1)
    
    Returns:
        dict: Dicionário com séries de estatísticas EWM
    """
    # Converte para Series do pandas
    series = pd.Series(data)
    
    # Calcula estatísticas EWM
    alpha = 2 / (span + 1)
    ewm = series.ewm(alpha=alpha, min_periods=min_periods)
    
    return {
        "mean": ewm.mean().values,
        "std": ewm.std().values,
        "var": ewm.var().values
    }

def calculate_grouped_stats(df, group_col, value_col, agg_funcs=None):
    """
    Calcula estatísticas agrupadas por uma coluna.
    
    Args:
        df (DataFrame): DataFrame com os dados
        group_col (str): Nome da coluna para agrupar
        value_col (str): Nome da coluna para calcular estatísticas
        agg_funcs (list): Lista de funções de agregação (padrão: ['mean', 'std', 'min', 'max', 'count'])
    
    Returns:
        DataFrame: DataFrame com estatísticas agrupadas
    """
    if agg_funcs is None:
        agg_funcs = ['mean', 'std', 'min', 'max', 'count']
    
    # Agrupa e calcula estatísticas
    grouped = df.groupby(group_col)[value_col].agg(agg_funcs).reset_index()
    
    return grouped

def calculate_correlation_matrix(df, columns=None, method='pearson'):
    """
    Calcula a matriz de correlação entre múltiplas colunas.
    
    Args:
        df (DataFrame): DataFrame com os dados
        columns (list): Lista de colunas para incluir (padrão: todas numéricas)
        method (str): Método de correlação ('pearson', 'spearman', 'kendall')
    
    Returns:
        DataFrame: Matriz de correlação
    """
    # Seleciona colunas
    if columns is None:
        df_corr = df.select_dtypes(include=['number'])
    else:
        df_corr = df[columns]
    
    # Calcula matriz de correlação
    corr_matrix = df_corr.corr(method=method)
    
    return corr_matrix

def calculate_pairwise_correlation(df, x_col, y_col, method='pearson'):
    """
    Calcula a correlação entre duas colunas.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da primeira coluna
        y_col (str): Nome da segunda coluna
        method (str): Método de correlação ('pearson', 'spearman', 'kendall')
    
    Returns:
        dict: Dicionário com coeficiente de correlação e p-valor
    """
    # Remove valores ausentes
    df_clean = df[[x_col, y_col]].dropna()
    
    # Verifica se há dados suficientes
    if len(df_clean) < 2:
        return {
            "coefficient": np.nan,
            "p_value": np.nan,
            "method": method
        }
    
    # Calcula correlação
    if method == 'pearson':
        coef, p_value = stats.pearsonr(df_clean[x_col], df_clean[y_col])
    elif method == 'spearman':
        coef, p_value = stats.spearmanr(df_clean[x_col], df_clean[y_col])
    elif method == 'kendall':
        coef, p_value = stats.kendalltau(df_clean[x_col], df_clean[y_col])
    else:
        raise ValueError(f"Método de correlação não reconhecido: {method}")
    
    return {
        "coefficient": coef,
        "p_value": p_value,
        "method": method
    }

# Funções de análise de tendências

def calculate_linear_trend(x, y):
    """
    Calcula a tendência linear de uma série.
    
    Args:
        x (array): Valores do eixo X (geralmente datas ou índices)
        y (array): Valores do eixo Y
    
    Returns:
        dict: Dicionário com coeficientes e estatísticas da regressão
    """
    # Remove valores ausentes
    mask = ~np.isnan(x) & ~np.isnan(y)
    x_clean = np.array(x)[mask]
    y_clean = np.array(y)[mask]
    
    # Verifica se há dados suficientes
    if len(x_clean) < 2:
        return {
            "slope": np.nan,
            "intercept": np.nan,
            "r_value": np.nan,
            "p_value": np.nan,
            "std_err": np.nan,
            "trend_values": np.array([np.nan] * len(x))
        }
    
    # Calcula regressão linear
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    
    # Calcula valores da tendência
    trend_values = np.full_like(x, np.nan, dtype=float)
    trend_values[mask] = slope * x_clean + intercept
    
    return {
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "p_value": p_value,
        "std_err": std_err,
        "trend_values": trend_values
    }

def calculate_seasonal_decomposition(data, period=7, model='additive'):
    """
    Decompõe uma série temporal em tendência, sazonalidade e resíduo.
    
    Args:
        data (array): Série temporal
        period (int): Período de sazonalidade (padrão: 7 para dados diários)
        model (str): Modelo de decomposição ('additive', 'multiplicative')
    
    Returns:
        dict: Dicionário com componentes da decomposição
    """
    # Remove valores ausentes
    series = pd.Series(data).dropna()
    
    # Verifica se há dados suficientes
    if len(series) < 2 * period:
        return {
            "trend": np.array([np.nan] * len(data)),
            "seasonal": np.array([np.nan] * len(data)),
            "residual": np.array([np.nan] * len(data))
        }
    
    # Decompõe a série
    decomposition = seasonal_decompose(series, model=model, period=period)
    
    # Prepara os resultados
    result = {
        "trend": np.array([np.nan] * len(data)),
        "seasonal": np.array([np.nan] * len(data)),
        "residual": np.array([np.nan] * len(data))
    }
    
    # Preenche os valores onde há dados
    valid_indices = np.where(~np.isnan(data))[0]
    start_idx = valid_indices[0]
    
    result["trend"][start_idx:start_idx+len(decomposition.trend)] = decomposition.trend.values
    result["seasonal"][start_idx:start_idx+len(decomposition.seasonal)] = decomposition.seasonal.values
    result["residual"][start_idx:start_idx+len(decomposition.resid)] = decomposition.resid.values
    
    return result

def calculate_autocorrelation(data, nlags=20):
    """
    Calcula a autocorrelação de uma série temporal.
    
    Args:
        data (array): Série temporal
        nlags (int): Número de lags a calcular
    
    Returns:
        dict: Dicionário com valores de autocorrelação e autocorrelação parcial
    """
    # Remove valores ausentes
    series = pd.Series(data).dropna()
    
    # Verifica se há dados suficientes
    if len(series) < nlags + 1:
        return {
            "acf": np.array([np.nan] * nlags),
            "pacf": np.array([np.nan] * nlags)
        }
    
    # Calcula autocorrelação e autocorrelação parcial
    acf_values = acf(series, nlags=nlags, fft=True)
    pacf_values = pacf(series, nlags=nlags)
    
    return {
        "acf": acf_values,
        "pacf": pacf_values
    }

def detect_change_points(data, window=5, threshold=2.0):
    """
    Detecta pontos de mudança em uma série temporal.
    
    Args:
        data (array): Série temporal
        window (int): Tamanho da janela para cálculo de médias móveis
        threshold (float): Limiar para detecção de mudanças (em desvios padrão)
    
    Returns:
        array: Índices dos pontos de mudança
    """
    # Remove valores ausentes
    series = pd.Series(data).dropna()
    
    # Verifica se há dados suficientes
    if len(series) < 2 * window:
        return np.array([])
    
    # Calcula médias móveis
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    
    # Calcula diferenças entre médias móveis consecutivas
    mean_diff = rolling_mean.diff().abs()
    
    # Normaliza as diferenças
    normalized_diff = mean_diff / rolling_std
    
    # Detecta pontos de mudança
    change_points = np.where(normalized_diff > threshold)[0]
    
    return change_points

# Funções de análise de distribuição

def test_normality(data, test='shapiro'):
    """
    Testa a normalidade de uma distribuição.
    
    Args:
        data (array): Série de dados
        test (str): Teste a usar ('shapiro', 'ks', 'anderson')
    
    Returns:
        dict: Dicionário com estatística de teste, p-valor e resultado
    """
    # Remove valores ausentes
    data_clean = np.array(data)[~np.isnan(data)]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 3:
        return {
            "test": test,
            "statistic": np.nan,
            "p_value": np.nan,
            "normal": False
        }
    
    # Realiza o teste de normalidade
    if test == 'shapiro':
        if len(data_clean) <= 5000:  # Shapiro-Wilk tem limite de tamanho
            statistic, p_value = stats.shapiro(data_clean)
        else:
            return test_normality(data, test='ks')  # Fallback para KS
    elif test == 'ks':
        statistic, p_value = stats.kstest(data_clean, 'norm', args=(np.mean(data_clean), np.std(data_clean)))
    elif test == 'anderson':
        result = stats.anderson(data_clean, dist='norm')
        statistic = result.statistic
        critical_values = result.critical_values
        significance_level = result.significance_level
        
        # Determina o p-valor aproximado
        p_value = 0.0
        for i, level in enumerate(significance_level):
            if statistic < critical_values[i]:
                p_value = level / 100.0
                break
    else:
        raise ValueError(f"Teste de normalidade não reconhecido: {test}")
    
    # Determina se a distribuição é normal
    normal = p_value > 0.05
    
    return {
        "test": test,
        "statistic": statistic,
        "p_value": p_value,
        "normal": normal
    }

def calculate_distribution_metrics(data):
    """
    Calcula métricas de distribuição.
    
    Args:
        data (array): Série de dados
    
    Returns:
        dict: Dicionário com métricas de distribuição
    """
    # Remove valores ausentes
    data_clean = np.array(data)[~np.isnan(data)]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 3:
        return {
            "mean": np.nan,
            "median": np.nan,
            "mode": np.nan,
            "std": np.nan,
            "skewness": np.nan,
            "kurtosis": np.nan,
            "iqr": np.nan,
            "range": np.nan
        }
    
    # Calcula métricas básicas
    mean = np.mean(data_clean)
    median = np.median(data_clean)
    mode_result = stats.mode(data_clean)
    mode = mode_result.mode[0]
    std = np.std(data_clean)
    skewness = stats.skew(data_clean)
    kurtosis = stats.kurtosis(data_clean)
    q1 = np.percentile(data_clean, 25)
    q3 = np.percentile(data_clean, 75)
    iqr = q3 - q1
    data_range = np.max(data_clean) - np.min(data_clean)
    
    return {
        "mean": mean,
        "median": median,
        "mode": mode,
        "std": std,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "iqr": iqr,
        "range": data_range
    }

def calculate_outliers(data, method='zscore', threshold=2.0):
    """
    Identifica outliers em uma série de dados.
    
    Args:
        data (array): Série de dados
        method (str): Método para detecção ('zscore', 'iqr', 'modified_zscore')
        threshold (float): Limiar para detecção
    
    Returns:
        dict: Dicionário com índices e valores dos outliers
    """
    # Remove valores ausentes
    data_array = np.array(data)
    mask = ~np.isnan(data_array)
    data_clean = data_array[mask]
    indices = np.where(mask)[0]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 3:
        return {
            "indices": np.array([]),
            "values": np.array([]),
            "is_outlier": np.zeros_like(data_array, dtype=bool)
        }
    
    # Detecta outliers
    outlier_mask = np.zeros_like(data_clean, dtype=bool)
    
    if method == 'zscore':
        # Método do z-score
        z_scores = np.abs((data_clean - np.mean(data_clean)) / np.std(data_clean))
        outlier_mask = z_scores > threshold
    
    elif method == 'iqr':
        # Método do intervalo interquartil
        q1 = np.percentile(data_clean, 25)
        q3 = np.percentile(data_clean, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        outlier_mask = (data_clean < lower_bound) | (data_clean > upper_bound)
    
    elif method == 'modified_zscore':
        # Método do z-score modificado (mais robusto)
        median = np.median(data_clean)
        mad = np.median(np.abs(data_clean - median))
        modified_z_scores = 0.6745 * np.abs(data_clean - median) / mad if mad > 0 else np.zeros_like(data_clean)
        outlier_mask = modified_z_scores > threshold
    
    else:
        raise ValueError(f"Método de detecção de outliers não reconhecido: {method}")
    
    # Obtém índices e valores dos outliers
    outlier_indices = indices[outlier_mask]
    outlier_values = data_clean[outlier_mask]
    
    # Cria máscara para o array original
    is_outlier = np.zeros_like(data_array, dtype=bool)
    is_outlier[outlier_indices] = True
    
    return {
        "indices": outlier_indices,
        "values": outlier_values,
        "is_outlier": is_outlier
    }

# Funções de análise de agrupamento

def perform_kmeans_clustering(df, columns, n_clusters=3, random_state=42):
    """
    Realiza agrupamento K-means.
    
    Args:
        df (DataFrame): DataFrame com os dados
        columns (list): Lista de colunas para usar no agrupamento
        n_clusters (int): Número de clusters
        random_state (int): Semente aleatória
    
    Returns:
        dict: Dicionário com rótulos de cluster e centróides
    """
    # Remove linhas com valores ausentes
    df_clean = df[columns].dropna()
    
    # Verifica se há dados suficientes
    if len(df_clean) < n_clusters:
        return {
            "labels": np.array([np.nan] * len(df)),
            "centroids": np.array([np.nan] * (n_clusters * len(columns))).reshape(n_clusters, len(columns)),
            "inertia": np.nan
        }
    
    # Normaliza os dados
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df_clean)
    
    # Realiza o agrupamento
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = kmeans.fit_predict(data_scaled)
    
    # Obtém centróides
    centroids_scaled = kmeans.cluster_centers_
    centroids = scaler.inverse_transform(centroids_scaled)
    
    # Prepara rótulos para o DataFrame original
    all_labels = np.full(len(df), np.nan)
    all_labels[df_clean.index] = labels
    
    return {
        "labels": all_labels,
        "centroids": centroids,
        "inertia": kmeans.inertia_
    }

def perform_pca(df, columns, n_components=2):
    """
    Realiza análise de componentes principais (PCA).
    
    Args:
        df (DataFrame): DataFrame com os dados
        columns (list): Lista de colunas para usar na análise
        n_components (int): Número de componentes principais
    
    Returns:
        dict: Dicionário com componentes principais e variância explicada
    """
    # Remove linhas com valores ausentes
    df_clean = df[columns].dropna()
    
    # Verifica se há dados suficientes
    if len(df_clean) < 2 or len(columns) < 2:
        return {
            "components": np.array([np.nan] * (n_components * len(columns))).reshape(n_components, len(columns)),
            "explained_variance_ratio": np.array([np.nan] * n_components),
            "transformed_data": np.array([np.nan] * (len(df_clean) * n_components)).reshape(len(df_clean), n_components)
        }
    
    # Normaliza os dados
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df_clean)
    
    # Realiza PCA
    pca = PCA(n_components=n_components)
    transformed_data = pca.fit_transform(data_scaled)
    
    return {
        "components": pca.components_,
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "transformed_data": transformed_data
    }

# Funções de análise de séries temporais

def calculate_day_of_week_stats(df, date_col, value_col):
    """
    Calcula estatísticas por dia da semana.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        value_col (str): Nome da coluna de valor
    
    Returns:
        DataFrame: DataFrame com estatísticas por dia da semana
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Extrai o dia da semana
    df['day_of_week'] = df[date_col].dt.dayofweek
    
    # Mapeia números para nomes dos dias
    day_names = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    # Agrupa por dia da semana e calcula estatísticas
    stats = df.groupby('day_of_week')[value_col].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    
    # Adiciona nomes dos dias
    stats['day_name'] = stats['day_of_week'].map(day_names)
    
    # Ordena por dia da semana
    stats = stats.sort_values('day_of_week')
    
    return stats

def calculate_monthly_stats(df, date_col, value_col):
    """
    Calcula estatísticas por mês.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        value_col (str): Nome da coluna de valor
    
    Returns:
        DataFrame: DataFrame com estatísticas por mês
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Extrai o mês
    df['month'] = df[date_col].dt.month
    
    # Mapeia números para nomes dos meses
    month_names = {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }
    
    # Agrupa por mês e calcula estatísticas
    stats = df.groupby('month')[value_col].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    
    # Adiciona nomes dos meses
    stats['month_name'] = stats['month'].map(month_names)
    
    # Ordena por mês
    stats = stats.sort_values('month')
    
    return stats

def calculate_weekly_aggregation(df, date_col, value_col, agg_func='mean'):
    """
    Agrega dados por semana.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        value_col (str): Nome da coluna de valor
        agg_func (str): Função de agregação ('mean', 'sum', 'max', 'min')
    
    Returns:
        DataFrame: DataFrame com dados agregados por semana
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Cria uma cópia para não modificar o original
    df_copy = df.copy()
    
    # Extrai a semana do ano
    df_copy['year'] = df_copy[date_col].dt.isocalendar().year
    df_copy['week'] = df_copy[date_col].dt.isocalendar().week
    
    # Agrupa por ano e semana
    grouped = df_copy.groupby(['year', 'week']).agg({value_col: agg_func}).reset_index()
    
    # Cria uma data representativa para cada semana (segunda-feira)
    grouped['date'] = grouped.apply(
        lambda row: datetime.fromisocalendar(int(row['year']), int(row['week']), 1),
        axis=1
    )
    
    return grouped

def calculate_monthly_aggregation(df, date_col, value_col, agg_func='mean'):
    """
    Agrega dados por mês.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        value_col (str): Nome da coluna de valor
        agg_func (str): Função de agregação ('mean', 'sum', 'max', 'min')
    
    Returns:
        DataFrame: DataFrame com dados agregados por mês
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Cria uma cópia para não modificar o original
    df_copy = df.copy()
    
    # Extrai o ano e mês
    df_copy['year_month'] = df_copy[date_col].dt.to_period('M')
    
    # Agrupa por ano-mês
    grouped = df_copy.groupby('year_month').agg({value_col: agg_func}).reset_index()
    
    # Converte o período para datetime
    grouped['date'] = grouped['year_month'].dt.to_timestamp()
    
    return grouped

# Funções de análise específicas para o sistema

def calculate_readiness_components_contribution(df, components=None):
    """
    Calcula a contribuição de cada componente para o score de prontidão.
    
    Args:
        df (DataFrame): DataFrame com os dados
        components (dict): Dicionário com nomes de colunas e pesos
    
    Returns:
        DataFrame: DataFrame com contribuições de cada componente
    """
    if components is None:
        components = {
            'sleep_quality': 0.20,
            'sleep_duration': 0.15,
            'stress': 0.15,
            'fatigue': 0.15,
            'muscle_soreness': 0.10,
            'energy': 0.10,
            'motivation': 0.05,
            'nutrition': 0.05,
            'hydration': 0.05
        }
    
    # Cria uma cópia para não modificar o original
    df_copy = df.copy()
    
    # Inverte componentes onde valores menores são melhores
    invert_components = ['stress', 'fatigue', 'muscle_soreness']
    
    for component in invert_components:
        if component in df_copy.columns:
            df_copy[f"{component}_inverted"] = 6 - df_copy[component]
    
    # Normaliza a duração do sono para escala 1-5
    if 'sleep_duration' in df_copy.columns:
        df_copy['sleep_duration_normalized'] = df_copy['sleep_duration'].apply(
            lambda x: max(1, min(5, (x - 4) / 1.5 + 1)) if not pd.isna(x) else np.nan
        )
    
    # Calcula a contribuição de cada componente
    contributions = pd.DataFrame()
    
    for component, weight in components.items():
        col_name = component
        
        # Usa versão invertida para componentes invertidos
        if component in invert_components:
            col_name = f"{component}_inverted"
        
        # Usa versão normalizada para duração do sono
        if component == 'sleep_duration':
            col_name = 'sleep_duration_normalized'
        
        # Verifica se a coluna existe
        if col_name in df_copy.columns:
            # Calcula a contribuição normalizada (0-100)
            contributions[component] = df_copy[col_name].apply(
                lambda x: (x - 1) * 25 * weight if not pd.isna(x) else np.nan
            )
    
    # Adiciona a data se disponível
    if 'date' in df.columns:
        contributions['date'] = df['date']
    
    return contributions

def calculate_training_load_metrics(df, duration_col='duration', rpe_col='rpe', date_col='date'):
    """
    Calcula métricas avançadas de carga de treino.
    
    Args:
        df (DataFrame): DataFrame com os dados
        duration_col (str): Nome da coluna de duração
        rpe_col (str): Nome da coluna de RPE
        date_col (str): Nome da coluna de data
    
    Returns:
        DataFrame: DataFrame com métricas de carga
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Cria uma cópia para não modificar o original
    df_copy = df.copy()
    
    # Calcula TRIMP e TSS
    df_copy['trimp'] = df_copy[duration_col] * df_copy[rpe_col]
    df_copy['tss'] = df_copy.apply(
        lambda row: (row[duration_col] * 60 * (row[rpe_col] / 10)**2 * 100) / 3600,
        axis=1
    )
    
    # Agrupa por data para obter carga diária
    daily_load = df_copy.groupby(df_copy[date_col].dt.date).agg({
        'trimp': 'sum',
        'tss': 'sum'
    }).reset_index()
    
    # Renomeia a coluna de data
    daily_load = daily_load.rename(columns={0: 'date'})
    
    # Ordena por data
    daily_load = daily_load.sort_values('date')
    
    # Calcula CTL e ATL
    daily_load['ctl'] = daily_load['tss'].ewm(span=42, adjust=False).mean()
    daily_load['atl'] = daily_load['tss'].ewm(span=7, adjust=False).mean()
    daily_load['tsb'] = daily_load['ctl'] - daily_load['atl']
    
    # Calcula monotonia e strain
    monotony_values = []
    strain_values = []
    
    for i in range(len(daily_load)):
        if i < 6:
            monotony_values.append(np.nan)
            strain_values.append(np.nan)
        else:
            window = daily_load.iloc[i-6:i+1]
            mean_load = window['tss'].mean()
            std_load = window['tss'].std()
            monotony = mean_load / std_load if std_load > 0 else 0
            monotony_values.append(monotony)
            weekly_load = window['tss'].sum()
            strain = weekly_load * monotony
            strain_values.append(strain)
    
    daily_load['monotony'] = monotony_values
    daily_load['strain'] = strain_values
    
    return daily_load

def calculate_psychological_metrics(df, anxiety_col='dass_anxiety', depression_col='dass_depression', 
                                   stress_col='dass_stress', mood_col='mood', date_col='date'):
    """
    Calcula métricas psicológicas.
    
    Args:
        df (DataFrame): DataFrame com os dados
        anxiety_col (str): Nome da coluna de ansiedade
        depression_col (str): Nome da coluna de depressão
        stress_col (str): Nome da coluna de estresse
        mood_col (str): Nome da coluna de humor
        date_col (str): Nome da coluna de data
    
    Returns:
        DataFrame: DataFrame com métricas psicológicas
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Cria uma cópia para não modificar o original
    df_copy = df.copy()
    
    # Calcula o score DASS total (0-100)
    df_copy['dass_score'] = df_copy.apply(
        lambda row: 100 - ((row[anxiety_col] + row[depression_col] + row[stress_col]) / 3 * 100 / 3),
        axis=1
    )
    
    # Calcula médias móveis para tendências
    df_copy['anxiety_ma7'] = df_copy[anxiety_col].rolling(window=7, min_periods=1).mean()
    df_copy['depression_ma7'] = df_copy[depression_col].rolling(window=7, min_periods=1).mean()
    df_copy['stress_ma7'] = df_copy[stress_col].rolling(window=7, min_periods=1).mean()
    df_copy['mood_ma7'] = df_copy[mood_col].rolling(window=7, min_periods=1).mean()
    df_copy['dass_score_ma7'] = df_copy['dass_score'].rolling(window=7, min_periods=1).mean()
    
    # Calcula variabilidade (desvio padrão móvel)
    df_copy['anxiety_std7'] = df_copy[anxiety_col].rolling(window=7, min_periods=2).std()
    df_copy['depression_std7'] = df_copy[depression_col].rolling(window=7, min_periods=2).std()
    df_copy['stress_std7'] = df_copy[stress_col].rolling(window=7, min_periods=2).std()
    df_copy['mood_std7'] = df_copy[mood_col].rolling(window=7, min_periods=2).std()
    
    return df_copy

def calculate_correlation_between_modules(readiness_df, training_df, psychological_df, 
                                         readiness_date_col='date', training_date_col='date', 
                                         psychological_date_col='date'):
    """
    Calcula correlações entre métricas de diferentes módulos.
    
    Args:
        readiness_df (DataFrame): DataFrame com dados de prontidão
        training_df (DataFrame): DataFrame com dados de treino
        psychological_df (DataFrame): DataFrame com dados psicológicos
        readiness_date_col (str): Nome da coluna de data no DataFrame de prontidão
        training_date_col (str): Nome da coluna de data no DataFrame de treino
        psychological_date_col (str): Nome da coluna de data no DataFrame psicológico
    
    Returns:
        DataFrame: Matriz de correlação entre métricas de diferentes módulos
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(readiness_df[readiness_date_col]):
        readiness_df = readiness_df.copy()
        readiness_df[readiness_date_col] = pd.to_datetime(readiness_df[readiness_date_col])
    
    if not pd.api.types.is_datetime64_any_dtype(training_df[training_date_col]):
        training_df = training_df.copy()
        training_df[training_date_col] = pd.to_datetime(training_df[training_date_col])
    
    if not pd.api.types.is_datetime64_any_dtype(psychological_df[psychological_date_col]):
        psychological_df = psychological_df.copy()
        psychological_df[psychological_date_col] = pd.to_datetime(psychological_df[psychological_date_col])
    
    # Extrai a data (sem hora)
    readiness_df['date_only'] = readiness_df[readiness_date_col].dt.date
    training_df['date_only'] = training_df[training_date_col].dt.date
    psychological_df['date_only'] = psychological_df[psychological_date_col].dt.date
    
    # Seleciona colunas relevantes
    readiness_cols = ['score', 'sleep_quality', 'stress', 'fatigue', 'muscle_soreness', 'energy', 'motivation']
    training_cols = ['trimp', 'tss', 'ctl', 'atl', 'tsb', 'monotony', 'strain']
    psychological_cols = ['dass_score', 'dass_anxiety', 'dass_depression', 'dass_stress', 'mood']
    
    # Filtra colunas disponíveis
    readiness_cols = [col for col in readiness_cols if col in readiness_df.columns]
    training_cols = [col for col in training_cols if col in training_df.columns]
    psychological_cols = [col for col in psychological_cols if col in psychological_df.columns]
    
    # Prepara DataFrames para merge
    readiness_selected = readiness_df[['date_only'] + readiness_cols].copy()
    readiness_selected = readiness_selected.add_prefix('readiness_')
    readiness_selected = readiness_selected.rename(columns={'readiness_date_only': 'date_only'})
    
    training_selected = training_df[['date_only'] + training_cols].copy()
    training_selected = training_selected.add_prefix('training_')
    training_selected = training_selected.rename(columns={'training_date_only': 'date_only'})
    
    psychological_selected = psychological_df[['date_only'] + psychological_cols].copy()
    psychological_selected = psychological_selected.add_prefix('psych_')
    psychological_selected = psychological_selected.rename(columns={'psych_date_only': 'date_only'})
    
    # Merge dos DataFrames
    merged = readiness_selected.merge(training_selected, on='date_only', how='outer')
    merged = merged.merge(psychological_selected, on='date_only', how='outer')
    
    # Calcula matriz de correlação
    corr_matrix = merged.drop(columns=['date_only']).corr()
    
    return corr_matrix

def identify_best_worst_days(df, metric_col, date_col='date', higher_is_better=True):
    """
    Identifica os melhores e piores dias com base em uma métrica.
    
    Args:
        df (DataFrame): DataFrame com os dados
        metric_col (str): Nome da coluna da métrica
        date_col (str): Nome da coluna de data
        higher_is_better (bool): Se valores mais altos são melhores
    
    Returns:
        dict: Dicionário com melhores e piores dias
    """
    # Converte para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Cria uma cópia para não modificar o original
    df_copy = df.copy()
    
    # Extrai o dia da semana
    df_copy['day_of_week'] = df_copy[date_col].dt.dayofweek
    
    # Mapeia números para nomes dos dias
    day_names = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    # Agrupa por dia da semana e calcula média
    day_stats = df_copy.groupby('day_of_week')[metric_col].mean().reset_index()
    
    # Adiciona nomes dos dias
    day_stats['day_name'] = day_stats['day_of_week'].map(day_names)
    
    # Ordena por métrica
    if higher_is_better:
        day_stats = day_stats.sort_values(metric_col, ascending=False)
    else:
        day_stats = day_stats.sort_values(metric_col, ascending=True)
    
    # Identifica os melhores e piores dias
    best_days = day_stats.head(3)
    worst_days = day_stats.tail(3)
    
    return {
        "best_days": best_days,
        "worst_days": worst_days
    }

def generate_insights(readiness_df, training_df, psychological_df):
    """
    Gera insights automáticos com base nos dados.
    
    Args:
        readiness_df (DataFrame): DataFrame com dados de prontidão
        training_df (DataFrame): DataFrame com dados de treino
        psychological_df (DataFrame): DataFrame com dados psicológicos
    
    Returns:
        list: Lista de insights
    """
    insights = []
    
    # Verifica se há dados suficientes
    if len(readiness_df) < 7 and len(training_df) < 7 and len(psychological_df) < 7:
        insights.append("Dados insuficientes para gerar insights. Continue registrando seus dados diariamente.")
        return insights
    
    # Insights de prontidão
    if len(readiness_df) >= 7:
        # Tendência de prontidão
        if 'score' in readiness_df.columns:
            recent_scores = readiness_df['score'].tail(7)
            trend = calculate_linear_trend(np.arange(len(recent_scores)), recent_scores)
            
            if trend['slope'] > 0.5:
                insights.append("Sua prontidão está melhorando significativamente nas últimas semanas.")
            elif trend['slope'] < -0.5:
                insights.append("Sua prontidão está diminuindo nas últimas semanas. Considere ajustar sua rotina.")
            
            # Componentes mais fracos
            if len(readiness_df) >= 3:
                components = ['sleep_quality', 'stress', 'fatigue', 'muscle_soreness', 'energy', 'motivation']
                available_components = [c for c in components if c in readiness_df.columns]
                
                if available_components:
                    recent_data = readiness_df[available_components].tail(3)
                    mean_values = recent_data.mean()
                    
                    # Para componentes onde valores menores são melhores
                    invert_components = ['stress', 'fatigue', 'muscle_soreness']
                    for component in invert_components:
                        if component in mean_values.index:
                            mean_values[component] = 6 - mean_values[component]
                    
                    weakest = mean_values.idxmin()
                    
                    component_names = {
                        'sleep_quality': 'qualidade do sono',
                        'stress': 'nível de estresse',
                        'fatigue': 'fadiga',
                        'muscle_soreness': 'dor muscular',
                        'energy': 'energia',
                        'motivation': 'motivação'
                    }
                    
                    insights.append(f"Seu componente mais fraco recentemente é {component_names.get(weakest, weakest)}. Foque em melhorar este aspecto.")
    
    # Insights de treino
    if len(training_df) >= 7:
        # Carga de treino
        if 'tss' in training_df.columns and 'ctl' in training_df.columns and 'atl' in training_df.columns:
            recent_tsb = training_df['ctl'].tail(1).values[0] - training_df['atl'].tail(1).values[0]
            
            if recent_tsb < -20:
                insights.append("Sua carga de treino aguda está muito alta em relação à crônica. Considere um período de recuperação.")
            elif recent_tsb > 10:
                insights.append("Você está bem recuperado e pronto para treinos mais intensos.")
            
            # Monotonia
            if 'monotony' in training_df.columns:
                recent_monotony = training_df['monotony'].tail(1).values[0]
                
                if not np.isnan(recent_monotony) and recent_monotony > 1.5:
                    insights.append("Sua monotonia de treino está alta. Tente variar mais seus treinos em intensidade e volume.")
    
    # Insights psicológicos
    if len(psychological_df) >= 7:
        # Estado psicológico
        psych_components = ['dass_anxiety', 'dass_depression', 'dass_stress']
        available_components = [c for c in psych_components if c in psychological_df.columns]
        
        if available_components:
            recent_data = psychological_df[available_components].tail(3)
            mean_values = recent_data.mean()
            
            highest = mean_values.idxmax()
            
            component_names = {
                'dass_anxiety': 'ansiedade',
                'dass_depression': 'depressão',
                'dass_stress': 'estresse'
            }
            
            if mean_values[highest] > 1.5:  # Valor moderado ou alto
                insights.append(f"Seu nível de {component_names.get(highest, highest)} está elevado. Considere técnicas de relaxamento ou consulte um profissional.")
    
    # Correlações entre módulos
    if len(readiness_df) >= 10 and len(training_df) >= 10:
        # Prepara dados para correlação
        readiness_df['date_only'] = pd.to_datetime(readiness_df['date']).dt.date
        training_df['date_only'] = pd.to_datetime(training_df['date']).dt.date
        
        # Merge dos DataFrames
        merged = pd.merge(
            readiness_df[['date_only', 'score']],
            training_df[['date_only', 'trimp']],
            on='date_only',
            how='inner'
        )
        
        if len(merged) >= 5:
            # Calcula correlação entre prontidão e TRIMP do dia anterior
            merged['trimp_next_day'] = merged['trimp'].shift(-1)
            corr = merged['score'].corr(merged['trimp_next_day'])
            
            if not np.isnan(corr):
                if corr > 0.4:
                    insights.append("Sua prontidão tem forte correlação positiva com o desempenho no treino do dia seguinte.")
                elif corr < -0.4:
                    insights.append("Dias com baixa prontidão tendem a preceder treinos menos intensos. Considere ajustar seu planejamento.")
    
    # Se não houver insights específicos
    if not insights:
        insights.append("Continue registrando seus dados diariamente para obter insights mais precisos.")
    
    return insights
