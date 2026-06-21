from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemDelegate,
    QStyle,
    QStyleOptionButton,
)


class CenterCheckBoxDelegate(QAbstractItemDelegate):
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

        checkbox_rect = option.widget.style().subElementRect(
            QStyle.SE_CheckBoxIndicator,
            checkbox_option,
            option.widget,
        )

        checkbox_option.rect = checkbox_rect
        checkbox_option.rect.moveCenter(option.rect.center())

        option.widget.style().drawControl(
            QStyle.CE_CheckBox,
            checkbox_option,
            painter,
            option.widget,
        )

    def sizeHint(
        self,
        option,
        index,
    ):
        return option.rect.size()
