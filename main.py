import json
import sys, shutil, os
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QVBoxLayout, QButtonGroup, QFileDialog, QMessageBox, \
    QPushButton
from PyQt5.QtCore import Qt
from design import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.scroll_layout_left = QVBoxLayout()
        self.scroll_layout_left.setAlignment(Qt.AlignTop)
        self.scroll_layout_right = QVBoxLayout()
        self.scroll_layout_right.setAlignment(Qt.AlignTop)
        self.selected_buttons_group = QButtonGroup()
        self.unselected_buttons_group = QButtonGroup()

        self.OpenButton.clicked.connect(self.get_pack)
        self.CreateButton.clicked.connect(self.create_pack)
        self.AllToRightButton.clicked.connect(self.all_to_right)
        self.AllToLeftButton.clicked.connect(self.all_to_left)
        self.OutPathSelectButton.clicked.connect(self.select_out_path)

        got_pack = False
        while not got_pack:
            got_pack = self.get_pack()
            if got_pack == 'closed':
                exit()

    def create_pack(self):
        if os.path.exists(self.out_path):
            dialog = QMessageBox.question(self, 'Overwrite?',
                                          f'There is existing pack at {self.out_path}, do you want to overwrite it?')
            if dialog == QMessageBox.No:
                return
            shutil.rmtree(self.out_path)

        self.statusBar.showMessage('Creating biomes list...')
        selected = []
        for button in self.selected_buttons_group.buttons():
            selected.append(button.text())
        print(selected)

        self.statusBar.showMessage('Creating new overworld file...')
        new_overworld = self.overworld.copy()
        new_overworld["generator"]["biome_source"]["biomes"] = \
            list(filter(lambda biome: biome["biome"] in selected, self.overworld["generator"]["biome_source"]["biomes"]))
        if self.randomSeedBox.isChecked():
            self.statusBar.showMessage('Generating seed...')
            new_overworld["generator"]["seed"] = random.randint(-100000000000, 100000000000)

        self.statusBar.showMessage('Creating new pack...')
        shutil.copytree(self.path, self.out_path)
        with open(self.out_path + '/data/minecraft/dimension/overworld.json', 'w') as out:
            out.write(json.dumps(new_overworld))

        self.statusBar.showMessage('Done!', 5000)

    def all_to_right(self):
        for button in self.unselected_buttons_group.buttons():
            self.unselected_buttons_group.removeButton(button)
            self.selected_buttons_group.addButton(button)
            self.scroll_layout_left.removeWidget(button)
            self.scroll_layout_right.addWidget(button)
            self.scrollAreaWidgetContentsLeft.setLayout(self.scroll_layout_left)
            self.scrollAreaWidgetContentsRight.setLayout(self.scroll_layout_right)

    def all_to_left(self):
        for button in self.selected_buttons_group.buttons():
            self.selected_buttons_group.removeButton(button)
            self.unselected_buttons_group.addButton(button)
            self.scroll_layout_right.removeWidget(button)
            self.scroll_layout_left.addWidget(button)
            self.scrollAreaWidgetContentsRight.setLayout(self.scroll_layout_right)
            self.scrollAreaWidgetContentsLeft.setLayout(self.scroll_layout_left)

    def get_pack(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        path = dialog.getExistingDirectory(self, 'Select datapack folder', '../')
        if not path:
            return 'closed'
        self.path = path
        path = self.path + '/data/minecraft/dimension/overworld.json'
        try:
            self.overworld = json.loads(open(path, 'r').read())
            self.PathDisplay.setText(self.path)
            self.out_path = '/'.join(self.path.split('/')[:-1]) + '/GeneratedPack'
            self.OutPathDisplay.setText(self.out_path)
        except FileNotFoundError:
            QMessageBox().warning(dialog, 'Please select a pack',
                                  'You have to select a datapack folder (folder that contains pack.png, pack.mcmeta, etc)')
            return False

        while self.scroll_layout_left.count():  # Чистим layout
            child = self.scroll_layout_left.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.scroll_layout_right.count():  # Чистим layout
            child = self.scroll_layout_right.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for btn in self.selected_buttons_group.buttons():
            self.selected_buttons_group.removeButton(btn)
        for btn in self.unselected_buttons_group.buttons():
            self.unselected_buttons_group.removeButton(btn)

        names = sorted(list(set(map(lambda biome: biome["biome"],
                                    self.overworld["generator"]["biome_source"]["biomes"]))))
        for name in names:
            btn = QPushButton(name)
            btn.setText(name)
            self.selected_buttons_group.addButton(btn)
            self.scroll_layout_right.addWidget(btn)
            btn.clicked.connect(self.biome_button_pressed)

        self.scrollAreaWidgetContentsRight.setLayout(self.scroll_layout_right)
        self.scrollAreaWidgetContentsLeft.setLayout(self.scroll_layout_left)
        self.repaint()

        return True

    def select_out_path(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        path = dialog.getExistingDirectory(self, 'Select folder for generated pack...', '../')
        if path:
            self.out_path = path
            self.OutPathDisplay.setText(self.out_path)

    def biome_button_pressed(self):
        button = self.sender()
        if button in self.selected_buttons_group.buttons():
            self.selected_buttons_group.removeButton(button)
            self.unselected_buttons_group.addButton(button)
            self.scroll_layout_right.removeWidget(button)
            self.scroll_layout_left.addWidget(button)
            self.scrollAreaWidgetContentsRight.setLayout(self.scroll_layout_right)
            self.scrollAreaWidgetContentsLeft.setLayout(self.scroll_layout_left)
        elif button in self.unselected_buttons_group.buttons():
            self.unselected_buttons_group.removeButton(button)
            self.selected_buttons_group.addButton(button)
            self.scroll_layout_left.removeWidget(button)
            self.scroll_layout_right.addWidget(button)
            self.scrollAreaWidgetContentsLeft.setLayout(self.scroll_layout_left)
            self.scrollAreaWidgetContentsRight.setLayout(self.scroll_layout_right)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
