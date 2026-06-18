UPDATE_CHECK_PAGE_STYLES = """
QLabel#pageTitle {
    font-size: 28px;
    font-weight: 700;
}

QLabel#targetCountLabel {
    padding: 7px 14px;
    border-radius: 8px;
    background-color: #e9f5ff;
    color: #0d6efd;
    font-size: 14px;
    font-weight: 700;
}

QLabel#summaryValueLabel {
    font-size: 18px;
    font-weight: 800;
}

QLabel#summaryTextLabel {
    font-size: 12px;
    color: #666666;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 700;
}

QFrame#optionFrame,
QFrame#summaryFrame,
QFrame#progressFrame,
QFrame#tableFrame,
QFrame#logFrame {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
}

QFrame#summaryItemFrame {
    border: 1px solid #eeeeee;
    border-radius: 8px;
    background-color: #fafafa;
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

QPushButton:disabled {
    color: #999999;
    background-color: #eeeeee;
    border-color: #dddddd;
}

QTableWidget {
    border: none;
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