"""
Main Window - Single window application with navigation
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from frontend.ui.dashboard import DashboardWindow
from frontend.ui.search import SearchWindow
from frontend.ui.insert import InsertWindow
from frontend.ui.admin import AdminPanel


class MainWindow(QWidget):
    """Main application window with sidebar navigation"""
    
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NEO Monitor V2 - Sistema de Monitorização de Asteroides")
        self.showMaximized()  # Start maximized
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Admin panel hotkey (Ctrl+Shift+A)
        self.admin_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        self.admin_shortcut.activated.connect(self.open_admin_panel)
        self.admin_panel = None
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f0f4f8;")
        
        # Create pages
        self.dashboard_page = DashboardWindow()
        self.dashboard_page.conn = self.conn
        self.dashboard_page.refresh_data(self.conn)
        # Remove search button from dashboard as we have it in sidebar now
        self.dashboard_page.search_button.hide()
        
        self.search_page = SearchWindow(self.conn)
        
        # Placeholder pages (will be implemented later)
        self.alerts_page = self.create_placeholder_page("Alertas (Em breve...)")
        self.monitoring_page = self.create_placeholder_page("Monitorização (Em breve...)")
        
        # Insert page (Day 4)
        self.insert_page = InsertWindow(self.conn)
        
        # Add pages to stack
        self.content_stack.addWidget(self.dashboard_page)  # Index 0
        self.content_stack.addWidget(self.search_page)     # Index 1
        self.content_stack.addWidget(self.alerts_page)     # Index 2
        self.content_stack.addWidget(self.monitoring_page) # Index 3
        self.content_stack.addWidget(self.insert_page)     # Index 4
        
        main_layout.addWidget(self.content_stack, 1)
        
        self.setLayout(main_layout)
        
        # Show dashboard by default
        self.show_page(0)
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #263238;
                border-right: 2px solid #1976d2;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1976d2;")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title = QLabel("🚀 NEO Monitor")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Sistema de Monitorização")
        subtitle.setFont(QFont("Arial", 9))
        subtitle.setStyleSheet("color: #e3f2fd;")
        header_layout.addWidget(subtitle)
        
        header.setLayout(header_layout)
        sidebar_layout.addWidget(header)
        
        # Navigation buttons
        sidebar_layout.addSpacing(20)
        
        self.nav_buttons = []
        
        # Dashboard button
        btn_dashboard = self.create_nav_button("📊 Dashboard", 0)
        self.nav_buttons.append(btn_dashboard)
        sidebar_layout.addWidget(btn_dashboard)
        
        # Search button
        btn_search = self.create_nav_button("🔍 Pesquisa", 1)
        self.nav_buttons.append(btn_search)
        sidebar_layout.addWidget(btn_search)
        
        # Alerts button
        btn_alerts = self.create_nav_button("⚠️ Alertas", 2)
        self.nav_buttons.append(btn_alerts)
        sidebar_layout.addWidget(btn_alerts)
        
        # Monitoring button
        btn_monitoring = self.create_nav_button("📈 Monitorização", 3)
        self.nav_buttons.append(btn_monitoring)
        sidebar_layout.addWidget(btn_monitoring)
        
        # Insert button
        btn_insert = self.create_nav_button("➕ Inserção", 4)
        self.nav_buttons.append(btn_insert)
        sidebar_layout.addWidget(btn_insert)
        
        sidebar_layout.addStretch()
        
        # Footer
        footer = QLabel("v2.0 - Dia 4")
        footer.setFont(QFont("Arial", 8))
        footer.setStyleSheet("color: #78909c; padding: 10px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(footer)
        
        sidebar.setLayout(sidebar_layout)
        return sidebar
    
    def create_nav_button(self, text: str, page_index: int):
        """Create navigation button"""
        button = QPushButton(text)
        button.setFixedHeight(50)
        button.setFont(QFont("Arial", 11))
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cfd8dc;
                border: none;
                border-left: 4px solid transparent;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #37474f;
                color: white;
            }
            QPushButton:pressed {
                background-color: #455a64;
            }
        """)
        button.clicked.connect(lambda: self.show_page(page_index))
        return button
    
    def show_page(self, index: int):
        """Show selected page and update button styles"""
        self.content_stack.setCurrentIndex(index)
        
        # Update button styles
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #37474f;
                        color: white;
                        border: none;
                        border-left: 4px solid #1976d2;
                        text-align: left;
                        padding-left: 20px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #cfd8dc;
                        border: none;
                        border-left: 4px solid transparent;
                        text-align: left;
                        padding-left: 20px;
                    }
                    QPushButton:hover {
                        background-color: #37474f;
                        color: white;
                    }
                    QPushButton:pressed {
                        background-color: #455a64;
                    }
                """)
    
    def create_placeholder_page(self, message: str):
        """Create placeholder page for features not yet implemented"""
        page = QWidget()
        page.setStyleSheet("background-color: #f0f4f8;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(message)
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #757575;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        info = QLabel("Esta funcionalidade será implementada nos próximos dias")
        info.setFont(QFont("Arial", 12))
        info.setStyleSheet("color: #9e9e9e;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        page.setLayout(layout)
        return page
    
    def open_admin_panel(self):
        """Open admin panel (Ctrl+Shift+A)"""
        if self.admin_panel is None or not self.admin_panel.isVisible():
            self.admin_panel = AdminPanel(self.conn)
            self.admin_panel.show()
        else:
            self.admin_panel.raise_()
            self.admin_panel.activateWindow()
