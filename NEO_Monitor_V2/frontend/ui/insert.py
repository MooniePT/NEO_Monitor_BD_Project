"""
Insert Window - Manual insertion and CSV import
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QTabWidget, QFileDialog, QProgressBar,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QDoubleValidator
import pyodbc
from pathlib import Path
from backend.services.insercao import importar_neo_csv
from frontend.ui.message_utils import show_message


class CSVImportThread(QThread):
    """Thread for CSV import to avoid blocking UI"""
    progress_update = pyqtSignal(int, int, float)  # current, total, elapsed
    import_complete = pyqtSignal(int)  # total inserted
    import_error = pyqtSignal(str)  # error message
    
    def __init__(self, conn, filepath):
        super().__init__()
        self.conn = conn
        self.filepath = filepath
    
    def run(self):
        try:
            def progress_callback(current, total, elapsed):
                self.progress_update.emit(current, total, elapsed)
            
            total_inserted = importar_neo_csv(self.conn, self.filepath, progress_callback)
            self.import_complete.emit(total_inserted)
        except Exception as e:
            self.import_error.emit(str(e))


class InsertWindow(QWidget):
    """Insert window with manual entry and CSV import"""
    
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.csv_filepath = None
        self.import_thread = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("➕ Inserção de Dados")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #212121;")
        layout.addWidget(title)
        
        subtitle = QLabel("Adicione asteroides manualmente ou importe de ficheiro CSV")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #757575;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 11))
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdbdbd;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #424242;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1976d2;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #bdbdbd;
            }
        """)
        
        # Create tabs
        self.manual_tab = self.create_manual_tab()
        self.csv_tab = self.create_csv_tab()
        
        self.tabs.addTab(self.manual_tab, "Inserção Manual")
        self.tabs.addTab(self.csv_tab, "Importação CSV")
        
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
    
    def create_manual_tab(self):
        """Create manual insertion tab"""
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Instructions
        instructions = QLabel("Preencha os campos abaixo para adicionar um novo asteroide:")
        instructions.setFont(QFont("Arial", 11))
        instructions.setStyleSheet("color: #424242;")
        layout.addWidget(instructions)
        
        # Form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Fields
        # Designação (obrigatório)
        self.pdes_input = self.create_form_field(
            form_layout, "Designação (pdes) *", 
            "Ex: 2024 AB", required=True
        )
        
        # Nome Completo (obrigatório)
        self.nome_input = self.create_form_field(
            form_layout, "Nome Completo *", 
            "Ex: Apophis", required=True
        )
        
        # Checkboxes row
        checkbox_layout = QHBoxLayout()
        
        self.neo_checkbox = QCheckBox("NEO (Near-Earth Object)")
        self.neo_checkbox.setChecked(True)  # Default checked
        self.neo_checkbox.setFont(QFont("Arial", 10))
        self.neo_checkbox.setStyleSheet("color: #212121;")
        checkbox_layout.addWidget(self.neo_checkbox)
        
        self.pha_checkbox = QCheckBox("PHA (Potentially Hazardous)")
        self.pha_checkbox.setFont(QFont("Arial", 10))
        self.pha_checkbox.setStyleSheet("color: #212121;")
        checkbox_layout.addWidget(self.pha_checkbox)
        
        checkbox_layout.addStretch()
        form_layout.addLayout(checkbox_layout)
        
        # H Magnitude (opcional)
        self.h_mag_input = self.create_form_field(
            form_layout, "H Magnitude", 
            "Ex: 18.5", is_number=True
        )
        
        # Diâmetro (opcional)
        self.diametro_input = self.create_form_field(
            form_layout, "Diâmetro (km)", 
            "Ex: 0.250", is_number=True
        )
        
        # MOID UA (opcional)
        self.moid_ua_input = self.create_form_field(
            form_layout, "MOID (UA - Unidades Astronômicas)", 
            "Ex: 0.05", is_number=True
        )
        
        # MOID LD (opcional)
        self.moid_ld_input = self.create_form_field(
            form_layout, "MOID (LD - Distâncias Lunares)", 
            "Ex: 19.5", is_number=True
        )
        
        # Albedo (opcional)
        self.albedo_input = self.create_form_field(
            form_layout, "Albedo (0.0 - 1.0)", 
            "Ex: 0.25", is_number=True
        )
        
        form_container.setLayout(form_layout)
        layout.addWidget(form_container)
        
        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.insert_button = QPushButton("Inserir Asteroide")
        self.insert_button.setFixedSize(200, 45)
        self.insert_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.insert_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.insert_button.clicked.connect(self.insert_asteroid)
        button_layout.addWidget(self.insert_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_csv_tab(self):
        """Create CSV import tab"""
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Instructions
        instructions = QLabel("Selecione um ficheiro CSV para importar asteroides em massa:")
        instructions.setFont(QFont("Arial", 11))
        instructions.setStyleSheet("color: #424242;")
        layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.select_file_button = QPushButton("📁 Selecionar Ficheiro CSV")
        self.select_file_button.setFixedHeight(40)
        self.select_file_button.setFont(QFont("Arial", 11))
        self.select_file_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.select_file_button.clicked.connect(self.select_csv_file)
        file_layout.addWidget(self.select_file_button)
        
        self.file_label = QLabel("Nenhum ficheiro selecionado")
        self.file_label.setFont(QFont("Arial", 10))
        self.file_label.setStyleSheet("color: #757575;")
        file_layout.addWidget(self.file_label, 1)
        
        layout.addLayout(file_layout)
        
        # Progress section
        progress_container = QFrame()
        progress_container.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("Aguardando seleção de ficheiro...")
        self.progress_label.setFont(QFont("Arial", 11))
        self.progress_label.setStyleSheet("color: #424242;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                text-align: center;
                background-color: white;
                color: #212121;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #1976d2;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        progress_container.setLayout(progress_layout)
        layout.addWidget(progress_container)
        
        # Import button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_button = QPushButton("⬆️ Importar CSV")
        self.import_button.setFixedSize(200, 45)
        self.import_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.import_button.setEnabled(False)
        self.import_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover:enabled {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
        self.import_button.clicked.connect(self.import_csv)
        button_layout.addWidget(self.import_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_form_field(self, parent_layout, label_text, placeholder, 
                         required=False, is_number=False):
        """Helper to create form field"""
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        label.setStyleSheet("color: #212121;")
        parent_layout.addWidget(label)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(35)
        input_field.setFont(QFont("Arial", 10))
        input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdbdbd;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                color: #212121;
            }
            QLineEdit:focus {
                border: 2px solid #1976d2;
            }
        """)
        
        if is_number:
            # Accept numbers with decimals (negative and positive)
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            input_field.setValidator(validator)
        
        parent_layout.addWidget(input_field)
        return input_field
    
    def insert_asteroid(self):
        """Insert asteroid manually"""
        # Validate required fields
        pdes = self.pdes_input.text().strip()
        nome = self.nome_input.text().strip()
        
        if not pdes:
            show_message(
                self, "Erro de Validação",
                "O campo 'Designação (pdes)' é obrigatório.",
                QMessageBox.Icon.Warning
            )
            self.pdes_input.setFocus()
            return
        
        if not nome:
            show_message(
                self, "Erro de Validação",
                "O campo 'Nome Completo' é obrigatório.",
                QMessageBox.Icon.Warning
            )
            self.nome_input.setFocus()
            return
        
        # Get optional fields
        h_mag = self._get_float_value(self.h_mag_input)
        diametro = self._get_float_value(self.diametro_input)
        moid_ua = self._get_float_value(self.moid_ua_input)
        moid_ld = self._get_float_value(self.moid_ld_input)
        albedo = self._get_float_value(self.albedo_input)
        

        # Validate ranges
        if diametro is not None and diametro <= 0:
            show_message(
                self, "Erro de Validação",
                "O Diâmetro deve ser maior que 0.",
                QMessageBox.Icon.Warning
            )
            return
        
        if moid_ua is not None and moid_ua < 0:
            show_message(
                self, "Erro de Validação",
                "O MOID (UA) deve ser maior ou igual a 0.",
                QMessageBox.Icon.Warning
            )
            return
        
        if moid_ld is not None and moid_ld < 0:
            show_message(
                self, "Erro de Validação",
                "O MOID (LD) deve ser maior ou igual a 0.",
                QMessageBox.Icon.Warning
            )
            return
        
        if albedo is not None and (albedo < 0 or albedo > 1):
            show_message(
                self, "Erro de Validação",
                "O Albedo deve estar entre 0.0 e 1.0.",
                QMessageBox.Icon.Warning
            )
            return
        
        # Insert into database (3FN: Asteroide sem moid)
        try:
            cursor = self.conn.cursor()
            
            # 1. Insert Asteroide (3FN: sem moid aqui!)
            sql_ast = """
                INSERT INTO dbo.Asteroide 
                (pdes, nome_completo, flag_neo, flag_pha, h_mag, diametro_km, albedo)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                SELECT SCOPE_IDENTITY();
            """
            
            cursor.execute(
                sql_ast,
                pdes,
                nome,
                1 if self.neo_checkbox.isChecked() else 0,
                1 if self.pha_checkbox.isChecked() else 0,
                h_mag,
                diametro,
                albedo
            )
            
            new_id = int(cursor.fetchone()[0])
            
            # 2. Insert Solucao_Orbital se moid fornecido (3FN: moid agora aqui!)
            if moid_ua is not None or moid_ld is not None:
                sql_sol = """
                    INSERT INTO dbo.Solucao_Orbital
                    (id_asteroide, fonte, moid_ua, moid_ld, solucao_atual)
                    VALUES (?, 'MANUAL', ?, ?, 1)
                """
                cursor.execute(sql_sol, new_id, moid_ua, moid_ld)
            
            self.conn.commit()
            cursor.close()
            
            show_message(
                self, "Sucesso!",
                f"Asteroide inserido com sucesso!\n\nID: {new_id}\nDesignação: {pdes}\nNome: {nome}",
                QMessageBox.Icon.Information
            )
            
            # Clear form
            self.clear_manual_form()
            
        except pyodbc.Error as e:
            show_message(
                self, "Erro na Base de Dados",
                f"Erro ao inserir asteroide:\n{str(e)}",
                QMessageBox.Icon.Critical
            )
        except Exception as e:
            show_message(
                self, "Erro",
                f"Erro inesperado:\n{str(e)}",
                QMessageBox.Icon.Critical
            )
    
    def clear_manual_form(self):
        """Clear all manual form fields"""
        self.pdes_input.clear()
        self.nome_input.clear()
        self.h_mag_input.clear()
        self.diametro_input.clear()
        self.moid_ua_input.clear()
        self.moid_ld_input.clear()
        self.albedo_input.clear()
        self.neo_checkbox.setChecked(True)
        self.pha_checkbox.setChecked(False)
        self.pdes_input.setFocus()
    
    def _get_float_value(self, input_field):
        """Get float value from input field, return None if empty"""
        text = input_field.text().strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    
    def select_csv_file(self):
        """Open file dialog to select CSV"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Ficheiro CSV",
            str(Path.home()),
            "Ficheiros CSV (*.csv);;Todos os ficheiros (*.*)"
        )
        
        if filepath:
            self.csv_filepath = filepath
            filename = Path(filepath).name
            self.file_label.setText(f"✅ {filename}")
            self.file_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.import_button.setEnabled(True)
            self.progress_label.setText(f"Ficheiro selecionado: {filename}")
            self.progress_bar.setValue(0)
    
    def import_csv(self):
        """Start CSV import in thread"""
        if not self.csv_filepath:
            return
        
        # Disable buttons during import
        self.import_button.setEnabled(False)
        self.select_file_button.setEnabled(False)
        self.progress_label.setText("Importando... Por favor aguarde...")
        self.progress_bar.setValue(0)
        
        # Start import thread
        self.import_thread = CSVImportThread(self.conn, self.csv_filepath)
        self.import_thread.progress_update.connect(self.update_progress)
        self.import_thread.import_complete.connect(self.import_finished)
        self.import_thread.import_error.connect(self.import_failed)
        self.import_thread.start()
    
    def update_progress(self, current, total, elapsed):
        """Update progress bar and label"""
        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(
            f"Importando: {current:,}/{total:,} registos ({percentage}%)"
        )
    
    def import_finished(self, total_inserted):
        """Handle successful import completion"""
        self.progress_bar.setValue(100)
        self.progress_label.setText(f"✅ Importação concluída com sucesso!")
        
        show_message(
            self, "Importação Concluída!",
            f"Total de {total_inserted:,} registos foram importados com sucesso!",
            QMessageBox.Icon.Information
        )
        
        # Re-enable buttons
        self.select_file_button.setEnabled(True)
        self.import_button.setEnabled(True)
    
    def import_failed(self, error_msg):
        """Handle import error"""
        self.progress_label.setText("❌ Erro durante a importação")
        
        show_message(
            self, "Erro na Importação",
            f"Ocorreu um erro durante a importação:\n\n{error_msg}",
            QMessageBox.Icon.Critical
        )
        
        # Re-enable buttons
        self.select_file_button.setEnabled(True)
        self.import_button.setEnabled(True)
