"""
NEO Monitor V2 - Main Entry Point
Clean, modern, professional asteroid monitoring system
"""
import sys
from PyQt6.QtWidgets import QApplication
from frontend.ui.login import LoginWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("NEO Monitor V2")
    app.setOrganizationName("UBI")
    
    # Create and show login window
    login_window = LoginWindow()
    
    # Handle successful login
    def on_login_success(username):
        print(f"✅ Login successful: {username}")
        login_window.close()
        # TODO: Open main dashboard window
        print("🚧 Dashboard coming next!")
        
    login_window.login_successful.connect(on_login_success)
    login_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
