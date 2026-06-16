DASHBOARD_PAGE_STYLE = """
QLabel#pageTitle {
    font-size: 28px;
    font-weight: 700;
}

QLabel#pageDescription {
    font-size: 15px;
    color: #666666;
}

QPushButton {
    padding: 7px 12px;
    border: 1px solid #cccccc;
    border-radius: 6px;
    background-color: #f5f5f5;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #eeeeee;
}

QPushButton#refreshButton,
QPushButton#limitButton {
    min-width: 58px;
}

QPushButton#limitButton[active="true"] {
    background-color: #198754;
    color: #ffffff;
    border-color: #198754;
}

QFrame#summaryCard,
QFrame#detailCard,
QFrame#artistCard,
QFrame#randomCard {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
}

QLabel#cardTitle {
    font-size: 14px;
    color: #666666;
    font-weight: 600;
}

QLabel#cardValue {
    font-size: 30px;
    font-weight: 800;
    color: #202124;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
}

QLabel#subText {
    font-size: 13px;
    color: #777777;
}

QLabel#recentScanValue {
    font-size: 18px;
    font-weight: 700;
    color: #202124;
}

QLabel#thumbnailLabel {
    background-color: #f1f3f5;
    border: 1px solid #dddddd;
    border-radius: 8px;
    color: #777777;
}

QLabel#artistName {
    font-size: 15px;
    font-weight: 700;
}

QLabel#artistInfo {
    font-size: 13px;
    color: #555555;
}

QLabel#randomHiddenText {
    font-size: 18px;
    font-weight: 800;
    color: #202124;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QTableWidget {
    border: none;
    background-color: #ffffff;
    gridline-color: #eeeeee;
    font-size: 14px;
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
