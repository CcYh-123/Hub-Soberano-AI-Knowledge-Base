import json
from pathlib import Path
from datetime import datetime

# Configuración de Rutas
# fashion_skill.py está en /scripts/sectors/fashion/
# 1 parent -> /scripts/sectors/
# 2 parent -> /scripts/
# 3 parent -> /Proyecto_Antigravity/
ROOT_DIR = Path(__file__).parent.parent.parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"

class FashionSkill:
    """Skill especializado en el sector Retail / Moda."""
    
    def __init__(self):
        self.sector_name = "fashion"

    def process_products(self, raw_products):
        """
        Procesa productos de moda y calcula descuentos.
        """
        processed = []
        for item in raw_products:
            original = item.get('precio_original', 0)
            oferta = item.get('precio_oferta', 0)
            
            # Cálculo de descuento
            discount_pct = 0
            if original > 0:
                discount_pct = round(((original - oferta) / original) * 100)
            
            # Lógica de Oportunidad (D017)
            tag = "MERCADO"
            if discount_pct > 50:
                tag = "OPORTUNIDAD DE ORO"
            elif discount_pct > 20:
                tag = "OFERTA"
                
            processed.append({
                "prenda": item.get('prenda', 'N/A'),
                "marca": item.get('marca', 'generic'),
                "precio_original": original,
                "precio_oferta": oferta,
                "descuento_pct": f"{discount_pct}%",
                "tag": tag
            })
        return processed

    def generate_sample_data(self):
        """Genera datos simulados para el sector moda."""
        sample = {
            "status": "success",
            "sector": "fashion",
            "timestamp": datetime.now().isoformat(),
            "products": [
                {
                    "prenda": "Chaqueta de Cuero",
                    "marca": "Zara",
                    "precio_original": 120,
                    "precio_oferta": 45,
                    "tag": "OPORTUNIDAD DE ORO"
                },
                {
                    "prenda": "Zapatillas Urbanas",
                    "marca": "Nike",
                    "precio_original": 150,
                    "precio_oferta": 90,
                    "tag": "OFERTA"
                },
                {
                    "prenda": "Vestido de Seda",
                    "marca": "Gucci",
                    "precio_original": 850,
                    "precio_oferta": 350,
                    "tag": "OPORTUNIDAD DE ORO"
                },
                {
                    "prenda": "Pantalón Denim",
                    "marca": "Levi's",
                    "precio_original": 90,
                    "precio_oferta": 65,
                    "tag": "TEMPORADA"
                }
            ]
        }
        
        file_path = DATA_DIR / "fashion_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample, f, indent=2, ensure_ascii=False)
        return str(file_path)

def create_fashion_skill():
    return FashionSkill()

if __name__ == "__main__":
    skill = FashionSkill()
    path = skill.generate_sample_data()
    print(f"✅ Datos de moda generados en: {path}")
