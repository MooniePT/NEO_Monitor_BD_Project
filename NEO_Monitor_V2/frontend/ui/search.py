"""
Search Window
Asteroid search with filters and pagination
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from backend.services.consultas import fetch_filtered_asteroids
from frontend.ui.message_utils import show_info, show_warning


class SearchWindow(QWidget):
    """Search window with filters and pagination"""
    
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.current_page = 1
        self.page_size = 50
        self.total_results = 0
        self.total_pages = 0
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NEO Monitor - Pesquisa de Asteroides")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("🔍 Pesquisa de Asteroides")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        main_layout.addWidget(title)
        
        # Filters frame
        filters_frame = QFrame()
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                border-radius: 8px;
            }
        """)
        
        filters_layout = QVBoxLayout()
        filters_layout.setContentsMargins(20, 20, 20, 20)
        filters_layout.setSpacing(15)
        
        # Filter title
        filter_title = QLabel("Filtros")
        filter_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        filter_title.setStyleSheet("color: #212121;")
        filters_layout.addWidget(filter_title)
        
        # First row: Name + Type
        row1_layout = QHBoxLayout()
        
        # Name filter
        name_layout = QVBoxLayout()
        name_label = QLabel("Nome / Designação:")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #212121;")
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome ou designação do asteroide")
        self.name_input.setFixedHeight(35)
        self.name_input.setFont(QFont("Arial", 10))
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 5px 10px;
                color: #212121;
            }
            QLineEdit:focus {
                border: 2px solid #1976d2;
            }
        """)
        name_layout.addWidget(self.name_input)
        row1_layout.addLayout(name_layout, 2)
        
        row1_layout.addSpacing(15)
        
        # Type filter
        type_layout = QVBoxLayout()
        type_label = QLabel("Tipo:")
        type_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        type_label.setStyleSheet("color: #212121;")
        type_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Todos", "NEO", "PHA"])
        self.type_combo.setFixedHeight(35)
        self.type_combo.setFont(QFont("Arial", 10))
        self.type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                color: #212121;
            }
            QComboBox:focus {
                border: 2px solid #1976d2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #212121;
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)
        type_layout.addWidget(self.type_combo)
        row1_layout.addLayout(type_layout, 1)
        
        filters_layout.addLayout(row1_layout)
        
        # Second row: Sort + Search button
        row2_layout = QHBoxLayout()
        
        # Sort filter
        sort_layout = QVBoxLayout()
        sort_label = QLabel("Ordenar por:")
        sort_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        sort_label.setStyleSheet("color: #212121;")
        sort_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Nome",
            "Tamanho (Maior)",
            "Tamanho (Menor)",
            "Perigo (Mais próximo)"
        ])
        self.sort_combo.setFixedHeight(35)
        self.sort_combo.setFont(QFont("Arial", 10))
        self.sort_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                color: #212121;
            }
            QComboBox:focus {
                border: 2px solid #1976d2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #212121;
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)
        sort_layout.addWidget(self.sort_combo)
        row2_layout.addLayout(sort_layout, 2)
        
        row2_layout.addSpacing(15)
        
        # Search button
        search_btn_layout = QVBoxLayout()
        search_btn_layout.addSpacing(25)  # Align with other fields
        
        self.search_button = QPushButton("🔍 Pesquisar")
        self.search_button.setFixedHeight(35)
        self.search_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.search_button.clicked.connect(self.search)
        search_btn_layout.addWidget(self.search_button)
        row2_layout.addLayout(search_btn_layout, 1)
        
        filters_layout.addLayout(row2_layout)
        
        filters_frame.setLayout(filters_layout)
        main_layout.addWidget(filters_frame)
        
        # Results label
        results_label = QLabel("Resultados")
        results_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        results_label.setStyleSheet("color: #424242;")
        main_layout.addWidget(results_label)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome Completo", "Designação", "Diâmetro (km)", 
            "H (mag)", "MOID (UA)", "NEO", "PHA"
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
                font-size: 10px;
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
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.table)
        
        # Pagination
        pagination_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("← Anterior")
        self.prev_button.setFixedSize(100, 35)
        self.prev_button.setFont(QFont("Arial", 9))
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        pagination_layout.addWidget(self.prev_button)
        
        pagination_layout.addStretch()
        
        self.page_label = QLabel("Página 1 de 1 (0 resultados)")
        self.page_label.setFont(QFont("Arial", 10))
        self.page_label.setStyleSheet("color: #212121;")
        pagination_layout.addWidget(self.page_label)
        
        pagination_layout.addStretch()
        
        self.next_button = QPushButton("Próxima →")
        self.next_button.setFixedSize(100, 35)
        self.next_button.setFont(QFont("Arial", 9))
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        pagination_layout.addWidget(self.next_button)
        
        main_layout.addLayout(pagination_layout)
        
        self.setLayout(main_layout)
        
        # Auto-search on Enter
        self.name_input.returnPressed.connect(self.search)
    
    def search(self):
        """Perform search with current filters"""
        # Reset to page 1 when new search
        self.current_page = 1
        self._execute_search()
    
    def _execute_search(self):
        """Execute search query"""
        if not self.conn:
            show_warning(self, "Sem Conexão", "Não há conexão ativa com a base de dados.")
            return
        
        # Get filters
        name = self.name_input.text().strip()
        tipo = self.type_combo.currentText()
        sort = self.sort_combo.currentText()
        
        # Map type to backend
        danger_level = "Todos"
        if tipo == "NEO":
            danger_level = "NEO"
        elif tipo == "PHA":
            danger_level = "PHA"
        
        try:
            # Call backend
            cols, rows = fetch_filtered_asteroids(
                self.conn,
                name=name if name else None,
                danger_level=danger_level,
                sort_by=sort,
                page=self.current_page,
                page_size=self.page_size
            )
            
            # Get total count from first row if available
            if rows:
                self.total_results = rows[0].get('TotalCount', len(rows))
                self.total_pages = (self.total_results + self.page_size - 1) // self.page_size
            else:
                self.total_results = 0
                self.total_pages = 0
            
            # Populate table
            self._populate_table(rows)
            
            # Update pagination
            self._update_pagination()
            
            # Show message if no results
            if not rows:
                show_info(self, "Sem Resultados", "Nenhum asteroide encontrado com os filtros especificados.")
                
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao executar pesquisa:\n\n{str(e)}")
    
    def _populate_table(self, rows):
        """Populate table with results"""
        self.table.setRowCount(0)
        
        for row_data in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # ID
            self.table.setItem(row_position, 0,
                QTableWidgetItem(str(row_data.get('id_asteroide', ''))))
            
            # Nome Completo
            self.table.setItem(row_position, 1,
                QTableWidgetItem(str(row_data.get('nome_completo', ''))))
            
            # Designação
            self.table.setItem(row_position, 2,
                QTableWidgetItem(str(row_data.get('pdes', ''))))
            
            # Diâmetro
            diameter = row_data.get('diametro_km', 0)
            if diameter:
                diameter_text = f"{float(diameter):.3f}"
            else:
                diameter_text = "N/A"
            self.table.setItem(row_position, 3,
                QTableWidgetItem(diameter_text))
            
            # h_mag (3FN: lowercase)
            h_mag = row_data.get('h_mag', 0)
            if h_mag:
                h_mag_text = f"{float(h_mag):.2f}"
            else:
                h_mag_text = "N/A"
            self.table.setItem(row_position, 4,
                QTableWidgetItem(h_mag_text))
            
            # MOID
            moid = row_data.get('moid_ua', 0)
            if moid:
                moid_text = f"{float(moid):.4f}"
            else:
                moid_text = "N/A"
            self.table.setItem(row_position, 5,
                QTableWidgetItem(moid_text))
            
            # NEO flag
            neo_flag = "✓" if row_data.get('flag_neo') == 1 else ""
            neo_item = QTableWidgetItem(neo_flag)
            neo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_position, 6, neo_item)
            
            # PHA flag
            pha_flag = "✓" if row_data.get('flag_pha') == 1 else ""
            pha_item = QTableWidgetItem(pha_flag)
            pha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_position, 7, pha_item)
    
    def _update_pagination(self):
        """Update pagination controls"""
        if self.total_pages == 0:
            self.page_label.setText("Página 1 de 1 (0 resultados)")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            self.page_label.setText(
                f"Página {self.current_page} de {self.total_pages} ({self.total_results} resultados)"
            )
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < self.total_pages)
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._execute_search()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._execute_search()
