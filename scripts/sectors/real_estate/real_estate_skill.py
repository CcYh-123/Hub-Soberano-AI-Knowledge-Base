"""
-----------------------------------------------------------------------
SCRIPT: real_estate_skill.py
DIRECTIVA: D014_SectorEspecializacion
ROL: Especialista en Análisis de Activos Inmobiliarios
-----------------------------------------------------------------------
"""
from pathlib import Path

class RealEstateSkill:
    def __init__(self):
        self.opportunity_threshold = 1500 # Precio/m2

    def process_properties(self, properties):
        """
        Aplica reglas de negocio específicas al sector inmobiliario.
        """
        for prop in properties:
            # Calcular métricas base si no existen
            precio = prop.get('precio', 0)
            m2 = prop.get('m2', 1)
            precio_m2 = precio / m2
            prop['precio_m2'] = round(precio_m2, 2)
            
            # Regla de Oro: Inversión por debajo de mercado
            if precio_m2 < self.opportunity_threshold:
                prop['tag'] = 'OPORTUNIDAD DE INVERSIÓN'
                prop['intelligence_note'] = f"Precio m2 (${precio_m2}) inferior a umbral estratégico (${self.opportunity_threshold})"
            
            # Regla Geográfica (Zonas Premium con Descuento)
            zona = prop.get('zona', '').lower()
            if zona in ['palermo', 'recoleta'] and precio_m2 < 2000:
                 prop['tag'] = 'OPORTUNIDAD PREMIUM'
                 prop['intelligence_note'] = "Zona de alta plusvalía a precio de oportunidad"
                 
        return properties
