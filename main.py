import sys
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QPushButton, QLabel, QFrame, QDialog,
                             QHeaderView, QAbstractItemView, QMessageBox,
                             QScrollArea, QSpinBox, QDoubleSpinBox, QFormLayout,
                             QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor
import time

# ── Constantes de Negocio ──
STOCK_MINIMO = 5  # Umbral de alerta de stock bajo

# ── Paleta de Colores Enterprise ──
COLOR_BG = "#F5F7FA"
COLOR_SIDEBAR = "#1A2634"
COLOR_HEADER = "#FFFFFF"
COLOR_TEXT = "#333333"
COLOR_TEXT_LIGHT = "#A0AEC0"
COLOR_ACCENT = "#2D3748"
COLOR_SUCCESS = "#48BB78"
COLOR_BORDER = "#E2E8F0"
COLOR_DANGER = "#E53E3E"
COLOR_WARNING_BG = "#FFF5F5"

class FarmaciaEnterprise(QMainWindow):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.init_supabase()
        self.init_ui()
        self.load_data()

    def init_supabase(self):
        try:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            self.supabase = create_client(url, key)
            self.connected = True
        except Exception as e:
            print(f"Error de conexión: {e}")
            self.connected = False

    def init_ui(self):
        self.setWindowTitle("Sistema de Gestión Universal - Inventario Inteligente")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', Arial;
            }}
            QMainWindow {{
                background-color: {COLOR_BG};
            }}
            QMessageBox {{
                background-color: {COLOR_BG};
                color: black;
            }}
            QMessageBox QPushButton, QInputDialog QPushButton {{
                background-color: #E2E8F0;
                color: black;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QSpinBox, QDoubleSpinBox, QComboBox {{
                color: black;
                background-color: white;
            }}
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── SIDEBAR ──
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background-color: {COLOR_SIDEBAR}; border: none;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)

        title_label = QLabel("SISTEMA\nUNIVERSAL")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        sidebar_layout.addWidget(title_label)

        sidebar_layout.addWidget(self.create_sidebar_button("Vista General", active=True))
        sidebar_layout.addWidget(self.create_sidebar_button("Inventario"))
        sidebar_layout.addWidget(self.create_sidebar_button("Ventas"))
        sidebar_layout.addWidget(self.create_sidebar_button("Reportes"))
        
        sidebar_layout.addStretch()

        self.conn_label = QLabel("● Sistema Online")
        conn_color = COLOR_SUCCESS if self.connected else "#F56565"
        self.conn_label.setStyleSheet(f"color: {conn_color}; font-weight: bold; font-size: 11px;")
        sidebar_layout.addWidget(self.conn_label)

        layout.addWidget(sidebar)

        # ── CONTENIDO PRINCIPAL ──
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Header
        header_container = QHBoxLayout()
        header_title = QLabel("Inventario General de Productos")
        header_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_title.setStyleSheet(f"color: {COLOR_ACCENT};")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar por nombre, rubro o unidad...")
        self.search_bar.setFixedWidth(400)
        self.search_bar.textChanged.connect(self.filter_data)
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: #FFFFFF;
                color: #1A2634;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_SIDEBAR};
            }}
        """)

        header_container.addWidget(header_title)
        header_container.addStretch()
        header_container.addWidget(self.search_bar)
        content_layout.addLayout(header_container)

        # Tabla y Panel de Acciones
        main_view_layout = QHBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nombre del Producto", "Unidad", "Precio Venta", "Costo", "Margen", "Stock"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                gridline-color: {COLOR_BORDER};
                alternate-background-color: #F9FAFB;
                selection-background-color: #CBD5E0;
                selection-color: {COLOR_SIDEBAR};
            }}
            QHeaderView::section {{
                background-color: #EDF2F7;
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLOR_BORDER};
                color: {COLOR_ACCENT};
                font-weight: bold;
                font-size: 13px;
                text-align: left;
            }}
            QTableWidget::item {{
                padding: 10px;
                color: {COLOR_TEXT};
                border-bottom: 1px solid {COLOR_BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: #CBD5E0;
                color: {COLOR_SIDEBAR};
                font-weight: bold;
            }}
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)

        main_view_layout.addWidget(self.table, stretch=4)

        # Panel de Acciones
        actions_panel = QFrame()
        actions_panel.setFixedWidth(200)
        actions_panel.setStyleSheet(f"background-color: white; border: 1px solid {COLOR_BORDER}; border-radius: 8px;")
        actions_layout = QVBoxLayout(actions_panel)
        actions_layout.setContentsMargins(15, 20, 15, 20)
        actions_layout.setSpacing(15)

        actions_title = QLabel("ACCIONES")
        actions_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        actions_title.setStyleSheet(f"color: {COLOR_TEXT_LIGHT};")
        actions_layout.addWidget(actions_title)

        self.btn_sell = self.create_action_button("Registrar Venta", "#3182CE")
        self.btn_sell.clicked.connect(self.action_vender)
        actions_layout.addWidget(self.btn_sell)

        self.btn_buy = self.create_action_button("Cargar Stock (Compra)", "#805AD5")
        self.btn_buy.clicked.connect(self.action_cargar_stock)
        actions_layout.addWidget(self.btn_buy)

        self.btn_price = self.create_action_button("Ajustar Precio", COLOR_ACCENT)
        self.btn_price.clicked.connect(self.action_ajustar_precio)
        actions_layout.addWidget(self.btn_price)

        self.btn_refresh = self.create_action_button("Sincronizar", "#718096")
        self.btn_refresh.clicked.connect(self.load_data)
        actions_layout.addWidget(self.btn_refresh)

        # Separador visual
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {COLOR_BORDER};")
        actions_layout.addWidget(separator)

        self.btn_resumen = self.create_action_button("Resumen del Dia", "#2F855A")
        self.btn_resumen.clicked.connect(self.action_resumen_dia)
        actions_layout.addWidget(self.btn_resumen)
        
        actions_layout.addStretch()

        # Indicador de stock bajo
        self.stock_alert_label = QLabel("")
        self.stock_alert_label.setWordWrap(True)
        self.stock_alert_label.setStyleSheet(f"color: {COLOR_DANGER}; font-size: 11px; font-weight: bold;")
        actions_layout.addWidget(self.stock_alert_label)

        main_view_layout.addWidget(actions_panel, stretch=1)
        content_layout.addLayout(main_view_layout)

        layout.addWidget(content_area)

        # StatusBar
        self.statusBar().setStyleSheet(f"background-color: white; color: {COLOR_ACCENT}; border-top: 1px solid {COLOR_BORDER};")
        self.statusBar().showMessage("Sistema listo.")

    def create_sidebar_button(self, text, active=False):
        btn = QPushButton(text)
        bg = "#2D3748" if active else "transparent"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #2D3748;
            }}
        """)
        return btn

    def create_action_button(self, text, color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {color}E0;
            }}
            QPushButton:pressed {{
                background-color: {color}C0;
            }}
        """)
        return btn

    def load_data(self):
        if not self.connected: return
        try:
            response = self.supabase.table("products").select("*").order("name").execute()
            self.all_data = response.data
            self.display_data(self.all_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar datos: {e}")

    def display_data(self, products):
        self.table.setRowCount(len(products))
        low_stock_count = 0

        for i, item in enumerate(products):
            price = float(item.get('price', 0))
            cost = float(item.get('cost_price', 0))
            margin = price - cost
            stock_value = item.get('stock', 0)
            is_low_stock = stock_value < STOCK_MINIMO

            # Nombre
            name_item = QTableWidgetItem(str(item.get("name")))
            self.table.setItem(i, 0, name_item)

            # Unidad
            unit_item = QTableWidgetItem(str(item.get("unit_type", "Unidades")))
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, unit_item)

            # Precio Venta
            price_item = QTableWidgetItem(f"$ {price:,.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 2, price_item)

            # Costo
            cost_item = QTableWidgetItem(f"$ {cost:,.2f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            cost_item.setForeground(QColor(COLOR_TEXT_LIGHT))
            self.table.setItem(i, 3, cost_item)

            # Margen
            margin_item = QTableWidgetItem(f"$ {margin:,.2f}")
            margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            margin_color = COLOR_SUCCESS if margin > 0 else COLOR_DANGER
            margin_item.setForeground(QColor(margin_color))
            margin_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(i, 4, margin_item)
            
            # Stock
            stock_item = QTableWidgetItem(f"{stock_value:,.3f}")
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 5, stock_item)

            # ── ALERTA DE STOCK BAJO: Resaltar toda la fila ──
            if is_low_stock:
                low_stock_count += 1
                for col in range(self.table.columnCount()):
                    cell = self.table.item(i, col)
                    if cell:
                        cell.setBackground(QColor(COLOR_WARNING_BG))
                        cell.setForeground(QColor(COLOR_DANGER))
                        cell.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        # Actualizar indicador de alertas en el panel lateral
        if low_stock_count > 0:
            self.stock_alert_label.setText(f"⚠ {low_stock_count} producto(s)\ncon stock bajo (<{STOCK_MINIMO})")
        else:
            self.stock_alert_label.setText("")

    def filter_data(self):
        text = self.search_bar.text().lower()
        if not hasattr(self, 'all_data'): return
        filtered = [x for x in self.all_data if text in x['name'].lower()]
        self.display_data(filtered)

    def action_vender(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto para vender.")
            return
        
        product_name = self.table.item(row, 0).text()
        current_product = next(x for x in self.all_data if x['name'] == product_name)
        unit = current_product.get('unit_type', 'Unidades')
        
        if current_product['stock'] <= 0:
            QMessageBox.critical(self, "Sin Stock", f"No hay {unit} disponibles.")
            return

        # Venta siempre con decimales, la BD lo soporta como FLOAT
        from PyQt6.QtWidgets import QInputDialog
        
        val, ok = QInputDialog.getDouble(self, "Registrar Venta", 
                                       f"Cantidad de {unit} a vender:", 1.0, 0.001, float(current_product['stock']), 3, step=0.001)
            
        if not ok: return
        sell_qty = float(str(val).replace(',', '.'))

        stock_actual = float(str(current_product['stock']).replace(',', '.'))
        precio_actual = float(str(current_product['price']).replace(',', '.'))
        costo_actual = float(str(current_product.get('cost_price', 0)).replace(',', '.'))

        new_stock = stock_actual - sell_qty
        sale_price = precio_actual * sell_qty
        cost_price = costo_actual * sell_qty

        try:
            # 1. Decrementar stock
            self.supabase.table("products").update({"stock": float(new_stock)}).eq("id", int(current_product['id'])).execute()
            
            # 2. Registrar en auditoría de ventas
            self.supabase.table("ventas_historial").insert({
                "product_id": int(current_product['id']),
                "product_name": product_name + f" ({sell_qty} {unit})",
                "sale_price": float(sale_price),
                "cost_price": float(cost_price)
            }).execute()
            
            # 3. Recargar y limpiar selección
            self.search_bar.setText("")
            self.load_data()
            self.table.clearSelection()
            self.table.setCurrentItem(None)
            
            profit = sale_price - cost_price
            self.statusBar().showMessage(
                f"✅ Venta: {product_name} | Ganancia: ${profit:,.2f} | Stock restante: {new_stock}", 4000
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo procesar la venta: {e}")

    def action_ajustar_precio(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto para ajustar.")
            return
        
        from PyQt6.QtWidgets import QInputDialog
        product_name = self.table.item(row, 0).text()
        current_product = next(x for x in self.all_data if x['name'] == product_name)
        
        new_price, ok = QInputDialog.getDouble(self, "Ajuste de Precio", 
                                                f"Nuevo precio para {product_name}:", 
                                                float(current_product['price']), 0, 1000000, 3, step=0.001)
        if ok:
            try:
                self.supabase.table("products").update({"price": float(new_price)}).eq("id", int(current_product['id'])).execute()
                self.search_bar.setText("")
                self.load_data()
                self.table.clearSelection()
                self.table.setCurrentItem(None)
                self.statusBar().showMessage(f"✅ Precio actualizado: {product_name} a ${new_price:,.2f}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar precio: {e}")

    def action_cargar_stock(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto para cargar stock.")
            return

        product_name = self.table.item(row, 0).text()
        current_product = next(x for x in self.all_data if x['name'] == product_name)
        
        # Diálogo de entrada
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Compra: {product_name}")
        dialog.setFixedWidth(400)
        layout = QFormLayout(dialog)
        
        unit_selector = QComboBox()
        unit_selector.addItems(["Unidades", "Packs", "Litros", "Kilos", "Metros", "Horas"])
        unit_selector.setCurrentText(current_product.get('unit_type', 'Unidades'))
        
        qty_input = QDoubleSpinBox()
        qty_input.setRange(0.001, 1000000)
        qty_input.setDecimals(3)
        qty_input.setSingleStep(0.001)
        qty_input.setValue(10)
        
        cost_input = QDoubleSpinBox()
        cost_input.setRange(0, 1000000)
        cost_input.setDecimals(3)
        cost_input.setSingleStep(0.001)
        cost_input.setPrefix("$ ")
        cost_input.setValue(float(current_product.get('cost_price', 0)))
        
        qty_label = QLabel(f"Cantidad de {unit_selector.currentText()}:")
        unit_selector.currentTextChanged.connect(lambda text: qty_label.setText(f"Cantidad de {text}:"))
        
        layout.addRow("Unidad de Medida:", unit_selector)
        layout.addRow(qty_label, qty_input)
        layout.addRow("Nuevo Precio de Costo:", cost_input)
        
        btn_confirm = QPushButton("Confirmar Ingreso")
        btn_confirm.setStyleSheet(f"background-color: #805AD5; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        
        def process_carga():
            try:
                # Casteo primitivo
                new_qty = float(str(qty_input.value()).replace(',', '.'))
                new_cost = float(str(cost_input.value()).replace(',', '.'))
                new_unit = unit_selector.currentText()
                
                stock_previo = float(str(current_product.get('stock', 0)).replace(',', '.'))
                total_stock = stock_previo + new_qty
                
                # 1. Actualizar BD ANTES del accept()
                self.supabase.table("products").update({
                    "stock": total_stock,
                    "cost_price": new_cost,
                    "unit_type": str(new_unit)
                }).eq("id", int(current_product['id'])).execute()
                
                # 2. Registrar en compras_historial
                self.supabase.table("compras_historial").insert({
                    "product_id": int(current_product['id']),
                    "product_name": product_name + f" ({new_unit})",
                    "quantity": new_qty,
                    "cost_price_at_purchase": new_cost
                }).execute()
                
                # Pequeño retraso para asimilar la DB
                time.sleep(0.5)
                
                # Recargar UI y mostrar mensaje, silenciado si falla el renderizado
                try:
                    self.search_bar.setText("")
                    self.load_data()
                    self.table.clearSelection()
                    self.table.setCurrentItem(None)
                    self.statusBar().showMessage(f"✅ Ingreso exitoso: {product_name} (+{new_qty} uds) | Nuevo Costo: ${new_cost:,.2f}", 5000)
                except Exception:
                    pass
                
                # Cerrar diálogo siempre al final
                dialog.accept()
            
            except Exception as e:
                # Si falló la consulta a Supabase u otra cosa no visual
                QMessageBox.critical(self, "Error", f"No se pudo registrar la compra: {e}")

        btn_confirm.clicked.connect(process_carga)
        layout.addRow(btn_confirm)
        
        dialog.exec()

    def action_resumen_dia(self):
        """Genera un ticket de cierre con el resumen financiero del día."""
        try:
            # Fecha de hoy a las 00:00 UTC
            hoy = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")
            
            # 1. Consultar ventas del día
            ventas = self.supabase.table("ventas_historial") \
                .select("*") \
                .gte("sold_at", hoy) \
                .order("sold_at", desc=True) \
                .execute().data
            
            total_facturado = sum(float(v.get('sale_price', 0)) for v in ventas)
            ganancia_total = sum(float(v.get('profit', 0)) for v in ventas)
            total_unidades = len(ventas)

            # 2. Productos con stock bajo
            productos_bajos = [p for p in self.all_data if p.get('stock', 0) < STOCK_MINIMO]
            
            # 3. Crear el diálogo
            dialog = QDialog(self)
            dialog.setWindowTitle("Resumen del Dia")
            dialog.setFixedSize(480, 620)
            dialog.setStyleSheet(f"background-color: white; font-family: 'Segoe UI', Arial;")
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(0)

            # ── HEADER ──
            header = QLabel("TICKET DE CIERRE")
            header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet(f"color: {COLOR_SIDEBAR}; margin-bottom: 5px;")
            layout.addWidget(header)

            fecha_label = QLabel(datetime.now().strftime("%d/%m/%Y - %H:%M hs"))
            fecha_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fecha_label.setStyleSheet(f"color: {COLOR_TEXT_LIGHT}; font-size: 13px; margin-bottom: 20px;")
            layout.addWidget(fecha_label)

            # ── LÍNEA DIVISORIA ──
            def add_divider():
                line = QLabel("- " * 30)
                line.setAlignment(Qt.AlignmentFlag.AlignCenter)
                line.setStyleSheet(f"color: {COLOR_BORDER}; font-size: 10px; margin: 8px 0;")
                layout.addWidget(line)
            
            add_divider()

            # ── TOTALES ──
            totales_frame = QFrame()
            totales_layout = QVBoxLayout(totales_frame)
            totales_layout.setSpacing(12)

            def add_metric(label_text, value_text, color=COLOR_SIDEBAR):
                row = QHBoxLayout()
                lbl = QLabel(label_text)
                lbl.setFont(QFont("Segoe UI", 13))
                lbl.setStyleSheet(f"color: {COLOR_TEXT};")
                val = QLabel(value_text)
                val.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
                val.setStyleSheet(f"color: {color};")
                val.setAlignment(Qt.AlignmentFlag.AlignRight)
                row.addWidget(lbl)
                row.addWidget(val)
                totales_layout.addLayout(row)
            
            add_metric("Unidades Vendidas:", str(total_unidades))
            add_metric("Total Facturado:", f"$ {total_facturado:,.2f}", "#3182CE")
            add_metric("Ganancia Real:", f"$ {ganancia_total:,.2f}", "#2F855A")

            layout.addWidget(totales_frame)
            add_divider()

            # ── DETALLE DE VENTAS ──
            if ventas:
                det_title = QLabel("DETALLE DE VENTAS")
                det_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                det_title.setStyleSheet(f"color: {COLOR_TEXT_LIGHT}; margin-top: 5px;")
                layout.addWidget(det_title)

                for v in ventas[:10]:  # Máximo 10 para no saturar
                    profit_val = float(v.get('profit', 0))
                    line = QLabel(f"  {v['product_name']}  —  $ {float(v['sale_price']):,.2f}  (+${profit_val:,.2f})")
                    line.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12px; padding: 2px 0;")
                    layout.addWidget(line)
                
                if len(ventas) > 10:
                    more = QLabel(f"  ... y {len(ventas) - 10} ventas mas")
                    more.setStyleSheet(f"color: {COLOR_TEXT_LIGHT}; font-size: 11px;")
                    layout.addWidget(more)
                
                add_divider()

            # ── ALERTAS DE REPOSICIÓN ──
            alert_title = QLabel("ALERTA DE REPOSICION")
            alert_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            alert_title.setStyleSheet(f"color: {COLOR_DANGER}; margin-top: 5px;")
            layout.addWidget(alert_title)

            if productos_bajos:
                for p in productos_bajos:
                    item_line = QLabel(f"  {p['name']}  —  Stock: {p['stock']} uds")
                    item_line.setStyleSheet(f"color: {COLOR_DANGER}; font-size: 12px; padding: 2px 0;")
                    layout.addWidget(item_line)
            else:
                ok_label = QLabel("  Todos los productos tienen stock suficiente.")
                ok_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 12px;")
                layout.addWidget(ok_label)

            add_divider()

            # ── FOOTER ──
            footer = QLabel("Soberania AI - Sistema de Gestion")
            footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
            footer.setStyleSheet(f"color: {COLOR_TEXT_LIGHT}; font-size: 11px; margin-top: 10px;")
            layout.addWidget(footer)

            layout.addStretch()
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el resumen: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FarmaciaEnterprise()
    window.show()
    sys.exit(app.exec())
