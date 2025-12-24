"""
NEO Monitor V2 - Login Screen - SIMPLIFIED & ROBUST
Explicit sizing to prevent ANY clipping issues
"""
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class LoginWindow(QWidget):
    """Simple, robust login window"""
    login_successful = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI with explicit sizing"""
        self.setWindowTitle("NEO Monitor - Login")
        self.resize(650, 600)
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Main container
        container = QFrame(self)
        container.setGeometry(50, 50, 550, 500)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # Layout inside container
        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("🚀 NEO MISSION CONTROL")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(40)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Login de Administrador")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #424242; border: none;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFixedHeight(30)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username label
        user_lbl = QLabel("Utilizador:")
        user_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        user_lbl.setStyleSheet("color: #212121; border: none;")
        user_lbl.setFixedHeight(25)
        layout.addWidget(user_lbl)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setFont(QFont("Arial", 11))
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdbdbd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #1976d2;
            }
        """)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(10)
        
        # Password label
        pass_lbl = QLabel("Palavra-passe:")
        pass_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        pass_lbl.setStyleSheet("color: #212121; border: none;")
        pass_lbl.setFixedHeight(25)
        layout.addWidget(pass_lbl)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setFont(QFont("Arial", 11))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdbdbd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #1976d2;
            }
        """)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Remember checkbox
        self.remember_checkbox = QCheckBox("Guardar dados")
        self.remember_checkbox.setFont(QFont("Arial", 9))
        self.remember_checkbox.setStyleSheet("color: #616161; border: none;")
        self.remember_checkbox.setFixedHeight(25)
        layout.addWidget(self.remember_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(15)
        
        # Login button
        login_btn = QPushButton("ENTRAR")
        login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_btn.setFixedHeight(50)
        login_btn.setFixedWidth(200)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setDefault(True)
        layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
    def handle_login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return
            
        if username == "admin" and password == "admin":
            self.login_successful.emit(username)
        else:
            QMessageBox.critical(self, "Erro", "Credenciais inválidas.")
            self.password_input.clear()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.login_successful.connect(lambda u: print(f"✅ Login: {u}"))
    window.show()
    sys.exit(app.exec())
