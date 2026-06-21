ARTIST_DETAIL_STYLES = """
QLabel#pageTitle {
    font-size: 28px;
    font-weight: 700;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
    margin-top: 8px;
}

QLabel#statusMessageLabel {
    padding: 8px 12px;
    border: 1px solid #cfe2ff;
    border-radius: 6px;
    background-color: #eef5ff;
    color: #0d6efd;
    font-size: 14px;
    font-weight: 700;
}

QLabel#historySummaryLabel {
    font-size: 14px;
    font-weight: 700;
    color: #0d6efd;
}

QFrame#infoFrame {
    border: 1px solid #dddddd;
    border-radius: 8px;
    background-color: #ffffff;
}

QPushButton#backButton,
QPushButton#refreshButton,
QPushButton#saveButton,
QPushButton#normalButton,
QPushButton#folderSelectButton,
QPushButton#copyButton,
QPushButton#shortcutButton,
QPushButton#artworkButton,
QPushButton#smallActionButton,
QPushButton#tagButton {
    padding: 8px 16px;
    border: 1px solid #cccccc;
    border-radius: 6px;
    background-color: #f5f5f5;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#saveButton {
    background-color: #198754;
    color: #ffffff;
    border-color: #198754;
    min-width: 80px;
}

QPushButton#backButton {
    min-width: 120px;
}

QPushButton#normalButton {
    min-width: 120px;
}

QPushButton#refreshButton,
QPushButton#folderSelectButton,
QPushButton#tagButton {
    min-width: 90px;
}

QPushButton#shortcutButton {
    min-width: 90px;
    padding: 6px 12px;
}

QPushButton#copyButton {
    min-width: 60px;
    padding: 6px 12px;
}

QPushButton#artworkButton {
    min-width: 110px;
    padding: 6px 12px;
}

QPushButton#smallActionButton {
    min-width: 60px;
    padding: 4px 10px;
}

QPushButton#backButton:hover,
QPushButton#refreshButton:hover,
QPushButton#normalButton:hover,
QPushButton#folderSelectButton:hover,
QPushButton#copyButton:hover,
QPushButton#shortcutButton:hover,
QPushButton#artworkButton:hover,
QPushButton#smallActionButton:hover,
QPushButton#tagButton:hover {
    background-color: #eeeeee;
}

QPushButton#saveButton:hover {
    background-color: #157347;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QLineEdit {
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 6px 8px;
    background-color: #ffffff;
    font-size: 14px;
}

QLineEdit:read-only {
    background-color: #f9f9f9;
}

QCheckBox {
    font-size: 14px;
    spacing: 6px;
}

QTableWidget {
    border: 1px solid #dddddd;
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 14px;
    gridline-color: #eeeeee;
}

QTextEdit {
    border: 1px solid #dddddd;
    border-radius: 8px;
    padding: 8px;
    background-color: #ffffff;
    font-size: 14px;
}
"""
