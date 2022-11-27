"""
Contains all the functions neccessary for LSB Image Steganography.

@author: libor_komanek
"""
import os
import numpy as np
from PIL import Image
from numpy.typing import NDArray
from unidecode import unidecode


def determineBytesPerPixel(mode: str) -> int:
	"""Determines the number of bytes in an image's single pixel based on its color mode.

	:param mode: image color mode
	:return: number of bytes in a pixel
	"""
	if mode == "RGB":
		return 3
	if mode == "RGBA":
		return 4
	raise Exception("This application only supports RGB and RGBA color modes!")


def calculateImageCapacity(img: Image) -> int:
	"""Calculates how many characters in total can be encoded in the given image.

	:param img: source image
	:return: number of characters encodable in the image
	"""
	bytes_per_pixel: int = determineBytesPerPixel(img.mode)  # dependent on image color mode
	capacity: int = img.width * img.height * bytes_per_pixel // 8
	return capacity


def clearLSBits(data: NDArray) -> NDArray:
	"""Sets the Least Significant Bit of every byte in the given data array to zero.

	:param data: array of image data
	:return: modified array of image data with every LSB set to zero
	"""
	for row in range(len(data)):
		for col in range(len(data[row])):
			data[row][col] &= 254
	return data


def encodeBits(data: NDArray, binary_string: str) -> NDArray:
	"""Encodes the given sequence of bits in the image data.
	Each bit in the sequence is stored as the least significant bit of bytes found in the data.

	:param data: array of image data with LSBs already set to zero
	:param binary_string: sequence of bits
	:return: array of image data containing a hidden message
	"""
	index: int = 0
	required_bytes: int = len(binary_string)
	for row in range(len(data)):
		for col in range(len(data[row])):
			if index < required_bytes:
				data[row][col] |= int(binary_string[index])  # bitwise OR
				index += 1
			else:
				return data


def encode(img: Image, message: str) -> Image:
	"""Encodes the given message in the given image.

	:param img: source image
	:param message: the message to be encoded in the image
	:return: modified image hiding a message
	"""
	capacity: int = calculateImageCapacity(img)
	message = unidecode(message)  # in this implementation, characters are limited to 8-bit size
	message_binary: str = "".join([format(ord(char), "08b") for char in message])
	if len(message_binary) > capacity:
		raise Exception(
			"The message is too long to be encoded in this image.\nTry choosing a shorter message or a bigger image.")

	data: NDArray = np.array(list(img.getdata()))  # load image data into an array
	data = clearLSBits(data)  # set the least significant bit of every byte in the image data to 0
	data = encodeBits(data, message_binary)  # encode message in binary code in the data
	bytes_per_pixel: int = determineBytesPerPixel(img.mode)
	size: tuple[int, int] = (img.height, img.width)
	data = data.reshape(*size, bytes_per_pixel)
	encoded_img: Image = Image.fromarray(data.astype("uint8"), img.mode)
	return encoded_img


def extractLSBits(data: NDArray) -> str:
	"""Extracts every Least Significant Bit in the given data array and stores them in a single string
	as a sequence of bits.

	:param data: array of image data
	:return: sequence of bits
	"""
	binary_string: str = ""
	for row in range(len(data)):
		for col in range(len(data[row])):
			binary_value: str = f"{data[row][col]:08b}"
			binary_string += binary_value[7]
	return binary_string


def convertBinaryStringToMessage(binary_string: str) -> str:
	"""Converts the sequence of bits into a string of ASCII characters.
	Any empty bytes (only containing zeros) are expected not to hold any information of value
	and are omitted.

	:param binary_string: sequence of bits
	:return: string of ASCII characters
	"""
	byte_list: list[str] = []
	# Split string into list of byte representations
	for i in range(0, len(binary_string), 8):
		byte_list.append(binary_string[i:i + 8])
	# Loop through the list of bytes and convert them into ASCII characters
	message: str = ""
	for representation in byte_list:
		if representation != "00000000":
			message += chr(int(representation, 2))
		else:
			return message  # a byte full of zeros means all encoded characters have already been decoded
	return message


def decode(img: Image) -> str:
	"""Finds a hidden message encoded in the given image.

	:param img: source image
	:return: discovered encoded message
	"""
	data: NDArray = np.array(list(img.getdata()))
	binary_string: str = extractLSBits(data)
	message: str = convertBinaryStringToMessage(binary_string)
	return message


def getImageInfo(img: Image, absolute_path: str) -> dict:
	"""Gathers information about an image and returns it in the form of a dictionary.

	Gathers this information:

	- name - name of the file (without the extension)
	- extension - the extension/type of the image
	- absolute_path - absolute path to the image
	- width - width in pixels
	- height - height in pixels
	- total_pixels - total number of pixels in the image
	- file_size - file size of the image in bytes
	- capacity - the maximum number of characters that can be encoded in the image using the LSB steganography
	- color_mode - the color mode of the image

	:param img: source image
	:param absolute_path: absolute path to image file
	:return: dictionary with information about the image
	"""
	width, height = img.size
	info: dict = {
		"name": os.path.splitext(os.path.basename(absolute_path))[0],
		"extension": img.format,
		"absolute_path": absolute_path,
		"width": width,
		"height": height,
		"total_pixels": width * height,
		"file_size": os.path.getsize(absolute_path),
		"capacity": calculateImageCapacity(img),
		"color_mode": img.mode
	}
	return info
