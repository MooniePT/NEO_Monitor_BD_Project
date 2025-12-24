"""
Database Configuration Window
Tela de configuração da conexão SQL Server
"""
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from backend.services.db_config import testar_conexao, ligar_bd
from frontend.ui.message_utils import show_info, show_warning, show_error


class DbConfigWindow(QWidget):
    """Database configuration window with connection testing"""
    
    connection_successful = pyqtSignal(object)  # Emits pyodbc.Connection object
    
    def __init__(self):
        super().__init__()
        self.config_file = "config.json"
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NEO Monitor - Configuração da Base de Dados")
        self.setMinimumSize(500, 550)
        self.setMaximumSize(600, 700)
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("Configuração da Base de Dados")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Configure a conexão ao SQL Server")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(10)
        
        # Container frame
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #bdbdbd;
                border-radius: 8px;
            }
        """)
        
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(15)
        
        # Server field
        server_label = QLabel("Servidor:")
        server_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        server_label.setStyleSheet("color: #212121;")
        container_layout.addWidget(server_label)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Ex: localhost\\SQLEXPRESS")
        self.server_input.setFixedHeight(35)
        self.server_input.setFont(QFont("Arial", 10))
        self.server_input.setStyleSheet("""
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
        self.server_input.returnPressed.connect(self.connect_to_database)
        container_layout.addWidget(self.server_input)
        
        # Database field
        db_label = QLabel("Base de Dados:")
        db_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        db_label.setStyleSheet("color: #212121;")
        container_layout.addWidget(db_label)
        
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("Ex: BD_PL2_09")
        self.database_input.setFixedHeight(35)
        self.database_input.setFont(QFont("Arial", 10))
        self.database_input.setStyleSheet("""
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
        self.database_input.returnPressed.connect(self.connect_to_database)
        container_layout.addWidget(self.database_input)
        
        # Authentication type
        auth_label = QLabel("Autenticação:")
        auth_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        auth_label.setStyleSheet("color: #212121;")
        container_layout.addWidget(auth_label)
        
        # Radio buttons
        self.auth_group = QButtonGroup()
        
        self.windows_auth_radio = QRadioButton("Autenticação Windows")
        self.windows_auth_radio.setFont(QFont("Arial", 10))
        self.windows_auth_radio.setStyleSheet("color: #424242;")
        self.windows_auth_radio.setChecked(True)
        self.auth_group.addButton(self.windows_auth_radio, 0)
        container_layout.addWidget(self.windows_auth_radio)
        
        self.sql_auth_radio = QRadioButton("Autenticação SQL Server")
        self.sql_auth_radio.setFont(QFont("Arial", 10))
        self.sql_auth_radio.setStyleSheet("color: #424242;")
        self.auth_group.addButton(self.sql_auth_radio, 1)
        container_layout.addWidget(self.sql_auth_radio)
        
        # User field (conditional)
        self.user_label = QLabel("Utilizador:")
        self.user_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.user_label.setStyleSheet("color: #212121;")
        self.user_label.setVisible(False)
        container_layout.addWidget(self.user_label)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nome de utilizador")
        self.user_input.setFixedHeight(35)
        self.user_input.setFont(QFont("Arial", 10))
        self.user_input.setStyleSheet("""
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
        self.user_input.setVisible(False)
        container_layout.addWidget(self.user_input)
        
        # Password field (conditional)
        self.password_label = QLabel("Password:")
        self.password_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.password_label.setStyleSheet("color: #212121;")
        self.password_label.setVisible(False)
        container_layout.addWidget(self.password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFixedHeight(35)
        self.password_input.setFont(QFont("Arial", 10))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
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
        self.password_input.returnPressed.connect(self.connect_to_database)
        self.password_input.setVisible(False)
        container_layout.addWidget(self.password_input)
        
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.test_button = QPushButton("Testar Conexão")
        self.test_button.setFixedHeight(40)
        self.test_button.setFont(QFont("Arial", 10))
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #ffa726;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fb8c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        self.connect_button = QPushButton("Conectar")
        self.connect_button.setFixedHeight(40)
        self.connect_button.setFont(QFont("Arial", 10))
        self.connect_button.setStyleSheet("""
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
        self.connect_button.clicked.connect(self.connect_to_database)
        button_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.windows_auth_radio.toggled.connect(self.on_auth_mode_changed)
        self.sql_auth_radio.toggled.connect(self.on_auth_mode_changed)
        
    def on_auth_mode_changed(self):
        """Show/hide user/password fields based on auth mode"""
        is_sql_auth = self.sql_auth_radio.isChecked()
        
        self.user_label.setVisible(is_sql_auth)
        self.user_input.setVisible(is_sql_auth)
        self.password_label.setVisible(is_sql_auth)
        self.password_input.setVisible(is_sql_auth)
        
        # Adjust window size to fit content
        self.adjustSize()
        
    def test_connection(self):
        """Test database connection"""
        server = self.server_input.text().strip()
        database = self.database_input.text().strip()
        
        if not server or not database:
            show_warning(
                self,
                "Campos Obrigatórios",
                "Por favor, preencha Servidor e Base de Dados."
            )
            return
        
        auth_mode = "windows" if self.windows_auth_radio.isChecked() else "sql"
        user = self.user_input.text().strip() if auth_mode == "sql" else None
        password = self.password_input.text() if auth_mode == "sql" else None
        
        # Test connection
        success, message = testar_conexao(server, database, auth_mode, user, password)
        
        if success:
            show_info(self, "Teste de Conexão", message)
        else:
            show_error(self, "Erro de Conexão", message)
    
    def connect_to_database(self):
        """Connect to database and emit signal"""
        server = self.server_input.text().strip()
        database = self.database_input.text().strip()
        
        if not server or not database:
            show_warning(
                self,
                "Campos Obrigatórios",
                "Por favor, preencha Servidor e Base de Dados."
            )
            return
        
        auth_mode = "windows" if self.windows_auth_radio.isChecked() else "sql"
        user = self.user_input.text().strip() if auth_mode == "sql" else None
        password = self.password_input.text() if auth_mode == "sql" else None
        
        try:
            # Establish connection
            conn = ligar_bd(server, database, auth_mode, user, password)
            
            # Save configuration
            self.save_config(server, database, auth_mode)
            
            # Emit signal with connection
            self.connection_successful.emit(conn)
            
        except Exception as e:
            show_error(
                self,
                "Erro ao Conectar",
                f"Não foi possível conectar à base de dados:\n\n{str(e)}"
            )
    
    def save_config(self, server: str, database: str, auth_mode: str):
        """Save configuration to JSON file"""
        config = {
            "server": server,
            "database": database,
            "auth_mode": auth_mode
        }
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            # Set defaults
            self.server_input.setText("localhost\\SQLEXPRESS")
            self.database_input.setText("BD_PL2_09")
            return
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            self.server_input.setText(config.get("server", "localhost\\SQLEXPRESS"))
            self.database_input.setText(config.get("database", "BD_PL2_09"))
            
            auth_mode = config.get("auth_mode", "windows")
            if auth_mode == "sql":
                self.sql_auth_radio.setChecked(True)
            else:
                self.windows_auth_radio.setChecked(True)
                
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            # Set defaults
            self.server_input.setText("localhost\\SQLEXPRESS")
            self.database_input.setText("BD_PL2_09")
