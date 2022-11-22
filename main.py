import filecmp
import sys
import platform
import subprocess
import os
import shutil
import time

from PyQt5.QtGui import QFont

import info
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidget, QWidget
from WindowUI import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
	def showAbout(self):
		QMessageBox.about(self, "Code Checker", info.ABOUT)

	def addFiles(self, listWidget: QListWidget):  # Add file into corresponding list
		def add():
			files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "./")  # Let user select and open files
			for file in files:
				if listWidget is self.codeList:  # Source code file
					if file in self.codeFiles:  # File is already added
						QMessageBox.information(self, "重复文件", info.REPEAT_FILE, QMessageBox.Yes)
						continue
					self.codeFiles.add(file)
				elif listWidget is self.dataList:  # Date generator file
					if file in self.dataFiles:
						QMessageBox.information(self, "重复文件", info.REPEAT_FILE, QMessageBox.Yes)
						continue
					self.dataFiles.add(file)
				listWidget.addItem(file)
		return add

	def removeFiles(self, listWidget: QListWidget):
		def remove():
			selectedFiles = listWidget.selectedItems()
			for file in selectedFiles:
				listWidget.takeItem(listWidget.row(file))
				# filePath = file.text().split('. ')[1]
				if listWidget is self.codeList:
					self.codeFiles.remove(file.text())
				elif listWidget is self.dataList:
					self.dataFiles.remove(file.text())
		return remove

	def getExtension(self, string):
		return string.split('.')[-1]

	def addProcessInfo(self, info):
		self.infoText.append(info)
		QApplication.processEvents()  # Refresh the window

	def setAllButtons(self, enable):
		self.startButton.setEnabled(enable)
		self.addCode.setEnabled(enable)
		self.addData.setEnabled(enable)
		self.removeCode.setEnabled(enable)
		self.removeData.setEnabled(enable)

	def generateData(self, idData, data):
		# Generate data
		self.addProcessInfo(f"Checking on data {idData}...")
		self.addProcessInfo(f"\t-Generating data {idData}")
		data_extension = self.getExtension(data)
		file = open(self.data_folder_path + "/data.in", "w")
		file.close()
		if data_extension == 'py':  # Python
			dataStatus = subprocess.call("python " + data + " > " + self.data_folder_path + "/data.in", shell=True)
		elif data_extension in ['c', 'cpp']:  # C/C++
			compiler = 'gcc' if data_extension == 'c' else 'g++'
			exe_suffix = ".exe" if platform.system() == 'Windows' else ""
			dataStatus = subprocess.call(compiler + " " + data + " -o " + self.data_folder_path + "/data"+exe_suffix, shell=True)
			if dataStatus == 0:
				command = self.data_folder_path + "/data" + exe_suffix + " > " + self.data_folder_path + "/data.in"
				if platform.system() == 'Windows':
					command = "start /b " + command
				dataStatus = subprocess.call(command, shell=True)
		elif data_extension == 'in':  # text file (.in)
			dataStatus = 0
			shutil.copy(data, self.data_folder_path + "/data.in")
		else:
			QMessageBox.critical(self, "错误", info.FILE_ERR)
			return 1
		if dataStatus != 0:
			QMessageBox.critical(self, "错误", info.RE(dataStatus))
			return 1
		self.addProcessInfo(f"\t-Data{idData} generated.")
		return 0

	def runCode(self, idCode, code):
		self.addProcessInfo(f"\tRunning code {idCode}...")
		code_extension = self.getExtension(code)
		file = open(self.out_folder_path + f"/out{idCode}.out", "w")
		file.close()
		data = self.data_folder_path+'/data.in'
		if code_extension == 'py':  # Python
			codeStatus = subprocess.call("python " + code + " < " + data + " > " + self.out_folder_path + f"/out{idCode}.out", shell=True)
		elif code_extension in ['c', 'cpp']:  # C/C++
			compiler = 'gcc' if code_extension == 'c' else 'g++'
			exe_suffix = ".exe" if platform.system() == 'Windows' else ""
			codeStatus = subprocess.call(
				compiler + " " + code + " -o " + self.out_folder_path + f"/code{idCode}",
				shell=True)
			if codeStatus == 0:
				command = self.out_folder_path + f"/code{idCode}" + exe_suffix + " < " + data + " > " + self.out_folder_path + f"/out{idCode}.out"
				if platform.system() == 'Windows':
					command = "start /b " + command
				codeStatus = subprocess.call(command, shell=True)
		else:
			QMessageBox.critical(self, "错误", info.FILE_ERR)
			return 1

		if codeStatus != 0:
			QMessageBox.critical(self, "错误", info.RE(codeStatus))
			return 1
		return 0

	def compareFiles(self, idData):
		files = []
		for idOut in range(len(self.codeFiles)):
			files.append(self.out_folder_path + (f"/out{idOut + 1}.out" if platform.system() == 'Linux' else f"\\out{idOut + 1}.out"))
		match = True
		for i in range(1, len(files)):
			if not filecmp.cmp(files[i], files[i - 1]):
				# print(files[i-1], files[i])
				# print(filecmp.cmp(files[i], files[i - 1]))
				match = False
		if match:
			self.addProcessInfo(f"All results match for data{idData + 1}")
		else:
			QMessageBox.critical(self, "糟糕", "拍不上了!!!")
			self.addProcessInfo("Mismatches occurred while comparing.")
			return 1
		return 0

	def checkCode(self):
		if self.checkTime.value() not in range(0, 101):
			QMessageBox.Warning(self, "你很危险啊!!!", "对拍次数超出范围")
			return
		self.setAllButtons(False)
		self.infoText.clear()
		self.addProcessInfo("Start Checking. Creating folder...")

		# Create Folders
		if not os.path.exists(self.folder_path):
			os.mkdir(self.folder_path)
		if not os.path.exists(self.data_folder_path):
			os.mkdir(self.data_folder_path)
		if not os.path.exists(self.out_folder_path):
			os.mkdir(self.out_folder_path)
		self.addProcessInfo("Done.")

		# Check
		count = self.checkTime.value()
		for _ in range(count):
			flag = True
			for idData, data in enumerate(self.dataFiles):
				dataStatus = self.generateData(idData + 1, data)
				if dataStatus != 0:
					break

				# Run codes
				self.addProcessInfo(f"Running code with data{idData + 1}")
				fail = False
				for idCode, code in enumerate(self.codeFiles):
					codeStatus = self.runCode(idCode + 1, code)
					if codeStatus != 0:
						fail = True
						break
				if fail:
					break
				self.addProcessInfo("Output generated.")

				# Compare .out files
				# time.sleep(0.5)
				match = self.compareFiles(idData)
				if match != 0:
					flag = False
					break
			if not flag:
				break

		# All work done
		self.addProcessInfo("All Checking Process Done.")
		self.setAllButtons(True)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.codeFiles = set()
		self.dataFiles = set()
		self.setupUi(self)

		# About menu action
		self.actionAbout.triggered.connect(self.showAbout)

		# Folder paths
		self.folder_path = "./check" if platform.system() == 'Linux' else '.\\check'
		self.data_folder_path = self.folder_path + ("/data" if platform.system() == 'Linux' else "\\data")
		self.out_folder_path = self.folder_path + ("/out" if platform.system() == 'Linux' else "\\out")

		# Lists action
		self.cnt_data = 0
		self.cnt_code = 0

		self.addCode.clicked.connect(self.addFiles(self.codeList))
		self.removeCode.clicked.connect(self.removeFiles(self.codeList))

		self.addData.clicked.connect(self.addFiles(self.dataList))
		self.removeData.clicked.connect(self.removeFiles(self.dataList))

		# Check button
		self.startButton.clicked.connect(self.checkCode)

		# Set infoText font
		if platform.system() == 'Linux':
			self.infoText.setFont(QFont("Noto Sans", 12, QFont.Medium))
		elif platform.system() == 'Windows':
			self.infoText.setFont(QFont("Microsoft YaHei", 12, QFont.Medium))


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
