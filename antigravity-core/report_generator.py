import os
from fpdf import FPDF
from datetime import datetime
from typing import List, Dict, Any

class AntigravityReport(FPDF):
    def header(self):
        # Logo o Texto de Marca
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(41, 128, 185) # Azul Antigravity
        self.cell(0, 10, "ANTIGRAVITY: SHIELD REPORT v2026", ln=True, align="L")
        self.set_draw_color(41, 128, 185)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 10, f"Page {self.page_no()} | CONFIDENCIAL - PROPERTY OF TENANT", align="C")

def generate_audit_report(tenant_id: str, audit_data: Dict[str, Any], critical_products: List[Dict[str, Any]]) -> str:
    """
    Genera un PDF profesional con el resumen de la auditoría.
    Retorna el path del archivo generado.
    """
    pdf = AntigravityReport()
    pdf.add_page()
    
    # Título y Info General
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0)
    pdf.cell(0, 15, f"AUDITORÍA DE CAPITAL: {tenant_id}", ln=True)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Fecha de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # Resumen Ejecutivo (Futurista / Alarma)
    pdf.set_fill_color(242, 242, 242)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, " [ RESUMEN EJECUTIVO ] ", ln=True, fill=True)
    pdf.ln(2)
    
    health_score = audit_data.get("inventory_health_score", 0)
    capital_leak = audit_data.get("capital_leak", 0)
    
    # Color según score
    if health_score < 50:
        pdf.set_text_color(192, 57, 43) # ROJO Alerta
    else:
        pdf.set_text_color(41, 128, 185)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(95, 10, f"Health Score: {health_score}/100", border=1, align="C")
    pdf.cell(95, 10, f"Capital Leak: ${capital_leak:,.2f}", border=1, ln=True, align="C")
    
    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.multi_cell(0, 6, f"Se ha detectado una brecha de capital de ${capital_leak:,.2f} debido a la inflación acumulada y la latencia de precios. "
                         f"Se sugiere un ajuste global de markup del {audit_data.get('suggested_global_markup', 0)}% para recuperar la rentabilidad.")
    
    pdf.ln(10)

    # Tabla de Productos Críticos
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "TOP 10 PRODUCTOS CRÍTICOS (MAYOR EROSIÓN)", ln=True)
    
    # Headers tabla
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255)
    pdf.cell(80, 8, "Producto (SKU)", border=1, fill=True)
    pdf.cell(35, 8, "Costo Viejo", border=1, fill=True, align="C")
    pdf.cell(35, 8, "Costo Nuevo", border=1, fill=True, align="C")
    pdf.cell(40, 8, "Perdida (Delta)", border=1, ln=True, fill=True, align="C")
    
    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "", 9)
    
    for prod in critical_products[:10]:
        pdf.cell(80, 8, str(prod.get("product_sku", "N/A")), border=1)
        pdf.cell(35, 8, f"${prod.get('costo_viejo', 0):.2f}", border=1, align="C")
        pdf.cell(35, 8, f"${prod.get('costo_nuevo', 0):.2f}", border=1, align="C")
        pdf.set_text_color(192, 57, 43)
        pdf.cell(40, 8, f"+ ${prod.get('delta_erosion', 0):.2f}", border=1, ln=True, align="C")
        pdf.set_text_color(0)

    # Salvar Reporte
    report_id = f"report_{tenant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    file_path = os.path.join("reports", report_id)
    pdf.output(file_path)
    
    return report_id
