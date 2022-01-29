import json
import sys, shutil, os
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QVBoxLayout, QButtonGroup, QFileDialog, QMessageBox
from design import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.scroll_layout = QVBoxLayout()
        self.biome_buttons_group = QButtonGroup()
        self.biome_buttons_group.setExclusive(False)

        self.OpenButton.clicked.connect(self.get_pack)
        self.CreateButton.clicked.connect(self.create_pack)
        self.AllButton.clicked.connect(self.check_all)
        self.NoneButton.clicked.connect(self.uncheck_all)
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
        checked = []
        for button in self.biome_buttons_group.buttons():
            if button.isChecked():
                checked.append(button.text())
        print(checked)

        self.statusBar.showMessage('Creating new overworld file...')
        new_overworld = self.overworld.copy()
        new_overworld["generator"]["biome_source"]["biomes"] = \
            list(filter(lambda biome: biome["biome"] in checked, self.overworld["generator"]["biome_source"]["biomes"]))
        if self.randomSeedBox.isChecked():
            self.statusBar.showMessage('Generating seed...')
            new_overworld["generator"]["seed"] = random.randint(-100000000000, 100000000000)

        self.statusBar.showMessage('Creating new pack...')
        shutil.copytree(self.path, self.out_path)
        with open(self.out_path + '/data/minecraft/dimension/overworld.json', 'w') as out:
            out.write(json.dumps(new_overworld))

        self.statusBar.showMessage('Done!', 5000)

    def check_all(self):
        for button in self.biome_buttons_group.buttons():
            button.setChecked(True)

    def uncheck_all(self):
        for button in self.biome_buttons_group.buttons():
            button.setChecked(False)

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

        while self.scroll_layout.count():  # Чистим layout
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        names = list(set(map(lambda biome: biome["biome"], self.overworld["generator"]["biome_source"]["biomes"])))
        for name in names:
            box = QCheckBox(name)
            box.setChecked(True)
            self.scroll_layout.addWidget(box)
            self.biome_buttons_group.addButton(box)

        self.scrollAreaWidgetContents.setLayout(self.scroll_layout)
        self.repaint()

        return True

    def select_out_path(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        path = dialog.getExistingDirectory(self, 'Select folder for generated pack...', '../')
        if path:
            self.out_path = path
            self.OutPathDisplay.setText(self.out_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
