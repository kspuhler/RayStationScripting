from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel, QTextEdit


import sys

import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Launcher.PreplanLauncher.publishedScripts import publishedScripts



class ClassSelector(QWidget):
    def __init__(self, classDict):
        super().__init__()
        self.classDict = classDict
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Preplan script selector")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select a script to run:"))

        self.comboBox = QComboBox()
        self.comboBox.addItems(self.classDict.keys())
        self.comboBox.currentTextChanged.connect(self.updateInfo)
        layout.addWidget(self.comboBox)

        self.infoDisplay = QTextEdit()
        self.infoDisplay.setReadOnly(True)
        layout.addWidget(self.infoDisplay)

        self.goButton = QPushButton("Go")
        self.goButton.clicked.connect(self.instantiateClass)
        layout.addWidget(self.goButton)

        self.setLayout(layout)
        self.updateInfo(self.comboBox.currentText())

    def updateInfo(self, selectedText):
        classRef = self.classDict[selectedText]
        try:
            infoText = classRef.getInfo()  # Must be a @classmethod
        except Exception as e:
            infoText = f"Could not retrieve info: {str(e)}"
        self.infoDisplay.setPlainText(infoText)

    def instantiateClass(self):
        selectedText = self.comboBox.currentText()
        classRef = self.classDict[selectedText]
        instance = classRef()
        print(f"Instantiated: {instance.__class__.__name__}")
        self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClassSelector(publishedScripts)
    window.show()
    sys.exit(app.exec_())