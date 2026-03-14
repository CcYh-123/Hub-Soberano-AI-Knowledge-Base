import math

def calculate_replacement_value(costo_original: float, dias_en_stock: int, tasa_inflacion_diaria: float) -> float:
    """
    Calcula el Valor de Reposición Real usando la fórmula de capitalización continua: V = C * e^(r*t)
    V: Valor proyectado
    C: Costo original
    r: Tasa de inflación diaria
    t: Días en stock
    """
    if dias_en_stock <= 0:
        return costo_original
    
    # Fórmula: C * e^(r * t)
    replacement_value = costo_original * math.exp(tasa_inflacion_diaria * dias_en_stock)
    return round(replacement_value, 2)

def calculate_capital_gap(valor_historico: float, valor_mercado_actual: float) -> float:
    """
    Calcula la brecha de capital entre lo pagado y el costo actual de reposición.
    """
    return round(valor_mercado_actual - valor_historico, 2)
