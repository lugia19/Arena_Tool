"""The Arena Maker window: the fight library plus building and launching. Run with `python -m arena_maker.gui`."""
import os
import sys
import traceback

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QCheckBox, QFileDialog, QHBoxLayout, QHeaderView, QMainWindow,
                             QMessageBox, QPlainTextEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                             QWidget)

from . import library, tools
from .build import PROFILE_NAME, build
from .package import launch
from .steam import find_game_dir

STYLESHEET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "stylesheet.qss")


class BuildWorker(QObject):
    log = pyqtSignal(str)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, fights, game_dir, data_dir, hide_vanilla, launch_after):
        super().__init__()
        self.args = (fights, game_dir, data_dir, hide_vanilla, launch_after)

    def run(self):
        fights, game_dir, data_dir, hide_vanilla, launch_after = self.args
        try:
            build(fights, game_dir, data_dir, hide_vanilla_arena=hide_vanilla, log=self.log.emit)
            self.log.emit("Build finished.")
            if launch_after:
                launch(tools.ME3, os.path.join(data_dir, PROFILE_NAME))
                self.log.emit("Game started.")
        except Exception:
            self.failed.emit(traceback.format_exc())
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self, data_dir: str):
        super().__init__()
        self.setWindowTitle("Arena Maker")
        self.resize(760, 520)
        self.setAcceptDrops(True)
        self.lib = library.load_library(data_dir)
        self.thread = self.worker = None

        self.fights = QTreeWidget()
        self.fights.setHeaderLabels(["#", "Tab", "Name", "Author"])
        self.fights.setRootIsDecorated(False)
        header = self.fights.header()  # Name takes the spare width; nothing to drag, so no horizontal scrollbar
        header.setStretchLastSection(False)
        for column, mode in enumerate((QHeaderView.ResizeMode.ResizeToContents, QHeaderView.ResizeMode.ResizeToContents,
                                       QHeaderView.ResizeMode.Stretch, QHeaderView.ResizeMode.ResizeToContents)):
            header.setSectionResizeMode(column, mode)
        self.hide_vanilla = QCheckBox("Hide vanilla arena")
        self.hide_vanilla.toggled.connect(self.set_hide_vanilla)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        def button(text, slot):
            widget = QPushButton(text)
            widget.clicked.connect(slot)
            return widget

        self.buttons = [button("▲", lambda: self.move_selected(-1)), button("▼", lambda: self.move_selected(1)),
                        button("Add folder…", self.add_folder), button("Add zip…", self.add_zip),
                        button("Remove", self.remove_selected), button("Open data folder", self.open_data_folder),
                        button("Build", lambda: self.start_build(False)),
                        button("Build && launch", lambda: self.start_build(True))]
        up, down, add_folder, add_zip, remove, open_folder, build_button, build_launch = self.buttons

        arrows = QVBoxLayout()
        arrows.addWidget(up)
        arrows.addWidget(down)
        arrows.addStretch()
        top = QHBoxLayout()
        top.addWidget(self.fights)
        top.addLayout(arrows)
        edit_row = QHBoxLayout()
        for widget in (add_folder, add_zip, remove):
            edit_row.addWidget(widget)
        edit_row.addStretch()
        edit_row.addWidget(self.hide_vanilla)
        build_row = QHBoxLayout()
        build_row.addWidget(open_folder)
        build_row.addStretch()
        build_row.addWidget(build_button)
        build_row.addWidget(build_launch)
        layout = QVBoxLayout()
        for row in (top, edit_row, build_row):
            layout.addLayout(row)
        layout.addWidget(self.log)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.refresh()

    # region Library
    def refresh(self, select: int = None):
        self.fights.clear()
        for number, (fight, _) in enumerate(library.library_fights(self.lib), 1):
            self.fights.addTopLevelItem(QTreeWidgetItem([str(number), fight.tab, fight.name, fight.author]))
        if select is not None and 0 <= select < self.fights.topLevelItemCount():
            self.fights.setCurrentItem(self.fights.topLevelItem(select))
        self.hide_vanilla.blockSignals(True)
        self.hide_vanilla.setChecked(self.lib.hide_vanilla)
        self.hide_vanilla.blockSignals(False)

    def selected(self):
        item = self.fights.currentItem()
        return self.fights.indexOfTopLevelItem(item) if item else None

    def add_paths(self, paths):
        for path in paths:
            try:
                for message in library.import_source(self.lib, path):
                    self.log.appendPlainText(message)
            except Exception as error:
                QMessageBox.critical(self, "Couldn't add fight", f"{path}\n\n{error}")
        self.refresh()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Add a fight or pack folder")
        if folder:
            self.add_paths([folder])

    def add_zip(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Add fight zips", "", "Zip files (*.zip)")
        self.add_paths(paths)

    def remove_selected(self):
        index = self.selected()
        if index is None:
            return
        entry = self.lib.entries[index]
        if QMessageBox.question(self, "Remove fight", f"Remove {entry.name} by {entry.author}?") == QMessageBox.StandardButton.Yes:
            library.remove(self.lib, index)
            self.refresh(min(index, len(self.lib.entries) - 1))

    def move_selected(self, offset: int):
        index = self.selected()
        if index is None or not 0 <= index + offset < len(self.lib.entries):
            return
        library.move(self.lib, index, index + offset)
        self.refresh(index + offset)

    def set_hide_vanilla(self, checked: bool):
        self.lib.hide_vanilla = checked
        library.save_library(self.lib)

    def open_data_folder(self):
        os.makedirs(self.lib.data_dir, exist_ok=True)
        os.startfile(self.lib.data_dir)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.add_paths([url.toLocalFile() for url in event.mimeData().urls()])
    # endregion

    # region Building
    def start_build(self, launch_after: bool):
        if not self.lib.entries:
            QMessageBox.information(self, "Nothing to build", "Add some fights first.")
            return
        game_dir = find_game_dir() or self.lib.game_dir
        if not game_dir:
            game_dir = QFileDialog.getExistingDirectory(self, "Select the ARMORED CORE VI Game folder")
            if not game_dir or not os.path.exists(os.path.join(game_dir, "armoredcore6.exe")):
                QMessageBox.warning(self, "Game not found", "That folder doesn't contain armoredcore6.exe.")
                return
            self.lib.game_dir = game_dir
            library.save_library(self.lib)
        try:
            fights = library.library_fights(self.lib)
        except Exception as error:
            QMessageBox.critical(self, "Couldn't load the fights", str(error))
            return

        for widget in self.buttons:
            widget.setEnabled(False)
        self.log.appendPlainText("Building...")
        self.thread = QThread()
        self.worker = BuildWorker(fights, game_dir, self.lib.data_dir, self.lib.hide_vanilla, launch_after)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.log.appendPlainText)
        self.worker.failed.connect(lambda details: QMessageBox.critical(self, "Build failed", details))
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.build_finished)
        self.thread.start()

    def build_finished(self):
        for widget in self.buttons:
            widget.setEnabled(True)
        self.thread = self.worker = None
    # endregion


def main():
    app = QApplication(sys.argv)
    with open(STYLESHEET, encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    try:
        tools.check_tools()
    except FileNotFoundError as error:
        QMessageBox.critical(None, "Arena Maker", str(error))
        sys.exit(1)
    window = MainWindow(library.DEFAULT_DATA_DIR)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
