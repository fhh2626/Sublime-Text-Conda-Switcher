# Conda Switcher v0.1 alpha
# by Haohao Fu (fhh2626_at_gmail.com)
#
#
########################################################################
# The aim of this tool is to provide a simple way to use 
# Sublime Text 4 + pyright + conda, by switching conda env 
# for both ST4 and pyright
########################################################################


import os, json

# the name of Python binary is different in different OS
if os.name == 'nt':
    PYTHON_BIN = 'python.exe'
elif os.name == 'posix':
    PYTHON_BIN = 'python'
else:
    raise RuntimeError(f"Unknown : {os_type}")

class CondaSwicher:
    def __init__(self, conda_path, config_path):
        self.conda_path = conda_path
        self.config_path = config_path

        self._GetCondaEnvs()

    def _GetCondaEnvs(self):
        items = os.listdir(self.conda_path + "/envs")

        # including base env
        self.env_names = ['base']
        self.env_paths = [os.path.join(self.conda_path, PYTHON_BIN)]


        for item in items:
            complete_path = os.path.join(self.conda_path, 'envs', item)
            if os.path.isdir(complete_path):
                python_exe_path = os.path.join(complete_path, PYTHON_BIN)

                if os.path.isfile(python_exe_path):
                    self.env_names.append(item)
                    self.env_paths.append(python_exe_path)

    def GetCondaEnvs(self):
        return self.env_names, self.env_paths

    def UpdateEnv(self, name):
        build_file = os.path.join(self.config_path, 'conda.sublime-build')
        path = self.env_paths[self.env_names.index(name)]

        if os.path.isfile(build_file):
            with open(build_file, 'r') as json_file:
                build_json = json.load(json_file)
            build_json['shell_cmd'] = f'{path} $file'
        else:
            build_json = {
                'shell_cmd': f'{path} $file'
            }
        with open(build_file, 'w') as file:
            json.dump(build_json, file)

    def UpdatePyrightEnv(self, name):
        build_file = os.path.join(self.config_path, 'LSP-pyright.sublime-settings')
        path = self.env_paths[self.env_names.index(name)]

        if os.path.isfile(build_file):
            with open(build_file, 'r') as json_file:
                build_json = json.load(json_file)
            build_json['settings']['python.pythonPath'] = path
        else:
            build_json = {
                'settings': {
		            'python.pythonPath': 
                    {
                        path,
                    }
	            }
            }
        with open(build_file, 'w') as file:
            json.dump(build_json, file)


import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFileDialog,
                               QPushButton, QLineEdit, QLabel, QListWidget, QGroupBox, QWidget)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CondaSwicher v0.1a")

        self._InitMainUI()
        self._LoadPath()
        self._ConnectSignalsSlots()
        self._Refresh()

        self.setGeometry(100, 100, 600, 400)

    def _InitMainUI(self):
        self.main_layout = QVBoxLayout()

        # set conda path selector
        self.conda_path_groupbox = QGroupBox("Conda Path")
        self.conda_path_layout = QHBoxLayout()

        self.conda_path_lineedit = QLineEdit()
        self.conda_path_button = QPushButton("Browse")

        self.conda_path_layout.addWidget(self.conda_path_lineedit)
        self.conda_path_layout.addWidget(self.conda_path_button)
        
        self.conda_path_groupbox.setLayout(self.conda_path_layout)

        # set config path selector
        self.config_path_groupbox = QGroupBox("Sublime Text Config Path")
        self.config_path_layout = QHBoxLayout()

        self.config_path_lineedit = QLineEdit()
        self.config_path_button = QPushButton("Browse")

        self.config_path_layout.addWidget(self.config_path_lineedit)
        self.config_path_layout.addWidget(self.config_path_button)
        
        self.config_path_groupbox.setLayout(self.config_path_layout)

        # list of envs
        self.env_groupbox = QGroupBox("Select envs")
        self.env_layout = QHBoxLayout()
        self.env_button_layout = QVBoxLayout()

        self.env_list = QListWidget()
        self.env_refresh_button = QPushButton("Refresh")
        self.env_change_button = QPushButton("Change")
        self.env_exit_button = QPushButton("Exit")

        self.env_button_layout.addWidget(self.env_refresh_button)
        self.env_button_layout.addWidget(self.env_change_button)
        self.env_button_layout.addWidget(self.env_exit_button)

        self.env_layout.addWidget(self.env_list)
        self.env_layout.addLayout(self.env_button_layout)

        self.env_groupbox.setLayout(self.env_layout)

        self.main_layout.addWidget(self.conda_path_groupbox)
        self.main_layout.addWidget(self.config_path_groupbox)
        self.main_layout.addWidget(self.env_groupbox)
        self.setLayout(self.main_layout)

    def _SavePath(self):

        if (not os.path.isdir(self.conda_path_lineedit.text())) or \
        (not os.path.isdir(self.config_path_lineedit.text())):
            return

        data = {
            'conda_path': self.conda_path_lineedit.text(),
            'config_path': self.config_path_lineedit.text()
        }

        with open('./CondaSwicher.sav', 'w') as file:
            json.dump(data, file)

    def _LoadPath(self):
        if os.path.isfile('./CondaSwicher.sav'):
            with open('./CondaSwicher.sav', 'r') as file:
                data = json.load(file)
            self.conda_path_lineedit.setText(data['conda_path'])
            self.config_path_lineedit.setText(data['config_path'])

    def _ConnectSignalsSlots(self):
        self.conda_path_button.clicked.connect(self._OpenFolderDialog(self.conda_path_lineedit))
        self.config_path_button.clicked.connect(self._OpenFolderDialog(self.config_path_lineedit))
        self.env_refresh_button.clicked.connect(self._Refresh)
        self.env_change_button.clicked.connect(self._SwitchCondaEnv)
        self.env_exit_button.clicked.connect(self._SavePath)
        self.env_exit_button.clicked.connect(QApplication.quit)

    # slot functions
    def _Refresh(self):
        self.env_list.clear()

        if (not os.path.isdir(self.conda_path_lineedit.text())) or \
        (not os.path.isdir(self.config_path_lineedit.text())):
            return

        self.conda_switcher = CondaSwicher(
            self.conda_path_lineedit.text(),
            self.config_path_lineedit.text()
        )

        for item in self.conda_switcher.GetCondaEnvs()[0]:
            self.env_list.addItem(item)

    def _OpenFolderDialog(self, lineEdit):
        def OpenFile():
            fileName = QFileDialog.getExistingDirectory(self, "Choose a folder")
            lineEdit.setText(fileName)
        return OpenFile

    def _SwitchCondaEnv(self):
        if self.env_list.count() > 0:
            env = self.env_list.currentItem().text()
            self.conda_switcher.UpdateEnv(env)
            self.conda_switcher.UpdatePyrightEnv(env)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
