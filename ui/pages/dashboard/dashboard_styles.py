DASHBOARD_PAGE_STYLE = """
QLabel#pageTitle {
    font-size: 26px;
    font-weight: 700;
}

QLabel#pageDescription {
    font-size: 14px;
    color: #666666;
}

QPushButton {
    padding: 6px 10px;
    border: 1px solid #cccccc;
    border-radius: 6px;
    background-color: #f5f5f5;
    font-size: 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #eeeeee;
}

QPushButton:disabled {
    color: #999999;
    background-color: #eeeeee;
    border-color: #dddddd;
}

QPushButton#refreshButton,
QPushButton#limitButton {
    min-width: 52px;
}

QPushButton#limitButton[active="true"] {
    background-color: #198754;
    color: #ffffff;
    border-color: #198754;
}

QFrame#summaryCard,
QFrame#detailCard,
QFrame#artistCard,
QFrame#randomCard,
QFrame#rankingCard,
QFrame#statusMetricCard {
    border: 1px solid #dddddd;
    border-radius: 10px;
    background-color: #ffffff;
}

QFrame#rankingCard {
    background-color: #fafafa;
}

QLabel#cardTitle {
    font-size: 11px;
    color: #666666;
    font-weight: 600;
}

QLabel#cardValue {
    font-size: 18px;
    font-weight: 800;
    color: #202124;
}

QLabel#sectionTitle {
    font-size: 17px;
    font-weight: 700;
}

QLabel#sectionSubTitle {
    font-size: 14px;
    font-weight: 700;
    color: #333333;
}

QLabel#subText {
    font-size: 12px;
    color: #777777;
}

QLabel#statusMetricValue {
    font-size: 22px;
    font-weight: 800;
    color: #202124;
}

QLabel#statusMetricTitle {
    font-size: 11px;
    color: #666666;
    font-weight: 600;
}

QLabel#statusDistributionTitle {
    font-size: 13px;
    color: #555555;
    font-weight: 600;
}

QLabel#statusDistributionValue {
    font-size: 14px;
    color: #202124;
    font-weight: 800;
}

QLabel#thumbnailLabel {
    background-color: #f1f3f5;
    border: 1px solid #dddddd;
    border-radius: 8px;
    color: #777777;
}

QLabel#artistName {
    font-size: 14px;
    font-weight: 700;
}

QLabel#artistInfo {
    font-size: 12px;
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
    font-size: 13px;
}

QHeaderView::section {
    background-color: #f5f5f5;
    border: none;
    border-bottom: 1px solid #dddddd;
    padding: 6px;
    font-weight: 700;
}

QTableWidget::item {
    padding: 3px;
}
"""
