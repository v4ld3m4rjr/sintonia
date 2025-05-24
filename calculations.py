"""
Módulo de cálculos para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo contém funções matemáticas e algoritmos para cálculos específicos do sistema.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats

# Cálculos de Prontidão

def calculate_readiness_score(sleep_quality, sleep_duration, stress, fatigue, 
                             muscle_soreness, energy, motivation, nutrition, hydration):
    """
    Calcula o score de prontidão (0-100) com base nos parâmetros fornecidos.
    
    Args:
        sleep_quality (int): Qualidade do sono (1-5)
        sleep_duration (float): Duração do sono em horas (4-10)
        stress (int): Nível de estresse (1-5, invertido)
        fatigue (int): Nível de fadiga (1-5, invertido)
        muscle_soreness (int): Nível de dor muscular (1-5, invertido)
        energy (int): Nível de energia (1-5)
        motivation (int): Nível de motivação (1-5)
        nutrition (int): Qualidade da nutrição (1-5)
        hydration (int): Nível de hidratação (1-5)
    
    Returns:
        int: Score de prontidão (0-100)
    """
    # Normaliza a duração do sono para escala 1-5
    sleep_duration_normalized = max(1, min(5, (sleep_duration - 4) / 1.5 + 1))
    
    # Inverte escalas onde valores menores são melhores
    stress_inverted = 6 - stress
    fatigue_inverted = 6 - fatigue
    muscle_soreness_inverted = 6 - muscle_soreness
    
    # Pesos para cada componente
    weights = {
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
    
    # Calcula o score ponderado
    weighted_score = (
        weights['sleep_quality'] * sleep_quality +
        weights['sleep_duration'] * sleep_duration_normalized +
        weights['stress'] * stress_inverted +
        weights['fatigue'] * fatigue_inverted +
        weights['muscle_soreness'] * muscle_soreness_inverted +
        weights['energy'] * energy +
        weights['motivation'] * motivation +
        weights['nutrition'] * nutrition +
        weights['hydration'] * hydration
    )
    
    # Converte para escala 0-100
    readiness_score = (weighted_score - 1) * 25
    
    # Arredonda para inteiro
    return round(readiness_score)

def calculate_volume_reduction(readiness_score):
    """
    Calcula a redução recomendada de volume de treino com base no score de prontidão.
    
    Args:
        readiness_score (int): Score de prontidão (0-100)
    
    Returns:
        dict: Dicionário com percentual de redução e recomendações
    """
    # Fórmula para calcular a redução de volume
    # Um score de 100 não requer redução (0%)
    # Um score de 50 sugere redução de 40% no volume
    # Um score de 0 sugere redução de 80% no volume
    
    reduction_pct = max(0, min(80, 80 - (readiness_score * 0.8)))
    
    # Determina a zona de redução
    if reduction_pct < 10:
        zone = "Mínima"
        color = "#4CAF50"  # Verde
        description = "Redução mínima de volume necessária"
        recommendation = "Prossiga com o treino planejado normalmente"
    elif reduction_pct < 25:
        zone = "Leve"
        color = "#8BC34A"  # Verde claro
        description = "Redução leve de volume recomendada"
        recommendation = "Reduza ligeiramente o volume (principalmente séries extras)"
    elif reduction_pct < 40:
        zone = "Moderada"
        color = "#FFC107"  # Amarelo
        description = "Redução moderada de volume recomendada"
        recommendation = "Reduza o volume em aproximadamente um terço"
    elif reduction_pct < 60:
        zone = "Significativa"
        color = "#FF9800"  # Laranja
        description = "Redução significativa de volume recomendada"
        recommendation = "Reduza o volume pela metade e diminua a intensidade"
    else:
        zone = "Severa"
        color = "#F44336"  # Vermelho
        description = "Redução severa de volume recomendada"
        recommendation = "Considere um treino muito leve ou um dia de recuperação ativa"
    
    return {
        "reduction_pct": round(reduction_pct),
        "zone": zone,
        "color": color,
        "description": description,
        "recommendation": recommendation
    }

# Cálculos de Treino

def calculate_trimp(duration, rpe):
    """
    Calcula o TRIMP (Training Impulse) com base na duração e RPE.
    
    Args:
        duration (int): Duração do treino em minutos
        rpe (int): Percepção de esforço na escala de Borg adaptada (0-10)
    
    Returns:
        int: Valor do TRIMP
    """
    # Fórmula simplificada: TRIMP = duração (min) × RPE
    trimp = duration * rpe
    
    return round(trimp)

def calculate_tss_from_rpe(duration, rpe):
    """
    Calcula o TSS (Training Stress Score) com base na duração e RPE.
    
    Args:
        duration (int): Duração do treino em minutos
        rpe (int): Percepção de esforço na escala de Borg adaptada (0-10)
    
    Returns:
        int: Valor do TSS
    """
    # Converte RPE (0-10) para fator de intensidade (IF)
    intensity_factor = rpe / 10
    
    # Fórmula do TSS: (duração em segundos × IF² × 100) ÷ 3600
    tss = (duration * 60 * intensity_factor**2 * 100) / 3600
    
    return round(tss)

def calculate_ctl(tss_series, time_constant=42):
    """
    Calcula o CTL (Chronic Training Load) com base na série de TSS.
    
    Args:
        tss_series (array): Série temporal de valores de TSS
        time_constant (int): Constante de tempo em dias (padrão: 42)
    
    Returns:
        array: Série de valores de CTL
    """
    # Usa média móvel exponencial com constante de tempo especificada
    alpha = 1 / time_constant
    ctl = pd.Series(tss_series).ewm(alpha=alpha, adjust=False).mean().values
    
    return ctl

def calculate_atl(tss_series, time_constant=7):
    """
    Calcula o ATL (Acute Training Load) com base na série de TSS.
    
    Args:
        tss_series (array): Série temporal de valores de TSS
        time_constant (int): Constante de tempo em dias (padrão: 7)
    
    Returns:
        array: Série de valores de ATL
    """
    # Usa média móvel exponencial com constante de tempo especificada
    alpha = 1 / time_constant
    atl = pd.Series(tss_series).ewm(alpha=alpha, adjust=False).mean().values
    
    return atl

def calculate_tsb(ctl, atl):
    """
    Calcula o TSB (Training Stress Balance) com base no CTL e ATL.
    
    Args:
        ctl (array): Série de valores de CTL
        atl (array): Série de valores de ATL
    
    Returns:
        array: Série de valores de TSB
    """
    # TSB = CTL - ATL
    tsb = ctl - atl
    
    return tsb

def calculate_monotony(tss_series, window=7):
    """
    Calcula a monotonia de treino para uma janela de dias.
    
    Args:
        tss_series (array): Série temporal de valores de TSS
        window (int): Tamanho da janela em dias (padrão: 7)
    
    Returns:
        float: Valor da monotonia
    """
    # Obtém a janela de dados
    if len(tss_series) < window:
        return 0
    
    window_data = tss_series[-window:]
    
    # Monotonia = média diária / desvio padrão
    mean_load = np.mean(window_data)
    std_load = np.std(window_data)
    
    # Evita divisão por zero
    if std_load == 0:
        return 0
    
    monotony = mean_load / std_load
    
    return monotony

def calculate_strain(tss_series, window=7):
    """
    Calcula o strain de treino para uma janela de dias.
    
    Args:
        tss_series (array): Série temporal de valores de TSS
        window (int): Tamanho da janela em dias (padrão: 7)
    
    Returns:
        float: Valor do strain
    """
    # Obtém a janela de dados
    if len(tss_series) < window:
        return 0
    
    window_data = tss_series[-window:]
    
    # Strain = carga semanal × monotonia
    weekly_load = np.sum(window_data)
    monotony = calculate_monotony(tss_series, window)
    
    strain = weekly_load * monotony
    
    return strain

def calculate_readiness_from_tsb(tsb):
    """
    Calcula o score de prontidão (0-100) com base no TSB.
    
    Args:
        tsb (float): Valor do TSB (Training Stress Balance)
    
    Returns:
        int: Score de prontidão (0-100)
    """
    # Converte TSB para escala 0-100
    # TSB de -30 ou menor corresponde a 0
    # TSB de +10 ou maior corresponde a 100
    # Valores intermediários são interpolados linearmente
    
    normalized_tsb = max(-30, min(10, tsb))
    readiness_score = (normalized_tsb + 30) * (100 / 40)
    
    return round(readiness_score)

# Cálculos Psicológicos

def calculate_dass_score(anxiety, depression, stress):
    """
    Calcula o score DASS total (0-100).
    
    Args:
        anxiety (int): Nível de ansiedade (0-3)
        depression (int): Nível de depressão (0-3)
        stress (int): Nível de estresse (0-3)
    
    Returns:
        int: Score DASS total (0-100)
    """
    # Calcula a média dos três componentes (0-3)
    mean_score = (anxiety + depression + stress) / 3
    
    # Converte para escala 0-100 (invertida, pois valores mais baixos são melhores)
    dass_score = 100 - (mean_score * 100 / 3)
    
    # Arredonda para inteiro
    return round(dass_score)

# Cálculos Estatísticos

def calculate_correlation(x, y):
    """
    Calcula o coeficiente de correlação de Pearson entre duas séries.
    
    Args:
        x (array): Primeira série de dados
        y (array): Segunda série de dados
    
    Returns:
        float: Coeficiente de correlação (-1 a 1)
    """
    # Remove valores ausentes
    mask = ~np.isnan(x) & ~np.isnan(y)
    x_clean = np.array(x)[mask]
    y_clean = np.array(y)[mask]
    
    # Verifica se há dados suficientes
    if len(x_clean) < 2:
        return None
    
    # Calcula correlação
    correlation, p_value = stats.pearsonr(x_clean, y_clean)
    
    return correlation

def calculate_trend(y, x=None):
    """
    Calcula a tendência linear de uma série temporal.
    
    Args:
        y (array): Série de valores
        x (array, optional): Série de valores para o eixo x (padrão: índices sequenciais)
    
    Returns:
        dict: Dicionário com coeficientes e estatísticas da tendência
    """
    # Remove valores ausentes
    y_clean = np.array(y)[~np.isnan(y)]
    
    # Verifica se há dados suficientes
    if len(y_clean) < 2:
        return {
            "slope": 0,
            "intercept": 0,
            "r_value": 0,
            "p_value": 1,
            "std_err": 0
        }
    
    # Cria eixo x se não fornecido
    if x is None:
        x = np.arange(len(y_clean))
    else:
        x = np.array(x)[~np.isnan(y)]
    
    # Calcula regressão linear
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y_clean)
    
    return {
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "p_value": p_value,
        "std_err": std_err
    }

def calculate_z_score(value, mean, std):
    """
    Calcula o z-score de um valor em relação a uma distribuição.
    
    Args:
        value (float): Valor a ser normalizado
        mean (float): Média da distribuição
        std (float): Desvio padrão da distribuição
    
    Returns:
        float: Z-score
    """
    # Evita divisão por zero
    if std == 0:
        return 0
    
    z_score = (value - mean) / std
    
    return z_score

def calculate_percentile(value, data):
    """
    Calcula o percentil de um valor em relação a um conjunto de dados.
    
    Args:
        value (float): Valor a ser avaliado
        data (array): Conjunto de dados
    
    Returns:
        float: Percentil (0-100)
    """
    # Remove valores ausentes
    data_clean = np.array(data)[~np.isnan(data)]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 1:
        return 50
    
    percentile = stats.percentileofscore(data_clean, value)
    
    return percentile

# Funções de Normalização e Transformação

def normalize_to_range(value, old_min, old_max, new_min=0, new_max=100):
    """
    Normaliza um valor de um intervalo para outro.
    
    Args:
        value (float): Valor a ser normalizado
        old_min (float): Valor mínimo do intervalo original
        old_max (float): Valor máximo do intervalo original
        new_min (float): Valor mínimo do novo intervalo (padrão: 0)
        new_max (float): Valor máximo do novo intervalo (padrão: 100)
    
    Returns:
        float: Valor normalizado
    """
    # Evita divisão por zero
    if old_max == old_min:
        return (new_max + new_min) / 2
    
    # Normaliza o valor
    normalized = (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
    
    # Limita ao intervalo
    normalized = max(new_min, min(new_max, normalized))
    
    return normalized

def smooth_data(data, window_size=3, method='moving_average'):
    """
    Suaviza uma série temporal usando diferentes métodos.
    
    Args:
        data (array): Série de dados a ser suavizada
        window_size (int): Tamanho da janela de suavização (padrão: 3)
        method (str): Método de suavização ('moving_average', 'exponential', 'gaussian')
    
    Returns:
        array: Série suavizada
    """
    # Converte para array numpy
    data_array = np.array(data)
    
    # Remove valores ausentes
    mask = ~np.isnan(data_array)
    data_clean = data_array[mask]
    
    # Verifica se há dados suficientes
    if len(data_clean) < window_size:
        return data_array
    
    # Aplica o método de suavização
    if method == 'moving_average':
        # Média móvel simples
        smoothed = np.convolve(data_clean, np.ones(window_size)/window_size, mode='same')
    elif method == 'exponential':
        # Média móvel exponencial
        alpha = 2 / (window_size + 1)
        smoothed = pd.Series(data_clean).ewm(alpha=alpha, adjust=False).mean().values
    elif method == 'gaussian':
        # Filtro gaussiano
        from scipy.ndimage import gaussian_filter1d
        smoothed = gaussian_filter1d(data_clean, sigma=window_size/3)
    else:
        # Método não reconhecido, retorna dados originais
        return data_array
    
    # Reconstrói o array com valores ausentes
    result = data_array.copy()
    result[mask] = smoothed
    
    return result

# Funções de Análise de Séries Temporais

def detect_outliers(data, threshold=2.0, method='z_score'):
    """
    Detecta outliers em uma série de dados.
    
    Args:
        data (array): Série de dados
        threshold (float): Limiar para detecção (padrão: 2.0)
        method (str): Método de detecção ('z_score', 'iqr')
    
    Returns:
        array: Máscara booleana indicando outliers
    """
    # Remove valores ausentes
    data_array = np.array(data)
    mask = ~np.isnan(data_array)
    data_clean = data_array[mask]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 4:
        return np.zeros_like(data_array, dtype=bool)
    
    # Detecta outliers
    if method == 'z_score':
        # Método do z-score
        z_scores = np.abs((data_clean - np.mean(data_clean)) / np.std(data_clean))
        outliers_mask = z_scores > threshold
    elif method == 'iqr':
        # Método do intervalo interquartil
        q1 = np.percentile(data_clean, 25)
        q3 = np.percentile(data_clean, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        outliers_mask = (data_clean < lower_bound) | (data_clean > upper_bound)
    else:
        # Método não reconhecido, não detecta outliers
        outliers_mask = np.zeros_like(data_clean, dtype=bool)
    
    # Reconstrói a máscara com valores ausentes
    result = np.zeros_like(data_array, dtype=bool)
    result[mask] = outliers_mask
    
    return result

def find_peaks(data, prominence=1.0, width=None, distance=None):
    """
    Encontra picos em uma série de dados.
    
    Args:
        data (array): Série de dados
        prominence (float): Proeminência mínima dos picos (padrão: 1.0)
        width (int): Largura mínima dos picos (padrão: None)
        distance (int): Distância mínima entre picos (padrão: None)
    
    Returns:
        array: Índices dos picos
    """
    from scipy.signal import find_peaks as scipy_find_peaks
    
    # Remove valores ausentes
    data_array = np.array(data)
    mask = ~np.isnan(data_array)
    data_clean = data_array[mask]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 3:
        return np.array([])
    
    # Encontra picos
    peaks, _ = scipy_find_peaks(data_clean, prominence=prominence, width=width, distance=distance)
    
    return peaks

def calculate_moving_stats(data, window_size=7):
    """
    Calcula estatísticas móveis para uma série temporal.
    
    Args:
        data (array): Série de dados
        window_size (int): Tamanho da janela (padrão: 7)
    
    Returns:
        dict: Dicionário com séries de estatísticas móveis
    """
    # Converte para Series do pandas
    series = pd.Series(data)
    
    # Calcula estatísticas móveis
    rolling = series.rolling(window=window_size, min_periods=1)
    
    return {
        "mean": rolling.mean().values,
        "std": rolling.std().values,
        "min": rolling.min().values,
        "max": rolling.max().values,
        "median": rolling.median().values
    }

# Funções de Análise de Distribuição

def analyze_distribution(data):
    """
    Analisa a distribuição de um conjunto de dados.
    
    Args:
        data (array): Conjunto de dados
    
    Returns:
        dict: Dicionário com estatísticas da distribuição
    """
    # Remove valores ausentes
    data_clean = np.array(data)[~np.isnan(data)]
    
    # Verifica se há dados suficientes
    if len(data_clean) < 2:
        return {
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "skewness": np.nan,
            "kurtosis": np.nan,
            "normality_test": {
                "statistic": np.nan,
                "p_value": np.nan,
                "normal": False
            }
        }
    
    # Calcula estatísticas básicas
    mean = np.mean(data_clean)
    median = np.median(data_clean)
    std = np.std(data_clean)
    skewness = stats.skew(data_clean)
    kurtosis = stats.kurtosis(data_clean)
    
    # Teste de normalidade (Shapiro-Wilk)
    if len(data_clean) >= 3 and len(data_clean) <= 5000:
        normality_test = stats.shapiro(data_clean)
        is_normal = normality_test[1] > 0.05
    else:
        normality_test = (np.nan, np.nan)
        is_normal = False
    
    return {
        "mean": mean,
        "median": median,
        "std": std,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "normality_test": {
            "statistic": normality_test[0],
            "p_value": normality_test[1],
            "normal": is_normal
        }
    }

# Funções de Análise de Correlação

def correlation_matrix(data_dict):
    """
    Calcula a matriz de correlação entre múltiplas séries.
    
    Args:
        data_dict (dict): Dicionário com séries de dados
    
    Returns:
        DataFrame: Matriz de correlação
    """
    # Cria DataFrame
    df = pd.DataFrame(data_dict)
    
    # Calcula matriz de correlação
    corr_matrix = df.corr(method='pearson')
    
    return corr_matrix

def partial_correlation(x, y, z):
    """
    Calcula a correlação parcial entre x e y, controlando para z.
    
    Args:
        x (array): Primeira série de dados
        y (array): Segunda série de dados
        z (array): Variável de controle
    
    Returns:
        float: Coeficiente de correlação parcial
    """
    # Remove valores ausentes
    mask = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(z)
    x_clean = np.array(x)[mask]
    y_clean = np.array(y)[mask]
    z_clean = np.array(z)[mask]
    
    # Verifica se há dados suficientes
    if len(x_clean) < 3:
        return None
    
    # Calcula correlações
    r_xy = stats.pearsonr(x_clean, y_clean)[0]
    r_xz = stats.pearsonr(x_clean, z_clean)[0]
    r_yz = stats.pearsonr(y_clean, z_clean)[0]
    
    # Calcula correlação parcial
    numerator = r_xy - r_xz * r_yz
    denominator = np.sqrt((1 - r_xz**2) * (1 - r_yz**2))
    
    # Evita divisão por zero
    if denominator == 0:
        return 0
    
    partial_corr = numerator / denominator
    
    return partial_corr
