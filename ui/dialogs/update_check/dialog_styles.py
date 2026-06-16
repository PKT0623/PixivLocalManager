UPDATE_CHECK_DIALOG_STYLE = """
QLabel#dialogTitle {
    font-size: 24px;
    font-weight: 800;
}

QLabel#descriptionLabel,
QLabel#statusLabel {
    font-size: 14px;
    color: #555555;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 700;
}

QFrame#optionFrame {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
}

QPushButton {
    padding: 8px 12px;
    border: 1px solid #cccccc;
    border-radius: 6px;
    background-color: #f5f5f5;
    font-size: 13px;
    font-weight: 600;
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

QTableWidget {
    border: 1px solid #dddddd;
    border-radius: 8px;
    background-color: #ffffff;
    gridline-color: #eeeeee;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #f5f5f5;
    border: none;
    border-bottom: 1px solid #dddddd;
    padding: 7px;
    font-weight: 700;
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
"""
