SETTINGS_PAGE_STYLE = """
QLabel#pageTitle {
    font-size: 28px;
    font-weight: 700;
}

QLabel#pageDescription {
    font-size: 15px;
    color: #666666;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
}

QLabel#fieldLabel {
    font-size: 14px;
    font-weight: 600;
    color: #333333;
}

QLabel#statusLabel {
    font-size: 14px;
    color: #198754;
    padding-top: 4px;
}

QLabel#infoText {
    font-size: 14px;
    color: #555555;
}

QTabWidget#settingsTabWidget::pane {
    border: none;
    background-color: transparent;
}

QTabBar::tab {
    padding: 10px 22px;
    margin-right: 4px;
    border: 1px solid #dddddd;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    background-color: #f5f5f5;
    font-size: 14px;
    font-weight: 600;
    color: #555555;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #198754;
    border-color: #dddddd;
}

QTabBar::tab:hover {
    background-color: #eeeeee;
}

QFrame#settingFrame {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
}

QLineEdit {
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 8px 10px;
    background-color: #ffffff;
    font-size: 14px;
}

QLineEdit:read-only {
    background-color: #f9f9f9;
    color: #555555;
}

QSpinBox {
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 6px 8px;
    background-color: #ffffff;
    font-size: 14px;
}

QCheckBox {
    font-size: 14px;
    color: #333333;
}

QPushButton {
    padding: 8px 14px;
    border: 1px solid #cccccc;
    border-radius: 6px;
    background-color: #f5f5f5;
    font-size: 14px;
    font-weight: 600;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #eeeeee;
}

QPushButton#primaryButton {
    background-color: #198754;
    color: #ffffff;
    border-color: #198754;
}

QPushButton#primaryButton:hover {
    background-color: #157347;
}

QPushButton#dangerButton {
    background-color: #dc3545;
    color: #ffffff;
    border-color: #dc3545;
}

QPushButton#dangerButton:hover {
    background-color: #bb2d3b;
}

QTextEdit {
    border: 1px solid #dddddd;
    border-radius: 6px;
    background-color: #ffffff;
    font-size: 13px;
    padding: 8px;
}

QTableWidget {
    border: 1px solid #dddddd;
    border-radius: 6px;
    background-color: #ffffff;
    alternate-background-color: #f8f9fa;
    gridline-color: #eeeeee;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #f1f3f5;
    border: none;
    border-right: 1px solid #dddddd;
    border-bottom: 1px solid #dddddd;
    padding: 7px;
    font-weight: 700;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #111111;
}
"""
