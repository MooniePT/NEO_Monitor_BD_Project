"""
Admin Panel for Database Maintenance
Includes database reset, structure creation, and verification tools
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QInputDialog, QTextEdit, QProgressDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path


class AdminPanel(QWidget):
    """Admin panel for database maintenance operations"""
    
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("🔧 Admin Panel - Manutenção da Base de Dados")
        self.setMinimumSize(850, 700)  # Increased from 800x600
        self.setStyleSheet("background-color: #f0f4f8;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("🔧 Painel de Administração")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #d32f2f;")  # Red for admin
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Funções avançadas de manutenção da base de dados")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #757575;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)
        
        # Dangerous Operations Section
        danger_frame = self.create_section_frame(
            "⚠️ OPERAÇÕES PERIGOSAS",
            "#ffebee",  # Light red
            "#d32f2f"   # Dark red
        )
        danger_layout = QVBoxLayout()
        danger_layout.setSpacing(15)
        
        # Reset button - SIMPLE
        reset_btn = QPushButton("🗑️ Reset Completo da BD")
        reset_btn.setMinimumHeight(50)
        reset_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover { background-color: #c62828; }
        """)
        reset_btn.setToolTip("Apaga TODAS as tabelas e recria estrutura vazia")
        reset_btn.clicked.connect(self.reset_database)
        danger_layout.addWidget(reset_btn)
        
        # Create 3FN button
        create_btn = QPushButton("📊 Criar Estrutura 3FN")
        create_btn.setMinimumHeight(50)
        create_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #f57c00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover { background-color: #ef6c00; }
        """)
        create_btn.setToolTip("Executa scripts de criação de tabelas normalizadas")
        create_btn.clicked.connect(self.create_3fn_structure)
        danger_layout.addWidget(create_btn)
        
        # Seed button
        seed_btn = QPushButton("📥 Seed Data (Lookup Tables)")
        seed_btn.setMinimumHeight(50)
        seed_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        seed_btn.setStyleSheet("""
            QPushButton {
                background-color: #fbc02d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover { background-color: #f9a825; }
        """)
        seed_btn.setToolTip("Popula tabelas de referência (Nivel_Alerta, Prioridade_Alerta, etc)")
        seed_btn.clicked.connect(self.seed_data)
        danger_layout.addWidget(seed_btn)
        
        danger_frame.setLayout(danger_layout)
        main_layout.addWidget(danger_frame)
        
        # Verification Section
        verify_frame = self.create_section_frame(
            "🔍 VERIFICAÇÃO",
            "#e8f5e9",  # Light green
            "#388e3c"   # Dark green
        )
        verify_layout = QVBoxLayout()
        verify_layout.setSpacing(15)
        
        # Verify button
        verify_btn = QPushButton("✓ Verificar Integridade")
        verify_btn.setMinimumHeight(50)
        verify_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover { background-color: #2e7d32; }
        """)
        verify_btn.setToolTip("Executa queries de verificação da estrutura e integridade de FKs")
        verify_btn.clicked.connect(self.verify_integrity)
        verify_layout.addWidget(verify_btn)
        
        # Stats button
        stats_btn = QPushButton("📈 Estatísticas de Tabelas")
        stats_btn.setMinimumHeight(50)
        stats_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover { background-color: #1565c0; }
        """)
        stats_btn.setToolTip("Mostra contagens e tamanhos de todas as tabelas na BD")
        stats_btn.clicked.connect(self.show_statistics)
        verify_layout.addWidget(stats_btn)
        
        verify_frame.setLayout(verify_layout)
        main_layout.addWidget(verify_frame)
        
        main_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("❌ Fechar Admin Panel")
        close_btn.setFixedHeight(40)
        close_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)
    
    def create_section_frame(self, title: str, bg_color: str, title_color: str) -> QFrame:
        """Create a section frame"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {title_color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        return frame
    
    def create_action_button(self, text: str, description: str, color: str) -> QPushButton:
        """Create an action button with description"""
        btn = QPushButton(f"{text}\n{description}")
        btn.setMinimumHeight(80)  # Increased from 60 to 80
        btn.setFont(QFont("Arial", 9))  # Slightly smaller font
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                text-align: left;
                line-height: 1.4;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """)
        return btn
    
    def darken_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Darken a hex color"""
        # Simple darkening - reduce each component
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def reset_database(self):
        """Reset entire database"""
        # Double confirmation
        reply = QMessageBox.warning(
            self,
            "⚠️ PERIGO - Reset de Base de Dados",
            "Isto vai APAGAR TODAS AS TABELAS E DADOS!\n\nTem ABSOLUTA CERTEZA que quer continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Second confirmation
        text, ok = QInputDialog.getText(
            self,
            "Confirmação Final",
            "Digite 'CONFIRMO' (em maiúsculas) para prosseguir:"
        )
        
        if not ok or text != "CONFIRMO":
            QMessageBox.information(self, "Cancelado", "Operação cancelada.")
            return
        
        try:
            self._run_sql_file("backend/sql/neo_monitoring_sql_normalizado/00_reset_database.sql")
            QMessageBox.information(
                self,
                "✅ Sucesso",
                "Base de dados resetada com sucesso!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro",
                f"Erro ao resetar BD:\n\n{str(e)}"
            )
    
    def create_3fn_structure(self):
        """Create 3FN normalized structure"""
        reply = QMessageBox.question(
            self,
            "Criar Estrutura 3FN",
            "Isto vai criar todas as tabelas normalizadas.\n\nContinuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            scripts = [
                "01_create_tables.sql",
                "02_create_views.sql",
                "03_create_triggers.sql"
            ]
            
            # Create custom progress dialog with visible text
            from PyQt6.QtWidgets import QDialog, QProgressBar
            from PyQt6.QtCore import QCoreApplication
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📊 Criar Estrutura 3FN")
            dialog.setMinimumSize(400, 150)
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Status label
            status_label = QLabel("Iniciando...")
            status_label.setFont(QFont("Arial", 11))
            status_label.setStyleSheet("color: #212121;")
            layout.addWidget(status_label)
            
            # Progress bar
            progress = QProgressBar()
            progress.setMinimum(0)
            progress.setMaximum(len(scripts))
            progress.setValue(0)
            progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #bdbdbd;
                    border-radius: 4px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #1976d2;
                }
            """)
            layout.addWidget(progress)
            
            dialog.setLayout(layout)
            dialog.show()
            
            # Process scripts
            for i, script in enumerate(scripts):
                status_label.setText(f"📄 Executando {script}...")
                QCoreApplication.processEvents()  # Update UI
                
                self._run_sql_file(f"backend/sql/neo_monitoring_sql_normalizado/{script}")
                
                progress.setValue(i + 1)
                QCoreApplication.processEvents()  # Update UI
            
            dialog.close()
            
            QMessageBox.information(
                self,
                "✅ Sucesso",
                "Estrutura 3FN criada com sucesso!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro",
                f"Erro ao criar estrutura:\n\n{str(e)}"
            )
    
    def seed_data(self):
        """Seed lookup tables"""
        try:
            self._run_sql_file("backend/sql/neo_monitoring_sql_normalizado/04_seed_data.sql")
            QMessageBox.information(
                self,
                "✅ Sucesso",
                "Dados de referência inseridos com sucesso!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro",
                f"Erro ao inserir seeds:\n\n{str(e)}"
            )
    
    def verify_integrity(self):
        """Verify database integrity"""
        try:
            cursor = self.conn.cursor()
            
            results = []
            results.append("=== VERIFICAÇÃO DE INTEGRIDADE ===\n")
            
            # Count tables
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'dbo' AND table_type = 'BASE TABLE'
            """)
            table_count = cursor.fetchone()[0]
            results.append(f"✓ Total de tabelas: {table_count}")
            
            # Check Asteroide
            cursor.execute("SELECT COUNT(*) FROM Asteroide")
            ast_count = cursor.fetchone()[0]
            results.append(f"✓ Asteroides: {ast_count}")
            
            # Check Solucao_Orbital
            cursor.execute("SELECT COUNT(*) FROM Solucao_Orbital")
            sol_count = cursor.fetchone()[0]
            results.append(f"✓ Soluções Orbitais: {sol_count}")
            
            # Check orphans
            cursor.execute("""
                SELECT COUNT(*) FROM Solucao_Orbital s
                LEFT JOIN Asteroide a ON s.id_asteroide = a.id_asteroide
                WHERE a.id_asteroide IS NULL
            """)
            orphans = cursor.fetchone()[0]
            if orphans == 0:
                results.append(f"✓ Órfãos em Solucao_Orbital: {orphans} (OK!)")
            else:
                results.append(f"⚠️ Órfãos em Solucao_Orbital: {orphans}")
            
            cursor.close()
            
            # Show results
            self._show_text_dialog("Verificação de Integridade", "\n".join(results))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro",
                f"Erro na verificação:\n\n{str(e)}"
            )
    
    def show_statistics(self):
        """Show table statistics in a proper table"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    t.name AS Tabela,
                    SUM(p.rows) AS Registos
                FROM sys.tables t
                INNER JOIN sys.partitions p ON t.object_id = p.object_id
                WHERE p.index_id IN (0,1) AND t.schema_id = SCHEMA_ID('dbo')
                GROUP BY t.name
                ORDER BY Registos DESC
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            
            # Create dialog with table
            from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📈 Estatísticas de Tabelas")
            dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("Contagens de Registos por Tabela")
            title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            title.setStyleSheet("color: #212121; padding: 10px;")
            layout.addWidget(title)
            
            # Table
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Tabela", "Registos"])
            table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                table.setItem(i, 0, QTableWidgetItem(row[0]))
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))
            
            # Style
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #bdbdbd;
                    gridline-color: #e0e0e0;
                }
                QHeaderView::section {
                    background-color: #1976d2;
                    color: white;
                    padding: 8px;
                    font-weight: bold;
                }
            """)
            
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            
            layout.addWidget(table)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro",
                f"Erro ao obter estatísticas:\n\n{str(e)}"
            )
    
    def _run_sql_file(self, filepath: str):
        """Run a SQL file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Ficheiro não encontrado: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        cursor = self.conn.cursor()
        statements = script.split('GO')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    # Some statements may fail (e.g., DROP if not exists) - continue
                    print(f"Warning in SQL: {str(e)}")
        
        self.conn.commit()
        cursor.close()
    
    def _show_text_dialog(self, title: str, text: str):
        """Show text in dialog"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText("Resultados:")
        dialog.setDetailedText(text)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.exec()
