"""
Dashboard Window
Main dashboard with KPIs and asteroid table
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from backend.services.consultas import fetch_ultimos_asteroides
from frontend.ui.message_utils import show_error, show_warning


class DashboardWindow(QWidget):
    """Main dashboard with overview and KPIs"""
    
    def __init__(self):
        super().__init__()
        self.conn = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NEO Monitor - Dashboard")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Title
        title_layout = QHBoxLayout()
        
        title = QLabel("Dashboard - Visão Geral")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Search button
        self.search_button = QPushButton("🔍 Pesquisar")
        self.search_button.setFixedSize(120, 35)
        self.search_button.setFont(QFont("Arial", 10))
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        self.search_button.clicked.connect(self.open_search)
        title_layout.addWidget(self.search_button)
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 Atualizar")
        self.refresh_button.setFixedSize(120, 35)
        self.refresh_button.setFont(QFont("Arial", 10))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        title_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(title_layout)
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        # Card 1 - Total NEOs
        self.neo_card = self.create_kpi_card(
            "Total NEOs",
            "0",
            "#e3f2fd",  # Light blue
            "#1976d2"   # Dark blue
        )
        kpi_layout.addWidget(self.neo_card)
        
        # Card 2 - Total PHAs
        self.pha_card = self.create_kpi_card(
            "Total PHAs",
            "0",
            "#fff3e0",  # Light orange
            "#f57c00"   # Dark orange
        )
        kpi_layout.addWidget(self.pha_card)
        
        # Card 3 - Alertas Ativos
        self.alert_card = self.create_kpi_card(
            "Alertas Ativos",
            "0",
            "#fffde7",  # Light yellow
            "#fbc02d"   # Dark yellow
        )
        kpi_layout.addWidget(self.alert_card)
        
        main_layout.addLayout(kpi_layout)
        
        # Table section
        table_title = QLabel("Últimos Asteroides Detectados")
        table_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        table_title.setStyleSheet("color: #424242;")
        main_layout.addWidget(table_title)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome Completo", "Diâmetro (km)", "H (mag)", "NEO", "PHA"
        ])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                gridline-color: #e0e0e0;
                color: #212121;
            }
            QTableWidget::item {
                padding: 5px;
                color: #212121;
            }
            QHeaderView::section {
                background-color: #1976d2;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        # Table properties
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def create_kpi_card(self, label_text: str, value_text: str, 
                        bg_color: str, text_color: str) -> QFrame:
        """Create a KPI card widget"""
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid #bdbdbd;
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Label
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 11))
        label.setStyleSheet(f"color: {text_color}; font-weight: bold;")
        layout.addWidget(label)
        
        layout.addStretch()
        
        # Value
        value = QLabel(value_text)
        value.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        value.setStyleSheet(f"color: {text_color};")
        value.setObjectName("kpi_value")
        layout.addWidget(value)
        
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def refresh_data(self, conn):
        """Refresh all data from database"""
        self.conn = conn
        
        try:
            # Load KPIs
            self._load_kpis()
            
            # Load table
            self._load_table()
            
        except Exception as e:
            show_error(
                self,
                "Erro ao Carregar Dados",
                f"Ocorreu um erro ao carregar os dados:\n\n{str(e)}"
            )
    
    def _load_kpis(self):
        """Load KPI values from database"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        try:
            # Total NEOs
            cursor.execute("SELECT COUNT(*) FROM Asteroide WHERE flag_neo=1")
            neo_count = cursor.fetchone()[0]
            neo_value_label = self.neo_card.findChild(QLabel, "kpi_value")
            if neo_value_label:
                neo_value_label.setText(str(neo_count))
            
            # Total PHAs
            cursor.execute("SELECT COUNT(*) FROM Asteroide WHERE flag_pha=1")
            pha_count = cursor.fetchone()[0]
            pha_value_label = self.pha_card.findChild(QLabel, "kpi_value")
            if pha_value_label:
                pha_value_label.setText(str(pha_count))
            
            # Alertas Ativos (table might not exist yet)
            try:
                cursor.execute("SELECT COUNT(*) FROM Alerta WHERE ativo=1")
                alert_count = cursor.fetchone()[0]
            except:
                alert_count = 0  # Table doesn't exist yet
            
            alert_value_label = self.alert_card.findChild(QLabel, "kpi_value")
            if alert_value_label:
                alert_value_label.setText(str(alert_count))
                
        except Exception as e:
            print(f"Error loading KPIs: {e}")
        finally:
            cursor.close()
    
    def _load_table(self):
        """Load asteroid table data"""
        if not self.conn:
            return
        
        try:
            # Fetch data using backend service
            cols, rows = fetch_ultimos_asteroides(self.conn, limit=20)
            
            # Clear table
            self.table.setRowCount(0)
            
            # Populate table
            for row_data in rows:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                
                # ID
                self.table.setItem(row_position, 0, 
                    QTableWidgetItem(str(row_data.get('id_asteroide', ''))))
                
                # Nome Completo
                self.table.setItem(row_position, 1, 
                    QTableWidgetItem(str(row_data.get('nome_completo', ''))))
                
                # Diâmetro
                diameter = row_data.get('diametro_km', 0)
                if diameter:
                    diameter_text = f"{float(diameter):.3f}"
                else:
                    diameter_text = "N/A"
                self.table.setItem(row_position, 2, 
                    QTableWidgetItem(diameter_text))
                
                # h_mag (3FN: lowercase)
                h_mag = row_data.get('h_mag', 0)
                if h_mag:
                    h_mag_text = f"{float(h_mag):.2f}"
                else:
                    h_mag_text = "N/A"
                self.table.setItem(row_position, 3, 
                    QTableWidgetItem(h_mag_text))
                
                # NEO flag
                neo_flag = "✓" if row_data.get('flag_neo') == 1 else ""
                neo_item = QTableWidgetItem(neo_flag)
                neo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_position, 4, neo_item)
                
                # PHA flag
                pha_flag = "✓" if row_data.get('flag_pha') == 1 else ""
                pha_item = QTableWidgetItem(pha_flag)
                pha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_position, 5, pha_item)
                
        except Exception as e:
            show_warning(
                self,
                "Aviso",
                f"Erro ao carregar tabela de asteroides:\n\n{str(e)}"
            )
    
    def on_refresh_clicked(self):
        """Handle refresh button click"""
        if self.conn:
            self.refresh_data(self.conn)
        else:
            show_warning(
                self,
                "Sem Conexão",
                "Não há conexão ativa com a base de dados."
            )
    
    def open_search(self):
        """Open search window"""
        if self.conn:
            from frontend.ui.search import SearchWindow
            self.search_window = SearchWindow(self.conn)
            self.search_window.show()
        else:
            show_warning(
                self,
                "Sem Conexão",
                "Não há conexão ativa com a base de dados."
            )
