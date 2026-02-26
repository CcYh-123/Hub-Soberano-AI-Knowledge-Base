"""
-----------------------------------------------------------------------
SCRIPT: pharmacy_skill.py
DIRECTIVA: D014_SectorEspecializacion
ROL: Especialista en Análisis de Patentes y Medicamentos
-----------------------------------------------------------------------
"""

class PharmacySkill:
    def __init__(self):
        self.opportunity_threshold = 20.0 # Umbral de precio bajo para medicamentos clave

    def process_products(self, products):
        """
        Aplica reglas de negocio específicas al sector farmacéutico.
        """
        for prod in products:
            precio = prod.get('precio', 0)
            
            # Regla de Oro: Medicamentos de alta demanda bajo umbral
            if precio < self.opportunity_threshold:
                prod['tag'] = 'OFERTA PATENTE'
                prod['intelligence_note'] = f"Precio (${precio}) inferior a la media de mercado (${self.opportunity_threshold})"
            
            # Regla de Demanda (Productos estacionales o virales)
            vistas = prod.get('vistas_24h', 0)
            if vistas > 1000 and precio < 50:
                 prod['tag'] = 'ALTA DEMANDA'
                 prod['intelligence_note'] = "Súper ventas en las últimas 24hs"
                 
        return products
