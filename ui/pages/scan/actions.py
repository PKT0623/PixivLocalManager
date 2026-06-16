from pathlib import Path

from .action_parts import (
    ScanFilterActions,
    ScanFolderActions,
    ScanResultActions,
    ScanWorkerActions,
)


class ScanActions(
    ScanFolderActions,
    ScanWorkerActions,
    ScanResultActions,
    ScanFilterActions,
):
    SCAN_RESULT_DIR = Path("data") / "scan_results"
    LATEST_SCAN_JSON_PATH = SCAN_RESULT_DIR / "latest_scan.json"
    LATEST_SCAN_CSV_PATH = SCAN_RESULT_DIR / "latest_scan.csv"
    RECENT_HISTORY_LIMIT = 10

    def __init__(self, page):
        self.page = page
        self.resume_payload = None
        self.current_run_preview_mode = False
