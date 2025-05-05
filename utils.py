# Funções utilitárias para o app de avaliação de prontidão

def calculate_score(sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao):
    # Calcula o score total de prontidão baseado nos 8 parâmetros.
    # Cada parâmetro é avaliado de 1 a 5, resultando em um score máximo de 40.
    return sono + fadiga + dor + estresse + vigor + tensao + apetite + prontidao

def ajuste_carga(score_total):
    # Calcula o ajuste percentual da carga de treino baseado no score total.
    # Usa uma regressão linear entre 50% e 100% da carga.
    score_percentual = (score_total / 40) * 100

    if score_percentual >= 90:
        return 100  # Carga total
    elif score_percentual <= 50:
        return 50   # Carga mínima
    else:
        # Regressão linear entre 50% e 100%
        return score_percentual
