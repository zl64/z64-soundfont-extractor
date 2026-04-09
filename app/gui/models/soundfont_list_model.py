from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

from app.core.n64_rom import Soundfont


class SoundfontListModel(QAbstractListModel):
    def __init__(self) -> None:
        super().__init__()
        self._items: list[Soundfont] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._items)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        soundfont = self._items[index.row()]

        match role:
            case Qt.ItemDataRole.DisplayRole:
                return soundfont.display_name
            case Qt.ItemDataRole.UserRole:
                return soundfont
            case _:
                return None

    def set_items(self, items: list[Soundfont]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()