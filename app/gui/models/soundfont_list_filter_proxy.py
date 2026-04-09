from PySide6.QtCore import QSortFilterProxyModel, Qt


class SoundfontListFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._show_modified_only: bool = False
        self._vanilla_hashes: list[str] = []

    def set_filter(self, enabled: bool, vanilla_hashes: list[str]) -> None:
        self._show_modified_only = enabled
        self._vanilla_hashes = vanilla_hashes
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        model = self.sourceModel()
        if model is None:
            return True

        if not self._show_modified_only:
            return True

        source_index = self.sourceModel().index(source_row, 0, source_parent)
        soundfont = source_index.data(Qt.ItemDataRole.UserRole)

        if not soundfont:
            return False

        return not soundfont.is_vanilla(self._vanilla_hashes)