STATISTICS_PAGE_STYLE = """
QWidget {
    font-family: "Segoe UI", "Malgun Gothic";
}

QLabel#pageTitle {
    font-size: 24px;
    font-weight: 700;
    color: #202124;
}

QLabel#pageDescription {
    font-size: 13px;
    color: #6c757d;
}

QPushButton#refreshButton {
    background-color: #2f6fed;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#refreshButton:hover {
    background-color: #255fd0;
}

QWidget#statisticsContent {
    background-color: transparent;
}

QWidget#sectionPanel {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #202124;
}

QLabel#subSectionTitle {
    font-size: 13px;
    font-weight: 700;
    color: #495057;
}

QLabel#sectionSummaryLabel {
    font-size: 12px;
    color: #6c757d;
}

QWidget#summaryCard,
QWidget#miniMetricCard {
    background-color: #ffffff;
    border: 1px solid #dfe3e8;
    border-radius: 12px;
}

QWidget#summaryCard:hover,
QWidget#miniMetricCard:hover {
    background-color: #f8f9fa;
}

QLabel#summaryCardTitle {
    font-size: 11px;
    color: #6c757d;
}

QLabel#miniMetricTitle {
    font-size: 11px;
    color: #6c757d;
}

QLabel#summaryCardValue {
    font-size: 17px;
    font-weight: 700;
    color: #202124;
}

QLabel#miniMetricValue {
    font-size: 17px;
    font-weight: 700;
    color: #202124;
}

QLabel#statusNameLabel,
QLabel#distributionNameLabel,
QLabel#qualityTitleLabel {
    font-size: 12px;
    color: #495057;
}

QLabel#statusValueLabel,
QLabel#distributionValueLabel,
QLabel#qualityValueLabel {
    font-size: 12px;
    color: #202124;
    font-weight: 700;
}

QLabel#qualityDetailLabel {
    font-size: 11px;
    color: #6c757d;
}

QProgressBar {
    height: 10px;
    border: none;
    border-radius: 5px;
    background-color: #e9ecef;
}

QProgressBar::chunk {
    border-radius: 5px;
    background-color: #2f6fed;
}

QProgressBar#statusProgress_up_to_date::chunk {
    background-color: #198754;
}

QProgressBar#statusProgress_need_update::chunk {
    background-color: #fd7e14;
}

QProgressBar#statusProgress_unknown::chunk {
    background-color: #6c757d;
}

QProgressBar#statusProgress_error::chunk {
    background-color: #dc3545;
}

QTabWidget::pane {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f1f3f5;
    color: #495057;
    padding: 8px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #2f6fed;
    color: #ffffff;
}

QTableWidget {
    border: none;
    gridline-color: #edf0f2;
    background-color: #ffffff;
    alternate-background-color: #f8f9fa;
    selection-background-color: #dbeafe;
    selection-color: #202124;
    font-size: 12px;
}

QHeaderView::section {
    background-color: #f1f3f5;
    color: #495057;
    border: none;
    border-bottom: 1px solid #dee2e6;
    padding: 7px 8px;
    font-weight: 700;
}

QTableWidget::item {
    padding: 6px 8px;
}
"""
