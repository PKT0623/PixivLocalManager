from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QStyleOptionButton,
    QStyledItemDelegate,
)


class CenterCheckBoxDelegate(QStyledItemDelegate):
    def paint(
        self,
        painter,
        option,
        index,
    ):
        checked = index.data(Qt.CheckStateRole) == Qt.Checked

        checkbox_option = QStyleOptionButton()
        checkbox_option.state = QStyle.State_Enabled

        if checked:
            checkbox_option.state |= QStyle.State_On
        else:
            checkbox_option.state |= QStyle.State_Off

        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()

        checkbox_rect = style.subElementRect(
            QStyle.SE_CheckBoxIndicator,
            checkbox_option,
            widget,
        )
        checkbox_rect.moveCenter(option.rect.center())
        checkbox_option.rect = checkbox_rect

        style.drawControl(
            QStyle.CE_CheckBox,
            checkbox_option,
            painter,
            widget,
        )

    def sizeHint(
        self,
        option,
        index,
    ):
        return QSize(36, option.rect.height())
