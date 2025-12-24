"""
Utility para garantir contraste adequado em QMessageBox
"""
from PyQt6.QtWidgets import QMessageBox


def show_info(parent, title: str, message: str):
    """Show information message with good contrast"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #ffffff;
        }
        QMessageBox QLabel {
            color: #212121;
            font-size: 11pt;
            min-width: 300px;
        }
        QMessageBox QPushButton {
            background-color: #1976d2;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #1565c0;
        }
    """)
    msg.exec()


def show_warning(parent, title: str, message: str):
    """Show warning message with good contrast"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #ffffff;
        }
        QMessageBox QLabel {
            color: #212121;
            font-size: 11pt;
            min-width: 300px;
        }
        QMessageBox QPushButton {
            background-color: #ffa726;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #fb8c00;
        }
    """)
    msg.exec()


def show_error(parent, title: str, message: str):
    """Show error message with good contrast"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #ffffff;
        }
        QMessageBox QLabel {
            color: #212121;
            font-size: 11pt;
            min-width: 300px;
        }
        QMessageBox QPushButton {
            background-color: #d32f2f;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #c62828;
        }
    """)
    msg.exec()


def show_message(parent, title: str, message: str, icon=QMessageBox.Icon.Information):
    """Generic message with custom icon and good contrast"""
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    
    # Choose button color based on icon type
    if icon == QMessageBox.Icon.Critical:
        button_color = "#d32f2f"
        button_hover = "#c62828"
    elif icon == QMessageBox.Icon.Warning:
        button_color = "#ffa726"
        button_hover = "#fb8c00"
    else:
        button_color = "#1976d2"
        button_hover = "#1565c0"
    
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: #ffffff;
        }}
        QMessageBox QLabel {{
            color: #212121;
            font-size: 11pt;
            min-width: 300px;
        }}
        QMessageBox QPushButton {{
            background-color: {button_color};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {button_hover};
        }}
    """)
    msg.exec()

