
import sqlite3
import json
import math
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List
from core.config_loader import config

DB_PATH = Path("data/antigravity.db")

@dataclass
class ProductSnapshot:
    sku: str
    cost_price: float
    current_price: float
    days_in_inventory: int
    monthly_inflation_rate: float = field(default_factory=lambda: config.get("economy.monthly_inflation", 0.05))
    target_margin: float = field(default_factory=lambda: config.get("economy.target_margin", 0.25))
    competition_ceiling: float = None

class WealthModel:
    """
    Protected Margin con ajuste inflacionario compuesto (Wealth Engine V1.8).
    """

    def inflation_adjusted_cost(
        self, 
        base_cost: float, 
        days_in_inventory: int,
        monthly_rate: float
    ) -> float:
        """
        Costo ajustado por inflación durante el tiempo en stock.
        Formula: C_adj = C_base × e^(r × t)
        """
        months = max(0, days_in_inventory / 30)
        continuous_rate = math.log(1 + monthly_rate)
        return base_cost * math.exp(continuous_rate * months)

    def protected_price(self, product: ProductSnapshot) -> dict:
        """
        Precio mínimo que preserva el margen real post-inflación.
        """
        # 1. Costo real ajustado por días en inventario
        real_cost = self.inflation_adjusted_cost(
            product.cost_price,
            product.days_in_inventory,
            product.monthly_inflation_rate
        )

        # 2. Forward cost: proyección al próximo mes de reposición
        forward_cost = real_cost * (1 + product.monthly_inflation_rate)

        # 3. Precio protegido base (Margen 25%)
        # P_protected = C_forward / (1 - margin_target)
        protected = forward_cost / (1 - product.target_margin)

        # 4. Competitiveness cap (placeholder if ceiling not provided)
        final_price = protected
        if product.competition_ceiling:
             final_price = min(protected, product.competition_ceiling)
             # Nunca debajo del breakeven inflacionario
             breakeven = forward_cost * 1.05
             final_price = max(final_price, breakeven)

        # 5. Profit Gap
        profit_gap = final_price - product.current_price
        current_margin = (product.current_price - real_cost) / product.current_price if product.current_price > 0 else 0

        return {
            "sku": product.sku,
            "real_cost": round(real_cost, 2),
            "forward_cost": round(forward_cost, 2),
            "protected_price": round(protected, 2),
            "recommended_price": round(final_price, 2),
            "current_margin_pct": round(current_margin * 100, 2),
            "target_margin_pct": product.target_margin * 100,
            "profit_gap_unit": round(profit_gap, 2),
            "urgency_score": self._urgency_score(profit_gap, current_margin)
        }

    def _urgency_score(self, profit_gap: float, current_margin: float) -> str:
        if current_margin < 0.20 or profit_gap > 50:
            return "🔴 CRÍTICO"
        elif current_margin < 0.23:
            return "🟡 URGENTE"
        else:
            return "🟢 MONITOREAR"

def run_advanced_simulation():
    print("🛰️ ANTIGRAVITY WEALTH ENGINE — AUDITORÍA TÉCNICA V1.8")
    print("="*95)
    
    if not DB_PATH.exists():
        print("❌ Error: Base de datos no encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener últimos registros de farmacia
    cursor.execute("""
        SELECT item_key, price, timestamp, metadata_json 
        FROM historical_data 
        WHERE sector = 'pharmacy' 
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    
    if not rows:
        print("ℹ️ No hay datos de farmacia para analizar.")
        conn.close()
        return

    model = WealthModel()
    processed_skus = set()
    results = []

    now = datetime.now()

    for row in rows:
        sku = row['item_key']
        if sku in processed_skus: continue
        processed_skus.add(sku)
        
        price = row['price']
        ts_str = row['timestamp']
        
        # Parse metadata_json to ensure robustness as requested
        try:
            meta = json.loads(row['metadata_json']) if row['metadata_json'] else {}
        except Exception:
            meta = {}

        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except:
            ts = now
        
        days_in_stock = (now - ts).days + 1 # Min 1 day
        
        # Simulación de costo: Basado en el reporte de batalla del usuario
        # Diclofenac (17%), Amoxicilina (20%), Paracetamol (21%)
        # Si no es uno de esos, aplicamos un factor de costo base
        if "Diclofenac" in sku:
            cost_base = price / 1.17 # Margen ~ 17%
        elif "Amoxicilina" in sku:
            cost_base = price / 1.25 # Margen ~ 20%
        elif "Paracetamol" in sku:
            cost_base = price / 1.26 # Margen ~ 21%
        else:
            # Genérico: Costo = Precio / 1.35
            cost_base = price / 1.35

        snapshot = ProductSnapshot(
            sku=sku,
            cost_price=round(cost_base, 2),
            current_price=price,
            days_in_inventory=days_in_stock
        )
        
        analysis = model.protected_price(snapshot)
        results.append(analysis)

    # Imprimir Tabla Ejecutiva
    header = f"{'PRODUCTO':<28} | {'MARGEN %':<10} | {'P.SUGERIDO':<12} | {'GANANCIA PERDIDA':<18} | {'URGENCIA'}"
    print(header)
    print("-" * len(header))
    
    for r in sorted(results, key=lambda x: x['profit_gap_unit'], reverse=True):
        print(f"{r['sku']:<28} | {r['current_margin_pct']:>8}% | ${r['recommended_price']:<10} | ${r['profit_gap_unit']:<16} | {r['urgency_score']}")

    print("="*95)
    print(f"✅ Análisis completado. {len(results)} blancos identificados.")
    conn.close()

if __name__ == "__main__":
    run_advanced_simulation()
