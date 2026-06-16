SCAN_PAGE_STYLES = """
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

QLabel#subSectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #333333;
}

QLabel#subText {
    font-size: 14px;
    color: #555555;
}

QFrame#inputFrame {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
}

QFrame#scanSubFrame {
    border: 1px solid #eeeeee;
    border-radius: 8px;
    background-color: #fafafa;
}

QLineEdit {
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 8px 10px;
    background-color: #f9f9f9;
    font-size: 14px;
}

QComboBox {
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 6px 10px;
    background-color: #ffffff;
    font-size: 13px;
    min-width: 100px;
}

QCheckBox {
    font-size: 13px;
    spacing: 6px;
}

QPushButton {
    padding: 8px 14px;
    border: 1px solid #cccccc;
    border-radius: 6px;
    background-color: #f5f5f5;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #eeeeee;
}

QPushButton#scanButton {
    background-color: #198754;
    color: #ffffff;
    border-color: #198754;
    min-width: 100px;
    max-width: 100px;
}

QPushButton#scanButton:hover {
    background-color: #157347;
}

QPushButton#folderSelectButton,
QPushButton#clearLogButton {
    min-width: 100px;
    max-width: 100px;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 8px;
    text-align: center;
    height: 22px;
    background-color: #f5f5f5;
    font-size: 13px;
    font-weight: 600;
}

QProgressBar::chunk {
    border-radius: 8px;
    background-color: #198754;
}

QTableWidget {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
    gridline-color: #eeeeee;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #f5f5f5;
    border: none;
    border-bottom: 1px solid #dddddd;
    padding: 8px;
    font-weight: 700;
}

QTableWidget::item {
    padding: 4px;
}
"""
