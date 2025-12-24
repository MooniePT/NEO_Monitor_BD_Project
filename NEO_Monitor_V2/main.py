"""
NEO Monitor V2 - Main Entry Point
Clean, modern, professional asteroid monitoring system

Flow: Login → DB Config → MainWindow (with Dashboard, Search, etc.)
"""
import sys
from PyQt6.QtWidgets import QApplication
from frontend.ui.login import LoginWindow
from frontend.ui.db_config import DbConfigWindow
from frontend.ui.main_window import MainWindow


class NEOMonitorApp:
    """Main application controller"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("NEO Monitor V2")
        self.app.setOrganizationName("UBI")
        
        self.login_window = None
        self.db_window = None
        self.main_window = None
        
    def start(self):
        """Start the application"""
        # Create login window
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
        
        return self.app.exec()
    
    def on_login_success(self, username):
        """Handle successful login"""
        print(f"✅ Login successful: {username}")
        self.login_window.hide()
        
        # Show DB Config window
        self.db_window = DbConfigWindow()
        self.db_window.connection_successful.connect(self.on_connection_success)
        self.db_window.show()
    
    def on_connection_success(self, conn):
        """Handle successful database connection"""
        print(f"✅ Database connection successful")
        self.db_window.hide()
        
        # Show Main Window (single window with navigation)
        self.main_window = MainWindow(conn)
        self.main_window.show()


def main():
    """Main application entry point"""
    app_controller = NEOMonitorApp()
    return app_controller.start()


if __name__ == "__main__":
    sys.exit(main())
