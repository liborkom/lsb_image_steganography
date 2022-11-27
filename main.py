"""
The core file of the application containing and running all the code for GUI interaction.

@author: libor_komanek
"""
import sys
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from pathlib import Path
from PIL import Image
from PIL.ImageQt import ImageQt
from steganography import encode, decode, getImageInfo


qtCreatorFile: str = "LSBSteganography.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
imageDisplaySize: tuple[int, int] = 350, 350  # width, height of image previews displayed in GUI (in pixels)


class AppGUI(QMainWindow, Ui_MainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		# Default variable values
		self.loaded_file_path: str or None = None
		self.loaded_image: Image or None = None
		self.modified_image: Image or None = None
		# Link buttons to methods
		self.buttonLoadImage.clicked.connect(self.loadImageFile)
		self.buttonSaveImage.clicked.connect(self.saveImageFile)
		self.buttonEncodeMessage.clicked.connect(self.encodeMessage)
		self.buttonDecodeImage.clicked.connect(self.decodeImage)

	def loadImageFile(self) -> None:
		"""Opens up a dialog for selecting an existing image file and loads this image into the application."""
		try:
			caption: str = "Load a PNG or BMP image"
			starting_directory: str = str(Path.home())
			filters: str = "Images (*.png *.bmp)"
			file: str = QFileDialog.getOpenFileName(self, caption, starting_directory, filters)[0]
			if len(file) > 0:
				image: Image = Image.open(file, "r")
				self.loaded_image = image
				self.loaded_file_path = file
				self.displayImage()
				self.displayImageInfo()
			else:
				raise Warning("No image selected.")
		except Exception as e:
			self.showErrorMessage(e)

	def saveImageFile(self) -> None:
		"""Opens up a dialog for choosing destination directory and file name for the image modified by this application.
		The image is then saved under the specified name in the selected directory.
		"""
		try:
			image: Image = self.modified_image
			if image is None:
				raise Exception("You need to load an image first!")
			caption: str = "Save the modified image as a PNG or BMP file"
			starting_directory: str = str(Path.home())
			filters: str = "Images (*.png *.bmp)"
			file: str = QFileDialog.getSaveFileName(self, caption, starting_directory, filters)[0]
			image.save(file)
			if len(file) > 0:
				self.showInformativeMessage(f"The image has been saved to a file.\nAbsolute path to the new file:\n{file}")
			else:
				raise Exception("No file name entered!")
		except Exception as e:
			self.showErrorMessage(e)

	def displayImage(self, modified: bool = False) -> None:
		"""Displays the loaded or modified image in its respective preview fields in the GUI.

		:param modified: whether the modified image should be displayed instead of the original one
		"""
		try:
			label: QLabel = self.labelOriginalImagePreview
			image: Image = self.loaded_image
			if modified:
				label = self.labelModifiedImagePreview
				image = self.modified_image
			pixmap: QPixmap = QPixmap.fromImage(ImageQt(image))
			pixmap = pixmap.scaled(imageDisplaySize[0], imageDisplaySize[1], Qt.AspectRatioMode.KeepAspectRatio)
			label.resize(pixmap.width(), pixmap.height())
			label.setPixmap(pixmap)
		except Exception as e:
			self.showErrorMessage(e)

	def displayImageInfo(self) -> None:
		"""Fills the GUI fields with information gathered about the loaded image."""
		try:
			image: Image = self.loaded_image
			file: str = self.loaded_file_path
			info: dict = getImageInfo(image, file)

			self.fieldFileName.setText(info['name'])
			self.fieldExtension.setText(info['extension'])
			self.fieldDimensions.setText(f"{info['width']}x{info['height']} ({info['total_pixels']} pixels in total)")
			self.fieldAbsolutePath.setText(info['absolute_path'])
			self.fieldFileSize.setText(f"{info['file_size']} B")
			self.fieldColorMode.setText(info['color_mode'])
			self.fieldCapacity.setText(f"{info['capacity']} characters")
		except Exception as e:
			self.showErrorMessage(e)

	def encodeMessage(self) -> None:
		"""Calls the function for encoding a message in the loaded image and displays the modified image's preview."""
		try:
			image: Image = self.loaded_image
			if image is None:
				raise Exception("You need to load an image first!")
			message: str = self.fieldMessage.toPlainText()
			if len(message) < 1:
				raise Exception("You need to enter a message first!")
			modified_image: Image = encode(image, message)
			self.modified_image = modified_image
			self.displayImage(True)
		except Exception as e:
			self.showErrorMessage(e)

	def decodeImage(self) -> None:
		"""
		Calls the function for decoding the loaded image to find a hidden message and displays the result
		in the correct GUI field.
		"""
		try:
			image: Image = self.loaded_image
			if image is None:
				raise Exception("You need to load an image first!")
			message: str = decode(image)
			self.fieldResult.setPlainText(message)
		except Exception as e:
			self.showErrorMessage(e)

	@staticmethod
	def showErrorMessage(e: Exception) -> None:
		"""Shows a popup message with information about an Exception.

		:param e: the exception that occurred
		"""
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Icon.Critical)
		msg.setWindowTitle("Ooops!")
		msg.setText("Something went wrong!")
		msg.setInformativeText(str(e))
		msg.exec()

	@staticmethod
	def showInformativeMessage(message: str) -> None:
		"""Shows a popup message with information.

		:param message: message to be displayed
		"""
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Icon.Information)
		msg.setWindowTitle("Notification")
		msg.setText("Notification")
		msg.setInformativeText(message)
		msg.exec()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = AppGUI()
	window.show()
	sys.exit(app.exec())
