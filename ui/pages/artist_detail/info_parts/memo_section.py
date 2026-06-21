from PySide6.QtWidgets import QFrame, QLabel, QTextEdit, QVBoxLayout


class ArtistMemoSectionMixin:
    def _create_memo_frame(self) -> QFrame:
        memo_frame = QFrame()
        memo_frame.setObjectName("infoFrame")

        memo_layout = QVBoxLayout(memo_frame)
        memo_layout.setContentsMargins(16, 16, 16, 16)
        memo_layout.setSpacing(8)

        memo_label = QLabel("장문 메모")
        memo_label.setObjectName("sectionTitle")

        self.memo_edit = QTextEdit()
        self.memo_edit.setMinimumHeight(180)
        self.memo_edit.setPlaceholderText("작가에 대한 장문 메모를 입력하세요.")

        reference_links_label = QLabel("참고 링크")
        reference_links_label.setObjectName("sectionTitle")

        self.reference_links_edit = QTextEdit()
        self.reference_links_edit.setMinimumHeight(90)
        self.reference_links_edit.setPlaceholderText(
            "참고할 링크를 줄 단위로 입력하세요."
        )

        download_note_label = QLabel("다운로드 메모")
        download_note_label.setObjectName("sectionTitle")

        self.download_note_edit = QTextEdit()
        self.download_note_edit.setMinimumHeight(120)
        self.download_note_edit.setPlaceholderText(
            "다운로드 기준, 제외 조건, 주의사항 등을 입력하세요."
        )

        memo_layout.addWidget(memo_label)
        memo_layout.addWidget(self.memo_edit)
        memo_layout.addWidget(reference_links_label)
        memo_layout.addWidget(self.reference_links_edit)
        memo_layout.addWidget(download_note_label)
        memo_layout.addWidget(self.download_note_edit)

        return memo_frame
